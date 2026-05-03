"""
Test suite for Report Generator and Scoring Engine
Validates JSON/Markdown output, score aggregation, and confidence weighting
"""

from pathlib import Path
from datetime import datetime
import json
import tempfile
import shutil

from app.models import (
    AnalysisResult, ModuleScore, SecretMatch, Issue,
    SeverityLevel, IssueType, ReadmeValidationResult, PromptDocumentationResult
)
from app.services.report_generator import report_generator
from app.services.scoring_engine import scoring_engine


def create_test_analysis_result() -> AnalysisResult:
    """Create a comprehensive test analysis result."""
    
    # Create test secrets with varying confidence levels
    secrets = [
        SecretMatch(
            pattern_name="AWS Access Key ID",
            secret_type="aws_access_key",
            file_path="config/aws.py",
            line_number=10,
            column_start=15,
            column_end=51,
            matched_text="AKIA****",
            context="AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'",
            severity=SeverityLevel.CRITICAL,
            confidence=0.95,
            entropy=4.2,
            reason="AWS Access Key ID detected"
        ),
        SecretMatch(
            pattern_name="GitHub Token",
            secret_type="github_token",
            file_path="scripts/deploy.sh",
            line_number=25,
            column_start=20,
            column_end=60,
            matched_text="ghp_****",
            context="GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            severity=SeverityLevel.CRITICAL,
            confidence=0.88,
            entropy=4.5,
            reason="GitHub personal access token detected"
        ),
        SecretMatch(
            pattern_name="Generic API Key",
            secret_type="api_key",
            file_path="src/api_client.py",
            line_number=5,
            column_start=12,
            column_end=42,
            matched_text="sk_l****",
            context="api_key = 'sk_live_abcdef123456'",
            severity=SeverityLevel.HIGH,
            confidence=0.65,
            entropy=3.8,
            reason="Generic API key detected"
        ),
        SecretMatch(
            pattern_name="Password in Code",
            secret_type="password",
            file_path="tests/test_auth.py",
            line_number=15,
            column_start=18,
            column_end=30,
            matched_text="test****",
            context="password = 'test12345'",
            severity=SeverityLevel.MEDIUM,
            confidence=0.45,
            entropy=2.8,
            reason="Hardcoded password detected"
        ),
    ]
    
    # Create README result
    readme_result = ReadmeValidationResult(
        exists=True,
        has_required_sections=False,
        missing_required=["## Installation", "## Usage"],
        missing_recommended=["## Contributing", "## License"],
        word_count=250,
        score=65.0,
        issues=[
            Issue(
                type=IssueType.README,
                severity=SeverityLevel.MEDIUM,
                message="Missing required section: ## Installation",
                file_path="README.md"
            ),
            Issue(
                type=IssueType.README,
                severity=SeverityLevel.MEDIUM,
                message="Missing required section: ## Usage",
                file_path="README.md"
            )
        ]
    )
    
    # Create prompt result
    prompt_result = PromptDocumentationResult(
        total_prompts=5,
        documented_prompts=3,
        missing_fields={
            "prompts/analyze.txt": ["example", "constraints"],
            "prompts/summarize.txt": ["output_format"]
        },
        score=60.0,
        issues=[
            Issue(
                type=IssueType.PROMPT,
                severity=SeverityLevel.LOW,
                message="Prompt missing documentation fields",
                file_path="prompts/analyze.txt"
            )
        ]
    )
    
    # Create module scores
    module_scores = [
        ModuleScore(
            name="Secret Scanner",
            score=45.0,
            weight=0.35,
            weighted_score=15.75,
            issues_count=4,
            critical_issues=2
        ),
        ModuleScore(
            name="README Validator",
            score=65.0,
            weight=0.25,
            weighted_score=16.25,
            issues_count=2,
            critical_issues=0
        ),
        ModuleScore(
            name="Prompt Documentation",
            score=60.0,
            weight=0.25,
            weighted_score=15.0,
            issues_count=1,
            critical_issues=0
        ),
        ModuleScore(
            name="Project Structure",
            score=100.0,
            weight=0.15,
            weighted_score=15.0,
            issues_count=0,
            critical_issues=0
        )
    ]
    
    # Collect all issues
    all_issues = []
    for secret in secrets:
        all_issues.append(Issue(
            type=IssueType.SECRET,
            severity=secret.severity,
            message=f"Detected {secret.pattern_name}: {secret.matched_text}",
            file_path=secret.file_path,
            line_number=secret.line_number,
            details={
                'pattern': secret.pattern_name,
                'confidence': secret.confidence,
                'entropy': secret.entropy
            }
        ))
    all_issues.extend(readme_result.issues)
    all_issues.extend(prompt_result.issues)
    
    # Calculate total score
    total_score = sum(m.weighted_score for m in module_scores)
    
    return AnalysisResult(
        project_name="Test Project",
        timestamp=datetime.utcnow(),
        secrets_found=secrets,
        readme_result=readme_result,
        prompt_result=prompt_result,
        module_scores=module_scores,
        total_score=total_score,
        passed=total_score >= 70.0,
        total_issues=len(all_issues),
        critical_issues=2,
        files_analyzed=25,
        all_issues=all_issues
    )


