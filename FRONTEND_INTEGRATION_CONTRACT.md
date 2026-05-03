# PolicyPilot Frontend Integration Contract

## Document Purpose
This contract defines the complete API specification and frontend implementation requirements for the PolicyPilot compliance dashboard. It provides all necessary information for frontend developers to integrate with the backend API and build a fully functional compliance checking interface.

---

## 1. API ENDPOINTS SPECIFICATION

### 1.1 Health Check Endpoints

#### GET /
**Purpose:** Root endpoint health check  
**Authentication:** None  
**Response:** 200 OK

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-03T09:30:00.000000Z"
}
```

#### GET /api/health
**Purpose:** API health check endpoint  
**Authentication:** None  
**Response:** 200 OK

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-03T09:30:00.000000Z"
}
```

---

### 1.2 File Upload Endpoints

#### POST /api/upload
**Purpose:** Upload project files for analysis  
**Content-Type:** multipart/form-data  
**Authentication:** None

**Request:**
```
POST /api/upload
Content-Type: multipart/form-data

files: [File, File, ...]  (multiple files supported)
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_received": 5,
  "files_processed": 5
}
```

**Error Response:** 400 Bad Request
```json
{
  "detail": "No files provided"
}
```

**Supported File Types:**
- `.py`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`
- `.pdf`, `.docx`, `.ipynb`, `.sh`, `.env.example`

**File Size Limit:** 100MB total

---

### 1.3 Analysis Endpoints

#### POST /api/analyze
**Purpose:** Analyze previously uploaded files  
**Content-Type:** application/json  
**Authentication:** None

**Request Body:**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "My Project"  // Optional, defaults to "Unnamed Project"
}
```

**Response:** 200 OK
```json
{
  "project_name": "My Project",
  "timestamp": "2026-05-03T09:30:00.000000Z",
  "secrets_found": [
    {
      "pattern_name": "AWS Access Key ID",
      "secret_type": "aws_access_key",
      "file_path": "config/settings.py",
      "line_number": 42,
      "column_start": 15,
      "column_end": 35,
      "matched_text": "AKIA****",
      "context": "AWS_ACCESS_KEY = 'AKIA...'",
      "severity": "critical",
      "confidence": 0.95,
      "entropy": 4.2,
      "reason": "AWS Access Key ID detected",
      "is_verified": false
    }
  ],
  "readme_result": {
    "exists": true,
    "has_required_sections": false,
    "missing_required": ["## Installation"],
    "missing_recommended": ["## Contributing", "## License"],
    "word_count": 250,
    "score": 75.0,
    "issues": [
      {
        "type": "readme",
        "severity": "high",
        "message": "Missing required section: ## Installation",
        "file_path": "README.md",
        "line_number": null,
        "details": null
      }
    ]
  },
  "prompt_result": {
    "total_prompts": 3,
    "documented_prompts": 2,
    "missing_fields": {
      "prompts/analyze.txt": ["example", "constraints"]
    },
    "score": 80.0,
    "issues": [
      {
        "type": "prompt",
        "severity": "high",
        "message": "Missing required field: example",
        "file_path": "prompts/analyze.txt",
        "line_number": null,
        "details": null
      }
    ]
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
      "score": 75.0,
      "weight": 0.25,
      "weighted_score": 18.75,
      "issues_count": 3,
      "critical_issues": 0
    },
    {
      "name": "Prompt Documentation",
      "score": 80.0,
      "weight": 0.25,
      "weighted_score": 20.0,
      "issues_count": 2,
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
  "total_score": 80.0,
  "passed": true,
  "total_issues": 6,
  "critical_issues": 1,
  "files_analyzed": 15,
  "all_issues": [
    {
      "type": "secret",
      "severity": "critical",
      "message": "Detected AWS Access Key ID: AKIA****",
      "file_path": "config/settings.py",
      "line_number": 42,
      "details": {
        "pattern": "AWS Access Key ID",
        "context": "AWS_ACCESS_KEY = 'AKIA...'"
      }
    }
  ]
}
```

