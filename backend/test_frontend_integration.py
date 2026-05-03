"""
Frontend Integration Compatibility Test Script

Tests that backend API responses match the frontend handoff specification exactly.
Run this script to verify frontend-backend compatibility before deployment.

Usage:
    python test_frontend_integration.py
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, Any

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.models import (
    AnalysisResult,
    SecretMatch,
    ReadmeValidationResult,
    PromptDocumentationResult,
    ModuleScore,
    Issue,
    SeverityLevel,
    IssueType
)


def test_analysis_result_schema():
    """Test that AnalysisResult has all required fields for frontend."""
    print("Testing AnalysisResult schema...")
    
    # Create a sample result
    result = AnalysisResult(
        project_name="Test Project",
        secrets_found=[],
        readme_result=None,
        prompt_result=None,
        module_scores=[],
        total_score=85.0,
        passed=True,
        total_issues=0,
        critical_issues=0,
        files_analyzed=10,
        all_issues=[],
        upload_id="test-upload-123"
    )
    
    # Convert to dict (simulates JSON serialization)
    result_dict = result.model_dump()
    
    # Required fields per frontend spec
    required_fields = [
        'project_name',
        'timestamp',
        'secrets_found',
        'readme_result',
        'prompt_result',
        'module_scores',
        'total_score',
        'passed',
        'total_issues',
        'critical_issues',
        'files_analyzed',
        'all_issues',
        'upload_id'  # NEW: Required for report downloads
    ]
    
    missing_fields = [field for field in required_fields if field not in result_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    print("  ✅ PASS: All required fields present")
    return True


def test_secret_match_schema():
    """Test that SecretMatch has all required fields for frontend."""
    print("Testing SecretMatch schema...")
    
    secret = SecretMatch(
        pattern_name="AWS Access Key",
        secret_type="aws_access_key",
        file_path="config.py",
        line_number=42,
        column_start=10,
        column_end=30,
        matched_text="AKIA****",
        context="AWS_KEY = 'AKIA...'",
        severity=SeverityLevel.CRITICAL,
        confidence=0.95,
        entropy=4.2,
        reason="AWS key detected",
        is_verified=False
    )
    
    secret_dict = secret.model_dump()
    
    required_fields = [
        'pattern_name',
        'secret_type',
        'file_path',
        'line_number',
        'column_start',
        'column_end',
        'matched_text',
        'context',
        'severity',
        'confidence',
        'entropy',
        'reason',
        'is_verified'
    ]
    
    missing_fields = [field for field in required_fields if field not in secret_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    print("  ✅ PASS: All required fields present")
    return True


def test_module_score_schema():
    """Test that ModuleScore has all required fields for frontend."""
    print("Testing ModuleScore schema...")
    
    score = ModuleScore(
        name="Secret Scanner",
        score=85.0,
        weight=0.35,
        weighted_score=29.75,
        issues_count=2,
        critical_issues=1
    )
    
    score_dict = score.model_dump()
    
    required_fields = [
        'name',
        'score',
        'weight',
        'weighted_score',
        'issues_count',
        'critical_issues'
    ]
    
    missing_fields = [field for field in required_fields if field not in score_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    # Verify module names match frontend expectations
    valid_module_names = [
        "Secret Scanner",
        "README Validator",
        "Prompt Documentation",
        "Project Structure"
    ]
    
    if score.name not in valid_module_names:
        print(f"  ⚠️  WARNING: Module name '{score.name}' not in expected list")
    
    print("  ✅ PASS: All required fields present")
    return True


def test_readme_result_schema():
    """Test that ReadmeValidationResult has all required fields."""
    print("Testing ReadmeValidationResult schema...")
    
    result = ReadmeValidationResult(
        exists=True,
        has_required_sections=False,
        missing_required=["## Installation"],
        missing_recommended=["## License"],
        word_count=250,
        score=75.0,
        issues=[]
    )
    
    result_dict = result.model_dump()
    
    required_fields = [
        'exists',
        'has_required_sections',
        'missing_required',
        'missing_recommended',
        'word_count',
        'score',
        'issues'
    ]
    
    missing_fields = [field for field in required_fields if field not in result_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    print("  ✅ PASS: All required fields present")
    return True


def test_prompt_result_schema():
    """Test that PromptDocumentationResult has all required fields."""
    print("Testing PromptDocumentationResult schema...")
    
    result = PromptDocumentationResult(
        total_prompts=5,
        documented_prompts=4,
        missing_fields={"prompt.txt": ["example"]},
        score=80.0,
        issues=[]
    )
    
    result_dict = result.model_dump()
    
    required_fields = [
        'total_prompts',
        'documented_prompts',
        'missing_fields',
        'score',
        'issues'
    ]
    
    missing_fields = [field for field in required_fields if field not in result_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    print("  ✅ PASS: All required fields present")
    return True


def test_issue_schema():
    """Test that Issue has all required fields."""
    print("Testing Issue schema...")
    
    issue = Issue(
        type=IssueType.SECRET,
        severity=SeverityLevel.CRITICAL,
        message="Secret detected",
        file_path="config.py",
        line_number=42,
        details={"pattern": "api_key"}
    )
    
    issue_dict = issue.model_dump()
    
    required_fields = [
        'type',
        'severity',
        'message',
        'file_path',
        'line_number',
        'details'
    ]
    
    missing_fields = [field for field in required_fields if field not in issue_dict]
    
    if missing_fields:
        print(f"  ❌ FAIL: Missing fields: {missing_fields}")
        return False
    
    print("  ✅ PASS: All required fields present")
    return True


def test_severity_levels():
    """Test that severity levels match frontend expectations."""
    print("Testing severity levels...")
    
    expected_severities = ["critical", "high", "medium", "low", "info"]
    actual_severities = [level.value for level in SeverityLevel]
    
    if set(expected_severities) != set(actual_severities):
        print(f"  ❌ FAIL: Severity mismatch")
        print(f"     Expected: {expected_severities}")
        print(f"     Actual: {actual_severities}")
        return False
    
    print("  ✅ PASS: Severity levels match")
    return True


def test_issue_types():
    """Test that issue types match frontend expectations."""
    print("Testing issue types...")
    
    expected_types = ["secret", "readme", "prompt", "structure"]
    actual_types = [t.value for t in IssueType]
    
    if set(expected_types) != set(actual_types):
        print(f"  ❌ FAIL: Issue type mismatch")
        print(f"     Expected: {expected_types}")
        print(f"     Actual: {actual_types}")
        return False
    
    print("  ✅ PASS: Issue types match")
    return True


def test_json_serialization():
    """Test that models serialize to JSON correctly."""
    print("Testing JSON serialization...")
    
    try:
        result = AnalysisResult(
            project_name="Test",
            secrets_found=[
                SecretMatch(
                    pattern_name="Test",
                    secret_type="test",
                    file_path="test.py",
                    line_number=1,
                    column_start=0,
                    matched_text="***",
                    context="test",
                    confidence=0.9,
                    entropy=4.0,
                    reason="test"
                )
            ],
            readme_result=ReadmeValidationResult(
                exists=True,
                has_required_sections=True,
                score=100.0
            ),
            prompt_result=PromptDocumentationResult(
                total_prompts=1,
                documented_prompts=1,
                score=100.0
            ),
            module_scores=[
                ModuleScore(
                    name="Secret Scanner",
                    score=100.0,
                    weight=0.35,
                    weighted_score=35.0,
                    issues_count=0,
                    critical_issues=0
                )
            ],
            total_score=100.0,
            passed=True,
            total_issues=0,
            critical_issues=0,
            files_analyzed=1,
            upload_id="test-123"
        )
        
        # Serialize to JSON
        json_str = result.model_dump_json()
        
        # Deserialize back
        json_dict = json.loads(json_str)
        
        # Verify upload_id is present
        if 'upload_id' not in json_dict:
            print("  ❌ FAIL: upload_id missing from JSON")
            return False
        
        print("  ✅ PASS: JSON serialization works correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ FAIL: Serialization error: {e}")
        return False


def run_all_tests():
    """Run all compatibility tests."""
    print("\n" + "="*60)
    print("PolicyPilot Frontend-Backend Compatibility Tests")
    print("="*60 + "\n")
    
    tests = [
        test_analysis_result_schema,
        test_secret_match_schema,
        test_module_score_schema,
        test_readme_result_schema,
        test_prompt_result_schema,
        test_issue_schema,
        test_severity_levels,
        test_issue_types,
        test_json_serialization
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 Backend is compatible with frontend specification!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n⚠️  Fix failing tests before deploying!")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

# Made with Bob
