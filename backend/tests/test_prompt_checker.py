"""
Comprehensive tests for Prompt Checker Service.

Tests cover:
- Prompt file detection
- JSON prompt validation
- Text prompt validation
- Field checking
- Score calculation
- Issue generation
"""
import pytest
import json
from pathlib import Path
from app.services.prompt_checker import PromptChecker
from app.models import IssueType, SeverityLevel


# ============================================================================
# Test Class: Prompt File Detection
# ============================================================================

class TestPromptFileDetection:
    """Test prompt file detection."""
    
    def test_find_json_prompts(self, test_project_dir):
        """Test finding JSON prompt files."""
        prompts_dir = test_project_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test.json").write_text('{"purpose": "test"}')
        
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) > 0
        assert any(f.suffix == ".json" for f in files)
    
    def test_find_text_prompts(self, test_project_dir):
        """Test finding text prompt files."""
        prompts_dir = test_project_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test.txt").write_text("Purpose: test")
        
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) > 0
        assert any(f.suffix == ".txt" for f in files)
    
    def test_find_markdown_prompts(self, test_project_dir):
        """Test finding markdown prompt files."""
        prompts_dir = test_project_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test.md").write_text("# Purpose\nTest")
        
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) > 0
        assert any(f.suffix == ".md" for f in files)
    
    def test_find_prompts_in_subdirectories(self, test_project_dir):
        """Test finding prompts in nested directories."""
        nested = test_project_dir / "docs" / "prompts" / "v1"
        nested.mkdir(parents=True)
        (nested / "prompt.json").write_text('{"purpose": "test"}')
        
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) > 0
    
    def test_no_prompts_found(self, test_project_dir):
        """Test when no prompt files exist."""
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) == 0
    
    def test_find_prompt_by_filename_pattern(self, test_project_dir):
        """Test finding files with 'prompt' in name."""
        (test_project_dir / "my_prompt.txt").write_text("Purpose: test")
        (test_project_dir / "system_prompt.md").write_text("# Purpose\nTest")
        
        checker = PromptChecker()
        files = checker._find_prompt_files(test_project_dir)
        
        assert len(files) >= 2


# ============================================================================
# Test Class: JSON Prompt Validation
# ============================================================================

class TestJSONPromptValidation:
    """Test JSON prompt validation."""
    
    def test_complete_json_prompt(self, sample_prompt_json):
        """Test validation of complete JSON prompt."""
        checker = PromptChecker()
        content = sample_prompt_json.read_text()
        
        is_documented, missing = checker._check_json_prompt(content, sample_prompt_json)
        
        assert is_documented is True
        assert len(missing) == 0
    
    def test_incomplete_json_prompt(self, test_project_dir):
        """Test validation of incomplete JSON prompt."""
        prompt_file = test_project_dir / "prompts" / "incomplete.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps({
            "purpose": "Test prompt",
            "input_format": "Text"
            # Missing output_format and example
        })
        prompt_file.write_text(content)
        
        checker = PromptChecker()
        is_documented, missing = checker._check_json_prompt(content, prompt_file)
        
        assert is_documented is False
        assert "output_format" in missing
        assert "example" in missing
    
    def test_invalid_json(self, test_project_dir):
        """Test handling of invalid JSON."""
        prompt_file = test_project_dir / "prompts" / "invalid.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text("{invalid json")
        
        checker = PromptChecker()
        content = prompt_file.read_text()
        is_documented, missing = checker._check_json_prompt(content, prompt_file)
        
        assert is_documented is False
        assert len(missing) > 0
    
    def test_empty_json_fields(self, test_project_dir):
        """Test detection of empty JSON fields."""
        prompt_file = test_project_dir / "prompts" / "empty.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps({
            "purpose": "",  # Empty
            "input_format": "Text",
            "output_format": "JSON",
            "example": "Example"
        })
        prompt_file.write_text(content)
        
        checker = PromptChecker()
        is_documented, missing = checker._check_json_prompt(content, prompt_file)
        
        assert "purpose" in missing


# ============================================================================
# Test Class: Text Prompt Validation
# ============================================================================

class TestTextPromptValidation:
    """Test text/markdown prompt validation."""
    
    def test_complete_text_prompt(self, sample_prompt_text):
        """Test validation of complete text prompt."""
        checker = PromptChecker()
        content = sample_prompt_text.read_text()
        
        is_documented, missing = checker._check_text_prompt(content, sample_prompt_text)
        
        assert is_documented is True
        assert len([m for m in missing if m in checker.required_fields]) == 0
    
    def test_incomplete_text_prompt(self, sample_prompt_incomplete):
        """Test validation of incomplete text prompt."""
        checker = PromptChecker()
        content = sample_prompt_incomplete.read_text()
        
        is_documented, missing = checker._check_text_prompt(content, sample_prompt_incomplete)
        
        assert is_documented is False
        assert len(missing) > 0
    
    def test_case_insensitive_field_matching(self, test_project_dir):
        """Test that field matching is case-insensitive."""
        prompt_file = test_project_dir / "prompts" / "test.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = """PURPOSE: Test prompt