#### POST /api/upload-and-analyze
**Purpose:** Upload files and analyze in one request  
**Content-Type:** multipart/form-data  
**Authentication:** None

**Request:**
```
POST /api/upload-and-analyze
Content-Type: multipart/form-data

files: [File, File, ...]
project_name: "My Project"  (optional form field)
```

**Response:** Same as POST /api/analyze (200 OK with AnalysisResult)

---

### 1.4 Report Endpoints

#### GET /api/report/{report_id}/{format}
**Purpose:** Download generated report  
**Authentication:** None  
**Path Parameters:**
- `report_id`: UUID string (same as upload_id)
- `format`: Report format - `json`, `html`, or `md`

**Response:** 200 OK
- Content-Type: `application/json` (for json)
- Content-Type: `text/html` (for html)
- Content-Type: `text/markdown` (for md)
- Content-Disposition: `attachment; filename="policypilot_report_{report_id}.{format}"`

**Error Response:** 400 Bad Request
```json
{
  "detail": "Invalid format. Use: json, html, or md"
}
```

**Error Response:** 404 Not Found
```json
{
  "detail": "Report not found"
}
```

---

### 1.5 Management Endpoints

#### DELETE /api/upload/{upload_id}
**Purpose:** Delete uploaded files  
**Authentication:** None  
**Path Parameters:**
- `upload_id`: UUID string

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Upload deleted successfully"
}
```

#### GET /api/config
**Purpose:** Get current configuration (non-sensitive)  
**Authentication:** None

**Response:** 200 OK
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

### 1.6 Error Responses

All endpoints may return error responses in the following format:

**400 Bad Request:**
```json
{
  "error": "Bad request message",
  "detail": "Detailed error information",
  "timestamp": "2026-05-03T09:30:00.000000Z"
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found",
  "detail": "Detailed error information",
  "timestamp": "2026-05-03T09:30:00.000000Z"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "Detailed error information",
  "timestamp": "2026-05-03T09:30:00.000000Z"
}
```

---

## 2. REQUEST/RESPONSE SCHEMAS

### 2.1 UploadResponse Schema
```typescript
interface UploadResponse {
  success: boolean;
  message: string;
  upload_id: string;  // UUID format
  files_received: number;
  files_processed: number;
}
```

### 2.2 AnalysisRequest Schema
```typescript
interface AnalysisRequest {
  upload_id: string;  // UUID format, required
  project_name?: string;  // Optional, defaults to "Unnamed Project"
}
```

### 2.3 AnalysisResponse Schema

#### Main AnalysisResult
```typescript
interface AnalysisResult {
  project_name: string;
  timestamp: string;  // ISO 8601 format
  secrets_found: SecretMatch[];
  readme_result: ReadmeValidationResult | null;
  prompt_result: PromptDocumentationResult | null;
  module_scores: ModuleScore[];
  total_score: number;  // 0-100
  passed: boolean;
  total_issues: number;
  critical_issues: number;
  files_analyzed: number;
  all_issues: Issue[];
}
```

#### SecretMatch Schema
```typescript
interface SecretMatch {
  pattern_name: string;
  secret_type: string;
  file_path: string;
  line_number: number;
  column_start: number;
  column_end: number | null;
  matched_text: string;  // Masked (e.g., "AKIA****")
  context: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: number;  // 0.0-1.0
  entropy: number;  // Shannon entropy value
  reason: string;
  is_verified: boolean;
}
```

#### ReadmeValidationResult Schema
```typescript
interface ReadmeValidationResult {
  exists: boolean;
  has_required_sections: boolean;
  missing_required: string[];
  missing_recommended: string[];
  word_count: number;
  score: number;  // 0-100
  issues: Issue[];
}
```

#### PromptDocumentationResult Schema
```typescript
interface PromptDocumentationResult {
  total_prompts: number;
  documented_prompts: number;
  missing_fields: Record<string, string[]>;  // filepath -> missing fields
  score: number;  // 0-100
  issues: Issue[];
}
```

#### ModuleScore Schema
```typescript
interface ModuleScore {
  name: string;  // "Secret Scanner", "README Validator", etc.
  score: number;  // 0-100
  weight: number;  // 0.0-1.0 (e.g., 0.35 = 35%)
  weighted_score: number;  // score * weight
  issues_count: number;
  critical_issues: number;
}
```

#### Issue Schema
```typescript
interface Issue {
  type: "secret" | "readme" | "prompt" | "structure";
  severity: "critical" | "high" | "medium" | "low" | "info";
  message: string;
  file_path: string | null;
  line_number: number | null;
  details: Record<string, any> | null;
}
```

### 2.4 Report Schema

Reports are generated in three formats with the following structure:

#### JSON Report Structure
```typescript
interface JSONReport {
  metadata: {
    report_id: string;
    project_name: string;
    generated_at: string;  // ISO 8601
    generator_version: string;
    analysis_timestamp: string;  // ISO 8601
  };
  summary: {
    total_score: number;
    grade: "A" | "B" | "C" | "D" | "F";
    status: "PASS" | "WARNING" | "FAIL";
    passed: boolean;
    total_issues: number;
    critical_issues: number;
    files_analyzed: number;
  };
  scores: {
    overall: {
      score: number;
      max_score: number;
      percentage: number;
      grade: string;
      passed: boolean;
    };
    modules: Array<{
      name: string;
      score: number;
      weight: number;
      weighted_score: number;
      issues_count: number;
      critical_issues: number;
      contribution_to_total: number;
    }>;
  };
  secrets: {
    total_found: number;
    by_severity: Record<string, number>;
    by_type: Record<string, number>;
    by_confidence: {
      high: number;
      medium: number;
      low: number;
    };
    statistics: {
      average_confidence: number;
      average_entropy: number;
      high_confidence_count: number;
      unique_files: number;
    };
    details: SecretMatch[];
  };
  readme: {
    exists: boolean;
    has_required_sections: boolean;
    score: number;
    word_count: number;
    missing_required: string[];
    missing_recommended: string[];
    issues_count: number;
  } | null;
  prompts: {
    total_prompts: number;
    documented_prompts: number;
    documentation_rate: number;
    score: number;
    missing_fields: Record<string, string[]>;
    issues_count: number;
  } | null;
  issues: {
    total: number;
    by_severity: Record<string, number>;
    by_type: Record<string, number>;
    details: Issue[];
  };
  recommendations: string[];
  compliance: {
    pass_threshold: number;
    warning_threshold: number;
    meets_requirements: boolean;
    areas_for_improvement: string[];
  };
}
```

#### HTML Report
- Styled HTML document with embedded CSS
- Includes score cards, tables, and visual indicators
- Responsive design
- Color-coded severity levels

#### Markdown Report
- Comprehensive markdown with tables
- Progress bars using Unicode characters
- Emoji indicators for severity
- Structured sections with headers

---

## 3. UPLOAD BEHAVIOR

### 3.1 File Upload Specifications

**Supported File Types:**
- Python: `.py`
- Documentation: `.md`, `.txt`, `.pdf`, `.docx`
- Configuration: `.json`, `.yaml`, `.yml`, `.env.example`
- Notebooks: `.ipynb`
- Scripts: `.sh`

**File Size Limits:**
- Maximum total upload size: 100MB
- Individual file size: No specific limit (within total)

**Multipart Form-Data Structure:**
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="files"; filename="file1.py"
Content-Type: text/x-python

[file content]
------WebKitFormBoundary...
Content-Disposition: form-data; name="files"; filename="file2.md"
Content-Type: text/markdown

[file content]
------WebKitFormBoundary...--
```

