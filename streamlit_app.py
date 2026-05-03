"""
PolicyPilot Streamlit Frontend
IBM watsonx.ai Policy Compliance Analyzer

This Streamlit app provides a user-friendly interface for the PolicyPilot backend API.
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import io

# Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="PolicyPilot - Compliance Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .score-excellent {
        color: #28a745;
        font-weight: bold;
    }
    .score-good {
        color: #17a2b8;
        font-weight: bold;
    }
    .score-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .score-fail {
        color: #dc3545;
        font-weight: bold;
    }
    .severity-critical {
        background-color: #dc3545;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .severity-high {
        background-color: #fd7e14;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .severity-medium {
        background-color: #ffc107;
        color: black;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .severity-low {
        background-color: #17a2b8;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# API Functions
def check_api_health() -> bool:
    """Check if the backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_files(files: List) -> Dict[str, Any]:
    """Upload files to the backend API."""
    files_data = [("files", (file.name, file, file.type)) for file in files]
    response = requests.post(f"{API_BASE_URL}/api/upload", files=files_data)
    response.raise_for_status()
    return response.json()


def analyze_project(upload_id: str, project_name: str) -> Dict[str, Any]:
    """Analyze uploaded project files."""
    response = requests.post(
        f"{API_BASE_URL}/api/analyze",
        json={"upload_id": upload_id, "project_name": project_name}
    )
    response.raise_for_status()
    return response.json()


def upload_and_analyze(files: List, project_name: str) -> Dict[str, Any]:
    """Upload and analyze in one request."""
    files_data = [("files", (file.name, file, file.type)) for file in files]
    data = {"project_name": project_name}
    response = requests.post(
        f"{API_BASE_URL}/api/upload-and-analyze",
        files=files_data,
        data=data
    )
    response.raise_for_status()
    return response.json()


def download_report(upload_id: str, format: str = "json") -> bytes:
    """Download generated report."""
    response = requests.get(f"{API_BASE_URL}/api/report/{upload_id}/{format}")
    response.raise_for_status()
    return response.content


def get_config() -> Dict[str, Any]:
    """Get backend configuration."""
    response = requests.get(f"{API_BASE_URL}/api/config")
    response.raise_for_status()
    return response.json()


# UI Helper Functions
def get_score_class(score: float) -> str:
    """Get CSS class for score display."""
    if score >= 90:
        return "score-excellent"
    elif score >= 80:
        return "score-good"
    elif score >= 70:
        return "score-warning"
    else:
        return "score-fail"