INPUT: Text format
OUTPUT: JSON format
EXAMPLE: Sample data
"""
        prompt_file.write_text(content)
        
        checker = PromptChecker()
        is_documented, missing = checker._check_text_prompt(content, prompt_file)
        
        # Should find fields despite uppercase
        assert is_documented is True
    
    def test_alternative_field_names(self, test_project_dir):
        """Test recognition of alternative field names."""
        prompt_file = test_project_dir / "prompts" / "test.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = """Goal: Test prompt
Parameters: Text format
Response: JSON format
Demo: Sample data
"""
        prompt_file.write_text(content)
        
        checker = PromptChecker()
        is_documented, missing = checker._check_text_prompt(content, prompt_file)
        
        # Should recognize alternative names
        required_missing = [m for m in missing if m in checker.required_fields]
        assert len(required_missing) == 0


# ============================================================================
# Test Class: Directory Checking
# ============================================================================

class TestDirectoryChecking:
    """Test directory-level prompt checking."""
    
    def test_check_directory_no_prompts(self, test_project_dir):
        """Test checking directory with no prompts."""
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        assert result.total_prompts == 0
        assert result.documented_prompts == 0
        assert result.score == 100.0  # No prompts = no issues
    
    def test_check_directory_all_documented(self, test_project_dir, sample_prompt_json, sample_prompt_text):
        """Test directory with all prompts documented."""
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        assert result.total_prompts >= 2
        assert result.documented_prompts == result.total_prompts
        assert result.score >= 90.0
    
    def test_check_directory_mixed_documentation(self, test_project_dir):
        """Test directory with mixed documentation quality."""
        prompts_dir = test_project_dir / "prompts"
        prompts_dir.mkdir()
        
        # Complete prompt
        complete = prompts_dir / "complete.json"
        complete.write_text(json.dumps({
            "purpose": "Test",
            "input_format": "Text",
            "output_format": "JSON",
            "example": "Example"
        }))
        
        # Incomplete prompt
        incomplete = prompts_dir / "incomplete.json"
        incomplete.write_text(json.dumps({
            "purpose": "Test"
        }))
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        assert result.total_prompts == 2
        assert result.documented_prompts == 1
        assert 0 < result.score < 100


# ============================================================================
# Test Class: Score Calculation
# ============================================================================

class TestScoreCalculation:
    """Test score calculation."""
    
    def test_perfect_score(self):
        """Test perfect documentation score."""
        checker = PromptChecker()
        score = checker._calculate_score(
            total_prompts=5,
            documented_prompts=5,
            missing_fields={}
        )
        
        assert score == 100.0
    
    def test_partial_documentation(self):
        """Test partial documentation score."""
        checker = PromptChecker()
        score = checker._calculate_score(
            total_prompts=10,
            documented_prompts=7,
            missing_fields={}
        )
        
        assert 60 < score < 80
    
    def test_missing_fields_reduce_score(self):
        """Test that missing fields reduce score."""
        checker = PromptChecker()
        
        score_no_missing = checker._calculate_score(
            total_prompts=5,
            documented_prompts=5,
            missing_fields={}
        )
        
        score_with_missing = checker._calculate_score(
            total_prompts=5,
            documented_prompts=5,
            missing_fields={
                "prompt1.txt": ["purpose", "example"],
                "prompt2.txt": ["constraints"]
            }
        )
        
        assert score_with_missing < score_no_missing
    
    def test_required_vs_recommended_penalty(self):
        """Test that required fields have higher penalty."""
        checker = PromptChecker()
        
        score_missing_required = checker._calculate_score(
            total_prompts=1,
            documented_prompts=0,
            missing_fields={"prompt.txt": ["purpose", "example"]}
        )
        
        score_missing_recommended = checker._calculate_score(
            total_prompts=1,
            documented_prompts=1,
            missing_fields={"prompt.txt": ["constraints", "version"]}
        )
        
        assert score_missing_required < score_missing_recommended
    
    def test_score_bounds(self):
        """Test that score stays within 0-100."""
        checker = PromptChecker()
        
        # Worst case
        score_worst = checker._calculate_score(
            total_prompts=10,
            documented_prompts=0,
            missing_fields={
                f"prompt{i}.txt": ["purpose", "input_format", "output_format", "example"]
                for i in range(10)
            }
        )
        
        assert 0 <= score_worst <= 100


# ============================================================================
# Test Class: Issue Generation
# ============================================================================

class TestIssueGeneration:
    """Test issue generation."""
    
    def test_empty_prompt_generates_issue(self, test_project_dir):
        """Test that empty prompt generates issue."""
        prompt_file = test_project_dir / "prompts" / "empty.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text("")
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        assert len(result.issues) > 0
        assert any("empty" in i.message.lower() for i in result.issues)
    
    def test_missing_required_field_generates_high_issue(self, test_project_dir):
        """Test that missing required fields generate high severity issues."""
        prompt_file = test_project_dir / "prompts" / "incomplete.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(json.dumps({"input_format": "Text"}))
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        high_issues = [i for i in result.issues if i.severity == SeverityLevel.HIGH]
        assert len(high_issues) > 0
        assert any("required" in i.message.lower() for i in high_issues)
    
    def test_missing_recommended_field_generates_medium_issue(self, test_project_dir):
        """Test that missing recommended fields generate medium issues."""
        prompt_file = test_project_dir / "prompts" / "partial.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(json.dumps({
            "purpose": "Test",
            "input_format": "Text",
            "output_format": "JSON",
            "example": "Example"
            # Missing recommended fields
        }))
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        medium_issues = [i for i in result.issues if i.severity == SeverityLevel.MEDIUM]
        assert len(medium_issues) > 0
    
    def test_issue_includes_file_path(self, test_project_dir):
        """Test that issues include file path."""
        prompt_file = test_project_dir / "prompts" / "test.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text("Incomplete prompt")
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        for issue in result.issues:
            assert issue.file_path is not None
            assert "test.txt" in issue.file_path


# ============================================================================
# Test Class: Prompt Structure Validation
# ============================================================================

class TestPromptStructureValidation:
    """Test prompt structure validation."""
    
    def test_has_clear_instructions(self):
        """Test detection of clear instructions."""
        checker = PromptChecker()
        content = "You must follow these instructions carefully."
        
        result = checker.validate_prompt_structure(content)
        
        assert result['has_clear_instructions'] is True
    
    def test_has_examples(self):
        """Test detection of examples."""
        checker = PromptChecker()
        content = "For example, you can use this format."
        
        result = checker.validate_prompt_structure(content)
        
        assert result['has_examples'] is True
    
    def test_has_constraints(self):
        """Test detection of constraints."""
        checker = PromptChecker()
        content = "You must not exceed 1000 tokens."
        
        result = checker.validate_prompt_structure(content)
        
        assert result['has_constraints'] is True
    
    def test_word_and_line_count(self):
        """Test word and line counting."""
        checker = PromptChecker()
        content = """Line 1 with words