**Multiple File Handling:**
- All files are uploaded with the same form field name: `files`
- Backend processes all files and stores them in a unique directory
- Upload ID (UUID) is generated to identify the upload session

### 3.2 Upload Response Details

**upload_id Generation:**
- UUID v4 format (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- Used for subsequent analysis and report retrieval
- Stored in backend for file management

**File Metadata Returned:**
- `files_received`: Number of files in the upload request
- `files_processed`: Number of files successfully saved (may differ if some files are skipped)

**Error Handling:**
- 400 Bad Request: No files provided
- 400 Bad Request: File type not allowed
- 413 Payload Too Large: Upload exceeds size limit
- 500 Internal Server Error: Upload processing failed

---

## 4. REPORT GENERATION

### 4.1 Report Formats

#### JSON Format
- **Purpose:** Machine-readable, complete data export
- **Content-Type:** `application/json`
- **Structure:** Comprehensive nested JSON with all analysis data
- **Use Case:** API integration, data processing, archival

#### HTML Format
- **Purpose:** Human-readable, styled report
- **Content-Type:** `text/html`
- **Structure:** Self-contained HTML with embedded CSS
- **Features:**
  - Color-coded severity levels
  - Score cards with visual indicators
  - Responsive design
  - Tables for detailed findings
- **Use Case:** Viewing in browser, printing, sharing

#### Markdown Format
- **Purpose:** Human-readable, version-control friendly
- **Content-Type:** `text/markdown`
- **Structure:** Structured markdown with tables and lists
- **Features:**
  - Progress bars using Unicode
  - Emoji indicators
  - Code blocks for examples
  - Hierarchical sections
- **Use Case:** Documentation, GitHub integration, version control

### 4.2 Report Content

All report formats include:

**Executive Summary:**
- Project name
- Overall score and grade
- Pass/fail status
- Total and critical issues count
- Files analyzed count

**Detailed Findings:**
- Secret detection results with confidence scores
- README validation results
- Prompt documentation results
- All issues grouped by severity

**Score Breakdown:**
- Module-by-module scores
- Weighted contributions
- Visual indicators (HTML/Markdown)

**Recommendations:**
- Actionable items to improve score
- Prioritized by severity
- Specific to detected issues

**Statistics:**
- Secret detection statistics (confidence, entropy, types)
- Issue distribution by severity and type
- File coverage metrics

---

## 5. SCORING SYSTEM

### 5.1 Score Calculation

**Weighted Scoring Formula:**
```
Total Score = (Secret Score × 0.35) + (README Score × 0.25) + 
              (Prompt Score × 0.25) + (Structure Score × 0.15)
```

**Component Weights:**
- **Secrets (35%):** Critical security issues
- **README (25%):** Documentation quality
- **Prompts (25%):** Prompt documentation completeness
- **Structure (15%):** Project organization

**Secret Score Calculation:**
- Starts at 100
- Deducts points based on severity and confidence:
  - Critical: 25 points × confidence multiplier
  - High: 15 points × confidence multiplier
  - Medium: 10 points × confidence multiplier
  - Low: 5 points × confidence multiplier
- Confidence multipliers:
  - High (≥0.8): 100% penalty
  - Medium (0.5-0.8): 70% penalty
  - Low (<0.5): 40% penalty

**README Score Calculation:**
- Starts at 100
- Deducts 20 points per missing required section
- Deducts 5 points per missing recommended section
- Deducts points for low word count:
  - <50 words: -20 points
  - 50-100 words: -10 points
  - 100-200 words: -5 points

**Prompt Score Calculation:**
- Base score from documentation ratio: (documented/total) × 100
- Deducts 5 points per missing required field
- Deducts 2 points per missing recommended field

### 5.2 Score Breakdown Schema

```typescript
interface ScoreBreakdown {
  module_scores: ModuleScore[];
  total_score: number;  // 0-100
  grade: "A" | "B" | "C" | "D" | "F";
  status: "PASS" | "WARNING" | "FAIL";
  passed: boolean;
}
```

### 5.3 Compliance Levels

**Grade Mapping:**
- **A (90-100):** Excellent - Minimal issues, high compliance
- **B (80-89):** Good - Minor issues, acceptable compliance
- **C (70-79):** Fair - Some issues, meets minimum requirements
- **D (60-69):** Poor - Multiple issues, below standard
- **F (<60):** Failing - Critical issues, non-compliant

**Status Mapping:**
- **PASS (≥70):** Meets compliance requirements
- **WARNING (50-69):** Below standard, needs improvement
- **FAIL (<50):** Does not meet compliance requirements

---

## 6. FRONTEND IMPLEMENTATION INSTRUCTIONS

### 6.1 Dashboard Overview Page

**UI Widgets:**
- **File Upload Dropzone**
  - Drag-and-drop area
  - Click to browse files
  - Visual feedback on hover
  - File type validation
  
- **Upload Button**
  - Primary action button
  - Disabled when no files selected
  - Shows loading state during upload
  
- **File List Display**
  - Table or list of selected files
  - Shows file name, size, type
  - Remove button for each file
  
- **Progress Indicators**
  - Upload progress bar
  - File count (X of Y uploaded)
  - Success/error messages

**Data Fields to Display:**
- File name (string)
- File size (formatted, e.g., "2.5 MB")
- File type/extension (string)
- Upload status (pending/uploading/success/error)

**Actions:**
1. **Select Files:**
   - User selects files via dropzone or file picker
   - Validate file types against allowed extensions
   - Display selected files in list

2. **Upload Files:**
   ```javascript
   const formData = new FormData();
   files.forEach(file => formData.append('files', file));
   
   const response = await fetch('/api/upload', {
     method: 'POST',
     body: formData
   });
   
   const result = await response.json();
   // Store result.upload_id for analysis
   ```

3. **Display Upload Result:**
   - Show success message with upload_id
   - Display files_received and files_processed
   - Enable "Analyze" button

**Error Handling:**
- Invalid file type: Show inline error, prevent upload
- Upload failed: Show error toast, allow retry
- Network error: Show error message with retry button

---

### 6.2 Analysis Page

**UI Widgets:**
- **Analysis Trigger Button**
  - Primary action button
  - Requires upload_id from previous step
  - Shows loading state during analysis
  
- **Results Display Cards**
  - Overall score card (large, prominent)
  - Module score cards (grid layout)
  - Issue summary cards
  
- **Score Visualization**
  - Circular progress gauge for overall score
  - Progress bars for module scores
  - Color-coded by grade (green/yellow/red)
  
- **Findings Tables**
  - Secrets table with severity badges
  - README issues list
  - Prompt issues list
  - Sortable and filterable

**Data Fields to Display:**

**Overall Score Card:**
- Total score (number, 0-100)
- Grade (letter, A-F)
- Status (PASS/WARNING/FAIL)
- Pass/fail indicator (icon/badge)

**Module Score Cards:**
- Module name (string)
- Score (number, 0-100)
- Weight percentage (number)
- Issues count (number)
- Critical issues count (number)

**Secrets Findings:**
- Pattern name (string)
- Secret type (string)
- File path (string)
- Line number (number)
- Severity (badge with color)
- Confidence (percentage)
- Matched text (masked string)

**README Issues:**
- Issue message (string)
- Severity (badge)
- Missing sections (list)
- Word count (number)
- Score (number)

**Prompt Issues:**
- File path (string)
- Missing fields (list)
- Severity (badge)
- Documentation rate (percentage)

**Actions:**

1. **Start Analysis:**
   ```javascript
   const response = await fetch('/api/analyze', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       upload_id: uploadId,
       project_name: projectName || 'Unnamed Project'
     })
   });
   
   const result = await response.json();
   // Display result in UI
   ```

2. **Display Results:**
   - Parse AnalysisResult response
   - Update score visualizations
   - Populate findings tables
   - Show recommendations

3. **Navigate to Reports:**
   - Button to view/download reports
   - Pass upload_id to reports page

**UI Layout Example:**
```
┌─────────────────────────────────────────┐
│  Overall Score: 85.5 / 100              │
│  Grade: B | Status: PASS ✅             │
└─────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┐
│ Secret       │ README       │ Prompt       │
│ Scanner      │ Validator    │ Docs         │
│ 75.0 (35%)   │ 90.0 (25%)   │ 85.0 (25%)   │
│ 1 issue      │ 2 issues     │ 1 issue      │
└──────────────┴──────────────┴──────────────┘

┌─────────────────────────────────────────┐
│ 🔒 Secrets Found (1)                    │
├─────────────────────────────────────────┤
│ [CRITICAL] AWS Access Key ID            │
│ File: config/settings.py:42             │
│ Confidence: 95%                         │
└─────────────────────────────────────────┘
```

---

### 6.3 Reports Page

**UI Widgets:**
- **Report Format Selector**
  - Radio buttons or dropdown
  - Options: JSON, HTML, Markdown
  - Default: HTML
  
- **Download Button**
  - Primary action button
  - Downloads selected format
  - Shows loading state
  
- **Report Preview Area**
  - For HTML format: iframe or embedded view
  - For Markdown: rendered preview
  - For JSON: formatted code block

**Data Fields to Display:**
- Report ID (upload_id)
- Generation timestamp (from analysis)
- Selected format (string)
- File size (if available)

**Actions:**

1. **Select Format:**
   ```javascript
   const [format, setFormat] = useState('html');
   // Update UI based on selection
   ```

2. **Generate/Download Report:**
   ```javascript
   const downloadReport = async (reportId, format) => {
     const response = await fetch(`/api/report/${reportId}/${format}`);
     
     if (response.ok) {
       const blob = await response.blob();
       const url = window.URL.createObjectURL(blob);
       const a = document.createElement('a');
       a.href = url;
       a.download = `policypilot_report_${reportId}.${format}`;
       a.click();
       window.URL.revokeObjectURL(url);
     }
   };
   ```

3. **Preview Report (HTML):**
   ```javascript
   const previewReport = async (reportId) => {
     const response = await fetch(`/api/report/${reportId}/html`);
     const html = await response.text();
     // Display in iframe or preview area
     document.getElementById('preview').srcdoc = html;
   };
   ```

**UI Layout Example:**
```
┌─────────────────────────────────────────┐
│ Report Format:                          │
│ ○ JSON  ● HTML  ○ Markdown             │
│                                         │
│ [Download Report]                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Preview:                                │
│ ┌─────────────────────────────────────┐ │
│ │ [HTML Report Preview]               │ │
│ │                                     │ │
│ │ PolicyPilot Analysis Report         │ │
│ │ Score: 85.5 / 100                   │ │
│ │ ...                                 │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

### 6.4 Error Handling

**UI Patterns:**

1. **Toast Notifications**
   - Position: Top-right corner
   - Duration: 3-5 seconds
   - Types: Success, Error, Warning, Info
   - Auto-dismiss with close button

2. **Inline Validation Messages**
   - Below form fields
   - Red text with error icon
   - Clear, actionable messages

3. **Loading Spinners**
   - During API calls
   - Disable interactive elements
   - Show progress percentage if available

4. **Retry Buttons**
   - For failed operations
   - Include error message
   - Allow user to retry action

**Error Response Structure:**
```typescript
interface ErrorResponse {
  error: string;  // User-friendly message
  detail?: string;  // Technical details
  timestamp: string;  // ISO 8601
}
```

**Error Handling Examples:**

```javascript
// Upload error
try {
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    showToast('error', error.error || 'Upload failed');
    return;
  }
  
  const result = await response.json();
  showToast('success', 'Files uploaded successfully');
} catch (error) {
  showToast('error', 'Network error. Please try again.');
}

