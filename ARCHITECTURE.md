# PolicyPilot - System Architecture & Engineering Specification

**Version:** 1.0  
**Date:** 2026-05-03  
**Project Type:** Hackathon Repository Compliance Analyzer  
**Tech Stack:** Node.js + Express + Git Automation

---

## 1. EXECUTIVE SUMMARY

PolicyPilot is a GitHub-integrated repository compliance analyzer that evaluates repositories for security risks, documentation completeness, and submission readiness. The system operates entirely locally without external APIs or databases, with full automation for Git commits and GitHub integration.

### Key Features
- Security risk detection and analysis
- README completeness validation
- Prompt documentation verification
- Submission readiness scoring (0-100)
- Automated Git commit generation
- Bob AI session evidence tracking
- JSON API + Markdown report output

### Critical Constraints
✅ No external APIs or API keys  
✅ No database required  
✅ Runs entirely locally  
✅ Integrates with external frontend (Streamlit/Google Stitch)  
✅ Fully automated GitHub commit workflow  
✅ Bob evidence documentation per commit milestone

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                            │
│              (Streamlit / Google Stitch UI)                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   API GATEWAY LAYER                          │
│                  (Express.js Server)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │ Middleware   │  │   CORS       │     │
│  │   Handler    │  │   Validator  │  │   Config     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  CORE ANALYSIS ENGINE                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Repository Orchestrator                     │  │
│  │  (Coordinates all analysis modules)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Security   │  │   README    │  │   Prompt    │        │
│  │  Analyzer   │  │  Validator  │  │  Verifier   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Scoring   │  │   Report    │  │    Git      │        │
│  │   Engine    │  │  Generator  │  │  Cloner     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              GIT AUTOMATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Commit     │  │   Message    │  │   GitHub     │     │
│  │   Manager    │  │   Generator  │  │   Pusher     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BOB EVIDENCE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Session    │  │   Prompt     │  │   Commit     │     │
│  │   Logger     │  │   Tracker    │  │   Mapper     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Runtime** | Node.js 18+ | JavaScript runtime environment |
| **Web Framework** | Express.js 4.x | REST API server |
| **Git Operations** | simple-git | Git clone, commit, push automation |
| **File Processing** | fs-extra | Enhanced file system operations |
| **Markdown Parsing** | marked | README analysis |
| **Security Scanning** | Custom regex + patterns | Vulnerability detection |
| **Testing** | Jest | Unit and integration tests |
| **Linting** | ESLint | Code quality |
| **Process Management** | PM2 (optional) | Production deployment |

---

## 3. BACKEND MODULE STRUCTURE

### 3.1 Directory Structure

