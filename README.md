# PolicyPilot

**AI-Powered Repository Compliance Analyzer**

PolicyPilot is an intelligent compliance checker that analyzes GitHub repositories for security risks, documentation completeness, and coding standards. It generates comprehensive readiness scores (0-100) with actionable insights for developers and teams.

## 🌟 Features

**Security Analysis** — Scans for hardcoded secrets, exposed credentials, and security vulnerabilities using intelligent pattern matching

**README Validation** — Checks documentation completeness against best practices (title, description, installation, usage, etc.)

**Prompt Documentation** — Verifies AI model prompts are properly documented with purpose, assumptions, and examples

**Submission Readiness** — Unified scoring algorithm (0-100) combining security, README quality, and documentation standards

**Interactive Dashboard** — Beautiful Streamlit UI with score gauges, progress bars, and detailed reports

**Multiple Export Formats** — Download analysis results as JSON, Markdown, or HTML reports

## 🏗️ Architecture

```
GitHub Repository
      ↓
streamlit_app.py (Frontend / UI)
      ↓
FastAPI Backend (app.main:app)
      ├─→ security_scanner.py      (Secret detection & analysis)
      ├─→ readme_validator.py      (Documentation quality)
      ├─→ prompt_checker.py        (Prompt documentation)
      ├─→ scoring_engine.py        (Unified scoring algorithm)
      └─→ report_generator.py      (Report generation)
      ↓
result: {score: 0-100, details: {...}, report: "..."}
```

## 📊 Scoring System

```
Overall Score = (Security × 0.40) + (README × 0.35) + (Prompts × 0.25)
```

| Score | Level | Status |
|-------|-------|--------|
| 90-100 | Excellent | ✅ Submission Ready |
| 80-89 | Good | ✅ Submission Ready |
| 70-79 | Fair | ⚠️ Needs Work |
| 60-69 | Poor | ❌ Not Ready |
| 0-59 | Critical | ❌ Not Ready |

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Xu-Kenneth/PolicyPilot.git
cd PolicyPilot
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Frontend:**
```bash
pip install -r requirements-streamlit.txt
```

### 4. Run Locally

**Terminal 1 - Backend API:**
```bash
cd backend
python run.py
# Server running on http://localhost:8000
# API docs: http://localhost:8000/api/docs
```

**Terminal 2 - Frontend UI:**
```bash
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

### 5. Test the App

1. Open http://localhost:8501 in your browser
2. You should see: **"✅ Backend API is healthy"**
3. Upload a project folder or files
4. Click "Analyze" and watch the scoring happen!
5. Download your compliance report

## 💻 Usage

### Upload & Analyze
1. Drag and drop files or click to upload
2. Enter project name (optional)
3. Click "Analyze"

### View Results
- **Score Card** — Main compliance score with letter grade
- **Module Breakdown** — Individual scores for Security, README, Prompts
- **Details Tab** — Specific findings and issues
- **Report Downloads** — JSON, Markdown, or HTML format

### Example Questions PolicyPilot Answers
- "Does this repo have hardcoded API keys or credentials?"
- "Is the README complete with all required sections?"
- "Are AI prompts properly documented?"
- "What's the security risk level?"
- "Is this project ready for submission?"

## 📋 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Streamlit |
| **Analysis** | Pattern matching, regex, heuristics |
| **Security** | Secret detection, entropy analysis |
| **UI** | Streamlit, Plotly |
| **Export** | JSON, Markdown, HTML |

## 🔐 Security Features

**Detects:**
- API keys and tokens (AWS, GitHub, Slack, etc.)
- Hardcoded passwords and database credentials
- Private SSH keys
- Database connection strings
- OAuth tokens
- Custom secrets based on patterns

**Analysis includes:**
- Entropy scores for potential secrets
- Confidence levels
- File locations and line numbers
- Severity ratings

## 📖 Documentation

Read the full documentation:

- **[START_HERE_DEPLOYMENT.md](START_HERE_DEPLOYMENT.md)** — Easy deployment guide
- **[DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)** — All deployment docs index
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Detailed system architecture
- **[API_EXAMPLES.md](backend/API_EXAMPLES.md)** — API endpoint examples
- **[STREAMLIT_README.md](STREAMLIT_README.md)** — Frontend guide

## 🌐 Live Demo

Check out PolicyPilot running live:

- **Frontend:** [Coming Soon - Streamlit Cloud]
- **Backend API:** [Coming Soon - Render]
- **API Docs:** [Coming Soon - Swagger UI]

## 💻 Local Development

### Running Tests
```bash
cd backend
pytest
```

### Project Structure
```
PolicyPilot/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── models.py               # Data models
│   │   └── services/
│   │       ├── secret_scanner.py   # Security analysis
│   │       ├── readme_validator.py # README validation
│   │       ├── prompt_checker.py   # Prompt documentation
│   │       ├── scoring_engine.py   # Score calculation
│   │       └── report_generator.py # Report creation
│   ├── requirements.txt
│   └── run.py
├── streamlit_app.py                # Frontend UI
├── requirements-streamlit.txt      # Frontend dependencies
├── Dockerfile.backend              # Backend container
├── Dockerfile.frontend             # Frontend container
├── docker-compose.yml              # Local Docker setup
└── README.md                        # This file
```

## 🚀 Deployment

### Option 1: Streamlit Cloud + Render (Recommended)
- **Frontend:** Deploy to [Streamlit Cloud](https://streamlit.io/cloud) (free)
- **Backend:** Deploy to [Render](https://render.com) (free tier)
- **Setup time:** ~15 minutes

See [START_HERE_DEPLOYMENT.md](START_HERE_DEPLOYMENT.md) for detailed instructions.

### Option 2: Docker Local Development
```bash
docker-compose up
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional security patterns
- [ ] Support for more file types
- [ ] Custom scoring rules
- [ ] GitHub webhook integration
- [ ] CI/CD pipeline examples

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Kenneth Xu** ([GitHub](https://github.com/Xu-Kenneth))

---

## 🙋 Support & Questions

- **Issues?** Check [TROUBLESHOOTING_RAILWAY.md](TROUBLESHOOTING_RAILWAY.md)
- **Questions?** Open a GitHub issue
- **Want to contribute?** Submit a pull request

---

**Made with ❤️ for developers who care about code quality**