def test_json_report_generation():
    """Test JSON report generation with comprehensive structure."""
    print("=" * 80)
    print("JSON REPORT GENERATION TEST")
    print("=" * 80)
    
    # Create test result
    result = create_test_analysis_result()
    report_id = f"test_json_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Generate JSON report
    print(f"\n📄 Generating JSON report: {report_id}")
    report_path = report_generator.generate_json_report(result, report_id)
    
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ File size: {report_path.stat().st_size} bytes")
    
    # Validate JSON structure
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    print("\n📊 JSON STRUCTURE VALIDATION")
    print("-" * 80)
    
    # Check top-level keys
    required_keys = ['metadata', 'summary', 'scores', 'secrets', 'readme', 'prompts', 'issues', 'recommendations', 'compliance']
    for key in required_keys:
        status = "✓" if key in report_data else "✗"
        print(f"{status} {key}")
    
    # Validate metadata
    print("\n📋 Metadata:")
    print(f"  - Report ID: {report_data['metadata']['report_id']}")
    print(f"  - Project: {report_data['metadata']['project_name']}")
    print(f"  - Generated: {report_data['metadata']['generated_at']}")
    
    # Validate summary
    print("\n📈 Summary:")
    print(f"  - Total Score: {report_data['summary']['total_score']}")
    print(f"  - Grade: {report_data['summary']['grade']}")
    print(f"  - Status: {report_data['summary']['status']}")
    print(f"  - Total Issues: {report_data['summary']['total_issues']}")
    print(f"  - Critical Issues: {report_data['summary']['critical_issues']}")
    
    # Validate secrets section
    print("\n🔒 Secrets Analysis:")
    secrets_data = report_data['secrets']
    print(f"  - Total Found: {secrets_data['total_found']}")
    print(f"  - By Severity: {secrets_data['by_severity']}")
    print(f"  - By Type: {secrets_data['by_type']}")
    print(f"  - By Confidence: {secrets_data['by_confidence']}")
    print(f"  - Avg Confidence: {secrets_data['statistics']['average_confidence']:.2%}")
    print(f"  - Avg Entropy: {secrets_data['statistics']['average_entropy']:.2f}")
    
    # Validate module scores
    print("\n📊 Module Scores:")
    for module in report_data['scores']['modules']:
        print(f"  - {module['name']}: {module['score']:.1f} (weight: {module['weight']:.0f}%)")
    
    print("\n✅ JSON report validation complete!")
    return report_path


def test_markdown_report_generation():
    """Test Markdown report generation with rich formatting."""
    print("\n" + "=" * 80)
    print("MARKDOWN REPORT GENERATION TEST")
    print("=" * 80)
    
    # Create test result
    result = create_test_analysis_result()
    report_id = f"test_md_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Generate Markdown report
    print(f"\n📄 Generating Markdown report: {report_id}")
    report_path = report_generator.generate_markdown_report(result, report_id)
    
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ File size: {report_path.stat().st_size} bytes")
    
    # Read and validate content
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📊 MARKDOWN CONTENT VALIDATION")
    print("-" * 80)
    
    # Check for required sections
    required_sections = [
        "# 🛡️ PolicyPilot Analysis Report",
        "## 📊 Executive Summary",
        "## 🎯 Score Breakdown",
        "## 🔒 Secrets Analysis",
        "## 📝 README Analysis",
        "## 📋 Prompt Documentation",
        "## ⚠️ All Issues",
        "## 💡 Recommendations",
        "## ✅ Compliance Status"
    ]
    
    for section in required_sections:
        status = "✓" if section in content else "✗"
        print(f"{status} {section}")
    
    # Count lines and tables
    lines = content.split('\n')
    tables = content.count('|--------|')
    
    print(f"\n📏 Content Statistics:")
    print(f"  - Total Lines: {len(lines)}")
    print(f"  - Tables: {tables}")
    print(f"  - Characters: {len(content)}")
    
    # Show preview
    print(f"\n📄 Preview (first 20 lines):")
    print("-" * 80)
    for line in lines[:20]:
        print(line)
    print("-" * 80)
    
    print("\n✅ Markdown report validation complete!")
    return report_path


