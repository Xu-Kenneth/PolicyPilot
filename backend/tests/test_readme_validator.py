"""
Comprehensive tests for README Validator Service.

Tests cover:
- README file detection
- Section validation
- Word count analysis
- Score calculation
- Quality indicators
- Issue generation
"""
import pytest
from pathlib import Path
from app.services.readme_validator import ReadmeValidator
from app.models import IssueType, SeverityLevel


# ============================================================================
# Test Class: README Detection
# ============================================================================

class TestReadmeDetection:
    """Test README file detection."""
    
    def test_find_readme_md(self, test_project_dir):
        """Test finding README.md file."""
        readme_path = test_project_dir / "README.md"
        readme_path.write_text("# Test")
        
        validator = ReadmeValidator()
        found = validator._find_readme(test_project_dir)
        
        assert found is not None
        assert found.name == "README.md"
    
    def test_find_readme_case_insensitive(self, test_project_dir):
        """Test finding README with different cases."""
        readme_path = test_project_dir / "readme.md"
        readme_path.write_text("# Test")
        
        validator = ReadmeValidator()
        found = validator._find_readme(test_project_dir)
        
        assert found is not None
    
    def test_find_readme_txt(self, test_project_dir):
        """Test finding README.txt file."""
        readme_path = test_project_dir / "README.txt"
        readme_path.write_text("Test Project")
        
        validator = ReadmeValidator()
        found = validator._find_readme(test_project_dir)
        
        assert found is not None
        assert found.name == "README.txt"
    
    def test_no_readme_found(self, test_project_dir):
        """Test when no README exists."""
        validator = ReadmeValidator()
        found = validator._find_readme(test_project_dir)
        
        assert found is None
    
    def test_prefer_markdown_over_txt(self, test_project_dir):
        """Test that .md is preferred over .txt."""
        (test_project_dir / "README.txt").write_text("Text version")
        (test_project_dir / "README.md").write_text("# Markdown version")
        
        validator = ReadmeValidator()
        found = validator._find_readme(test_project_dir)
        
        assert found.suffix == ".md"


# ============================================================================
# Test Class: Section Validation
# ============================================================================

class TestSectionValidation:
    """Test README section validation."""
    
    def test_all_required_sections_present(self, sample_readme_complete):
        """Test README with all required sections."""
        validator = ReadmeValidator()
        content = sample_readme_complete.read_text()
        
        missing_required, missing_recommended = validator._check_sections(content)
        
        assert len(missing_required) == 0
    
    def test_missing_required_sections(self, test_project_dir):
        """Test README missing required sections."""
        readme = test_project_dir / "README.md"
        readme.write_text("# Title\n\nSome content")
        
        validator = ReadmeValidator()
        content = readme.read_text()
        
        missing_required, _ = validator._check_sections(content)
        
        assert len(missing_required) > 0
        assert "## Description" in missing_required
        assert "## Installation" in missing_required
        assert "## Usage" in missing_required
    
    def test_case_insensitive_section_matching(self, test_project_dir):
        """Test that section matching is case-insensitive."""
        readme = test_project_dir / "README.md"
        content = """# Test Project
## DESCRIPTION
Project description here
## installation
Install instructions
## UsAgE
Usage instructions
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        missing_required, _ = validator._check_sections(content)
        
        # Should find sections despite case differences
        assert len(missing_required) == 0
    
    def test_recommended_sections(self, test_project_dir):
        """Test detection of recommended sections."""
        readme = test_project_dir / "README.md"
        content = """# Test
## Description
Desc
## Installation
Install
## Usage
Use
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        _, missing_recommended = validator._check_sections(content)
        
        assert len(missing_recommended) > 0
        assert any("Features" in s for s in missing_recommended)


# ============================================================================
# Test Class: Word Count
# ============================================================================

class TestWordCount:
    """Test word count functionality."""
    
    def test_word_count_simple(self, test_project_dir):
        """Test word count for simple text."""
        readme = test_project_dir / "README.md"
        readme.write_text("one two three four five")
        
        validator = ReadmeValidator()
        content = readme.read_text()
        count = validator._count_words(content)
        
        assert count == 5
    
    def test_word_count_with_markdown(self, test_project_dir):
        """Test word count ignores markdown syntax."""
        readme = test_project_dir / "README.md"
        content = "# Title\n**bold** *italic* `code` [link](url)"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        count = validator._count_words(content)
        
        # Should count words, not markdown syntax
        assert count >= 4
    
    def test_word_count_empty(self, test_project_dir):
        """Test word count for empty file."""
        readme = test_project_dir / "README.md"
        readme.write_text("")
        
        validator = ReadmeValidator()
        count = validator._count_words("")
        
        assert count == 0
    
    def test_word_count_multiline(self, test_project_dir):
        """Test word count across multiple lines."""
        readme = test_project_dir / "README.md"
        content = """Line one has words
Line two has more words
Line three continues"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        count = validator._count_words(content)
        
        assert count == 11


# ============================================================================
# Test Class: Score Calculation
# ============================================================================

class TestScoreCalculation:
    """Test README score calculation."""
    
    def test_perfect_score(self, sample_readme_complete):
        """Test perfect README gets high score."""
        validator = ReadmeValidator()
        result = validator.validate(sample_readme_complete.parent)
        
        assert result.score >= 80.0
    
    def test_missing_required_reduces_score(self, test_project_dir):
        """Test that missing required sections reduce score."""
        readme = test_project_dir / "README.md"
        readme.write_text("# Title\n\nMinimal content")
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert result.score < 70.0
    
    def test_low_word_count_reduces_score(self, test_project_dir):
        """Test that low word count reduces score."""
        readme = test_project_dir / "README.md"
        content = """# Title
