# PolicyPilot Frontend-Backend Integration Guide

## Overview
This document provides the complete integration specifications between the PolicyPilot React frontend and FastAPI backend, ensuring exact compatibility with the Google Stitch frontend handoff specification.

## Backend Refinements Applied

### 1. AnalysisResult Schema Enhancement
**File**: `backend/app/models.py`

Added `upload_id` field to `AnalysisResult` model to support frontend report download functionality:

```python
class AnalysisResult(BaseModel):
    # ... existing fields ...
    upload_id: Optional[str] = None  # NEW: Report identifier for downloads
```

**Purpose**: The frontend uses `upload_id` from the analysis response to construct download URLs for reports in different formats (JSON, HTML, Markdown).

### 2. Scoring Engine Update
**File**: `backend/app/services/scoring_engine.py`

Updated `analyze_project()` method signature to accept and pass through `upload_id`:

```python
def analyze_project(
    self, 
    directory: Path, 
    project_name: str, 
    upload_id: str | None = None  # NEW parameter
) -> AnalysisResult:
```

### 3. API Endpoint Updates
**File**: `backend/app/main.py`

Updated both analysis endpoints to pass `upload_id` to the scoring engine:

```python
# POST /api/analyze
result = scoring_engine.analyze_project(
    directory=upload_path,
    project_name=request.project_name or "Unnamed Project",
    upload_id=request.upload_id  # NEW
)

# POST /api/upload-and-analyze
result = scoring_engine.analyze_project(
    directory=upload_path,
    project_name=project_name,
    upload_id=upload_id  # NEW
)
```

### 4. Enhanced CORS Configuration
**File**: `backend/app/main.py`

Configured CORS for optimal frontend integration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"                           # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Disposition"],  # For file downloads
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

## Frontend-Backend Contract Verification

### ✅ Exact Schema Matches

All response schemas match the frontend handoff specification:

#### AnalysisResult
```typescript
interface AnalysisResult {
  project_name: string;
  timestamp: string;              // ISO 8601 format
  secrets_found: SecretMatch[];
  readme_result: ReadmeValidationResult | null;
  prompt_result: PromptDocumentationResult | null;
  module_scores: ModuleScore[];
  total_score: number;            // 0-100
  passed: boolean;
  total_issues: number;
  critical_issues: number;
  files_analyzed: number;
  all_issues: Issue[];
  upload_id: string | null;       // ✅ ADDED for report downloads
}
```

#### SecretMatch
```typescript
interface SecretMatch {
  pattern_name: string;
  secret_type: string;            // ✅ Backend provides this
  file_path: string;
  line_number: number;
  column_start: number;
  column_end: number | null;
  matched_text: string;
  context: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: number;             // 0.0-1.0
  entropy: number;
  reason: string;
  is_verified: boolean;
}
```

#### ModuleScore
```typescript
interface ModuleScore {
  name: string;                   // ✅ "Secret Scanner", "README Validator", etc.
  score: number;                  // 0-100
  weight: number;                 // 0.0-1.0 (e.g., 0.35 = 35%)
  weighted_score: number;         // score * weight
  issues_count: number;
  critical_issues: number;
}
```

### ✅ API Endpoints

All endpoints match frontend expectations:

| Method | Endpoint | Frontend Usage | Status |
|--------|----------|----------------|--------|
| POST | `/api/upload` | File upload | ✅ Compatible |
| POST | `/api/analyze` | Analyze uploaded files | ✅ Compatible + upload_id |
| POST | `/api/upload-and-analyze` | Combined operation | ✅ Compatible + upload_id |
| GET | `/api/report/{report_id}/{format}` | Download reports | ✅ Compatible |
| DELETE | `/api/upload/{upload_id}` | Cleanup | ✅ Compatible |
| GET | `/api/config` | Get configuration | ✅ Compatible |
| GET | `/api/health` | Health check | ✅ Compatible |

## Integration Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env

# Run the server
python run.py
```

Backend will start on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if using npm/yarn)
npm install

# Start development server
npm run dev
```

Frontend should connect to `http://localhost:8000`

### 3. Environment Variables

**Backend** (`.env`):
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB

# Scoring Thresholds
PASS_THRESHOLD=70.0
WARNING_THRESHOLD=50.0
```

**Frontend** (environment-specific):
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### 4. API Usage Flow

#### Flow 1: Upload and Analyze (Two-Step)
```javascript
// Step 1: Upload files
const formData = new FormData();
files.forEach(file => formData.append('files', file));

const uploadResponse = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
});
const { upload_id } = await uploadResponse.json();

// Step 2: Analyze
const analysisResponse = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    upload_id: upload_id,
    project_name: 'My Project'
  })
});
const result = await analysisResponse.json();

// Step 3: Download report using upload_id from result
const reportUrl = `http://localhost:8000/api/report/${result.upload_id}/json`;
```

#### Flow 2: Upload and Analyze (Combined)
```javascript
const formData = new FormData();
files.forEach(file => formData.append('files', file));
formData.append('project_name', 'My Project');

const response = await fetch('http://localhost:8000/api/upload-and-analyze', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// Download report using upload_id from result
const reportUrl = `http://localhost:8000/api/report/${result.upload_id}/html`;
```

### 5. Report Downloads

The frontend can download reports in three formats using the `upload_id` from the analysis result:

```javascript
// JSON format
fetch(`http://localhost:8000/api/report/${upload_id}/json`)

// HTML format
fetch(`http://localhost:8000/api/report/${upload_id}/html`)

// Markdown format
fetch(`http://localhost:8000/api/report/${upload_id}/md`)
```

## Frontend Data Mapping

### Module Name Mapping
The backend provides these exact module names that the frontend expects:

```javascript
const moduleIcons = {
  "Secret Scanner": "🔒",
  "README Validator": "📝",
  "Prompt Documentation": "📋",
  "Project Structure": "📁"
};
```

### Severity Levels
Both frontend and backend use identical severity levels:
- `critical` - Red/Rose tone, highest priority
- `high` - Orange tone
- `medium` - Yellow tone
- `low` - Blue tone
- `info` - Gray tone

### Score Thresholds
```javascript
// Backend configuration (configurable via settings)
PASS_THRESHOLD = 70.0
WARNING_THRESHOLD = 50.0

// Frontend should use these for status display:
// score >= 70: "PASS" (green)
// score >= 50: "WARNING" (yellow)
// score < 50: "FAIL" (red)
```

## Testing Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-03T10:30:00.000Z"
}
```

### 2. Upload Test
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@test.py" \
  -F "files=@README.md"
```

### 3. Analysis Test
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"upload_id": "abc123", "project_name": "Test Project"}'
```

### 4. Report Download Test
```bash
curl http://localhost:8000/api/report/abc123/json -o report.json
```

## Production Considerations

### 1. CORS Configuration
For production, update CORS origins in `backend/app/main.py`:

```python
allow_origins=[
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com"
],
```

### 2. File Upload Limits
Adjust in `backend/app/config.py`:
```python
max_upload_size: int = 100 * 1024 * 1024  # 100MB default
```

### 3. Security Headers
Consider adding security headers for production:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)
```

### 4. Rate Limiting
Implement rate limiting for production (not included in current implementation).

## Troubleshooting

### Issue: CORS Errors
**Solution**: Verify backend CORS configuration includes your frontend origin.

### Issue: upload_id not in response
**Solution**: Ensure you're using the updated backend code with `upload_id` field added.

### Issue: Report not found (404)
**Solution**: Reports are generated asynchronously. Wait a moment after analysis completes, or use the combined `/api/upload-and-analyze` endpoint which generates reports synchronously.

### Issue: File upload fails
**Solution**: Check file size limits and allowed extensions in `backend/app/config.py`.

## Summary of Changes

✅ **Schema Compatibility**: Added `upload_id` to `AnalysisResult` model
✅ **API Enhancement**: Updated analysis endpoints to include `upload_id` in responses
✅ **CORS Configuration**: Configured for local development with common frontend ports
✅ **Type Safety**: Used proper Python type hints (`str | None`)
✅ **Documentation**: Complete integration guide with examples

## Next Steps

1. ✅ Backend refinements complete
2. ✅ CORS configured for development
3. ✅ Integration documentation created
4. ⏳ Test frontend-backend integration
5. ⏳ Deploy to staging environment
6. ⏳ Configure production CORS and security

---

**Last Updated**: 2026-05-03
**Backend Version**: 1.0.0
**Compatible Frontend**: Google Stitch PolicyPilot React App