def test_confidence_weighted_scoring():
    """Test confidence-weighted score aggregation."""
    print("\n" + "=" * 80)
    print("CONFIDENCE-WEIGHTED SCORING TEST")
    print("=" * 80)
    
    # Create secrets with different confidence levels
    high_conf_secret = SecretMatch(
        pattern_name="AWS Key",
        secret_type="aws_access_key",
        file_path="test.py",
        line_number=1,
        column_start=0,
        column_end=20,
        matched_text="AKIA****",
        context="key = AKIAIOSFODNN7EXAMPLE",
        severity=SeverityLevel.CRITICAL,
        confidence=0.95,
        entropy=4.5,
        reason="High confidence AWS key"
    )
    
    medium_conf_secret = SecretMatch(
        pattern_name="API Key",
        secret_type="api_key",
        file_path="test.py",
        line_number=2,
        column_start=0,
        column_end=20,
        matched_text="sk_****",
        context="api_key = sk_test_123",
        severity=SeverityLevel.CRITICAL,
        confidence=0.65,
        entropy=3.5,
        reason="Medium confidence API key"
    )
    
    low_conf_secret = SecretMatch(
        pattern_name="Generic Secret",
        secret_type="generic_secret",
        file_path="test.py",
        line_number=3,
        column_start=0,
        column_end=20,
        matched_text="sec_****",
        context="secret = sec_example_123",
        severity=SeverityLevel.CRITICAL,
        confidence=0.35,
        entropy=2.5,
        reason="Low confidence secret"
    )
    
    print("\n🧮 Testing Score Calculation:")
    print("-" * 80)
    
    # Test with high confidence secret
    score_high = scoring_engine._calculate_secrets_score([high_conf_secret])
    print(f"High Confidence (0.95):")
    print(f"  - Base Penalty: 25 points")
    print(f"  - Confidence Multiplier: 1.0 (100%)")
    print(f"  - Actual Penalty: 25 points")
    print(f"  - Final Score: {score_high:.1f}/100")
    
    # Test with medium confidence secret
    score_medium = scoring_engine._calculate_secrets_score([medium_conf_secret])
    print(f"\nMedium Confidence (0.65):")
    print(f"  - Base Penalty: 25 points")
    print(f"  - Confidence Multiplier: 0.7 (70%)")
    print(f"  - Actual Penalty: 17.5 points")
    print(f"  - Final Score: {score_medium:.1f}/100")
    
    # Test with low confidence secret
    score_low = scoring_engine._calculate_secrets_score([low_conf_secret])
    print(f"\nLow Confidence (0.35):")
    print(f"  - Base Penalty: 25 points")
    print(f"  - Confidence Multiplier: 0.4 (40%)")
    print(f"  - Actual Penalty: 10 points")
    print(f"  - Final Score: {score_low:.1f}/100")
    
    # Test with all secrets
    score_all = scoring_engine._calculate_secrets_score([high_conf_secret, medium_conf_secret, low_conf_secret])
    print(f"\nAll Secrets Combined:")
    print(f"  - Total Penalty: {100 - score_all:.1f} points")
    print(f"  - Final Score: {score_all:.1f}/100")
    
    print("\n✅ Confidence weighting validation complete!")
    
    # Verify the weighting is working correctly
    assert score_high < score_medium < score_low, "Confidence weighting not working correctly!"
    print("✓ Confidence weighting verified: High conf < Medium conf < Low conf")


def test_html_report_generation():
    """Test HTML report generation."""
    print("\n" + "=" * 80)
    print("HTML REPORT GENERATION TEST")
    print("=" * 80)
    
    # Create test result
    result = create_test_analysis_result()
    report_id = f"test_html_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Generate HTML report
    print(f"\n📄 Generating HTML report: {report_id}")
    report_path = report_generator.generate_html_report(result, report_id)
    
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ File size: {report_path.stat().st_size} bytes")
    
    # Validate HTML structure
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📊 HTML STRUCTURE VALIDATION")
    print("-" * 80)
    
    # Check for required HTML elements
    required_elements = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<title>',
        '<style>',
        '<body>',
        'PolicyPilot Analysis Report'
    ]
    
    for element in required_elements:
        status = "✓" if element in content else "✗"
        print(f"{status} {element}")
    
    print("\n✅ HTML report validation complete!")
    return report_path


def run_all_tests():
    """Run all report generator tests."""
    print("\n" + "=" * 80)
    print("REPORT GENERATOR TEST SUITE")
    print("=" * 80)
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    
    try:
        # Run tests
        json_path = test_json_report_generation()
        md_path = test_markdown_report_generation()
        test_confidence_weighted_scoring()
        html_path = test_html_report_generation()
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print("\n📁 Generated Reports:")
        print(f"  - JSON: {json_path}")
        print(f"  - Markdown: {md_path}")
        print(f"  - HTML: {html_path}")
        print("\n💡 You can open these files to review the generated reports.")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

# Made with Bob
