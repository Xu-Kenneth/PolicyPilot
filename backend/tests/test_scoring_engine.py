"""
Comprehensive tests for Scoring Engine Service.

Tests cover:
- Project analysis
- Module score calculation
- Secret scoring with confidence weighting
- Total score calculation
- Issue collection
- Recommendations generation
- Grade and status determination
"""
import pytest
from pathlib import Path
from app.services.scoring_engine import ScoringEngine
from app.models import (
    SecretMatch,
    SeverityLevel,
    ReadmeValidationResult,
    PromptDocumentationResult,
    Issue,
    IssueType
)


# ============================================================================
# Test Class: Scoring Engine Initialization
# ============================================================================

class TestScoringEngineInit:
    """Test scoring engine initialization."""
    
    def test_engine_initialization(self):
        """Test engine initializes with correct settings."""
        engine = ScoringEngine()
        
        assert engine.weights is not None
        assert engine.pass_threshold > 0
        assert engine.warning_threshold > 0
        assert engine.pass_threshold > engine.warning_threshold
    
    def test_weights_sum_to_one(self):
        """Test that scoring weights sum to 1.0."""
        engine = ScoringEngine()
        total_weight = sum(engine.weights.values())
        
        assert abs(total_weight - 1.0) < 0.01  # Allow small floating point error


# ============================================================================
# Test Class: Secret Scoring
# ============================================================================

class TestSecretScoring:
    """Test secret scoring with confidence weighting."""
    
    def test_no_secrets_perfect_score(self):
        """Test that no secrets gives perfect score."""
        engine = ScoringEngine()
        score = engine._calculate_secrets_score([])
        
        assert score == 100.0
    
    def test_critical_secret_high_penalty(self, sample_secret_match):
        """Test that critical secrets have high penalty."""
        engine = ScoringEngine()
        sample_secret_match.severity = SeverityLevel.CRITICAL
        sample_secret_match.confidence = 0.95
        
        score = engine._calculate_secrets_score([sample_secret_match])
        
        assert score < 80.0  # Should have significant penalty
    
    def test_confidence_affects_penalty(self):
        """Test that confidence affects penalty amount."""
        engine = ScoringEngine()
        
        # High confidence secret
        high_conf_secret = SecretMatch(
            pattern_name="Test",
            secret_type="test",
            file_path="test.py",
            line_number=1,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.CRITICAL,
            confidence=0.95,
            entropy=4.0,
            reason="Test"
        )
        
        # Low confidence secret
        low_conf_secret = SecretMatch(
            pattern_name="Test",
            secret_type="test",
            file_path="test.py",
            line_number=1,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.CRITICAL,
            confidence=0.3,
            entropy=2.0,
            reason="Test"
        )
        
        high_conf_score = engine._calculate_secrets_score([high_conf_secret])
        low_conf_score = engine._calculate_secrets_score([low_conf_secret])
        
        # Low confidence should have less penalty
        assert low_conf_score > high_conf_score
    
    def test_multiple_secrets_cumulative_penalty(self):
        """Test that multiple secrets have cumulative penalty."""
        engine = ScoringEngine()
        
        secret1 = SecretMatch(
            pattern_name="Test1",
            secret_type="test",
            file_path="test.py",
            line_number=1,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.HIGH,
            confidence=0.8,
            entropy=3.5,
            reason="Test"
        )
        
        secret2 = SecretMatch(
            pattern_name="Test2",
            secret_type="test",
            file_path="test.py",
            line_number=2,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.HIGH,
            confidence=0.8,
            entropy=3.5,
            reason="Test"
        )
        
        score_one = engine._calculate_secrets_score([secret1])
        score_two = engine._calculate_secrets_score([secret1, secret2])
        
        assert score_two < score_one
    
    def test_severity_affects_penalty(self):
        """Test that severity level affects penalty."""
        engine = ScoringEngine()
        
        critical = SecretMatch(
            pattern_name="Test",
            secret_type="test",
            file_path="test.py",
            line_number=1,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.CRITICAL,
            confidence=0.8,
            entropy=3.5,
            reason="Test"
        )
        
        low = SecretMatch(
            pattern_name="Test",
            secret_type="test",
            file_path="test.py",
            line_number=1,
            column_start=0,
            matched_text="****",
            context="",
            severity=SeverityLevel.LOW,
            confidence=0.8,
            entropy=3.5,
            reason="Test"
        )
        
        critical_score = engine._calculate_secrets_score([critical])
        low_score = engine._calculate_secrets_score([low])
        
        assert low_score > critical_score