```
PolicyPilot/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analyze.routes.js       # Analysis endpoints
│   │   │   ├── health.routes.js        # Health check
│   │   │   └── report.routes.js        # Report download
│   │   ├── middleware/
│   │   │   ├── errorHandler.js         # Global error handling
│   │   │   ├── validator.js            # Request validation
│   │   │   └── cors.js                 # CORS configuration
│   │   └── controllers/
│   │       ├── analyzeController.js    # Analysis orchestration
│   │       └── reportController.js     # Report generation
│   │
│   ├── core/
│   │   ├── orchestrator/
│   │   │   └── AnalysisOrchestrator.js # Main coordinator
│   │   ├── analyzers/
│   │   │   ├── SecurityAnalyzer.js     # Security scanning
│   │   │   ├── ReadmeValidator.js      # README checks
│   │   │   └── PromptVerifier.js       # Prompt doc checks
│   │   ├── scoring/
│   │   │   ├── ScoringEngine.js        # Score calculation
│   │   │   └── weights.config.js       # Scoring weights
│   │   ├── git/
│   │   │   ├── GitCloner.js            # Repository cloning
│   │   │   └── GitCleaner.js           # Temp cleanup
│   │   └── reports/
│   │       ├── JsonReportGenerator.js  # JSON output
│   │       └── MarkdownReportGenerator.js # MD output
│   │
│   ├── automation/
│   │   ├── commits/
│   │   │   ├── CommitManager.js        # Commit orchestration
│   │   │   ├── CommitGrouper.js        # Logical grouping
│   │   │   └── MessageGenerator.js     # Commit messages
│   │   ├── github/
│   │   │   ├── GitHubPusher.js         # Push automation
│   │   │   └── BranchManager.js        # Branch operations
│   │   └── workflows/
│   │       └── githubActions.yml       # CI/CD template
│   │
│   ├── evidence/
│   │   ├── SessionLogger.js            # Bob session tracking
│   │   ├── PromptTracker.js            # Prompt documentation
│   │   ├── CommitMapper.js             # Commit-to-evidence mapping
│   │   └── EvidenceExporter.js         # Export functionality
│   │
│   ├── utils/
│   │   ├── fileUtils.js                # File operations
│   │   ├── logger.js                   # Logging utility
│   │   ├── constants.js                # App constants
│   │   └── validators.js               # Input validators
│   │
│   ├── config/
│   │   ├── app.config.js               # App configuration
│   │   ├── analysis.config.js          # Analysis rules
│   │   └── git.config.js               # Git settings
│   │
│   └── server.js                       # Express server entry
│
├── tests/
│   ├── unit/
│   │   ├── analyzers/
│   │   ├── scoring/
│   │   └── automation/
│   ├── integration/
│   │   ├── api/
│   │   └── workflows/
│   └── fixtures/
│       └── sample-repos/
│
├── temp/                               # Temporary clone directory
├── reports/                            # Generated reports
├── evidence/                           # Bob session evidence
│   ├── sessions/
│   ├── prompts/
│   └── commits/
│
├── .github/
│   └── workflows/
│       └── ci.yml                      # GitHub Actions
│
├── docs/
│   ├── API.md                          # API documentation
│   ├── SCORING.md                      # Scoring methodology
│   └── AUTOMATION.md                   # Git automation guide
│
├── package.json
├── .env.example
├── .gitignore
├── README.md
└── ARCHITECTURE.md                     # This file
```

### 3.2 Module Descriptions

#### 3.2.1 API Layer (`src/api/`)

**Purpose:** Handle HTTP requests, routing, and response formatting

**Key Components:**
- **Routes:** Define API endpoints and map to controllers
- **Middleware:** Request validation, error handling, CORS
- **Controllers:** Business logic orchestration

**Commit Unit:** `feat: implement REST API layer with Express routes`

---

#### 3.2.2 Core Analysis Engine (`src/core/`)

**Purpose:** Execute repository analysis and generate insights

**Key Components:**

1. **AnalysisOrchestrator.js**
   - Coordinates all analysis modules
   - Manages analysis workflow
   - Aggregates results

2. **SecurityAnalyzer.js**
   - Scans for hardcoded secrets (API keys, tokens, passwords)
   - Detects vulnerable dependencies
   - Identifies insecure file permissions
   - Checks for exposed sensitive files (.env, credentials)

3. **ReadmeValidator.js**
   - Validates README.md existence
   - Checks required sections (Installation, Usage, License)
   - Evaluates documentation quality
   - Verifies code examples and badges

4. **PromptVerifier.js**
   - Checks for `/prompts` directory
   - Validates prompt documentation structure
   - Verifies AI interaction evidence
   - Ensures prompt versioning

5. **ScoringEngine.js**
   - Calculates weighted scores
   - Applies scoring algorithm
   - Generates final readiness score

**Commit Units:**
- `feat: implement security analyzer with pattern detection`
- `feat: add README validator with completeness checks`
- `feat: create prompt verifier for AI documentation`
- `feat: build scoring engine with weighted algorithm`

---

#### 3.2.3 Git Automation Layer (`src/automation/`)

**Purpose:** Automate Git operations and GitHub integration