// Analysis error
try {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ upload_id: uploadId })
  });
  
  if (!response.ok) {
    const error = await response.json();
    if (response.status === 404) {
      showToast('error', 'Upload not found. Please upload files again.');
    } else {
      showToast('error', error.error || 'Analysis failed');
    }
    return;
  }
  
  const result = await response.json();
  displayResults(result);
} catch (error) {
  showToast('error', 'Network error. Please try again.');
}
```

**Common Error Scenarios:**

| Error | Status | Message | Action |
|-------|--------|---------|--------|
| No files provided | 400 | "No files provided" | Show inline error, require file selection |
| Invalid file type | 400 | "File type not allowed" | Show file type error, remove invalid file |
| Upload too large | 413 | "Upload exceeds size limit" | Show size error, suggest reducing files |
| Upload not found | 404 | "Upload not found" | Redirect to upload page |
| Report not found | 404 | "Report not found" | Show error, suggest re-running analysis |
| Server error | 500 | "Internal server error" | Show error with retry button |
| Network error | - | "Network error" | Show error with retry button |

---

### 6.5 Data Flow Examples

#### Flow 1: Upload and Analyze
```
User Action                 Frontend                    Backend
─────────────────────────────────────────────────────────────────
1. Select files         → Validate file types
                        → Display file list
                        