## Description
Short
## Installation
pip install
## Usage
Run it
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        # Should have penalty for low word count
        assert result.score < 90.0
    
    def test_score_calculation_formula(self, test_project_dir):
        """Test score calculation formula."""
        readme = test_project_dir / "README.md"
        content = """# Title
## Description
Description here
## Installation
Install instructions
## Usage
Usage instructions
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        missing_required, missing_recommended = validator._check_sections(content)
        word_count = validator._count_words(content)
        
        score = validator._calculate_score(
            missing_required,
            missing_recommended,
            word_count
        )
        
        assert 0 <= score <= 100
    
    def test_score_bounds(self, test_project_dir):
        """Test that score stays within 0-100 bounds."""
        readme = test_project_dir / "README.md"
        readme.write_text("x")  # Minimal content
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert 0 <= result.score <= 100


# ============================================================================
# Test Class: Issue Generation
# ============================================================================

class TestIssueGeneration:
    """Test issue generation."""
    
    def test_no_readme_generates_critical_issue(self, test_project_dir):
        """Test that missing README generates critical issue."""
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert len(result.issues) > 0
        assert any(
            issue.severity == SeverityLevel.CRITICAL 
            for issue in result.issues
        )
        assert any(
            "No README" in issue.message 
            for issue in result.issues
        )
    
    def test_missing_required_generates_high_issue(self, test_project_dir):
        """Test that missing required sections generate high severity issues."""
        readme = test_project_dir / "README.md"
        readme.write_text("# Title\n\nContent")
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        high_issues = [i for i in result.issues if i.severity == SeverityLevel.HIGH]
        assert len(high_issues) > 0
        assert any("required section" in i.message.lower() for i in high_issues)
    
    def test_missing_recommended_generates_medium_issue(self, test_project_dir):
        """Test that missing recommended sections generate medium issues."""
        readme = test_project_dir / "README.md"
        content = """# Title
## Description
Desc
## Installation
Install
## Usage
Use
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        medium_issues = [i for i in result.issues if i.severity == SeverityLevel.MEDIUM]
        assert len(medium_issues) > 0
    
    def test_low_word_count_generates_issue(self, test_project_dir):
        """Test that low word count generates issue."""
        readme = test_project_dir / "README.md"
        content = """# Title
## Description
Short
## Installation
pip
## Usage
run
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        word_count_issues = [
            i for i in result.issues 
            if "word" in i.message.lower()
        ]
        assert len(word_count_issues) > 0
    
    def test_issue_has_file_path(self, test_project_dir):
        """Test that issues include file path."""
        readme = test_project_dir / "README.md"
        readme.write_text("# Title")
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        for issue in result.issues:
            if issue.file_path:
                assert "README" in issue.file_path


# ============================================================================
# Test Class: Validation Result
# ============================================================================

class TestValidationResult:
    """Test validation result structure."""
    
    def test_result_structure_complete(self, sample_readme_complete):
        """Test result has all required fields."""
        validator = ReadmeValidator()
        result = validator.validate(sample_readme_complete.parent)
        
        assert hasattr(result, 'exists')
        assert hasattr(result, 'has_required_sections')
        assert hasattr(result, 'missing_required')
        assert hasattr(result, 'missing_recommended')
        assert hasattr(result, 'word_count')
        assert hasattr(result, 'score')
        assert hasattr(result, 'issues')
    
    def test_result_exists_flag(self, test_project_dir):
        """Test exists flag is set correctly."""
        validator = ReadmeValidator()
        
        # No README
        result_no_readme = validator.validate(test_project_dir)
        assert result_no_readme.exists is False
        
        # With README
        (test_project_dir / "README.md").write_text("# Test")
        result_with_readme = validator.validate(test_project_dir)
        assert result_with_readme.exists is True
    
    def test_result_has_required_sections_flag(self, test_project_dir):
        """Test has_required_sections flag."""
        readme = test_project_dir / "README.md"
        
        # Incomplete
        readme.write_text("# Title")
        validator = ReadmeValidator()
        result_incomplete = validator.validate(test_project_dir)
        assert result_incomplete.has_required_sections is False
        
        # Complete
        content = """# Title
## Description
Desc
## Installation
Install
## Usage
Use
"""
        readme.write_text(content)
        result_complete = validator.validate(test_project_dir)
        assert result_complete.has_required_sections is True


# ============================================================================
# Test Class: Quality Indicators
# ============================================================================

class TestQualityIndicators:
    """Test quality indicator checks."""
    
    def test_has_code_examples(self, test_project_dir):
        """Test detection of code examples."""
        readme = test_project_dir / "README.md"
        content = """# Test
