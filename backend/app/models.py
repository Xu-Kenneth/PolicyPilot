"""
Pydantic models for request/response validation.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueType(str, Enum):
    """Types of issues that can be detected."""
    SECRET = "secret"
    README = "readme"
    PROMPT = "prompt"
    STRUCTURE = "structure"


class Issue(BaseModel):
    """Represents a single issue found during analysis."""
    type: IssueType
    severity: SeverityLevel
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class SecretMatch(BaseModel):
    """Represents a detected secret with detailed metadata."""
    pattern_name: str
    secret_type: str
    file_path: str
    line_number: int
    column_start: int
    column_end: Optional[int] = None
    matched_text: str
    context: str
    severity: SeverityLevel = SeverityLevel.CRITICAL
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    entropy: float = Field(ge=0.0, description="Shannon entropy of the secret")
    reason: str = Field(description="Why this was flagged as a secret")
    is_verified: bool = Field(default=False, description="Whether the secret was verified as valid")


class ReadmeValidationResult(BaseModel):
    """Results from README validation."""
    exists: bool
    has_required_sections: bool
    missing_required: List[str] = []
    missing_recommended: List[str] = []
    word_count: int = 0
    score: float = 0.0
    issues: List[Issue] = []


class PromptDocumentationResult(BaseModel):
    """Results from prompt documentation check."""
    total_prompts: int = 0
    documented_prompts: int = 0
    missing_fields: Dict[str, List[str]] = {}
    score: float = 0.0
    issues: List[Issue] = []


class ModuleScore(BaseModel):
    """Score for a specific module."""
    name: str
    score: float
    weight: float
    weighted_score: float
    issues_count: int
    critical_issues: int


class AnalysisResult(BaseModel):
    """Complete analysis results."""
    project_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Module results
    secrets_found: List[SecretMatch] = []
    readme_result: Optional[ReadmeValidationResult] = None
    prompt_result: Optional[PromptDocumentationResult] = None
    
    # Scoring
    module_scores: List[ModuleScore] = []
    total_score: float = 0.0
    passed: bool = False
    
    # Summary
    total_issues: int = 0
    critical_issues: int = 0
    files_analyzed: int = 0
    
    # All issues
    all_issues: List[Issue] = []


class UploadResponse(BaseModel):
    """Response after file upload."""
    success: bool
    message: str
    upload_id: str
    files_received: int
    files_processed: int


class AnalysisRequest(BaseModel):
    """Request to analyze uploaded files."""
    upload_id: str
    project_name: Optional[str] = "Unnamed Project"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Made with Bob