Line 2 with more words
Line 3 continues"""
        
        result = checker.validate_prompt_structure(content)
        
        assert result['word_count'] > 0
        assert result['line_count'] == 3
    
    def test_has_formatting(self):
        """Test detection of markdown formatting."""
        checker = PromptChecker()
        content = "# Title\n**Bold** and `code`"
        
        result = checker.validate_prompt_structure(content)
        
        assert result['has_formatting'] is True


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_large_prompt(self, test_project_dir):
        """Test handling of very large prompt file."""
        prompt_file = test_project_dir / "prompts" / "large.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = "Purpose: Test\n" + "word " * 10000
        prompt_file.write_text(content)
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        # Should handle large files
        assert result.total_prompts >= 1
    
    def test_unicode_prompt(self, test_project_dir):
        """Test prompt with unicode content."""
        prompt_file = test_project_dir / "prompts" / "unicode.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        content = """目的: テストプロンプト
入力: テキスト形式
出力: JSON形式
例: サンプルデータ
"""
        prompt_file.write_text(content, encoding='utf-8')
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        # Should handle unicode
        assert result.total_prompts >= 1
    
    def test_binary_file_as_prompt(self, test_project_dir):
        """Test handling of binary file with .txt extension."""
        prompt_file = test_project_dir / "prompts" / "binary.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_bytes(b'\x00\x01\x02\x03')
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        # Should handle gracefully
        assert isinstance(result.total_prompts, int)


# ============================================================================
# Test Class: Integration Tests
# ============================================================================

@pytest.mark.integration
class TestPromptCheckerIntegration:
    """Integration tests for prompt checker."""
    
    def test_realistic_prompt_directory(self, test_project_dir):
        """Test checking realistic prompt directory."""
        prompts_dir = test_project_dir / "prompts"
        prompts_dir.mkdir()
        
        # System prompt
        (prompts_dir / "system.json").write_text(json.dumps({
            "purpose": "System initialization prompt",
            "input_format": "None",
            "output_format": "System state",
            "example": "Initialize system",
            "constraints": "Must complete in 5 seconds",
            "version": "1.0.0"
        }))
        
        # User prompt
        (prompts_dir / "user_query.txt").write_text("""Purpose: Handle user queries
Input: User question text
Output: Structured response
Example: Q: What is X? A: X is...
Constraints: Max 500 tokens
""")
        
        # Incomplete prompt
        (prompts_dir / "draft.md").write_text("# Draft Prompt\nWork in progress")
        
        checker = PromptChecker()
        result = checker.check_directory(test_project_dir)
        
        assert result.total_prompts == 3
        assert result.documented_prompts >= 2
        assert 50 < result.score < 100
        assert len(result.issues) > 0


# Made with Bob