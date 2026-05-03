# PolicyPilot Backend

FastAPI-based backend for PolicyPilot - IBM watsonx Policy Compliance Checker.

## Features

- 📤 **File Upload System**: Secure file upload with validation
- 🔒 **Secret Scanner**: Detects hardcoded secrets and credentials
- 📝 **README Validator**: Checks documentation completeness
- 📋 **Prompt Documentation Checker**: Validates prompt file documentation
- 📊 **Scoring Engine**: Calculates compliance scores with weighted modules
- 📄 **Report Generator**: Creates JSON, HTML, and Markdown reports

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Running the Server

**Development mode:**
```bash
python run.py
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Health Check
```http
GET /api/health
```

### Upload Files
```http
POST /api/upload
Content-Type: multipart/form-data

files: [file1, file2, ...]
```

### Analyze Project
```http
POST /api/analyze
Content-Type: application/json

{
  "upload_id": "uuid",
  "project_name": "My Project"
}
```

### Upload and Analyze (Combined)
```http
POST /api/upload-and-analyze
Content-Type: multipart/form-data

files: [file1, file2, ...]
project_name: "My Project"
```

### Get Report
```http
GET /api/report/{report_id}/{format}

format: json | html | md
```

### Delete Upload
```http
DELETE /api/upload/{upload_id}
```

### Get Configuration
```http
GET /api/config
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── file_handler.py       # File upload handling
│       ├── secret_scanner.py     # Secret detection
│       ├── readme_validator.py   # README validation
│       ├── prompt_checker.py     # Prompt documentation
│       ├── scoring_engine.py     # Score calculation
│       └── report_generator.py   # Report generation
├── uploads/             # Uploaded files (created at runtime)
├── reports/             # Generated reports (created at runtime)
├── temp/                # Temporary files (created at runtime)
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment configuration
├── .gitignore          # Git ignore rules
├── run.py              # Server entry point
└── README.md           # This file
```

## Configuration

Configuration is managed through environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | PolicyPilot | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `DEBUG` | false | Debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `MAX_UPLOAD_SIZE` | 104857600 | Max upload size (bytes) |
| `PASS_THRESHOLD` | 70.0 | Passing score threshold |
| `WARNING_THRESHOLD` | 50.0 | Warning score threshold |

## Scoring System

The scoring system uses weighted modules:

| Module | Weight | Description |
|--------|--------|-------------|
| Secret Scanner | 35% | Critical security issues |
| README Validator | 25% | Documentation quality |
| Prompt Documentation | 25% | Prompt file documentation |
| Project Structure | 15% | Project organization |

**Score Ranges:**
- **90-100**: Grade A (Excellent)
- **80-89**: Grade B (Good)
- **70-79**: Grade C (Pass)
- **60-69**: Grade D (Warning)
- **0-59**: Grade F (Fail)

## Secret Detection Patterns

The secret scanner detects:
- API keys
- Passwords
- Tokens
- Secret keys
- Private keys
- AWS credentials
- GitHub tokens
- Slack tokens

## Development

### Adding New Validators

1. Create a new service in `app/services/`
2. Implement the validation logic
3. Add to `scoring_engine.py`
4. Update weights in `config.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env or use different port
uvicorn app.main:app --port 8001
```

### Module Import Errors
```bash
# Ensure you're in the backend directory
cd backend
# Reinstall dependencies
pip install -r requirements.txt
```

### File Upload Issues
- Check `MAX_UPLOAD_SIZE` setting
- Verify file extensions are allowed
- Ensure `uploads/` directory is writable

## Security Considerations

- Files are validated before processing
- Uploaded files are stored in isolated directories
- Secret patterns use regex for detection
- No external API calls (fully local)
- No database required

## License

Part of PolicyPilot - IBM watsonx Policy Compliance Checker

## Support

For issues and questions, please refer to the main project documentation.