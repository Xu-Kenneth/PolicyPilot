"""
Report Generator Service - Production-Ready Implementation
Generates comprehensive JSON and Markdown reports with detailed statistics,
score aggregation, and actionable insights.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from app.config import settings
from app.models import AnalysisResult, SeverityLevel, IssueType


class ReportGenerator:
    """
    Production-ready report generator with comprehensive output formats.
    
    Features:
    - Detailed JSON reports with nested statistics
    - Rich Markdown reports with tables and charts
    - Score aggregation with confidence weighting
    - Actionable recommendations
    - Export-ready formats
    """
    
    def __init__(self):
        self.reports_dir = settings.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_json_report(self, result: AnalysisResult, report_id: str) -> Path:
        """
        Generate comprehensive JSON report with detailed statistics.
        
        Args:
            result: Analysis results
            report_id: Unique report identifier
            
        Returns:
            Path to generated report
        """
        report_path = self.reports_dir / f"{report_id}.json"
        
        # Build comprehensive report structure
        report_data = {
            "metadata": {
                "report_id": report_id,
                "project_name": result.project_name,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "generator_version": "1.0.0",
                "analysis_timestamp": result.timestamp.isoformat() + "Z"
            },
            "summary": {
                "total_score": round(result.total_score, 2),
                "grade": self._get_grade(result.total_score),
                "status": self._get_status(result.total_score),
                "passed": result.passed,
                "total_issues": result.total_issues,
                "critical_issues": result.critical_issues,
                "files_analyzed": result.files_analyzed
            },
            "scores": {
                "overall": {
                    "score": round(result.total_score, 2),
                    "max_score": 100.0,
                    "percentage": round(result.total_score, 2),
                    "grade": self._get_grade(result.total_score),
                    "passed": result.passed
                },
                "modules": [
                    {
                        "name": module.name,
                        "score": round(module.score, 2),
                        "weight": round(module.weight * 100, 1),
                        "weighted_score": round(module.weighted_score, 2),
                        "issues_count": module.issues_count,
                        "critical_issues": module.critical_issues,
                        "contribution_to_total": round(module.weighted_score, 2)
                    }
                    for module in result.module_scores
                ]
            },
            "secrets": {
                "total_found": len(result.secrets_found),
                "by_severity": self._group_secrets_by_severity(result.secrets_found),
                "by_type": self._group_secrets_by_type(result.secrets_found),
                "by_confidence": self._group_secrets_by_confidence(result.secrets_found),
                "statistics": {
                    "average_confidence": self._calculate_average_confidence(result.secrets_found),
                    "average_entropy": self._calculate_average_entropy(result.secrets_found),
                    "high_confidence_count": len([s for s in result.secrets_found if s.confidence >= 0.8]),
                    "unique_files": len(set(s.file_path for s in result.secrets_found))
                },
                "details": [
                    {
                        "pattern_name": secret.pattern_name,
                        "secret_type": secret.secret_type,
                        "file_path": secret.file_path,
                        "line_number": secret.line_number,
                        "column_start": secret.column_start,
                        "column_end": secret.column_end,
                        "matched_text": secret.matched_text,
                        "severity": secret.severity.value,
                        "confidence": round(secret.confidence, 3),
                        "entropy": round(secret.entropy, 3),
                        "reason": secret.reason,
                        "context_preview": secret.context[:200] if len(secret.context) > 200 else secret.context
                    }
                    for secret in result.secrets_found
                ]
            },
            "readme": self._format_readme_results(result.readme_result) if result.readme_result else None,
            "prompts": self._format_prompt_results(result.prompt_result) if result.prompt_result else None,
            "issues": {
                "total": len(result.all_issues),
                "by_severity": self._group_issues_by_severity(result.all_issues),
                "by_type": self._group_issues_by_type(result.all_issues),
                "details": [
                    {
                        "type": issue.type.value,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "details": issue.details
                    }
                    for issue in result.all_issues
                ]
            },
            "recommendations": self._generate_recommendations(result),
            "compliance": {
                "pass_threshold": settings.pass_threshold,
                "warning_threshold": settings.warning_threshold,
                "meets_requirements": result.passed,
                "areas_for_improvement": self._identify_improvement_areas(result)
            }
        }
        
        # Save with pretty formatting
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def generate_markdown_report(self, result: AnalysisResult, report_id: str) -> Path:
        """
        Generate comprehensive Markdown report with detailed statistics.
        
        Args:
            result: Analysis results
            report_id: Unique report identifier
            
        Returns:
            Path to generated report
        """
        report_path = self.reports_dir / f"{report_id}.md"
        
        # Generate comprehensive markdown content
        md_content = self._generate_comprehensive_markdown(result, report_id)
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return report_path
    
    def generate_html_report(self, result: AnalysisResult, report_id: str) -> Path:
        """
        Generate HTML report with enhanced styling.
        
        Args:
            result: Analysis results
            report_id: Unique report identifier
            
        Returns:
            Path to generated report
        """
        report_path = self.reports_dir / f"{report_id}.html"
        
        # Prepare context
        context = self._prepare_html_context(result)
        
        # Render template
        html_content = self._render_html_template(context)
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_comprehensive_markdown(self, result: AnalysisResult, report_id: str) -> str:
        """Generate comprehensive Markdown report content."""
        
        grade = self._get_grade(result.total_score)
        status = self._get_status(result.total_score)
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        md = f"""# 🛡️ PolicyPilot Analysis Report

