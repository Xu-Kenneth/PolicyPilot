"""
Pytest configuration and shared fixtures for PolicyPilot backend tests.
"""
import os
import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Generator

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.config import settings
from app.models import (
    SecretMatch,
    SeverityLevel,
    ReadmeValidationResult,
    PromptDocumentationResult,
    Issue,
    IssueType
)


# ============================================================================
# Test Client Fixtures
# ============================================================================

@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for async endpoints."""
    from httpx import ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# ============================================================================
# Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def test_project_dir(temp_dir: Path) -> Path:
    """Create a test project directory structure."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create subdirectories
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()
    (project_dir / "prompts").mkdir()
    
    return project_dir


@pytest.fixture
def upload_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Create temporary upload directory."""
    upload_path = temp_dir / "uploads"
    upload_path.mkdir()
    
    # Temporarily override settings
    original_upload_dir = settings.upload_dir
    settings.upload_dir = upload_path
    
    yield upload_path
    
    # Restore original settings
    settings.upload_dir = original_upload_dir


@pytest.fixture
def reports_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Create temporary reports directory."""
    reports_path = temp_dir / "reports"
    reports_path.mkdir()
    
    # Temporarily override settings
    original_reports_dir = settings.reports_dir
    settings.reports_dir = reports_path
    
    yield reports_path
    
    # Restore original settings
    settings.reports_dir = original_reports_dir


# ============================================================================
# Sample File Fixtures
# ============================================================================

@pytest.fixture
def sample_python_file(test_project_dir: Path) -> Path:
    """Create a sample Python file."""
    file_path = test_project_dir / "src" / "app.py"
    content = '''
"""Sample application file."""
import os

API_KEY = "sk_test_1234567890abcdefghijklmnop"
DATABASE_URL = "postgresql://user:password123@localhost/db"

def main():
    """Main function."""
    token = os.getenv("AUTH_TOKEN", "default_token")
    print(f"Starting app with token: {token}")

if __name__ == "__main__":
    main()
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_readme_complete(test_project_dir: Path) -> Path:
    """Create a complete README file."""
    readme_path = test_project_dir / "README.md"
    content = '''# Test Project

## Description
This is a comprehensive test project for PolicyPilot.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Run the application with:
```bash
python app.py
```

## Features
- Feature 1
- Feature 2
- Feature 3

## Requirements
- Python 3.8+
- FastAPI

## Configuration
Set environment variables in .env file.

## Contributing
Pull requests are welcome.

## License
MIT License
'''
    readme_path.write_text(content)
    return readme_path


@pytest.fixture
def sample_readme_incomplete(test_project_dir: Path) -> Path:
    """Create an incomplete README file."""
    readme_path = test_project_dir / "README.md"
    content = '''# Test Project

This is a test project.
'''
    readme_path.write_text(content)
    return readme_path


@pytest.fixture
def sample_prompt_json(test_project_dir: Path) -> Path:
    """Create a sample JSON prompt file."""
    prompt_path = test_project_dir / "prompts" / "test_prompt.json"
    content = '''{
    "purpose": "Test prompt for analysis",
    "input_format": "Text input",
    "output_format": "JSON response",
    "example": "Input: test\\nOutput: {result: success}",
    "constraints": "Max 1000 tokens",
    "version": "1.0.0",
    "author": "Test Author"
}'''
    prompt_path.write_text(content)
    return prompt_path


@pytest.fixture
def sample_prompt_text(test_project_dir: Path) -> Path:
    """Create a sample text prompt file."""
    prompt_path = test_project_dir / "prompts" / "test_prompt.txt"
    content = '''Purpose: Test prompt for analysis
Input: Text input format
Output: JSON response format
Example: Sample input and output
Constraints: Maximum 1000 tokens
Version: 1.0.0
Author: Test Author
'''
    prompt_path.write_text(content)
    return prompt_path


@pytest.fixture
def sample_prompt_incomplete(test_project_dir: Path) -> Path:
    """Create an incomplete prompt file."""
    prompt_path = test_project_dir / "prompts" / "incomplete_prompt.txt"
    content = '''This is a prompt without proper documentation.'''
    prompt_path.write_text(content)
    return prompt_path


# ============================================================================
# Secret Sample Fixtures
# ============================================================================

@pytest.fixture
def sample_secrets_file(test_project_dir: Path) -> Path:
    """Create a file with various secret patterns."""
    file_path = test_project_dir / "src" / "secrets.py"
    content = '''
# AWS Credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub Token (FAKE - for testing only)
GITHUB_TOKEN = "ghp_FAKE1234567890abcdefghijklmnopqrstuvwxyz"

# API Keys (FAKE - for testing only)
STRIPE_KEY = "sk_test_FAKE1234567890abcdefghijklmnop"
API_KEY = "AIzaSyFAKE1234567890abcdefghijklmnopqrstuv"

# Database URLs (FAKE - for testing only)
DATABASE_URL = "postgresql://testuser:testpass123@localhost:5432/testdb"
REDIS_URL = "redis://:testpassword@localhost:6379/0"

