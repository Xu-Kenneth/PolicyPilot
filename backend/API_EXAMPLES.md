# PolicyPilot API Examples

Complete examples for using the PolicyPilot backend API.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required (local deployment).

---

## 1. Health Check

Check if the API is running.

### Request

```bash
curl http://localhost:8000/api/health
```

### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## 2. Upload Files

Upload project files for analysis.

### Request

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@README.md" \
  -F "files=@main.py" \
  -F "files=@config.json"
```

### Response

```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_received": 3,
  "files_processed": 3
}
```

---

## 3. Analyze Project

Analyze previously uploaded files.

### Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_name": "My Watsonx Project"
  }'
```

### Response

```json
{
  "project_name": "My Watsonx Project",
  "timestamp": "2024-01-15T10:35:00.000Z",
  "secrets_found": [
    {
      "pattern_name": "api_key",
      "file_path": "config.py",
      "line_number": 15,
      "matched_text": "api_**********************",
      "context": "API_KEY = 'sk-1234567890abcdef'",
      "severity": "critical"
    }
  ],
  "readme_result": {
    "exists": true,
    "has_required_sections": true,
    "missing_required": [],
    "missing_recommended": ["## Contributing", "## License"],
    "word_count": 450,
    "score": 85.0,
    "issues": []
  },
  "prompt_result": {
    "total_prompts": 5,
    "documented_prompts": 4,
    "missing_fields": {
      "prompts/query.txt": ["example"]
    },
    "score": 80.0,
    "issues": []
  },
  "module_scores": [
    {
      "name": "Secret Scanner",
      "score": 75.0,
      "weight": 0.35,
      "weighted_score": 26.25,
      "issues_count": 1,
      "critical_issues": 1
    },
    {
      "name": "README Validator",
      "score": 85.0,
      "weight": 0.25,
      "weighted_score": 21.25,
      "issues_count": 2,
      "critical_issues": 0
    },
    {
      "name": "Prompt Documentation",
      "score": 80.0,
      "weight": 0.25,
      "weighted_score": 20.0,
      "issues_count": 1,
      "critical_issues": 0
    },
    {
      "name": "Project Structure",
      "score": 100.0,
      "weight": 0.15,
      "weighted_score": 15.0,
      "issues_count": 0,
      "critical_issues": 0
    }
  ],
  "total_score": 82.5,
  "passed": true,
  "total_issues": 4,
  "critical_issues": 1,
  "files_analyzed": 15,
  "all_issues": [...]
}
```

---

## 4. Upload and Analyze (Combined)

Upload and analyze in a single request.

### Request

```bash
curl -X POST http://localhost:8000/api/upload-and-analyze \
  -F "files=@README.md" \
  -F "files=@main.py" \
  -F "files=@prompts/query.txt" \
  -F "project_name=My Watsonx Project"
```

### Response

Same as the Analyze endpoint response.

---

## 5. Download Report (JSON)

Download the analysis report in JSON format.

### Request

```bash
curl http://localhost:8000/api/report/550e8400-e29b-41d4-a716-446655440000/json \
  -o report.json
```

### Response

Downloads `report.json` file with complete analysis results.

---

## 6. Download Report (HTML)

Download the analysis report in HTML format.

### Request

```bash
curl http://localhost:8000/api/report/550e8400-e29b-41d4-a716-446655440000/html \
  -o report.html
```

### Response

Downloads `report.html` file with formatted, styled report.

---

## 7. Download Report (Markdown)

Download the analysis report in Markdown format.

### Request

```bash
curl http://localhost:8000/api/report/550e8400-e29b-41d4-a716-446655440000/md \
  -o report.md
```

### Response

Downloads `report.md` file with markdown-formatted report.

---

## 8. Delete Upload

Delete uploaded files after analysis.

### Request

```bash
curl -X DELETE http://localhost:8000/api/upload/550e8400-e29b-41d4-a716-446655440000
```

### Response

```json
{
  "success": true,
  "message": "Upload deleted successfully"
}
```

---

## 9. Get Configuration

Get current API configuration.

### Request

```bash
curl http://localhost:8000/api/config
```

### Response

```json
{
  "app_name": "PolicyPilot",
  "version": "1.0.0",
  "max_upload_size_mb": 100.0,
  "allowed_extensions": [
    ".py", ".md", ".txt", ".json", ".yaml", ".yml",
    ".pdf", ".docx", ".ipynb", ".sh", ".env.example"
  ],
  "pass_threshold": 70.0,
  "warning_threshold": 50.0,
  "scoring_weights": {
    "secrets": 0.35,
    "readme": 0.25,
    "prompts": 0.25,
    "structure": 0.15
  }
}
```

---

## Python Examples

### Using requests library

```python
import requests

# Upload and analyze
files = {
    'files': [
        ('files', open('README.md', 'rb')),
        ('files', open('main.py', 'rb')),
    ]
}
data = {'project_name': 'My Project'}

response = requests.post(
    'http://localhost:8000/api/upload-and-analyze',
    files=files,
    data=data
)

result = response.json()
print(f"Score: {result['total_score']}")
print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")

# Download HTML report
report_id = result['timestamp']  # Use appropriate ID
report_response = requests.get(
    f'http://localhost:8000/api/report/{report_id}/html'
)

with open('report.html', 'wb') as f:
    f.write(report_response.content)
```

---

## JavaScript Examples

### Using fetch API

```javascript
// Upload and analyze
const formData = new FormData();
formData.append('files', fileInput.files[0]);
formData.append('files', fileInput.files[1]);
formData.append('project_name', 'My Project');

const response = await fetch('http://localhost:8000/api/upload-and-analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Score: ${result.total_score}`);
console.log(`Status: ${result.passed ? 'PASS' : 'FAIL'}`);

// Download report
const reportResponse = await fetch(
  `http://localhost:8000/api/report/${result.timestamp}/html`
);
const blob = await reportResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'report.html';
a.click();
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "No files provided",
  "detail": "HTTPException: 400",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 404 Not Found

```json
{
  "error": "Upload 550e8400-e29b-41d4-a716-446655440000 not found",
  "detail": "HTTPException: 404",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 413 Payload Too Large

```json
{
  "error": "File too large. Maximum size: 100.0MB",
  "detail": "HTTPException: 413",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "Unexpected error occurred",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Interactive API Documentation

Visit these URLs when the server is running:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

These provide interactive documentation where you can test all endpoints directly in your browser.