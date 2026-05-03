"""
README validator service for checking documentation quality.
"""
import re
from pathlib import Path
from typing import List, Optional, Tuple

from app.config import settings
from app.models import ReadmeValidationResult, Issue, IssueType, SeverityLevel


class ReadmeValidator:
    """Validates README files for completeness and quality."""
    
    def __init__(self):
        self.required_sections = settings.required_readme_sections
        self.recommended_sections = settings.recommended_readme_sections
    
    def validate(self, directory: Path) -> ReadmeValidationResult:
        """
        Validate README in a directory.
        
        Args:
            directory: Directory to check for README
            
        Returns:
            Validation results
        """
        # Find README file
        readme_path = self._find_readme(directory)
        
        if not readme_path:
            return ReadmeValidationResult(
                exists=False,
                has_required_sections=False,
                missing_required=self.required_sections,
                missing_recommended=self.recommended_sections,
                score=0.0,
                issues=[
                    Issue(
                        type=IssueType.README,
                        severity=SeverityLevel.CRITICAL,
                        message="No README file found in project root"
                    )
                ]
            )
        
        # Read README content
        content = self._read_readme(readme_path)
        
        # Check sections
        missing_required, missing_recommended = self._check_sections(content)
        
        # Calculate word count
        word_count = self._count_words(content)
        
        # Generate issues
        issues = self._generate_issues(
            missing_required,
            missing_recommended,
            word_count,
            readme_path
        )
        
        # Calculate score
        score = self._calculate_score(
            missing_required,
            missing_recommended,
            word_count
        )
        
        return ReadmeValidationResult(
            exists=True,
            has_required_sections=len(missing_required) == 0,
            missing_required=missing_required,
            missing_recommended=missing_recommended,
            word_count=word_count,
            score=score,
            issues=issues
        )
    
    def _find_readme(self, directory: Path) -> Optional[Path]:
        """
        Find README file in directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            Path to README or None
        """
        readme_names = [
            'README.md',
            'readme.md',
            'README.MD',
            'README.txt',
            'readme.txt',
            'README',
            'readme'
        ]
        
        for name in readme_names:
            readme_path = directory / name
            if readme_path.exists() and readme_path.is_file():
                return readme_path
        
        return None
    
    def _read_readme(self, readme_path: Path) -> str:
        """
        Read README content.
        
        Args:
            readme_path: Path to README
            
        Returns:
            README content
        """
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def _check_sections(self, content: str) -> Tuple[List[str], List[str]]:
        """
        Check for required and recommended sections.
        
        Args:
            content: README content
            
        Returns:
            Tuple of (missing_required, missing_recommended)
        """
        content_lower = content.lower()
        
        missing_required = []
        for section in self.required_sections:
            # Check if section header exists (case-insensitive)
            section_pattern = re.escape(section.lower())
            if not re.search(section_pattern, content_lower):
                missing_required.append(section)
        
        missing_recommended = []
        for section in self.recommended_sections:
            section_pattern = re.escape(section.lower())
            if not re.search(section_pattern, content_lower):
                missing_recommended.append(section)
        
        return missing_required, missing_recommended
    
    def _count_words(self, content: str) -> int:
        """
        Count words in README.
        
        Args:
            content: README content
            
        Returns:
            Word count
        """
        # Remove markdown syntax
        text = re.sub(r'[#*`\[\]()]', '', content)
        # Split on whitespace and count
        words = text.split()
        return len(words)
    
    def _generate_issues(
        self,
        missing_required: List[str],
        missing_recommended: List[str],
        word_count: int,
        readme_path: Path
    ) -> List[Issue]:
        """
        Generate issues based on validation results.
        
        Args:
            missing_required: Missing required sections
            missing_recommended: Missing recommended sections
            word_count: Word count
            readme_path: Path to README
            
        Returns:
            List of issues
        """
        issues = []
        
        # Missing required sections
        for section in missing_required:
            issues.append(Issue(
                type=IssueType.README,
                severity=SeverityLevel.HIGH,
                message=f"Missing required section: {section}",
                file_path=str(readme_path)
            ))
        
        # Missing recommended sections
        for section in missing_recommended:
            issues.append(Issue(
                type=IssueType.README,
                severity=SeverityLevel.MEDIUM,
                message=f"Missing recommended section: {section}",
                file_path=str(readme_path)
            ))
        
        # Word count issues
        if word_count < 50:
            issues.append(Issue(
                type=IssueType.README,
                severity=SeverityLevel.HIGH,
                message=f"README is too short ({word_count} words). Should be at least 50 words.",
                file_path=str(readme_path)
            ))
        elif word_count < 100:
            issues.append(Issue(
                type=IssueType.README,
                severity=SeverityLevel.MEDIUM,
                message=f"README is brief ({word_count} words). Consider adding more details.",
                file_path=str(readme_path)
            ))
        
        return issues
    
    def _calculate_score(
        self,
        missing_required: List[str],
        missing_recommended: List[str],
        word_count: int
    ) -> float:
        """
        Calculate README quality score.
        
        Args:
            missing_required: Missing required sections
            missing_recommended: Missing recommended sections
            word_count: Word count
            
        Returns:
            Score from 0-100
        """
        score = 100.0
        
        # Deduct for missing required sections (20 points each)
        score -= len(missing_required) * 20
        
        # Deduct for missing recommended sections (5 points each)
        score -= len(missing_recommended) * 5
        
        # Deduct for low word count
        if word_count < 50:
            score -= 20
        elif word_count < 100:
            score -= 10
        elif word_count < 200:
            score -= 5
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def check_quality_indicators(self, content: str) -> dict:
        """
        Check for quality indicators in README.
        
        Args:
            content: README content
            
        Returns:
            Dictionary with quality indicators
        """
        indicators = {
            'has_code_examples': bool(re.search(r'```', content)),
            'has_links': bool(re.search(r'\[.*?\]\(.*?\)', content)),
            'has_images': bool(re.search(r'!\[.*?\]\(.*?\)', content)),
            'has_badges': bool(re.search(r'!\[.*?\]\(https://img\.shields\.io', content)),
            'has_table_of_contents': bool(re.search(r'(?i)table of contents', content)),
            'has_license_section': bool(re.search(r'(?i)## license', content)),
        }
        
        return indicators


# Global instance
readme_validator = ReadmeValidator()

# Made with Bob