**Key Components:**

1. **CommitManager.js**
   - Orchestrates commit creation
   - Groups changes logically
   - Manages commit workflow

2. **CommitGrouper.js**
   - Analyzes file changes
   - Groups related changes
   - Creates logical commit boundaries

3. **MessageGenerator.js**
   - Generates conventional commit messages
   - Follows format: `type(scope): description`
   - Includes detailed body and footer

4. **GitHubPusher.js**
   - Authenticates with GitHub
   - Pushes commits automatically
   - Handles push failures

**Commit Unit:** `feat: implement Git automation with commit grouping`

---

#### 3.2.4 Bob Evidence Layer (`src/evidence/`)

**Purpose:** Track and document Bob AI interactions

**Key Components:**

1. **SessionLogger.js**
   - Logs Bob mode sessions (Plan/Code/Advanced/Ask/Orchestrator)
   - Captures timestamps and context
   - Exports session summaries

2. **PromptTracker.js**
   - Documents prompts used
   - Maps prompts to commits
   - Maintains prompt history

3. **CommitMapper.js**
   - Links commits to Bob sessions
   - Creates evidence trail
   - Generates commit-to-session mapping

**Commit Unit:** `feat: add Bob evidence tracking and documentation`

---

## 4. API CONTRACTS

### 4.1 Endpoint Specifications

#### POST `/api/analyze`

**Description:** Analyze a GitHub repository

**Request:**
```json
{
  "repoUrl": "https://github.com/username/repo",
  "branch": "main",
  "options": {
    "includeSecurityScan": true,
    "includeReadmeCheck": true,
    "includePromptVerification": true,
    "generateReport": true
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "analysisId": "uuid-v4",
  "timestamp": "2026-05-03T05:30:00Z",
  "repository": {
    "url": "https://github.com/username/repo",
    "branch": "main",
    "clonedAt": "2026-05-03T05:30:05Z"
  },
  "results": {
    "security": {
      "score": 85,
      "issues": [
        {
          "severity": "high",
          "type": "hardcoded_secret",
          "file": "config/database.js",
          "line": 12,
          "description": "Potential API key detected",
          "recommendation": "Move to environment variables"
        }
      ],
      "summary": "2 high, 3 medium, 5 low severity issues"
    },
    "readme": {
      "score": 90,
      "exists": true,
      "sections": {
        "installation": true,
        "usage": true,
        "license": true,
        "contributing": false,
        "tests": true
      },
      "quality": {
        "hasCodeExamples": true,
        "hasBadges": true,
        "hasTableOfContents": false
      },
      "recommendations": [
        "Add contributing guidelines",
        "Include table of contents"
      ]
    },
    "prompts": {
      "score": 75,
      "directoryExists": true,
      "promptCount": 8,
      "documented": true,
      "versioned": false,
      "recommendations": [
        "Add version tags to prompts",
        "Include prompt metadata"
      ]
    },
    "overallScore": 83,
    "readinessLevel": "Good",
    "submissionReady": true
  },
  "reportUrl": "/api/reports/uuid-v4"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REPO_URL",
    "message": "Invalid GitHub repository URL",
    "details": "URL must be in format: https://github.com/username/repo"
  }
}
```

---

#### GET `/api/reports/:analysisId`

**Description:** Download analysis report

**Query Parameters:**
- `format`: `json` | `markdown` (default: `json`)

**Response (200 OK - JSON):**
```json
{
  "analysisId": "uuid-v4",
  "generatedAt": "2026-05-03T05:30:00Z",
  "repository": "username/repo",
  "results": { /* full analysis results */ }
}
```

**Response (200 OK - Markdown):**
```markdown
# PolicyPilot Analysis Report

**Repository:** username/repo
**Analysis Date:** 2026-05-03
**Overall Score:** 83/100

## Security Analysis
...
```

---

#### GET `/api/health`