# ============================================================================
# Test Class: Module Score Calculation
# ============================================================================

class TestModuleScoreCalculation:
    """Test module score calculation."""
    
    def test_module_scores_structure(self, sample_readme_result, sample_prompt_result):
        """Test that module scores have correct structure."""
        engine = ScoringEngine()
        module_scores = engine._calculate_module_scores(
            [],
            sample_readme_result,
            sample_prompt_result
        )
        
        assert len(module_scores) == 4  # secrets, readme, prompts, structure
        
        for module in module_scores:
            assert hasattr(module, 'name')
            assert hasattr(module, 'score')
            assert hasattr(module, 'weight')
            assert hasattr(module, 'weighted_score')
            assert hasattr(module, 'issues_count')
            assert hasattr(module, 'critical_issues')
    
    def test_weighted_scores_calculated(self, sample_readme_result, sample_prompt_result):
        """Test that weighted scores are calculated correctly."""
        engine = ScoringEngine()
        module_scores = engine._calculate_module_scores(
            [],
            sample_readme_result,
            sample_prompt_result
        )
        
        for module in module_scores:
            expected_weighted = module.score * module.weight
            assert abs(module.weighted_score - expected_weighted) < 0.01
    
    def test_readme_score_integration(self):
        """Test README score integration."""
        engine = ScoringEngine()
        
        readme_result = ReadmeValidationResult(
            exists=True,
            has_required_sections=True,
            missing_required=[],
            missing_recommended=[],
            word_count=300,
            score=95.0,
            issues=[]
        )
        
        module_scores = engine._calculate_module_scores([], readme_result, None)
        readme_module = next(m for m in module_scores if "README" in m.name)
        
        assert readme_module.score == 95.0
    
    def test_prompt_score_integration(self):
        """Test prompt score integration."""
        engine = ScoringEngine()
        
        prompt_result = PromptDocumentationResult(
            total_prompts=5,
            documented_prompts=5,
            missing_fields={},
            score=100.0,
            issues=[]
        )
        
        module_scores = engine._calculate_module_scores([], None, prompt_result)
        prompt_module = next(m for m in module_scores if "Prompt" in m.name)
        
        assert prompt_module.score == 100.0


# ============================================================================
# Test Class: Total Score Calculation
# ============================================================================

class TestTotalScoreCalculation:
    """Test total score calculation."""
    
    def test_total_score_weighted_sum(self, sample_readme_result, sample_prompt_result):
        """Test that total score is weighted sum of modules."""
        engine = ScoringEngine()
        module_scores = engine._calculate_module_scores(
            [],
            sample_readme_result,
            sample_prompt_result
        )
        
        total = engine._calculate_total_score(module_scores)
        expected = sum(m.weighted_score for m in module_scores)
        
        assert abs(total - expected) < 0.01
    
    def test_total_score_bounds(self, sample_readme_result, sample_prompt_result):
        """Test that total score stays within 0-100."""
        engine = ScoringEngine()
        module_scores = engine._calculate_module_scores(
            [],
            sample_readme_result,
            sample_prompt_result
        )
        
        total = engine._calculate_total_score(module_scores)
        
        assert 0 <= total <= 100


# ============================================================================
# Test Class: Project Analysis
# ============================================================================

class TestProjectAnalysis:
    """Test complete project analysis."""
    
    def test_analyze_empty_project(self, test_project_dir):
        """Test analyzing empty project."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        assert result.project_name == "Test Project"
        assert result.total_score >= 0
        assert result.files_analyzed >= 0
    
    def test_analyze_project_with_secrets(self, test_project_dir, sample_secrets_file):
        """Test analyzing project with secrets."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        assert len(result.secrets_found) > 0
        assert result.total_score < 100
        assert result.critical_issues > 0
    
    def test_analyze_project_with_readme(self, test_project_dir, sample_readme_complete):
        """Test analyzing project with README."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        assert result.readme_result is not None
        assert result.readme_result.exists is True
    
    def test_analyze_project_with_prompts(self, test_project_dir, sample_prompt_json):
        """Test analyzing project with prompts."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        assert result.prompt_result is not None
        assert result.prompt_result.total_prompts > 0
    
    def test_pass_fail_determination(self, test_project_dir):
        """Test pass/fail determination."""
        engine = ScoringEngine()
        
        # Create good project
        (test_project_dir / "README.md").write_text("""# Project
## Description
Good description
## Installation
Install instructions
## Usage
Usage instructions
""")
        
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        # Should pass or fail based on threshold
        if result.total_score >= engine.pass_threshold:
            assert result.passed is True
        else:
            assert result.passed is False


