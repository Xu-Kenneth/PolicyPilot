"""
Scoring engine for calculating overall project compliance scores.
"""
from pathlib import Path
from typing import List

from app.config import settings
from app.models import (
    AnalysisResult,
    ModuleScore,
    Issue,
    IssueType,
    SeverityLevel,
    SecretMatch,
    ReadmeValidationResult,
    PromptDocumentationResult
)
from app.services.secret_scanner import secret_scanner
from app.services.readme_validator import readme_validator
from app.services.prompt_checker import prompt_checker


class ScoringEngine:
    """Calculates compliance scores based on all checks."""
    
    def __init__(self):
        self.weights = settings.scoring_weights
        self.pass_threshold = settings.pass_threshold
        self.warning_threshold = settings.warning_threshold
    
    def analyze_project(self, directory: Path, project_name: str) -> AnalysisResult:
        """
        Perform complete project analysis.
        
        Args:
            directory: Project directory to analyze
            project_name: Name of the project
            
        Returns:
            Complete analysis results
        """
        # Run all checks
        secrets = secret_scanner.scan_directory(directory)
        readme_result = readme_validator.validate(directory)
        prompt_result = prompt_checker.check_directory(directory)
        
        # Calculate module scores
        module_scores = self._calculate_module_scores(
            secrets,
            readme_result,
            prompt_result
        )
        
        # Calculate total score
        total_score = self._calculate_total_score(module_scores)
        
        # Determine pass/fail
        passed = total_score >= self.pass_threshold
        
        # Collect all issues
        all_issues = self._collect_all_issues(secrets, readme_result, prompt_result)
        
        # Count files analyzed
        files_analyzed = self._count_files(directory)
        
        # Count critical issues
        critical_issues = sum(1 for issue in all_issues if issue.severity == SeverityLevel.CRITICAL)
        
        return AnalysisResult(
            project_name=project_name,
            secrets_found=secrets,
            readme_result=readme_result,
            prompt_result=prompt_result,
            module_scores=module_scores,
            total_score=total_score,
            passed=passed,
            total_issues=len(all_issues),
            critical_issues=critical_issues,
            files_analyzed=files_analyzed,
            all_issues=all_issues
        )
    
    def _calculate_module_scores(
        self,
        secrets: List[SecretMatch],
        readme_result: ReadmeValidationResult,
        prompt_result: PromptDocumentationResult
    ) -> List[ModuleScore]:
        """
        Calculate scores for each module.
        
        Args:
            secrets: Detected secrets
            readme_result: README validation results
            prompt_result: Prompt documentation results
            
        Returns:
            List of module scores
        """
        module_scores = []
        
        # Secrets score (inverse - fewer secrets = higher score)
        secrets_score = self._calculate_secrets_score(secrets)
        module_scores.append(ModuleScore(
            name="Secret Scanner",
            score=secrets_score,
            weight=self.weights['secrets'],
            weighted_score=secrets_score * self.weights['secrets'],
            issues_count=len(secrets),
            critical_issues=len(secrets)  # All secrets are critical
        ))
        
        # README score
        readme_score = readme_result.score if readme_result else 0.0
        readme_issues = len(readme_result.issues) if readme_result else 0
        readme_critical = sum(
            1 for issue in (readme_result.issues if readme_result else [])
            if issue.severity == SeverityLevel.CRITICAL
        )
        module_scores.append(ModuleScore(
            name="README Validator",
            score=readme_score,
            weight=self.weights['readme'],
            weighted_score=readme_score * self.weights['readme'],
            issues_count=readme_issues,
            critical_issues=readme_critical
        ))
        
        # Prompt documentation score
        prompt_score = prompt_result.score if prompt_result else 100.0
        prompt_issues = len(prompt_result.issues) if prompt_result else 0
        prompt_critical = sum(
            1 for issue in (prompt_result.issues if prompt_result else [])
            if issue.severity == SeverityLevel.CRITICAL
        )
        module_scores.append(ModuleScore(
            name="Prompt Documentation",
            score=prompt_score,
            weight=self.weights['prompts'],
            weighted_score=prompt_score * self.weights['prompts'],
            issues_count=prompt_issues,
            critical_issues=prompt_critical
        ))
        
        # Structure score (basic check for now)
        structure_score = 100.0  # Default to perfect if no specific checks
        module_scores.append(ModuleScore(
            name="Project Structure",
            score=structure_score,
            weight=self.weights['structure'],
            weighted_score=structure_score * self.weights['structure'],
            issues_count=0,
            critical_issues=0
        ))
        
        return module_scores
    
    def _calculate_secrets_score(self, secrets: List[SecretMatch]) -> float:
        """
        Calculate score based on secrets found with confidence weighting.
        
        Uses confidence scores to weight the penalty for each secret.
        High-confidence secrets receive full penalty, low-confidence receive reduced penalty.
        
        Args:
            secrets: List of detected secrets
            
        Returns:
            Score from 0-100
        """
        if not secrets:
            return 100.0
        
        # Start at 100 and deduct based on severity and confidence
        score = 100.0
        
        for secret in secrets:
            # Base penalty by severity
            if secret.severity == SeverityLevel.CRITICAL:
                base_penalty = 25  # Critical secrets heavily penalized
            elif secret.severity == SeverityLevel.HIGH:
                base_penalty = 15
            elif secret.severity == SeverityLevel.MEDIUM:
                base_penalty = 10
            else:
                base_penalty = 5
            
            # Apply confidence weighting
            # High confidence (≥0.8): 100% penalty
            # Medium confidence (0.5-0.8): 70% penalty
            # Low confidence (<0.5): 40% penalty
            confidence_multiplier = 1.0
            if secret.confidence < 0.5:
                confidence_multiplier = 0.4
            elif secret.confidence < 0.8:
                confidence_multiplier = 0.7
            
            weighted_penalty = base_penalty * confidence_multiplier
            score -= weighted_penalty
        
        return max(0.0, score)
    
    def _calculate_total_score(self, module_scores: List[ModuleScore]) -> float:
        """
        Calculate weighted total score.
        
        Args:
            module_scores: List of module scores
            
        Returns:
            Total weighted score
        """
        total = sum(score.weighted_score for score in module_scores)
        return round(total, 2)
    
    def _collect_all_issues(
        self,
        secrets: List[SecretMatch],
        readme_result: ReadmeValidationResult,
        prompt_result: PromptDocumentationResult
    ) -> List[Issue]:
        """
        Collect all issues from all modules.
        
        Args:
            secrets: Detected secrets
            readme_result: README validation results
            prompt_result: Prompt documentation results
            
        Returns:
            List of all issues
        """
        all_issues = []
        
        # Convert secrets to issues
        for secret in secrets:
            all_issues.append(Issue(
                type=IssueType.SECRET,
                severity=secret.severity,
                message=f"Detected {secret.pattern_name}: {secret.matched_text}",
                file_path=secret.file_path,
                line_number=secret.line_number,
                details={
                    'pattern': secret.pattern_name,
                    'context': secret.context
                }
            ))
        
        # Add README issues
        if readme_result:
            all_issues.extend(readme_result.issues)
        
        # Add prompt issues
        if prompt_result:
            all_issues.extend(prompt_result.issues)
        
        # Sort by severity
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 4
        }
        all_issues.sort(key=lambda x: severity_order[x.severity])
        
        return all_issues
    
    def _count_files(self, directory: Path) -> int:
        """
        Count total files in directory.
        
        Args:
            directory: Directory to count files in
            
        Returns:
            Number of files
        """
        count = 0
        for item in directory.rglob('*'):
            if item.is_file():
                # Skip hidden files and common non-source files
                if not item.name.startswith('.') and item.suffix not in {'.pyc', '.pyo'}:
                    count += 1
        return count
    
    def get_grade(self, score: float) -> str:
        """
        Get letter grade for a score.
        
        Args:
            score: Score from 0-100
            
        Returns:
            Letter grade
        """
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
    
    def get_status(self, score: float) -> str:
        """
        Get status description for a score.
        
        Args:
            score: Score from 0-100
            
        Returns:
            Status description
        """
        if score >= self.pass_threshold:
            return "PASS"
        elif score >= self.warning_threshold:
            return "WARNING"
        else:
            return "FAIL"
    
    def get_recommendations(self, result: AnalysisResult) -> List[str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            result: Analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for critical issues
        if result.critical_issues > 0:
            recommendations.append(
                f"⚠️ Address {result.critical_issues} critical issue(s) immediately"
            )
        
        # Check secrets
        if result.secrets_found:
            recommendations.append(
                f"🔒 Remove {len(result.secrets_found)} hardcoded secret(s) from your code"
            )
        
        # Check README
        if result.readme_result and not result.readme_result.exists:
            recommendations.append("📝 Add a README.md file to document your project")
        elif result.readme_result and result.readme_result.missing_required:
            recommendations.append(
                f"📝 Add missing required README sections: {', '.join(result.readme_result.missing_required)}"
            )
        
        # Check prompts
        if result.prompt_result and result.prompt_result.total_prompts > 0:
            undocumented = result.prompt_result.total_prompts - result.prompt_result.documented_prompts
            if undocumented > 0:
                recommendations.append(
                    f"📋 Document {undocumented} prompt file(s) with required fields"
                )
        
        # General recommendations based on score
        if result.total_score < self.pass_threshold:
            recommendations.append(
                f"📊 Improve overall score to at least {self.pass_threshold} to pass compliance check"
            )
        
        return recommendations


# Global instance
scoring_engine = ScoringEngine()

# Made with Bob