**Description:** Health check endpoint

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "timestamp": "2026-05-03T05:30:00Z"
}
```

---

### 4.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REPO_URL` | 400 | Invalid GitHub URL format |
| `CLONE_FAILED` | 500 | Failed to clone repository |
| `ANALYSIS_FAILED` | 500 | Analysis process failed |
| `REPORT_NOT_FOUND` | 404 | Analysis report not found |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 5. DATA FLOW

### 5.1 Analysis Pipeline

```
User Request
    │
    ▼
[1] API Gateway receives POST /api/analyze
    │
    ▼
[2] Validator checks request format
    │
    ▼
[3] GitCloner clones repository to temp/
    │
    ▼
[4] AnalysisOrchestrator initializes
    │
    ├──▶ [5a] SecurityAnalyzer scans files
    │   │     └──▶ Pattern matching
    │   │     └──▶ File permission checks
    │   │     └──▶ Dependency analysis
    │   │
    ├──▶ [5b] ReadmeValidator checks README
    │   │     └──▶ Section detection
    │   │     └──▶ Quality assessment
    │   │     └──▶ Completeness scoring
    │   │
    └──▶ [5c] PromptVerifier checks /prompts
          │     └──▶ Directory existence
          │     └──▶ File count
          │     └──▶ Documentation quality
          │
          ▼
[6] ScoringEngine calculates scores
    │   └──▶ Weighted aggregation
    │   └──▶ Readiness determination
    │
    ▼
[7] ReportGenerator creates outputs
    │   ├──▶ JSON report
    │   └──▶ Markdown report
    │
    ▼
[8] GitCleaner removes temp files
    │
    ▼
[9] Response sent to frontend
```

### 5.2 Git Automation Flow

```
Code Changes Generated
    │
    ▼
[1] CommitGrouper analyzes changes
    │   └──▶ Groups by module
    │   └──▶ Groups by feature
    │   └──▶ Groups by file type
    │
    ▼
[2] MessageGenerator creates messages
    │   └──▶ Conventional commit format
    │   └──▶ Detailed descriptions
    │   └──▶ Breaking change notes
    │
    ▼
[3] CommitManager stages changes
    │   └──▶ git add per group
    │   └──▶ git commit with message
    │
    ▼
[4] SessionLogger records evidence
    │   └──▶ Links commit to Bob session
    │   └──▶ Saves prompt history
    │
    ▼
[5] GitHubPusher pushes commits
    │   └──▶ Authenticates
    │   └──▶ git push origin branch
    │
    ▼
[6] Evidence exported to /evidence
```

---

## 6. SCORING SYSTEM

### 6.1 Scoring Algorithm

**Overall Score Formula:**
```
Overall Score = (Security × 0.40) + (README × 0.35) + (Prompts × 0.25)
```

### 6.2 Component Scoring

#### Security Score (0-100)

**Calculation:**
```javascript
securityScore = 100 - (
  (highSeverityIssues × 15) +
  (mediumSeverityIssues × 8) +
  (lowSeverityIssues × 3)
)
// Minimum score: 0
```

**Issue Severity Weights:**
- High: -15 points (hardcoded secrets, exposed credentials)
- Medium: -8 points (insecure permissions, vulnerable deps)
- Low: -3 points (missing security headers, weak configs)

---

#### README Score (0-100)

**Calculation:**
```javascript
readmeScore = (
  (existencePoints × 0.20) +      // 20 points
  (requiredSections × 0.40) +     // 40 points
  (qualityMetrics × 0.40)         // 40 points
)
```

**Required Sections (40 points total):**
- Installation: 10 points
- Usage: 10 points
- License: 10 points
- Contributing: 5 points
- Tests: 5 points

**Quality Metrics (40 points total):**
- Code examples: 15 points
- Badges: 10 points
- Table of contents: 10 points
- Screenshots/demos: 5 points

---

#### Prompt Documentation Score (0-100)

