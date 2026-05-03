# PolicyPilot Streamlit Frontend

Complete Streamlit application for PolicyPilot compliance analyzer.

## Quick Start

### 1. Start Backend API
```bash
cd backend
python run.py
# API runs on http://localhost:8000
```

### 2. Install Streamlit Dependencies
```bash
pip install -r requirements-streamlit.txt
```

### 3. Run Streamlit App
```bash
streamlit run streamlit_app.py
# App opens at http://localhost:8501
```

## Features

### 📤 Upload & Analyze
- Drag-and-drop file upload
- Multiple file support
- Project name configuration
- One-click analysis

### 📊 Results Dashboard
- Score gauge with grade (A-F)
- Module breakdown with progress bars
- Detailed metrics (issues, critical issues, status)
- Interactive tabs for:
  - 🔒 Secret detection results
  - 📝 README validation
  - 📋 Prompt documentation
  - ⚠️ All issues table

### 📄 Report Downloads
- JSON format (machine-readable)
- HTML format (interactive web report)
- Markdown format (GitHub-friendly)
- Preview functionality

## Configuration

### API URL
Set the backend API URL in `.streamlit/secrets.toml`:

```toml
API_BASE_URL = "http://localhost:8000"
```

Or use environment variable:
```bash
export API_BASE_URL="http://localhost:8000"
```

### Theme
Customize theme in `.streamlit/config.toml`:
- Primary color: #667eea (purple)
- Background: white
- Secondary background: light gray

## API Integration

The Streamlit app connects to these backend endpoints:

- `GET /api/health` - Health check
- `POST /api/upload` - Upload files
- `POST /api/analyze` - Analyze project
- `POST /api/upload-and-analyze` - Combined operation
- `GET /api/report/{upload_id}/{format}` - Download reports
- `GET /api/config` - Get configuration

## UI Components

### Score Display
- Gradient background (purple)
- Large score number
- Letter grade (A-F)
- Pass/Fail status

### Module Scores
- Progress bars for each module
- Score and issue count metrics
- Expandable details with weights

### Secret Detection
- Severity badges (Critical, High, Medium, Low)
- Confidence and entropy scores
- Code context display
- File location with line numbers

### README Validation
- Score and word count
- Missing required sections
- Missing recommended sections
- Completion status

### Prompt Documentation
- Total and documented prompt counts
- Missing fields by file
- Score display

## Error Handling

- API connection check on startup
- Graceful error messages
- Exception handling for all API calls
- User-friendly error display

## Session State

The app uses Streamlit session state to store:
- `analysis_result` - Complete analysis data
- `upload_id` - For report downloads

## Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Set `API_BASE_URL` in secrets
4. Deploy

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-streamlit.txt .
RUN pip install -r requirements-streamlit.txt

COPY streamlit_app.py .
COPY .streamlit/ .streamlit/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
```

## Troubleshooting

### API Connection Failed
- Ensure backend is running on http://localhost:8000
- Check CORS configuration in backend
- Verify API_BASE_URL setting

### File Upload Issues
- Check file size limits (100MB default)
- Verify file types are allowed
- Ensure backend uploads/ directory exists

### Report Download Errors
- Wait for analysis to complete
- Check upload_id is valid
- Verify reports/ directory exists in backend

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/streamlit-dashboard.png)

### Analysis Results
![Results](docs/screenshots/streamlit-results.png)

### Report Downloads
![Reports](docs/screenshots/streamlit-reports.png)

## Development

### Adding New Features
1. Add API function in streamlit_app.py
2. Create UI component
3. Handle errors
4. Update documentation

### Custom Styling
Modify CSS in the `st.markdown()` section at the top of streamlit_app.py.

### Testing
```bash
# Run backend tests
cd backend
python test_frontend_integration.py

# Test Streamlit app manually
streamlit run streamlit_app.py
```

## Support

For issues and questions:
- Backend API: See `backend/README.md`
- Integration: See `backend/FRONTEND_BACKEND_INTEGRATION.md`
- Architecture: See `ARCHITECTURE.md`

---

**Built with ❤️ using Streamlit and IBM watsonx.ai**