"""
Configuration settings for PolicyPilot backend.
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "PolicyPilot"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File Upload
    upload_dir: Path = Path("uploads")
    temp_dir: Path = Path("temp")
    reports_dir: Path = Path("reports")
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [
        ".py", ".md", ".txt", ".json", ".yaml", ".yml",
        ".pdf", ".docx", ".ipynb", ".sh", ".env.example"
    ]
    
    # Secret Scanner
    secret_patterns: dict = {
        "api_key": r"(?i)(api[_-]?key|apikey)[\s]*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        "password": r"(?i)(password|passwd|pwd)[\s]*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?",
        "token": r"(?i)(token|auth[_-]?token)[\s]*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?",
        "secret": r"(?i)(secret|secret[_-]?key)[\s]*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        "private_key": r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
        "aws_key": r"(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)[\s]*[=:]\s*['\"]?([A-Z0-9]{20,})['\"]?",
        "github_token": r"(?i)gh[pousr]_[A-Za-z0-9_]{36,}",
        "slack_token": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}",
    }
    
    # README Validation
    required_readme_sections: List[str] = [
        "# ",  # Title
        "## Description",
        "## Installation",
        "## Usage",
    ]
    recommended_readme_sections: List[str] = [
        "## Features",
        "## Requirements",
        "## Configuration",
        "## Contributing",
        "## License",
    ]
    
    # Prompt Documentation
    required_prompt_fields: List[str] = [
        "purpose",
        "input_format",
        "output_format",
        "example",
    ]
    recommended_prompt_fields: List[str] = [
        "constraints",
        "edge_cases",
        "version",
        "author",
    ]
    
    # Scoring Weights
    scoring_weights: dict = {
        "secrets": 0.35,      # 35% - Critical security issue
        "readme": 0.25,       # 25% - Documentation quality
        "prompts": 0.25,      # 25% - Prompt documentation
        "structure": 0.15,    # 15% - Project structure
    }
    
    # Thresholds
    pass_threshold: float = 70.0
    warning_threshold: float = 50.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)

# Made with Bob