# ============================================================================
# Test Class: Issue Collection
# ============================================================================

class TestIssueCollection:
    """Test issue collection from all modules."""
    
    def test_collect_secret_issues(self, sample_secret_match):
        """Test collecting issues from secrets."""
        engine = ScoringEngine()
        issues = engine._collect_all_issues([sample_secret_match], None, None)
        
        assert len(issues) > 0
        assert any(i.type == IssueType.SECRET for i in issues)
    
    def test_collect_readme_issues(self, sample_readme_result):
        """Test collecting issues from README."""
        engine = ScoringEngine()
        issues = engine._collect_all_issues([], sample_readme_result, None)
        
        readme_issues = [i for i in issues if i.type == IssueType.README]
        assert len(readme_issues) == len(sample_readme_result.issues)
    
    def test_collect_prompt_issues(self, sample_prompt_result):
        """Test collecting issues from prompts."""
        engine = ScoringEngine()
        issues = engine._collect_all_issues([], None, sample_prompt_result)
        
        prompt_issues = [i for i in issues if i.type == IssueType.PROMPT]
        assert len(prompt_issues) == len(sample_prompt_result.issues)
    
    def test_issues_sorted_by_severity(self, sample_secret_match, sample_readme_result):
        """Test that issues are sorted by severity."""
        engine = ScoringEngine()
        issues = engine._collect_all_issues(
            [sample_secret_match],
            sample_readme_result,
            None
        )
        
        # Check that critical issues come first
        if len(issues) > 1:
            severity_order = {
                SeverityLevel.CRITICAL: 0,
                SeverityLevel.HIGH: 1,
                SeverityLevel.MEDIUM: 2,
                SeverityLevel.LOW: 3,
                SeverityLevel.INFO: 4
            }
            
            for i in range(len(issues) - 1):
                current_order = severity_order[issues[i].severity]
                next_order = severity_order[issues[i + 1].severity]
                assert current_order <= next_order


# ============================================================================
# Test Class: Grade and Status
# ============================================================================

class TestGradeAndStatus:
    """Test grade and status determination."""
    
    def test_grade_a(self):
        """Test grade A for score >= 90."""
        engine = ScoringEngine()
        assert engine.get_grade(95.0) == "A"
        assert engine.get_grade(90.0) == "A"
    
    def test_grade_b(self):
        """Test grade B for score 80-89."""
        engine = ScoringEngine()
        assert engine.get_grade(85.0) == "B"
        assert engine.get_grade(80.0) == "B"
    
    def test_grade_c(self):
        """Test grade C for score 70-79."""
        engine = ScoringEngine()
        assert engine.get_grade(75.0) == "C"
        assert engine.get_grade(70.0) == "C"
    
    def test_grade_d(self):
        """Test grade D for score 60-69."""
        engine = ScoringEngine()
        assert engine.get_grade(65.0) == "D"
        assert engine.get_grade(60.0) == "D"
    
    def test_grade_f(self):
        """Test grade F for score < 60."""
        engine = ScoringEngine()
        assert engine.get_grade(50.0) == "F"
        assert engine.get_grade(0.0) == "F"
    
    def test_status_pass(self):
        """Test PASS status."""
        engine = ScoringEngine()
        score = engine.pass_threshold + 5
        assert engine.get_status(score) == "PASS"
    
    def test_status_warning(self):
        """Test WARNING status."""
        engine = ScoringEngine()
        score = (engine.pass_threshold + engine.warning_threshold) / 2
        assert engine.get_status(score) == "WARNING"
    
    def test_status_fail(self):
        """Test FAIL status."""
        engine = ScoringEngine()
        score = engine.warning_threshold - 5
        assert engine.get_status(score) == "FAIL"


# ============================================================================
# Test Class: Recommendations
# ============================================================================