```python
print("hello")
```
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_code_examples'] is True
    
    def test_has_links(self, test_project_dir):
        """Test detection of links."""
        readme = test_project_dir / "README.md"
        content = "# Test\n[Link](https://example.com)"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_links'] is True
    
    def test_has_images(self, test_project_dir):
        """Test detection of images."""
        readme = test_project_dir / "README.md"
        content = "# Test\n![Image](image.png)"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_images'] is True
    
    def test_has_badges(self, test_project_dir):
        """Test detection of badges."""
        readme = test_project_dir / "README.md"
        content = "# Test\n![Build](https://img.shields.io/badge/build-passing-green)"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_badges'] is True
    
    def test_has_table_of_contents(self, test_project_dir):
        """Test detection of table of contents."""
        readme = test_project_dir / "README.md"
        content = "# Test\n\n## Table of Contents\n- [Section 1](#section-1)"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_table_of_contents'] is True
    
    def test_has_license_section(self, test_project_dir):
        """Test detection of license section."""
        readme = test_project_dir / "README.md"
        content = "# Test\n\n## License\nMIT License"
        readme.write_text(content)
        
        validator = ReadmeValidator()
        indicators = validator.check_quality_indicators(content)
        
        assert indicators['has_license_section'] is True


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_readme(self, test_project_dir):
        """Test validation of empty README."""
        readme = test_project_dir / "README.md"
        readme.write_text("")
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert result.exists is True
        assert result.word_count == 0
        assert result.score < 50
    
    def test_very_long_readme(self, test_project_dir):
        """Test validation of very long README."""
        readme = test_project_dir / "README.md"
        content = "# Title\n" + "word " * 10000
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert result.word_count > 5000
        # Should not penalize for being too long
        assert result.score >= 0
    
    def test_unicode_content(self, test_project_dir):
        """Test README with unicode content."""
        readme = test_project_dir / "README.md"
        content = """# プロジェクト
## 説明
これはテストです
## インストール
pip install test
## 使い方
python app.py
"""
        readme.write_text(content, encoding='utf-8')
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        # Should handle unicode gracefully
        assert result.exists is True
        assert result.word_count > 0
    
    def test_special_characters(self, test_project_dir):
        """Test README with special characters."""
        readme = test_project_dir / "README.md"
        content = """# Test™
## Description®
Special chars: © § ¶ † ‡
## Installation
pip install
## Usage
Run it
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert result.exists is True
    
    def test_malformed_markdown(self, test_project_dir):
        """Test README with malformed markdown."""
        readme = test_project_dir / "README.md"
        content = """# Title
## Description
[Broken link](
**Unclosed bold
`Unclosed code
## Installation
Install
## Usage
Use
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        # Should still validate despite malformed markdown
        assert result.exists is True
        assert result.score >= 0


# ============================================================================
# Test Class: Integration Tests
# ============================================================================

@pytest.mark.integration
class TestReadmeValidatorIntegration:
    """Integration tests for README validator."""
    
    def test_validate_real_project_structure(self, test_project_dir):
        """Test validation of realistic project."""
        readme = test_project_dir / "README.md"
        content = """# PolicyPilot Test Project

[![Build Status](https://img.shields.io/badge/build-passing-green)]()

## Description
This is a comprehensive test project for validating the README validator.
It includes all required sections and many recommended ones.

## Features
- Feature 1: Advanced scanning
- Feature 2: Detailed reporting
- Feature 3: Easy integration

## Requirements
- Python 3.8+
- FastAPI
- pytest

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Run the application:
```bash
python app.py
```

## Configuration
Set environment variables in `.env` file:
```
API_KEY=your_key
DEBUG=true
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
MIT License - see LICENSE file for details.

## Contact
- Email: test@example.com
- GitHub: @testuser
"""
        readme.write_text(content)
        
        validator = ReadmeValidator()
        result = validator.validate(test_project_dir)
        
        assert result.exists is True
        assert result.has_required_sections is True
        assert result.score >= 90.0
        assert result.word_count > 100
        assert len(result.missing_required) == 0
    
    def test_compare_good_vs_bad_readme(self, temp_dir):
        """Test scoring difference between good and bad READMEs."""
        # Good README
        good_dir = temp_dir / "good"
        good_dir.mkdir()
        good_readme = good_dir / "README.md"
        good_readme.write_text("""# Project
## Description
Comprehensive description with many details about the project.
## Installation
Detailed installation instructions.
## Usage
Detailed usage examples.
## Features
Many features listed.
## Contributing
Contribution guidelines.
## License
MIT License
""")
        
        # Bad README
        bad_dir = temp_dir / "bad"
        bad_dir.mkdir()
        bad_readme = bad_dir / "README.md"
        bad_readme.write_text("# Project\nShort description.")
        
        validator = ReadmeValidator()
        good_result = validator.validate(good_dir)
        bad_result = validator.validate(bad_dir)
        
        assert good_result.score > bad_result.score
        assert good_result.score >= 80.0
        assert bad_result.score < 50.0


# Made with Bob