2. Click "Upload"       → POST /api/upload
                          (multipart/form-data)
                                                    → Save files
                                                    → Generate upload_id
                        ← UploadResponse
                        → Store upload_id
                        → Show success message
                        
3. Click "Analyze"      → POST /api/analyze
                          { upload_id, project_name }
                                                    → Run secret scanner
                                                    → Validate README
                                                    → Check prompts
                                                    → Calculate scores
                                                    → Generate reports (background)
                        ← AnalysisResult
                        → Display scores
                        → Show findings
                        → Enable report download
```

#### Flow 2: Upload and Analyze (Combined)
```
User Action                 Frontend                    Backend
─────────────────────────────────────────────────────────────────
1. Select files         → Validate file types
                        → Display file list
                        
2. Click "Analyze Now"  → POST /api/upload-and-analyze
                          (multipart/form-data)
                          + project_name field
                                                    → Save files
                                                    → Run analysis
                                                    → Generate reports
                        ← AnalysisResult
                        → Display scores
                        → Show findings
                        → Enable report download
```

#### Flow 3: Download Report
```
User Action                 Frontend                    Backend
─────────────────────────────────────────────────────────────────
1. Select format        → Update UI
   (HTML/JSON/MD)       → Show preview (if HTML)
                        
2. Click "Download"     → GET /api/report/{id}/{format}
                                                    → Retrieve report file
                        ← File (with Content-Disposition)
                        → Trigger browser download
                        → Show success message
