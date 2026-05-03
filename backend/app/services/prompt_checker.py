"""
Prompt documentation checker service for validating prompt files.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any

from app.config import settings
from app.models import PromptDocumentationResult, Issue, IssueType, SeverityLevel


class PromptChecker:
    """Checks prompt files for proper documentation."""
    
    def __init__(self):
        self.required_fields = settings.required_prompt_fields
        self.recommended_fields = settings.recommended_prompt_fields
    
    def check_directory(self, directory: Path) -> PromptDocumentationResult:
        """
        Check all prompt files in a directory.
        
        Args:
            directory: Directory to check
            
        Returns:
            Prompt documentation results
        """
        prompt_files = self._find_prompt_files(directory)
        
        if not prompt_files:
            return PromptDocumentationResult(
                total_prompts=0,
                documented_prompts=0,
                score=100.0,  # No prompts = no issues
                issues=[]
            )
        
        total_prompts = len(prompt_files)
        documented_prompts = 0
        missing_fields: Dict[str, List[str]] = {}
        issues: List[Issue] = []
        
        for prompt_file in prompt_files:
            is_documented, file_missing_fields, file_issues = self._check_prompt_file(prompt_file)
            
            if is_documented:
                documented_prompts += 1
            
            if file_missing_fields:
                missing_fields[str(prompt_file)] = file_missing_fields
            
            issues.extend(file_issues)
        
        # Calculate score
        score = self._calculate_score(total_prompts, documented_prompts, missing_fields)
        
        return PromptDocumentationResult(
            total_prompts=total_prompts,
            documented_prompts=documented_prompts,
            missing_fields=missing_fields,
            score=score,
            issues=issues
        )
    
    def _find_prompt_files(self, directory: Path) -> List[Path]:
        """
        Find all prompt-related files.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of prompt file paths
        """
        prompt_files = []
        
        # Look for common prompt file patterns
        patterns = [
            '**/prompts/**/*.txt',
            '**/prompts/**/*.md',
            '**/prompts/**/*.json',
            '**/*prompt*.txt',
            '**/*prompt*.md',
            '**/*prompt*.json',
        ]
        
        for pattern in patterns:
            prompt_files.extend(directory.glob(pattern))
        
        # Remove duplicates
        return list(set(prompt_files))
    
    def _check_prompt_file(self, file_path: Path) -> tuple[bool, List[str], List[Issue]]:
        """
        Check a single prompt file.
        
        Args:
            file_path: Path to prompt file
            
        Returns:
            Tuple of (is_documented, missing_fields, issues)
        """
        issues = []
        missing_fields = []
        
        # Read file content
        content = self._read_file(file_path)
        
        if not content:
            issues.append(Issue(
                type=IssueType.PROMPT,
                severity=SeverityLevel.HIGH,
                message="Prompt file is empty",
                file_path=str(file_path)
            ))
            return False, self.required_fields, issues
        
        # Check if it's JSON format
        if file_path.suffix == '.json':
            is_documented, missing = self._check_json_prompt(content, file_path)
            missing_fields = missing
        else:
            is_documented, missing = self._check_text_prompt(content, file_path)
            missing_fields = missing
        
        # Generate issues for missing fields
        for field in missing_fields:
            severity = SeverityLevel.HIGH if field in self.required_fields else SeverityLevel.MEDIUM
            issues.append(Issue(
                type=IssueType.PROMPT,
                severity=severity,
                message=f"Missing {'required' if field in self.required_fields else 'recommended'} field: {field}",
                file_path=str(file_path)
            ))
        
        return is_documented, missing_fields, issues
    
    def _check_json_prompt(self, content: str, file_path: Path) -> tuple[bool, List[str]]:
        """
        Check JSON-formatted prompt file.
        
        Args:
            content: File content
            file_path: Path to file
            
        Returns:
            Tuple of (is_documented, missing_fields)
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return False, self.required_fields
        
        missing_fields = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        # Check recommended fields
        for field in self.recommended_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        # Consider documented if all required fields are present
        is_documented = all(field not in missing_fields for field in self.required_fields)
        
        return is_documented, missing_fields
    
    def _check_text_prompt(self, content: str, file_path: Path) -> tuple[bool, List[str]]:
        """
        Check text/markdown prompt file.
        
        Args:
            content: File content
            file_path: Path to file
            
        Returns:
            Tuple of (is_documented, missing_fields)
        """
        content_lower = content.lower()
        missing_fields = []
        
        # Check for field markers in text
        field_patterns = {
            'purpose': r'(?:purpose|description|goal|objective):',
            'input_format': r'(?:input|input format|parameters):',
            'output_format': r'(?:output|output format|response|result):',
            'example': r'(?:example|sample|demo):',
            'constraints': r'(?:constraints|limitations|restrictions):',
            'edge_cases': r'(?:edge cases|special cases|corner cases):',
            'version': r'(?:version|v\d+):',
            'author': r'(?:author|created by|maintainer):',
        }
        
        for field, pattern in field_patterns.items():
            if not re.search(pattern, content_lower):
                missing_fields.append(field)
        
        # Consider documented if all required fields are present
        is_documented = all(field not in missing_fields for field in self.required_fields)
        
        return is_documented, missing_fields
    
    def _read_file(self, file_path: Path) -> str:
        """
        Read file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def _calculate_score(
        self,
        total_prompts: int,
        documented_prompts: int,
        missing_fields: Dict[str, List[str]]
    ) -> float:
        """
        Calculate prompt documentation score.
        
        Args:
            total_prompts: Total number of prompts
            documented_prompts: Number of documented prompts
            missing_fields: Missing fields per file
            
        Returns:
            Score from 0-100
        """
        if total_prompts == 0:
            return 100.0
        
        # Base score from documentation ratio
        documentation_ratio = documented_prompts / total_prompts
        score = documentation_ratio * 100
        
        # Deduct for missing fields
        total_missing_required = sum(
            1 for fields in missing_fields.values()
            for field in fields
            if field in self.required_fields
        )
        total_missing_recommended = sum(
            1 for fields in missing_fields.values()
            for field in fields
            if field in self.recommended_fields
        )
        
        # Deduct 5 points per missing required field
        score -= total_missing_required * 5
        
        # Deduct 2 points per missing recommended field
        score -= total_missing_recommended * 2
        
        return max(0.0, min(100.0, score))
    
    def validate_prompt_structure(self, content: str) -> Dict[str, Any]:
        """
        Validate the structure of a prompt.
        
        Args:
            content: Prompt content
            
        Returns:
            Validation results
        """
        results = {
            'has_clear_instructions': bool(re.search(r'(?:you must|you should|please|instruction)', content.lower())),
            'has_examples': bool(re.search(r'(?:example|sample|for instance)', content.lower())),
            'has_constraints': bool(re.search(r'(?:constraint|limitation|must not|should not)', content.lower())),
            'word_count': len(content.split()),
            'line_count': len(content.splitlines()),
            'has_formatting': bool(re.search(r'[#*`-]', content)),
        }
        
        return results


# Global instance
prompt_checker = PromptChecker()

# Made with Bob