# JWT Token (FAKE - for testing only)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.FAKE.FAKE"

# Slack Token (FAKE - for testing only)
SLACK_TOKEN = "xoxb-FAKE-1234567890-1234567890-abcdefghijklmnopqrstuvwx"
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_false_positives_file(test_project_dir: Path) -> Path:
    """Create a file with false positive patterns."""
    file_path = test_project_dir / "src" / "config_example.py"
    content = '''
# Example configuration - not real secrets
API_KEY = "your_api_key_here"
SECRET_KEY = "insert_your_secret_here"
PASSWORD = "example_password"
TOKEN = "replace_with_your_token"

# Environment variable references
api_key = os.getenv("API_KEY")
secret = os.environ.get("SECRET_KEY")

# Test/Mock values
TEST_API_KEY = "test_key_12345"
MOCK_TOKEN = "mock_token_abcdef"
'''
    file_path.write_text(content)
    return file_path


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def sample_secret_match() -> SecretMatch:
    """Create a sample SecretMatch object."""
    return SecretMatch(
        pattern_name="AWS Access Key ID",
        secret_type="aws_access_key",
        file_path="src/config.py",
        line_number=10,
        column_start=15,
        column_end=35,
        matched_text="AKIA****EXAMPLE",
        context="AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'",
        severity=SeverityLevel.CRITICAL,
        confidence=0.95,
        entropy=4.2,
        reason="AWS Access Key ID detected"
    )


@pytest.fixture
def sample_readme_result() -> ReadmeValidationResult:
    """Create a sample README validation result."""
    return ReadmeValidationResult(
        exists=True,
        has_required_sections=True,
        missing_required=[],
        missing_recommended=["## Contributing", "## License"],
        word_count=250,
        score=85.0,
        issues=[
            Issue(
                type=IssueType.README,
                severity=SeverityLevel.MEDIUM,
                message="Missing recommended section: ## Contributing",
                file_path="README.md"
            )
        ]
    )


@pytest.fixture
def sample_prompt_result() -> PromptDocumentationResult:
    """Create a sample prompt documentation result."""
    return PromptDocumentationResult(
        total_prompts=5,
        documented_prompts=4,
        missing_fields={
            "prompts/incomplete.txt": ["purpose", "example"]
        },
        score=80.0,
        issues=[
            Issue(
                type=IssueType.PROMPT,
                severity=SeverityLevel.HIGH,
                message="Missing required field: purpose",
                file_path="prompts/incomplete.txt"
            )
        ]
    )


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_upload_files():
    """Create mock upload files for testing."""
    files = []
    
    # Python file
    py_content = b'print("Hello World")\nAPI_KEY = "test_key"'
    py_file = UploadFile(
        filename="test.py",
        file=BytesIO(py_content)
    )
    files.append(py_file)
    
    # README file
    md_content = b'# Test Project\n\n## Description\nTest description'
    md_file = UploadFile(
        filename="README.md",
        file=BytesIO(md_content)
    )
    files.append(md_file)
    
    return files


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_settings():
    """Provide test-specific settings."""
    return {
        "pass_threshold": 70.0,
        "warning_threshold": 50.0,
        "scoring_weights": {
            "secrets": 0.35,
            "readme": 0.25,
            "prompts": 0.25,
            "structure": 0.15
        }
    }


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Cleanup logic runs after test
    # Remove any test uploads or reports
    test_dirs = ["uploads", "reports", "temp"]
    for dir_name in test_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            for item in dir_path.iterdir():
                if item.name.startswith("test_"):
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)


# ============================================================================
# Parametrize Fixtures
# ============================================================================

@pytest.fixture(params=[
    "AKIAIOSFODNN7EXAMPLE",
    "AKIA1234567890ABCDEF",
    "ASIATESTACCESSKEY123"
])
def aws_access_key_samples(request):
    """Parametrized AWS access key samples."""
    return request.param


@pytest.fixture(params=[
    "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
    "gho_abcdefghijklmnopqrstuvwxyz1234567890",
    "ghu_zyxwvutsrqponmlkjihgfedcba0987654321"
])
def github_token_samples(request):
    """Parametrized GitHub token samples."""
    return request.param


@pytest.fixture(params=[
    SeverityLevel.CRITICAL,
    SeverityLevel.HIGH,
    SeverityLevel.MEDIUM,
    SeverityLevel.LOW,
    SeverityLevel.INFO
])
def severity_levels(request):
    """Parametrized severity levels."""
    return request.param


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_file(directory: Path, filename: str, content: str) -> Path:
    """Helper to create test files."""
    file_path = directory / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path


def create_test_structure(base_dir: Path, structure: dict) -> None:
    """
    Helper to create complex directory structures.
    
    Args:
        base_dir: Base directory
        structure: Dict with structure definition
    """
    for name, content in structure.items():
        path = base_dir / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_test_structure(path, content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)


# Make helper functions available
pytest.create_test_file = create_test_file
pytest.create_test_structure = create_test_structure

# Made with Bob