**Calculation:**
```javascript
promptScore = (
  (directoryExists × 0.30) +      // 30 points
  (promptCount × 0.30) +          // 30 points (1-5: 10, 6-10: 20, 11+: 30)
  (documentation × 0.25) +        // 25 points
  (versioning × 0.15)             // 15 points
)
```

**Scoring Breakdown:**
- `/prompts` directory exists: 30 points
- Prompt count: 0-30 points (scaled)
- Documentation quality: 25 points
- Version control: 15 points

---

### 6.3 Readiness Levels

| Score Range | Level | Submission Ready | Description |
|-------------|-------|------------------|-------------|
| 90-100 | Excellent | ✅ Yes | Production-ready, exemplary |
| 80-89 | Good | ✅ Yes | Minor improvements needed |
| 70-79 | Fair | ⚠️ Conditional | Moderate issues to address |
| 60-69 | Poor | ❌ No | Significant improvements needed |
| 0-59 | Critical | ❌ No | Major issues, not ready |

---

## 7. GIT AUTOMATION STRATEGY

### 7.1 Commit Grouping Strategy

**Principle:** Each commit should represent a single, logical unit of work that can be understood and reviewed independently.

#### Grouping Rules

1. **By Module:**
   - All files in `src/api/` → `feat: implement API layer`
   - All files in `src/core/analyzers/` → `feat: add security analyzer`

2. **By Feature:**
   - Related files across modules → `feat: add README validation`
   - Example: `ReadmeValidator.js` + `readme.config.js` + tests

3. **By Type:**
   - Configuration files → `chore: add project configuration`
   - Documentation → `docs: create API documentation`
   - Tests → `test: add unit tests for scoring engine`

4. **By Dependency:**
   - Changes that depend on each other → Single commit
   - Independent changes → Separate commits

#### Commit Sequence Example

```
1. chore: initialize Node.js project with dependencies
2. feat: implement Express server and API routes
3. feat: add Git cloner for repository downloads
4. feat: implement security analyzer with pattern detection
5. feat: add README validator with completeness checks
6. feat: create prompt verifier for AI documentation
7. feat: build scoring engine with weighted algorithm
8. feat: implement JSON and Markdown report generators
9. feat: add Git automation with commit grouping
10. feat: implement Bob evidence tracking system
11. test: add comprehensive unit tests
12. docs: create API and architecture documentation
13. chore: configure GitHub Actions CI/CD
```

---

### 7.2 Commit Message Format