```

#### Flow 4: Error Recovery
```
User Action                 Frontend                    Backend
─────────────────────────────────────────────────────────────────
1. Upload fails         → POST /api/upload
                                                    → Error occurs
                        ← 500 Error Response
                        → Show error toast
                        → Enable retry button
                        
2. Click "Retry"        → POST /api/upload (again)
                                                    → Process successfully
                        ← UploadResponse
                        → Show success message
                        → Continue to analysis
```

---

## 7. COMPLETE API REFERENCE

### Quick Reference Table

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| GET | `/` | Root health check | None | HealthResponse |
| GET | `/api/health` | API health check | None | HealthResponse |
| POST | `/api/upload` | Upload files | multipart/form-data (files) | UploadResponse |
| POST | `/api/analyze` | Analyze uploaded files | AnalysisRequest (JSON) | AnalysisResult |
| POST | `/api/upload-and-analyze` | Upload and analyze | multipart/form-data (files + project_name) | AnalysisResult |
| GET | `/api/report/{id}/{format}` | Download report | None | File (json/html/md) |
| DELETE | `/api/upload/{id}` | Delete upload | None | Success message |
| GET | `/api/config` | Get configuration | None | Config object |

### Authentication
- **Current:** None required
- **Future:** Consider adding API key or JWT authentication for production

### Rate Limiting
- **Current:** Not implemented
- **Recommendation:** Implement rate limiting in production (e.g., 100 requests/hour per IP)

### CORS
- **Current:** Allows all origins (`*`)
- **Production:** Configure specific allowed origins

### Content Types
- **Requests:** `application/json` or `multipart/form-data`
- **Responses:** `application/json`, `text/html`, `text/markdown`

### Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: Upload exceeds size limit
- `500 Internal Server Error`: Server error

---

## 8. IMPLEMENTATION CHECKLIST

### Frontend Development Tasks

**Phase 1: Setup**
- [ ] Set up React/Vue/Angular project
- [ ] Configure API base URL
- [ ] Set up routing (Dashboard, Analysis, Reports)
- [ ] Install UI component library
- [ ] Set up state management

**Phase 2: Upload Page**
- [ ] Create file dropzone component
- [ ] Implement file validation
- [ ] Create file list display
- [ ] Implement upload progress indicator
- [ ] Handle upload API call
- [ ] Store upload_id in state
- [ ] Add error handling

**Phase 3: Analysis Page**
- [ ] Create score visualization components
- [ ] Create module score cards
- [ ] Create findings tables
- [ ] Implement analysis API call
- [ ] Display results dynamically
- [ ] Add filtering/sorting to tables
- [ ] Add error handling

**Phase 4: Reports Page**
- [ ] Create format selector
- [ ] Implement report download
- [ ] Add HTML preview
- [ ] Add Markdown preview
- [ ] Handle report API calls
- [ ] Add error handling

**Phase 5: Polish**
- [ ] Add loading states
- [ ] Implement toast notifications
- [ ] Add responsive design
- [ ] Optimize performance
- [ ] Add accessibility features
- [ ] Write tests

---

## 9. TESTING RECOMMENDATIONS

### API Testing
```bash
# Health check
curl http://localhost:8000/api/health