**Report ID:** `{report_id}`  
**Generated:** {timestamp}

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Project Name** | {result.project_name} |
| **Overall Score** | **{result.total_score:.1f}/100** |
| **Grade** | **{grade}** |
| **Status** | **{status}** {'✅' if result.passed else '❌'} |
| **Total Issues** | {result.total_issues} |
| **Critical Issues** | {result.critical_issues} |
| **Files Analyzed** | {result.files_analyzed} |

"""
        
        # Score breakdown with visual indicators
        md += "## 🎯 Score Breakdown\n\n"
        md += "| Module | Score | Weight | Contribution | Issues | Status |\n"
        md += "|--------|-------|--------|--------------|--------|--------|\n"
        
        for module in result.module_scores:
            status_icon = "✅" if module.score >= 70 else "⚠️" if module.score >= 50 else "❌"
            bar = self._create_progress_bar(module.score)
            md += f"| {module.name} | {module.score:.1f} {bar} | {module.weight*100:.0f}% | {module.weighted_score:.1f} | {module.issues_count} | {status_icon} |\n"
        
        md += f"\n**Weighted Total:** {result.total_score:.1f}/100\n\n"
        
        # Secrets analysis
        if result.secrets_found:
            md += "## 🔒 Secrets Analysis\n\n"
            md += f"**Total Secrets Found:** {len(result.secrets_found)}\n\n"
            
            # Statistics
            avg_conf = self._calculate_average_confidence(result.secrets_found)
            avg_entropy = self._calculate_average_entropy(result.secrets_found)
            high_conf = len([s for s in result.secrets_found if s.confidence >= 0.8])
            
            md += "### Statistics\n\n"
            md += f"- **Average Confidence:** {avg_conf:.1%}\n"
            md += f"- **Average Entropy:** {avg_entropy:.2f}\n"
            md += f"- **High Confidence (≥80%):** {high_conf}\n"
            md += f"- **Unique Files:** {len(set(s.file_path for s in result.secrets_found))}\n\n"
            
            # By severity
            severity_groups = self._group_secrets_by_severity(result.secrets_found)
            if severity_groups:
                md += "### By Severity\n\n"
                md += "| Severity | Count | Percentage |\n"
                md += "|----------|-------|------------|\n"
                for severity, count in sorted(severity_groups.items(), key=lambda x: self._severity_order(x[0])):
                    pct = (count / len(result.secrets_found)) * 100
                    md += f"| {severity.upper()} | {count} | {pct:.1f}% |\n"
                md += "\n"
            
            # By type
            type_groups = self._group_secrets_by_type(result.secrets_found)
            if type_groups:
                md += "### By Type\n\n"
                md += "| Secret Type | Count |\n"
                md += "|-------------|-------|\n"
                for secret_type, count in sorted(type_groups.items(), key=lambda x: x[1], reverse=True)[:10]:
                    md += f"| {secret_type} | {count} |\n"
                md += "\n"
            
            # Detailed list (top 20)
            md += "### Detected Secrets (Top 20)\n\n"
            for i, secret in enumerate(result.secrets_found[:20], 1):
                severity_emoji = self._get_severity_emoji(secret.severity.value)
                md += f"#### {i}. {severity_emoji} {secret.pattern_name}\n\n"
                md += f"- **Type:** `{secret.secret_type}`\n"
                md += f"- **Severity:** {secret.severity.value.upper()}\n"
                md += f"- **Location:** `{secret.file_path}:{secret.line_number}:{secret.column_start}`\n"
                md += f"- **Confidence:** {secret.confidence:.1%} | **Entropy:** {secret.entropy:.2f}\n"
                md += f"- **Matched:** `{secret.matched_text}`\n"
                md += f"- **Reason:** {secret.reason}\n\n"
            
            if len(result.secrets_found) > 20:
                md += f"*... and {len(result.secrets_found) - 20} more secrets. See JSON report for complete list.*\n\n"
        
        # README analysis
        if result.readme_result:
            md += "## 📝 README Analysis\n\n"
            md += f"- **Exists:** {'✅ Yes' if result.readme_result.exists else '❌ No'}\n"
            md += f"- **Score:** {result.readme_result.score:.1f}/100\n"
            md += f"- **Word Count:** {result.readme_result.word_count}\n"
            md += f"- **Has Required Sections:** {'✅ Yes' if result.readme_result.has_required_sections else '❌ No'}\n\n"
            
            if result.readme_result.missing_required:
                md += "**Missing Required Sections:**\n"
                for section in result.readme_result.missing_required:
                    md += f"- {section}\n"
                md += "\n"
            
            if result.readme_result.missing_recommended:
                md += "**Missing Recommended Sections:**\n"
                for section in result.readme_result.missing_recommended:
                    md += f"- {section}\n"
                md += "\n"
        
        # Prompt documentation
        if result.prompt_result:
            md += "## 📋 Prompt Documentation\n\n"
            md += f"- **Total Prompts:** {result.prompt_result.total_prompts}\n"
            md += f"- **Documented:** {result.prompt_result.documented_prompts}\n"
            md += f"- **Score:** {result.prompt_result.score:.1f}/100\n\n"
            
            if result.prompt_result.missing_fields:
                md += "**Missing Documentation Fields:**\n\n"
                for prompt, fields in result.prompt_result.missing_fields.items():
                    md += f"- `{prompt}`: {', '.join(fields)}\n"
                md += "\n"
        
        # All issues grouped by severity
        if result.all_issues:
            md += f"## ⚠️ All Issues ({len(result.all_issues)})\n\n"
            
            for severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM, SeverityLevel.LOW, SeverityLevel.INFO]:
                severity_issues = [i for i in result.all_issues if i.severity == severity]
                if severity_issues:
                    emoji = self._get_severity_emoji(severity.value)
                    md += f"### {emoji} {severity.value.upper()} ({len(severity_issues)})\n\n"
                    
                    for issue in severity_issues[:15]:  # Limit to 15 per severity
                        md += f"- **{issue.message}**\n"
                        if issue.file_path:
                            location = f"`{issue.file_path}`"
                            if issue.line_number:
                                location += f":{issue.line_number}"
                            md += f"  - Location: {location}\n"
                        if issue.details:
                            md += f"  - Details: {json.dumps(issue.details, indent=2)}\n"
                    
                    if len(severity_issues) > 15:
                        md += f"\n*... and {len(severity_issues) - 15} more {severity.value} issues*\n"
                    md += "\n"
        
        # Recommendations
        recommendations = self._generate_recommendations(result)
        if recommendations:
            md += "## 💡 Recommendations\n\n"
            for i, rec in enumerate(recommendations, 1):
                md += f"{i}. {rec}\n"
            md += "\n"
        
        # Compliance status
        md += "## ✅ Compliance Status\n\n"
        md += f"- **Pass Threshold:** {settings.pass_threshold}\n"
        md += f"- **Warning Threshold:** {settings.warning_threshold}\n"
        md += f"- **Current Score:** {result.total_score:.1f}\n"
        md += f"- **Status:** **{status}** {'✅' if result.passed else '❌'}\n\n"
        
        if not result.passed:
            points_needed = settings.pass_threshold - result.total_score
            md += f"**Points needed to pass:** {points_needed:.1f}\n\n"
        
        # Areas for improvement
        improvement_areas = self._identify_improvement_areas(result)
        if improvement_areas:
            md += "### Areas for Improvement\n\n"
            for area in improvement_areas:
                md += f"- {area}\n"
            md += "\n"
        
        # Footer
        md += "---\n\n"
        md += f"*Report generated by PolicyPilot v1.0.0*  \n"
        md += f"*IBM watsonx Policy Compliance Checker*  \n"
        md += f"*{timestamp}*\n"
        
        return md
    
    def _create_progress_bar(self, score: float, width: int = 10) -> str:
        """Create a text-based progress bar."""
        filled = int((score / 100) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level."""
        emojis = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': '⚪'
        }
        return emojis.get(severity.lower(), '⚪')
    
    def _severity_order(self, severity: str) -> int:
        """Get sort order for severity."""
        order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        return order.get(severity.lower(), 999)
    
    def _group_secrets_by_severity(self, secrets: List) -> Dict[str, int]:
        """Group secrets by severity level."""
        groups = {}
        for secret in secrets:
            severity = secret.severity.value
            groups[severity] = groups.get(severity, 0) + 1
        return groups
    
    def _group_secrets_by_type(self, secrets: List) -> Dict[str, int]:
        """Group secrets by type."""
        groups = {}
        for secret in secrets:
            secret_type = secret.secret_type
            groups[secret_type] = groups.get(secret_type, 0) + 1
        return groups
    
    def _group_secrets_by_confidence(self, secrets: List) -> Dict[str, int]:
        """Group secrets by confidence level."""
        groups = {
            'high': 0,      # >= 0.8
            'medium': 0,    # 0.5 - 0.8
            'low': 0        # < 0.5
        }
        for secret in secrets:
            if secret.confidence >= 0.8:
                groups['high'] += 1
            elif secret.confidence >= 0.5:
                groups['medium'] += 1
            else:
                groups['low'] += 1
        return groups
    
    def _calculate_average_confidence(self, secrets: List) -> float:
        """Calculate average confidence score."""
        if not secrets:
            return 0.0
        return sum(s.confidence for s in secrets) / len(secrets)
    
    def _calculate_average_entropy(self, secrets: List) -> float:
        """Calculate average entropy."""
        if not secrets:
            return 0.0
        return sum(s.entropy for s in secrets) / len(secrets)
    
    def _group_issues_by_severity(self, issues: List) -> Dict[str, int]:
        """Group issues by severity."""
        groups = {}
        for issue in issues:
            severity = issue.severity.value
            groups[severity] = groups.get(severity, 0) + 1
        return groups
    
    def _group_issues_by_type(self, issues: List) -> Dict[str, int]:
        """Group issues by type."""
        groups = {}
        for issue in issues:
            issue_type = issue.type.value
            groups[issue_type] = groups.get(issue_type, 0) + 1
        return groups
    
    def _format_readme_results(self, readme_result) -> Dict[str, Any]:
        """Format README results for JSON output."""
        return {
            "exists": readme_result.exists,
            "has_required_sections": readme_result.has_required_sections,
            "score": round(readme_result.score, 2),
            "word_count": readme_result.word_count,
            "missing_required": readme_result.missing_required,
            "missing_recommended": readme_result.missing_recommended,
            "issues_count": len(readme_result.issues)
        }
    
    def _format_prompt_results(self, prompt_result) -> Dict[str, Any]:
        """Format prompt results for JSON output."""
        return {
            "total_prompts": prompt_result.total_prompts,
            "documented_prompts": prompt_result.documented_prompts,
            "documentation_rate": round((prompt_result.documented_prompts / prompt_result.total_prompts * 100) if prompt_result.total_prompts > 0 else 100, 2),
            "score": round(prompt_result.score, 2),
            "missing_fields": prompt_result.missing_fields,
            "issues_count": len(prompt_result.issues)
        }
    
    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate actionable recommendations."""
        from app.services.scoring_engine import scoring_engine
        return scoring_engine.get_recommendations(result)
    
    def _identify_improvement_areas(self, result: AnalysisResult) -> List[str]:
        """Identify specific areas for improvement."""
        areas = []
        
        for module in result.module_scores:
            if module.score < 70:
                areas.append(f"{module.name}: Score {module.score:.1f}/100 - {module.issues_count} issues to address")
        
        return areas
    
    def _get_grade(self, score: float) -> str:
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
    
    def _get_status(self, score: float) -> str:
        """Get status for score."""
        if score >= settings.pass_threshold:
            return "PASS"
        elif score >= settings.warning_threshold:
            return "WARNING"
        else:
            return "FAIL"
    
    def _prepare_html_context(self, result: AnalysisResult) -> dict:
        """Prepare context for HTML template."""
        from app.services.scoring_engine import scoring_engine
        
        return {
            'result': result,
            'grade': self._get_grade(result.total_score),
            'status': self._get_status(result.total_score),
            'recommendations': scoring_engine.get_recommendations(result),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'severity_colors': {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#17a2b8',
                'info': '#6c757d'
            }
        }
    
    def _render_html_template(self, context: dict) -> str:
        """Render HTML template."""
        # Use inline template (same as before, keeping it for compatibility)
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolicyPilot Analysis Report - {{ result.project_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 3px solid #0f62fe; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #0f62fe; font-size: 2em; margin-bottom: 10px; }
        .header .meta { color: #666; font-size: 0.9em; }
        .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; text-align: center; }
        .score-card .score { font-size: 4em; font-weight: bold; margin: 10px 0; }
        .score-card .grade { font-size: 2em; opacity: 0.9; }
        .score-card .status { font-size: 1.2em; margin-top: 10px; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 20px; display: inline-block; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-item { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0f62fe; }
        .summary-item .label { color: #666; font-size: 0.9em; margin-bottom: 5px; }
        .summary-item .value { font-size: 1.8em; font-weight: bold; color: #333; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #0f62fe; font-size: 1.5em; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e0e0e0; }
        .module-scores { display: grid; gap: 15px; }
        .module-score { background: #f8f9fa; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .module-score .name { font-weight: 600; }
        .module-score .score { font-size: 1.5em; font-weight: bold; color: #0f62fe; }
        .issue { background: white; border-left: 4px solid #ccc; padding: 15px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .issue.critical { border-left-color: #dc3545; }
        .issue.high { border-left-color: #fd7e14; }
        .issue.medium { border-left-color: #ffc107; }
        .issue.low { border-left-color: #17a2b8; }
        .issue .severity { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.85em; font-weight: 600; color: white; margin-right: 10px; }
        .issue .severity.critical { background: #dc3545; }
        .issue .severity.high { background: #fd7e14; }
        .issue .severity.medium { background: #ffc107; color: #333; }
        .issue .severity.low { background: #17a2b8; }
        .issue .message { margin: 5px 0; }
        .issue .file { color: #666; font-size: 0.9em; font-family: monospace; }
        .recommendations { background: #e7f3ff; border-left: 4px solid #0f62fe; padding: 20px; border-radius: 4px; }
        .recommendations ul { list-style: none; }
        .recommendations li { padding: 8px 0; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ PolicyPilot Analysis Report</h1>
            <div class="meta">
                <strong>Project:</strong> {{ result.project_name }} | 
                <strong>Generated:</strong> {{ timestamp }} | 
                <strong>Files Analyzed:</strong> {{ result.files_analyzed }}
            </div>
        </div>

        <div class="score-card">
            <div class="grade">Grade: {{ grade }}</div>
            <div class="score">{{ "%.1f"|format(result.total_score) }}</div>
            <div class="status">{{ status }}</div>
        </div>

        <div class="summary">
            <div class="summary-item">
                <div class="label">Total Issues</div>
                <div class="value">{{ result.total_issues }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Critical Issues</div>
                <div class="value" style="color: #dc3545;">{{ result.critical_issues }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Secrets Found</div>
                <div class="value" style="color: #fd7e14;">{{ result.secrets_found|length }}</div>
            </div>
            <div class="summary-item">
                <div class="label">Files Analyzed</div>
                <div class="value">{{ result.files_analyzed }}</div>
            </div>
        </div>

        {% if recommendations %}
        <div class="section">
            <h2>📋 Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {% for rec in recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>📊 Module Scores</h2>
            <div class="module-scores">
                {% for module in result.module_scores %}
                <div class="module-score">
                    <div>
                        <div class="name">{{ module.name }}</div>
                        <div style="font-size: 0.9em; color: #666;">
                            Weight: {{ "%.0f"|format(module.weight * 100) }}% | 
                            Issues: {{ module.issues_count }}
                        </div>
                    </div>
                    <div class="score">{{ "%.1f"|format(module.score) }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        {% if result.all_issues %}
        <div class="section">
            <h2>⚠️ Issues Found ({{ result.all_issues|length }})</h2>
            {% for issue in result.all_issues[:20] %}
            <div class="issue {{ issue.severity.value }}">
                <span class="severity {{ issue.severity.value }}">{{ issue.severity.value.upper() }}</span>
                <div class="message">{{ issue.message }}</div>
                {% if issue.file_path %}
                <div class="file">📄 {{ issue.file_path }}{% if issue.line_number %}:{{ issue.line_number }}{% endif %}</div>
                {% endif %}
            </div>
            {% endfor %}
            {% if result.all_issues|length > 20 %}
            <p style="text-align: center; color: #666; margin-top: 15px;">
                ... and {{ result.all_issues|length - 20 }} more issues
            </p>
            {% endif %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by PolicyPilot v1.0.0 | IBM watsonx Policy Compliance Checker</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_content)
        return template.render(**context)
    
    def get_report_path(self, report_id: str, format: str = 'json') -> Optional[Path]:
        """
        Get path to an existing report.
        
        Args:
            report_id: Report identifier
            format: Report format (json, html, md)
            
        Returns:
            Path to report or None if not found
        """
        report_path = self.reports_dir / f"{report_id}.{format}"
        return report_path if report_path.exists() else None


# Global instance
report_generator = ReportGenerator()

# Made with Bob