**Convention:** Conventional Commits (https://www.conventionalcommits.org/)

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(analyzer): implement security pattern detection

- Add regex patterns for API keys, tokens, passwords
- Scan all JavaScript, Python, and config files
- Generate severity-based issue reports
- Include file path and line number in findings

Closes #12
```

---

### 7.3 Automated Commit Workflow

#### Implementation in CommitManager.js

```javascript
class CommitManager {
  async autoCommit(changes, bobSession) {
    // 1. Group changes logically
    const groups = await this.grouper.groupChanges(changes);
    
    // 2. For each group
    for (const group of groups) {
      // 3. Generate commit message
      const message = await this.messageGenerator.generate(
        group.type,
        group.scope,
        group.files,
        bobSession
      );
      
      // 4. Stage files
      await this.git.add(group.files);
      
      // 5. Commit with message
      await this.git.commit(message);
      
      // 6. Log evidence
      await this.evidenceLogger.logCommit({
        commitHash: await this.git.revparse(['HEAD']),
        message: message,
        files: group.files,
        bobSession: bobSession.id,
        timestamp: new Date()
      });
    }
    
    // 7. Push to GitHub
    await this.pusher.push();
  }
}
```

---

### 7.4 GitHub Push Automation

#### Authentication Methods

1. **Personal Access Token (PAT):**
   ```bash
   git remote set-url origin https://<TOKEN>@github.com/user/repo.git
   git push origin main
   ```

2. **SSH Key:**
   ```bash
   git remote set-url origin git@github.com:user/repo.git
   git push origin main
   ```

#### GitHubPusher.js Implementation

```javascript
class GitHubPusher {
  async push(branch = 'main') {
    try {
      // 1. Verify authentication
      await this.verifyAuth();
      
      // 2. Push commits
      await this.git.push('origin', branch);
      
      // 3. Log success
      this.logger.info(`Pushed to ${branch} successfully`);
      
      return { success: true, branch };
    } catch (error) {
      // 4. Handle failures
      this.logger.error('Push failed:', error);
      throw new Error(`GitHub push failed: ${error.message}`);
    }
  }
}
```

---

### 7.5 GitHub Actions Integration

#### Workflow File: `.github/workflows/ci.yml`

```yaml
name: PolicyPilot CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run linter
      run: npm run lint
      
    - name: Run tests
      run: npm test
      
    - name: Run integration tests
      run: npm run test:integration
      
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build application
      run: npm run build
      
    - name: Archive artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/
```

---

## 8. BOB EVIDENCE STRATEGY

### 8.1 Evidence Documentation Structure

```
evidence/
├── sessions/
│   ├── 2026-05-03_plan_session_001.md
│   ├── 2026-05-03_code_session_001.md
│   ├── 2026-05-03_advanced_session_001.md
│   └── session_index.json
│
├── prompts/
│   ├── 001_initial_architecture.md
│   ├── 002_api_implementation.md
│   ├── 003_security_analyzer.md
│   └── prompt_index.json
│
└── commits/
    ├── commit_to_session_map.json
    └── evidence_summary.md
```

---

### 8.2 Session Documentation Format

#### File: `sessions/2026-05-03_plan_session_001.md`

```markdown
# Bob Session Evidence

**Session ID:** plan_001
**Mode:** Plan
**Date:** 2026-05-03
**Duration:** 45 minutes
**Objective:** Design PolicyPilot system architecture

## Context
User requested a comprehensive architecture plan for PolicyPilot, a repository compliance analyzer with GitHub automation.

## Key Decisions
1. Selected Node.js + Express for backend
2. Designed modular analyzer architecture
3. Created weighted scoring algorithm
4. Planned Git automation strategy

## Outputs Generated
- ARCHITECTURE.md (this document)
- System design diagrams
- API contract specifications
- Scoring methodology

## Related Commits
- `chore: initialize project structure`
- `docs: create architecture documentation`

## Prompts Used
- 001_initial_architecture.md
- 002_clarifying_questions.md

## Next Steps
- Switch to Code mode for implementation
- Begin with API layer development
```

---

### 8.3 Prompt Documentation Format

#### File: `prompts/001_initial_architecture.md`

```markdown
# Prompt: Initial Architecture Design

**Prompt ID:** 001
**Date:** 2026-05-03
**Mode:** Plan
**Session:** plan_001

## User Prompt
```
You are the principal architect for a hackathon project called PolicyPilot.

[Full prompt text...]
```

## Bob's Response Summary
Created comprehensive system architecture including:
- High-level architecture diagram
- Module structure
- API contracts
- Scoring system
- Git automation strategy

## Artifacts Generated
- ARCHITECTURE.md
- Module specifications
- API documentation

## Commit Mapping
- Commit: `docs: create architecture documentation`
- Hash: `abc123...`
```

---

### 8.4 Commit-to-Session Mapping

#### File: `commits/commit_to_session_map.json`

```json
{
  "commits": [
    {
      "hash": "abc123def456",
      "message": "feat: implement Express server and API routes",
      "timestamp": "2026-05-03T06:00:00Z",
      "session": {
        "id": "code_001",
        "mode": "Code",
        "date": "2026-05-03"
      },
      "prompts": ["002_api_implementation.md"],
      "files": [
        "src/server.js",
        "src/api/routes/analyze.routes.js",
        "src/api/controllers/analyzeController.js"
      ],
      "evidence": "evidence/sessions/2026-05-03_code_session_001.md"
    }
  ]
}
```

---

### 8.5 Evidence Export Automation

#### SessionLogger.js Implementation

```javascript
class SessionLogger {
  async logSession(session) {
    const sessionDoc = {
      id: session.id,
      mode: session.mode,
      timestamp: new Date(),
      objective: session.objective,
      decisions: session.decisions,
      outputs: session.outputs,
      commits: session.commits,
      prompts: session.prompts
    };
    
    // 1. Save session markdown
    await this.saveSessionMarkdown(sessionDoc);
    
    // 2. Update session index
    await this.updateSessionIndex(sessionDoc);
    
    // 3. Link to commits
    await this.linkCommits(sessionDoc);
    
    return sessionDoc;
  }
}
```

---

### 8.6 Mode-Specific Evidence

#### Plan Mode Evidence
- Architecture decisions
- Design diagrams
- System specifications
- Technology choices

#### Code Mode Evidence
- Implementation details
- Code structure decisions
- Module dependencies
- Refactoring rationale

#### Advanced Mode Evidence
- Complex problem-solving
- Integration challenges
- Performance optimizations
- Advanced patterns used

#### Ask Mode Evidence
- Questions asked
- Explanations provided
- Recommendations given
- Learning outcomes

#### Orchestrator Mode Evidence
- Task breakdown
- Subtask delegation
- Workflow coordination
- Integration points

---

## 9. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Commits 1-3)
**Duration:** 2-3 hours

1. **Project Initialization**
   - Commit: `chore: initialize Node.js project with dependencies`
   - Files: `package.json`, `.gitignore`, `.env.example`
   - Evidence: Setup session documentation

2. **Express Server Setup**
   - Commit: `feat: implement Express server and API routes`
   - Files: `src/server.js`, `src/api/routes/`, `src/api/middleware/`
   - Evidence: API design decisions

3. **Git Operations**
   - Commit: `feat: add Git cloner for repository downloads`
   - Files: `src/core/git/GitCloner.js`, `src/core/git/GitCleaner.js`
   - Evidence: Git integration approach

---

### Phase 2: Core Analysis (Commits 4-7)
**Duration:** 4-5 hours

4. **Security Analyzer**
   - Commit: `feat: implement security analyzer with pattern detection`
   - Files: `src/core/analyzers/SecurityAnalyzer.js`, `src/config/analysis.config.js`
   - Evidence: Security patterns and detection logic

5. **README Validator**
   - Commit: `feat: add README validator with completeness checks`
   - Files: `src/core/analyzers/ReadmeValidator.js`
   - Evidence: Validation criteria decisions

6. **Prompt Verifier**
   - Commit: `feat: create prompt verifier for AI documentation`
   - Files: `src/core/analyzers/PromptVerifier.js`
   - Evidence: Prompt documentation standards

7. **Scoring Engine**
   - Commit: `feat: build scoring engine with weighted algorithm`
   - Files: `src/core/scoring/ScoringEngine.js`, `src/core/scoring/weights.config.js`
   - Evidence: Scoring methodology rationale

---

### Phase 3: Reporting (Commits 8-9)
**Duration:** 2-3 hours

8. **Report Generators**
   - Commit: `feat: implement JSON and Markdown report generators`
   - Files: `src/core/reports/JsonReportGenerator.js`, `src/core/reports/MarkdownReportGenerator.js`
   - Evidence: Report format decisions

9. **Analysis Orchestrator**
   - Commit: `feat: add analysis orchestrator for workflow coordination`
   - Files: `src/core/orchestrator/AnalysisOrchestrator.js`
   - Evidence: Workflow design

---

### Phase 4: Automation (Commits 10-11)
**Duration:** 3-4 hours

10. **Git Automation**
    - Commit: `feat: implement Git automation with commit grouping`
    - Files: `src/automation/commits/`, `src/automation/github/`
    - Evidence: Automation strategy and implementation

11. **Bob Evidence System**
    - Commit: `feat: implement Bob evidence tracking system`
    - Files: `src/evidence/`
    - Evidence: Evidence tracking methodology

---

### Phase 5: Testing & Documentation (Commits 12-14)
**Duration:** 3-4 hours

12. **Unit Tests**
    - Commit: `test: add comprehensive unit tests`
    - Files: `tests/unit/`
    - Evidence: Testing strategy

13. **Documentation**
    - Commit: `docs: create API and architecture documentation`
    - Files: `docs/API.md`, `docs/SCORING.md`, `docs/AUTOMATION.md`
    - Evidence: Documentation approach

14. **CI/CD Setup**
    - Commit: `chore: configure GitHub Actions CI/CD`
    - Files: `.github/workflows/ci.yml`
    - Evidence: CI/CD pipeline design

---

### Total Estimated Time: 14-19 hours

---

## 10. DEPLOYMENT & OPERATIONS

### 10.1 Local Development

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with GitHub token

# Start development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint
```

### 10.2 Production Deployment

```bash
# Build for production
npm run build

# Start with PM2
pm2 start src/server.js --name policypilot

# Monitor
pm2 monit

# View logs
pm2 logs policypilot
```

### 10.3 Environment Variables

```bash
# .env
NODE_ENV=production
PORT=3000
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
TEMP_DIR=./temp
REPORTS_DIR=./reports
EVIDENCE_DIR=./evidence
LOG_LEVEL=info
```

---

## 11. SECURITY CONSIDERATIONS

### 11.1 GitHub Token Security
- Store token in environment variables only
- Never commit token to repository
- Use read-only token when possible
- Rotate tokens regularly

### 11.2 Repository Cloning
- Clone to temporary directory
- Clean up after analysis
- Limit clone depth to reduce disk usage
- Timeout long-running clones

### 11.3 Input Validation
- Validate GitHub URLs
- Sanitize file paths
- Limit repository size
- Prevent path traversal attacks

---

## 12. PERFORMANCE OPTIMIZATION

### 12.1 Analysis Performance
- Parallel analyzer execution
- Stream large files instead of loading into memory
- Cache analysis results
- Implement timeout mechanisms

### 12.2 Git Operations
- Shallow clones (depth=1)
- Sparse checkout for large repos
- Cleanup temp files immediately
- Limit concurrent clone operations

---

## 13. MONITORING & LOGGING

### 13.1 Logging Strategy

```javascript
// logger.js
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});
```

### 13.2 Metrics to Track
- Analysis duration
- Repository clone time
- API response times
- Error rates
- Commit success rates

---

## 14. FUTURE ENHANCEMENTS

### 14.1 Phase 2 Features
- Support for private repositories
- Webhook integration for automatic analysis
- Historical trend tracking
- Custom rule configuration
- Multi-language support

### 14.2 Advanced Features
- Machine learning for pattern detection
- Integration with CI/CD pipelines
- Slack/Discord notifications
- Team collaboration features
- Custom report templates

---

## 15. CONCLUSION

PolicyPilot is designed as a comprehensive, locally-running repository compliance analyzer with full GitHub automation. The architecture prioritizes:

✅ **Modularity:** Clear separation of concerns  
✅ **Automation:** Fully automated Git workflow  
✅ **Evidence:** Complete Bob session tracking  
✅ **Scalability:** Easy to extend with new analyzers  
✅ **Maintainability:** Well-documented and tested  

The system is ready for implementation following the commit-by-commit roadmap, with each commit representing a logical, reviewable unit of work.

---

**Next Steps:**
1. Review and approve this architecture plan
2. Switch to Code mode for implementation
3. Begin Phase 1: Foundation setup
4. Follow commit roadmap sequentially

---

*Document Version: 1.0*  
*Last Updated: 2026-05-03*  
*Author: Bob (Plan Mode)*