# Upload files
curl -X POST http://localhost:8000/api/upload \
  -F "files=@test.py" \
  -F "files=@README.md"

# Analyze
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<uuid>","project_name":"Test"}'

# Download report
curl http://localhost:8000/api/report/<uuid>/html -o report.html
```

### Frontend Testing
- Unit tests for components
- Integration tests for API calls
- E2E tests for user flows
- Accessibility testing
- Cross-browser testing

---

## 10. DEPLOYMENT NOTES

### Backend Requirements
- Python 3.9+
- FastAPI
- Uvicorn
- Dependencies in requirements.txt

### Frontend Requirements
- Node.js 16+
- Modern browser support
- HTTPS recommended for production

### Environment Variables
```bash
# Backend
DEBUG=false
HOST=0.0.0.0
PORT=8000
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Production Considerations
- Enable HTTPS
- Configure CORS properly
- Add authentication
- Implement rate limiting
- Set up monitoring
- Configure logging
- Add backup strategy

---

## APPENDIX A: Example Payloads

### Example Upload Response
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "upload_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "files_received": 3,
  "files_processed": 3
}
```

### Example Analysis Response (Abbreviated)
```json
{
  "project_name": "Sample Project",
  "timestamp": "2026-05-03T09:30:00.000000Z",
  "total_score": 85.5,
  "passed": true,
  "total_issues": 4,
  "critical_issues": 1,
  "files_analyzed": 12,
  "module_scores": [
    {
      "name": "Secret Scanner",
      "score": 75.0,
      "weight": 0.35,
      "weighted_score": 26.25,
      "issues_count": 1,
      "critical_issues": 1
    }
  ]
}
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-05-03  
**Backend Version:** 1.0.0  
**Contact:** PolicyPilot Development Team

---

*This contract is ready for Google Stitch frontend generation and provides all necessary specifications for building a complete PolicyPilot compliance dashboard.*