class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendations_for_secrets(self, test_project_dir, sample_secrets_file):
        """Test recommendations when secrets found."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        recommendations = engine.get_recommendations(result)
        
        if result.secrets_found:
            assert any("secret" in r.lower() for r in recommendations)
    
    def test_recommendations_for_missing_readme(self, test_project_dir):
        """Test recommendations when README missing."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        recommendations = engine.get_recommendations(result)
        
        if not result.readme_result or not result.readme_result.exists:
            assert any("readme" in r.lower() for r in recommendations)
    
    def test_recommendations_for_critical_issues(self, test_project_dir, sample_secrets_file):
        """Test recommendations for critical issues."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        recommendations = engine.get_recommendations(result)
        
        if result.critical_issues > 0:
            assert any("critical" in r.lower() for r in recommendations)
    
    def test_recommendations_for_low_score(self, test_project_dir):
        """Test recommendations for low score."""
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        recommendations = engine.get_recommendations(result)
        
        if result.total_score < engine.pass_threshold:
            assert any("score" in r.lower() or "improve" in r.lower() for r in recommendations)
    
    def test_no_recommendations_for_perfect_project(self, test_project_dir):
        """Test minimal recommendations for perfect project."""
        # Create perfect project
        (test_project_dir / "README.md").write_text("""# Perfect Project
## Description
Comprehensive description
## Installation
Detailed installation
## Usage
Detailed usage
## Features
Many features
## Contributing
Contribution guidelines
## License
MIT License
""")
        
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Perfect Project")
        recommendations = engine.get_recommendations(result)
        
        # Should have few or no recommendations
        assert len(recommendations) <= 2


# ============================================================================
# Test Class: File Counting
# ============================================================================

class TestFileCounting:
    """Test file counting functionality."""
    
    def test_count_files_empty_directory(self, test_project_dir):
        """Test counting files in empty directory."""
        engine = ScoringEngine()
        count = engine._count_files(test_project_dir)
        
        assert count == 0
    
    def test_count_files_with_files(self, test_project_dir):
        """Test counting files."""
        (test_project_dir / "file1.py").write_text("content")
        (test_project_dir / "file2.md").write_text("content")
        (test_project_dir / "subdir").mkdir()
        (test_project_dir / "subdir" / "file3.txt").write_text("content")
        
        engine = ScoringEngine()
        count = engine._count_files(test_project_dir)
        
        assert count >= 3
    
    def test_skip_hidden_files(self, test_project_dir):
        """Test that hidden files are skipped."""
        (test_project_dir / ".hidden").write_text("content")
        (test_project_dir / "visible.py").write_text("content")
        
        engine = ScoringEngine()
        count = engine._count_files(test_project_dir)
        
        # Should only count visible file
        assert count == 1
    
    def test_skip_pyc_files(self, test_project_dir):
        """Test that .pyc files are skipped."""
        (test_project_dir / "file.py").write_text("content")
        (test_project_dir / "file.pyc").write_bytes(b"compiled")
        
        engine = ScoringEngine()
        count = engine._count_files(test_project_dir)
        
        # Should only count .py file
        assert count == 1


# ============================================================================
# Test Class: Integration Tests
# ============================================================================

@pytest.mark.integration
class TestScoringEngineIntegration:
    """Integration tests for scoring engine."""
    
    def test_full_analysis_workflow(self, test_project_dir):
        """Test complete analysis workflow."""
        # Create realistic project
        (test_project_dir / "README.md").write_text("""# Test Project
## Description
Test description
## Installation
pip install
## Usage
python app.py
""")
        
        (test_project_dir / "src").mkdir()
        (test_project_dir / "src" / "app.py").write_text("""
def main():
    print("Hello World")
""")
        
        (test_project_dir / "prompts").mkdir()
        (test_project_dir / "prompts" / "test.json").write_text("""{
    "purpose": "Test",
    "input_format": "Text",
    "output_format": "JSON",
    "example": "Example"
}""")
        
        engine = ScoringEngine()
        result = engine.analyze_project(test_project_dir, "Test Project")
        
        # Verify complete result structure
        assert result.project_name == "Test Project"
        assert result.total_score >= 0
        assert result.module_scores is not None
        assert len(result.module_scores) == 4
        assert result.readme_result is not None
        assert result.prompt_result is not None
        assert isinstance(result.passed, bool)
        assert result.files_analyzed > 0
    
    def test_score_consistency(self, test_project_dir):
        """Test that scoring is consistent across runs."""
        # Create project
        (test_project_dir / "README.md").write_text("# Test\n## Description\nTest")
        
        engine = ScoringEngine()
        result1 = engine.analyze_project(test_project_dir, "Test")
        result2 = engine.analyze_project(test_project_dir, "Test")
        
        # Scores should be identical
        assert result1.total_score == result2.total_score


# Made with Bob