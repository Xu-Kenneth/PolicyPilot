# PolicyPilot - Quick Start Guide

This guide provides a quick overview of the PolicyPilot architecture and implementation plan.

---

## 📋 What is PolicyPilot?

PolicyPilot is a **GitHub-integrated repository compliance analyzer** that:
- Scans repositories for security risks
- Validates README completeness
- Verifies prompt documentation
- Generates submission readiness scores (0-100)
- **Automatically commits and pushes changes to GitHub**
- **Tracks Bob AI session evidence**

---

## 🎯 Key Features

✅ **No External APIs** - Runs entirely locally  
✅ **No Database** - File-based storage  
✅ **GitHub Integration** - Clone repos via URL  
✅ **Dual Output** - JSON API + Markdown reports  
✅ **Full Automation** - Auto-commits with conventional messages  
✅ **Evidence Tracking** - Complete Bob session documentation  

---

## 🏗️ Architecture Overview

### Technology Stack
- **Backend:** Node.js + Express.js
- **Git Operations:** simple-git library
- **File Processing:** fs-extra
- **Testing:** Jest
- **CI/CD:** GitHub Actions

### Core Components

1. **API Layer** - REST endpoints for frontend integration
2. **Analysis Engine** - Security, README, and Prompt analyzers
3. **Scoring System** - Weighted algorithm (Security 40%, README 35%, Prompts 25%)
4. **Git Automation** - Commit grouping, message generation, auto-push
5. **Evidence System** - Bob session tracking and documentation

---

## 📊 Scoring System

### Overall Score Formula
```
Overall = (Security × 0.40) + (README × 0.35) + (Prompts × 0.25)
```

### Readiness Levels
| Score | Level | Submission Ready |
|-------|-------|------------------|
| 90-100 | Excellent | ✅ Yes |
| 80-89 | Good | ✅ Yes |
| 70-79 | Fair | ⚠️ Conditional |
| 60-69 | Poor | ❌ No |
| 0-59 | Critical | ❌ No |

---

## 🔄 Git Automation Strategy

### Commit Grouping Rules
1. **By Module** - All API files together
2. **By Feature** - Related functionality together
3. **By Type** - Docs, tests, configs separately
4. **By Dependency** - Dependent changes in one commit

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(analyzer): implement security pattern detection

- Add regex patterns for API keys, tokens, passwords
- Scan all JavaScript, Python, and config files
- Generate severity-based issue reports

Closes #12
```

### Automation Flow
1. Code changes generated
2. CommitGrouper analyzes and groups changes
3. MessageGenerator creates conventional commit messages
4. CommitManager stages and commits
5. SessionLogger records evidence
6. GitHubPusher pushes to GitHub
7. Evidence exported to `/evidence`

---

## 📝 Bob Evidence Strategy

### Evidence Structure
```
evidence/
├── sessions/          # Bob mode session logs
│   ├── 2026-05-03_plan_session_001.md
│   ├── 2026-05-03_code_session_001.md
│   └── session_index.json
├── prompts/           # Prompt documentation
│   ├── 001_initial_architecture.md
│   └── prompt_index.json
└── commits/           # Commit-to-session mapping
    ├── commit_to_session_map.json
    └── evidence_summary.md