def get_grade(score: float) -> str:
    """Get letter grade for score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def display_score_gauge(score: float, passed: bool):
    """Display score gauge with visual indicator."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score_class = get_score_class(score)
        grade = get_grade(score)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
            <h1 style="font-size: 4rem; margin: 0;">{score:.1f}</h1>
            <h2 style="margin: 0.5rem 0;">Grade {grade}</h2>
            <h3 style="margin: 0;">{status}</h3>
        </div>
        """, unsafe_allow_html=True)


def display_module_scores(module_scores: List[Dict]):
    """Display module scores with progress bars."""
    st.subheader("📊 Module Breakdown")
    
    for module in module_scores:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{module['name']}**")
            st.progress(module['score'] / 100)
        
        with col2:
            st.metric("Score", f"{module['score']:.1f}")
        
        with col3:
            st.metric("Issues", module['issues_count'])
        
        # Show details in expander
        with st.expander(f"Details for {module['name']}"):
            st.write(f"**Weight:** {module['weight'] * 100:.0f}%")
            st.write(f"**Weighted Score:** {module['weighted_score']:.2f}")
            st.write(f"**Critical Issues:** {module['critical_issues']}")


def display_secrets(secrets: List[Dict]):
    """Display detected secrets."""
    if not secrets:
        st.success("✅ No secrets detected!")
        return
    
    st.error(f"🔒 {len(secrets)} Secret(s) Detected")
    
    for i, secret in enumerate(secrets, 1):
        with st.expander(f"Secret #{i}: {secret['pattern_name']} - {secret['severity'].upper()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**File:** `{secret['file_path']}`")
                st.write(f"**Line:** {secret['line_number']}")
                st.write(f"**Type:** {secret['secret_type']}")
            
            with col2:
                st.write(f"**Severity:** {secret['severity'].upper()}")
                st.write(f"**Confidence:** {secret['confidence']:.2f}")
                st.write(f"**Entropy:** {secret['entropy']:.2f}")
            
            st.write(f"**Matched Text:** `{secret['matched_text']}`")
            st.code(secret['context'], language="python")
            st.info(f"💡 **Reason:** {secret['reason']}")


def display_readme_result(readme: Dict):
    """Display README validation results."""
    if not readme:
        st.warning("⚠️ No README.md found")
        return
    
    st.subheader("📝 README Validation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score", f"{readme['score']:.1f}")
    
    with col2:
        st.metric("Word Count", readme['word_count'])
    
    with col3:
        status = "✅ Complete" if readme['has_required_sections'] else "❌ Incomplete"
        st.metric("Status", status)
    
    if readme['missing_required']:
        st.error("**Missing Required Sections:**")
        for section in readme['missing_required']:
            st.write(f"- {section}")
    
    if readme['missing_recommended']:
        st.warning("**Missing Recommended Sections:**")
        for section in readme['missing_recommended']:
            st.write(f"- {section}")


def display_prompt_result(prompt: Dict):
    """Display prompt documentation results."""
    if not prompt:
        st.info("ℹ️ No prompt files found")
        return
    
    st.subheader("📋 Prompt Documentation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score", f"{prompt['score']:.1f}")
    
    with col2:
        st.metric("Total Prompts", prompt['total_prompts'])
    
    with col3:
        st.metric("Documented", prompt['documented_prompts'])
    
    if prompt['missing_fields']:
        st.warning("**Files with Missing Fields:**")
        for filepath, fields in prompt['missing_fields'].items():
            st.write(f"**{filepath}:**")
            for field in fields:
                st.write(f"  - {field}")


def display_all_issues(issues: List[Dict]):
    """Display all issues in a table."""
    if not issues:
        st.success("✅ No issues found!")
        return
    
    st.subheader(f"⚠️ All Issues ({len(issues)})")
    
    # Convert to DataFrame for better display
    df_data = []
    for issue in issues:
        df_data.append({
            "Type": issue['type'],
            "Severity": issue['severity'],
            "Message": issue['message'],
            "File": issue.get('file_path', 'N/A'),
            "Line": issue.get('line_number', 'N/A')
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)


# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 PolicyPilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">IBM watsonx.ai Policy Compliance Analyzer</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=PolicyPilot", use_column_width=True)
        st.markdown("---")
        
        # API Health Check
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Unavailable")
            st.info(f"Backend URL: {API_BASE_URL}")
            st.stop()
        
        # Configuration
        try:
            config = get_config()
            st.subheader("⚙️ Configuration")
            st.write(f"**Version:** {config['version']}")
            st.write(f"**Pass Threshold:** {config['pass_threshold']}")
            st.write(f"**Max Upload:** {config['max_upload_size_mb']:.0f} MB")
        except:
            st.warning("Could not load configuration")
        
        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("- [Architecture](ARCHITECTURE.md)")
        st.markdown("- [API Reference](backend/FRONTEND_BACKEND_INTEGRATION.md)")
        st.markdown("- [Quick Start](QUICK_START.md)")
    
    # Main Content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📊 Results", "📄 Reports"])
    
    with tab1:
        st.header("Upload Project Files")
        
        # Project name input
        project_name = st.text_input(
            "Project Name",
            value="My Project",
            help="Enter a name for your project"
        )
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to analyze",
            accept_multiple_files=True,
            help="Upload Python, Markdown, JSON, YAML, and other project files"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")
            
            # Show file list
            with st.expander("View uploaded files"):
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.size} bytes)")
            
            # Analyze button
            if st.button("🔍 Analyze Project", type="primary", use_container_width=True):
                with st.spinner("Analyzing project..."):
                    try:
                        # Upload and analyze
                        result = upload_and_analyze(uploaded_files, project_name)
                        
                        # Store result in session state
                        st.session_state['analysis_result'] = result
                        st.session_state['upload_id'] = result.get('upload_id')
                        
                        st.success("✅ Analysis complete!")
                        st.balloons()
                        
                        # Switch to results tab
                        st.info("👉 Check the 'Results' tab to view detailed analysis")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
    
    with tab2:
        st.header("Analysis Results")
        
        if 'analysis_result' not in st.session_state:
            st.info("👈 Upload and analyze files first")
        else:
            result = st.session_state['analysis_result']
            
            # Project info
            st.subheader("📋 Project Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Project", result['project_name'])
            
            with col2:
                timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
                st.metric("Analyzed", timestamp.strftime("%Y-%m-%d %H:%M"))
            
            with col3:
                st.metric("Files", result['files_analyzed'])
            
            st.markdown("---")
            
            # Score gauge
            display_score_gauge(result['total_score'], result['passed'])
            
            st.markdown("---")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Issues", result['total_issues'])
            
            with col2:
                st.metric("Critical Issues", result['critical_issues'], 
                         delta=None if result['critical_issues'] == 0 else "⚠️")
            
            with col3:
                status = "PASS" if result['passed'] else "FAIL"
                st.metric("Status", status)
            
            st.markdown("---")
            
            # Module scores
            display_module_scores(result['module_scores'])
            
            st.markdown("---")
            
            # Detailed results in tabs
            detail_tabs = st.tabs(["🔒 Secrets", "📝 README", "📋 Prompts", "⚠️ All Issues"])
            
            with detail_tabs[0]:
                display_secrets(result['secrets_found'])
            
            with detail_tabs[1]:
                display_readme_result(result.get('readme_result'))
            
            with detail_tabs[2]:
                display_prompt_result(result.get('prompt_result'))
            
            with detail_tabs[3]:
                display_all_issues(result.get('all_issues', []))
    
    with tab3:
        st.header("Download Reports")
        
        if 'upload_id' not in st.session_state:
            st.info("👈 Analyze a project first to generate reports")
        else:
            upload_id = st.session_state['upload_id']
            
            st.write("Download your analysis report in multiple formats:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📄 JSON")
                st.write("Machine-readable format for automation")
                if st.button("Download JSON", use_container_width=True):
                    try:
                        report = download_report(upload_id, "json")
                        st.download_button(
                            label="💾 Save JSON Report",
                            data=report,
                            file_name=f"policypilot_report_{upload_id}.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("🌐 HTML")
                st.write("Interactive web report")
                if st.button("Download HTML", use_container_width=True):
                    try:
                        report = download_report(upload_id, "html")
                        st.download_button(
                            label="💾 Save HTML Report",
                            data=report,
                            file_name=f"policypilot_report_{upload_id}.html",
                            mime="text/html"
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col3:
                st.subheader("📝 Markdown")
                st.write("GitHub-friendly documentation")
                if st.button("Download Markdown", use_container_width=True):
                    try:
                        report = download_report(upload_id, "md")
                        st.download_button(
                            label="💾 Save Markdown Report",
                            data=report,
                            file_name=f"policypilot_report_{upload_id}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Preview JSON report
            if st.checkbox("Preview JSON Report"):
                try:
                    report = download_report(upload_id, "json")
                    report_data = json.loads(report)
                    st.json(report_data)
                except Exception as e:
                    st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

# Made with Bob