```

### What Gets Tracked
- **Plan Mode:** Architecture decisions, design diagrams
- **Code Mode:** Implementation details, code structure
- **Advanced Mode:** Complex problem-solving, integrations
- **Ask Mode:** Questions, explanations, recommendations
- **Orchestrator Mode:** Task breakdown, workflow coordination

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (2-3 hours)
1. Project initialization
2. Express server setup
3. Git operations

### Phase 2: Core Analysis (4-5 hours)
4. Security analyzer
5. README validator
6. Prompt verifier
7. Scoring engine

### Phase 3: Reporting (2-3 hours)
8. Report generators
9. Analysis orchestrator

### Phase 4: Automation (3-4 hours)
10. Git automation
11. Bob evidence system

### Phase 5: Testing & Docs (3-4 hours)
12. Unit tests
13. Documentation
14. CI/CD setup

**Total Time:** 14-19 hours

---

## 📁 Project Structure

```
PolicyPilot/
├── src/
│   ├── api/              # Express routes, controllers, middleware
│   ├── core/             # Analysis engine, scoring, reports
│   ├── automation/       # Git automation, commit management
│   ├── evidence/         # Bob session tracking
│   ├── utils/            # Utilities and helpers
│   ├── config/           # Configuration files
│   └── server.js         # Entry point
├── tests/                # Unit and integration tests
├── temp/                 # Temporary clone directory
├── reports/              # Generated reports
├── evidence/             # Bob session evidence
├── docs/                 # Documentation
└── .github/workflows/    # GitHub Actions
```

---

## 🔌 API Endpoints

### POST `/api/analyze`
Analyze a GitHub repository

**Request:**
```json
{
  "repoUrl": "https://github.com/username/repo",
  "branch": "main",
  "options": {
    "includeSecurityScan": true,
    "includeReadmeCheck": true,
    "includePromptVerification": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "security": { "score": 85, "issues": [...] },
    "readme": { "score": 90, "sections": {...} },
    "prompts": { "score": 75, "promptCount": 8 },
    "overallScore": 83,
    "submissionReady": true
  }
}
```

### GET `/api/reports/:analysisId`
Download analysis report (JSON or Markdown)

### GET `/api/health`
Health check endpoint

---

## 🔐 Security Considerations

- Store GitHub token in environment variables
- Clone to temporary directory and cleanup
- Validate all inputs
- Limit repository size
- Timeout long-running operations

---

## 📚 Documentation Files

1. **[`ARCHITECTURE.md`](ARCHITECTURE.md)** - Complete system architecture (1300+ lines)
   - System design
   - Module specifications
   - API contracts
   - Scoring algorithms
   - Git automation details
   - Bob evidence strategy
   - Implementation roadmap

2. **[`DIAGRAMS.md`](DIAGRAMS.md)** - Visual architecture diagrams (600+ lines)
   - High-level architecture
   - Analysis pipeline
   - Git automation workflow
   - Module dependencies
   - Data flow
   - Scoring algorithm
   - Commit grouping
   - Evidence tracking
   - API flow
   - Deployment architecture
   - Security process
   - Implementation timeline

3. **`QUICK_START.md`** - This file

---

## ✅ Next Steps

1. **Review the Plan**
   - Read [`ARCHITECTURE.md`](ARCHITECTURE.md) for complete details
   - Review [`DIAGRAMS.md`](DIAGRAMS.md) for visual understanding
   - Provide feedback or request changes

2. **Approve and Implement**
   - Once approved, switch to **Code mode**
   - Follow the 14-commit implementation roadmap
   - Each commit will be automatically created with evidence

3. **Track Progress**
   - Bob will document each session
   - Evidence will be exported to `/evidence`
   - Commits will be linked to sessions

---

## 🎯 Success Criteria

✅ All analyzers implemented and tested  
✅ Scoring system accurate and weighted correctly  
✅ Git automation working with conventional commits  
✅ Bob evidence fully documented  
✅ API endpoints functional  
✅ Reports generated in JSON and Markdown  
✅ GitHub integration complete  
✅ CI/CD pipeline configured  

---

## 💡 Key Design Decisions

1. **Node.js + Express** - Best for file processing and Git operations
2. **No Database** - File-based storage for simplicity
3. **Weighted Scoring** - Security prioritized (40% weight)
4. **Conventional Commits** - Industry standard for commit messages
5. **Evidence Tracking** - Complete audit trail of Bob sessions
6. **Modular Architecture** - Easy to extend with new analyzers

---

## 🤝 Ready to Implement?

Once you approve this plan, I'll switch to **Code mode** and begin implementation following the commit-by-commit roadmap. Each commit will be:
- Logically grouped
- Conventionally formatted
- Automatically pushed to GitHub
- Fully documented with evidence

**Are you ready to proceed?**

---

*Quick Start Guide Version: 1.0*  
*Last Updated: 2026-05-03*  
*Author: Bob (Plan Mode)*