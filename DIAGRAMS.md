# PolicyPilot - Architecture Diagrams

This document contains Mermaid diagrams visualizing the PolicyPilot system architecture.

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend Layer"]
        UI[Streamlit/Google Stitch UI]
    end
    
    subgraph API["API Gateway Layer"]
        Routes[Express Routes]
        Middleware[Middleware]
        Controllers[Controllers]
    end
    
    subgraph Core["Core Analysis Engine"]
        Orchestrator[Analysis Orchestrator]
        Security[Security Analyzer]
        Readme[README Validator]
        Prompt[Prompt Verifier]
        Scoring[Scoring Engine]
        Reports[Report Generator]
        Git[Git Cloner]
    end
    
    subgraph Automation["Git Automation Layer"]
        CommitMgr[Commit Manager]
        CommitGrp[Commit Grouper]
        MsgGen[Message Generator]
        Pusher[GitHub Pusher]
    end
    
    subgraph Evidence["Bob Evidence Layer"]
        SessionLog[Session Logger]
        PromptTrack[Prompt Tracker]
        CommitMap[Commit Mapper]
    end
    
    UI -->|HTTP/REST| Routes
    Routes --> Middleware
    Middleware --> Controllers
    Controllers --> Orchestrator
    
    Orchestrator --> Git
    Git --> Security
    Git --> Readme
    Git --> Prompt
    
    Security --> Scoring
    Readme --> Scoring
    Prompt --> Scoring
    
    Scoring --> Reports
    Reports --> Controllers
    
    Orchestrator --> CommitMgr
    CommitMgr --> CommitGrp
    CommitMgr --> MsgGen
    CommitMgr --> Pusher
    
    CommitMgr --> SessionLog
    SessionLog --> PromptTrack
    SessionLog --> CommitMap
    
    style Frontend fill:#e1f5ff
    style API fill:#fff4e1
    style Core fill:#e8f5e9
    style Automation fill:#f3e5f5
    style Evidence fill:#fff9c4
```

---

## 2. Analysis Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant Orch as Orchestrator
    participant Git as Git Cloner
    participant Sec as Security Analyzer
    participant Read as README Validator
    participant Prom as Prompt Verifier
    participant Score as Scoring Engine
    participant Rep as Report Generator
    
    User->>API: POST /api/analyze
    API->>API: Validate Request
    API->>Orch: Initialize Analysis
    Orch->>Git: Clone Repository
    Git-->>Orch: Repository Ready
    
    par Parallel Analysis
        Orch->>Sec: Scan Security
        Orch->>Read: Validate README
        Orch->>Prom: Verify Prompts
    end
    
    Sec-->>Orch: Security Results
    Read-->>Orch: README Results
    Prom-->>Orch: Prompt Results
    
    Orch->>Score: Calculate Scores
    Score-->>Orch: Final Score
    
    Orch->>Rep: Generate Reports
    Rep-->>Orch: JSON + Markdown
    
    Orch->>Git: Cleanup Temp Files
    Orch-->>API: Analysis Complete
    API-->>User: Return Results
```

---

## 3. Git Automation Workflow

```mermaid
flowchart TD
    Start[Code Changes Generated] --> Analyze[Commit Grouper Analyzes Changes]
    
    Analyze --> Group1{Group by Module?}
    Group1 -->|Yes| ModuleGroup[Group API files together]
    Group1 -->|No| Group2{Group by Feature?}
    
    Group2 -->|Yes| FeatureGroup[Group related feature files]
    Group2 -->|No| Group3{Group by Type?}
    
    Group3 -->|Yes| TypeGroup[Group docs, tests, config]
    Group3 -->|No| SingleGroup[Single commit group]
    
    ModuleGroup --> GenMsg[Message Generator Creates Commit Message]
    FeatureGroup --> GenMsg
    TypeGroup --> GenMsg
    SingleGroup --> GenMsg
    
    GenMsg --> Stage[Stage Files with git add]
    Stage --> Commit[Create Commit with Message]
    Commit --> Evidence[Session Logger Records Evidence]
    
    Evidence --> MoreGroups{More Groups?}
    MoreGroups -->|Yes| Analyze
    MoreGroups -->|No| Push[GitHub Pusher Pushes Commits]
    
    Push --> Export[Export Evidence to /evidence]
    Export --> End[Complete]
    
    style Start fill:#e1f5ff
    style GenMsg fill:#fff4e1
    style Commit fill:#e8f5e9
    style Evidence fill:#fff9c4
    style Push fill:#f3e5f5
    style End fill:#c8e6c9
```

---

## 4. Module Dependency Graph

```mermaid
graph LR
    subgraph API Layer
        Server[server.js]
        Routes[Routes]
        Controllers[Controllers]
        Middleware[Middleware]
    end
    
    subgraph Core Layer
        Orch[Orchestrator]
        SecAn[Security Analyzer]
        ReadVal[README Validator]
        PromVer[Prompt Verifier]
        ScoreEng[Scoring Engine]
        RepGen[Report Generator]
        GitOps[Git Operations]
    end
    
    subgraph Automation Layer
        CommitMgr[Commit Manager]
        CommitGrp[Commit Grouper]
        MsgGen[Message Generator]
        GitPush[GitHub Pusher]
    end
    
    subgraph Evidence Layer
        SessLog[Session Logger]
        PromTrack[Prompt Tracker]
        CommMap[Commit Mapper]
    end
    
    subgraph Utils
        FileUtil[File Utils]
        Logger[Logger]
        Config[Config]
    end
    
    Server --> Routes
    Routes --> Controllers
    Controllers --> Middleware
    Controllers --> Orch
    
    Orch --> GitOps
    Orch --> SecAn
    Orch --> ReadVal
    Orch --> PromVer
    Orch --> ScoreEng
    Orch --> RepGen
    
    SecAn --> Config
    ReadVal --> Config
    PromVer --> Config
    ScoreEng --> Config
    
    Orch --> CommitMgr
    CommitMgr --> CommitGrp
    CommitMgr --> MsgGen
    CommitMgr --> GitPush
    CommitMgr --> SessLog
    
    SessLog --> PromTrack
    SessLog --> CommMap
    
    GitOps --> FileUtil
    GitOps --> Logger
    RepGen --> FileUtil
    CommitMgr --> Logger
    
    style API Layer fill:#e1f5ff
    style Core Layer fill:#e8f5e9
    style Automation Layer fill:#f3e5f5
    style Evidence Layer fill:#fff9c4
    style Utils fill:#fff4e1
```

---

## 5. Data Flow Diagram

```mermaid
flowchart TB
    Input[GitHub Repository URL] --> Validate{Valid URL?}
    Validate -->|No| Error[Return Error]
    Validate -->|Yes| Clone[Clone to temp/]
    
    Clone --> Parse[Parse Repository Structure]
    Parse --> Analyze[Run Analyzers]
    
    subgraph Analysis
        Analyze --> SecScan[Security Scan]
        Analyze --> ReadCheck[README Check]
        Analyze --> PromCheck[Prompt Check]
        
        SecScan --> SecData[Security Data]
        ReadCheck --> ReadData[README Data]
        PromCheck --> PromData[Prompt Data]
    end
    
    SecData --> Aggregate[Aggregate Results]
    ReadData --> Aggregate
    PromData --> Aggregate
    
    Aggregate --> Calculate[Calculate Scores]
    Calculate --> Generate[Generate Reports]
    
    Generate --> JSON[JSON Report]
    Generate --> MD[Markdown Report]
    
    JSON --> Store[Store in reports/]
    MD --> Store
    
    Store --> Cleanup[Cleanup temp/]
    Cleanup --> Response[Return Response]
    
    Response --> Frontend[Frontend Display]
    
    style Input fill:#e1f5ff
    style Analysis fill:#e8f5e9
    style Generate fill:#fff4e1
    style Response fill:#c8e6c9
```

---

## 6. Scoring Algorithm Flow

```mermaid
flowchart TD
    Start[Start Scoring] --> GetSec[Get Security Results]
    GetSec --> CalcSec[Calculate Security Score]
    
    CalcSec --> Formula1["Score = 100 - penalties"]
    Formula1 --> Penalty1["High: -15 points each"]
    Formula1 --> Penalty2["Medium: -8 points each"]
    Formula1 --> Penalty3["Low: -3 points each"]
    
    Penalty1 --> SecScore[Security Score 0-100]
    Penalty2 --> SecScore
    Penalty3 --> SecScore
    
    Start --> GetRead[Get README Results]
    GetRead --> CalcRead[Calculate README Score]
    
    CalcRead --> Exist["Existence: 20 points"]
    CalcRead --> Sections["Required Sections: 40 points"]
    CalcRead --> Quality["Quality Metrics: 40 points"]
    
    Exist --> ReadScore[README Score 0-100]
    Sections --> ReadScore
    Quality --> ReadScore
    
    Start --> GetProm[Get Prompt Results]
    GetProm --> CalcProm[Calculate Prompt Score]
    
    CalcProm --> Dir["Directory Exists: 30 points"]
    CalcProm --> Count["Prompt Count: 30 points"]
    CalcProm --> Doc["Documentation: 25 points"]
    CalcProm --> Ver["Versioning: 15 points"]
    
    Dir --> PromScore[Prompt Score 0-100]
    Count --> PromScore
    Doc --> PromScore
    Ver --> PromScore
    
    SecScore --> Weight["Apply Weights"]
    ReadScore --> Weight
    PromScore --> Weight
    
    Weight --> Final["Overall = Security×0.40 + README×0.35 + Prompts×0.25"]
    Final --> Level{Determine Level}
    
    Level -->|90-100| Excellent[Excellent]
    Level -->|80-89| Good[Good]
    Level -->|70-79| Fair[Fair]
    Level -->|60-69| Poor[Poor]
    Level -->|0-59| Critical[Critical]
    
    Excellent --> Ready[Submission Ready: Yes]
    Good --> Ready
    Fair --> Conditional[Submission Ready: Conditional]
    Poor --> NotReady[Submission Ready: No]
    Critical --> NotReady
    
    Ready --> End[Return Final Score]
    Conditional --> End
    NotReady --> End
    
    style Start fill:#e1f5ff
    style SecScore fill:#ffcdd2
    style ReadScore fill:#c8e6c9
    style PromScore fill:#fff9c4
    style Final fill:#e1bee7
    style End fill:#b2dfdb
```

---

## 7. Commit Grouping Strategy

```mermaid
flowchart TD
    Changes[Code Changes Detected] --> Analyze[Analyze File Changes]
    
    Analyze --> CheckModule{Same Module?}
    CheckModule -->|Yes| ModuleCommit[Create Module Commit]
    CheckModule -->|No| CheckFeature{Related Feature?}
    
    CheckFeature -->|Yes| FeatureCommit[Create Feature Commit]
    CheckFeature -->|No| CheckType{Same Type?}
    
    CheckType -->|Yes| TypeCommit[Create Type Commit]
    CheckType -->|No| CheckDep{Dependencies?}
    
    CheckDep -->|Yes| DepCommit[Create Dependency Commit]
    CheckDep -->|No| IndCommit[Create Individual Commits]
    
    ModuleCommit --> GenMsg[Generate Commit Message]
    FeatureCommit --> GenMsg
    TypeCommit --> GenMsg
    DepCommit --> GenMsg
    IndCommit --> GenMsg
    
    GenMsg --> Format["Format: type scope: subject"]
    Format --> Examples
    
    subgraph Examples
        Ex1["feat api: implement REST endpoints"]
        Ex2["feat analyzer: add security scanner"]
        Ex3["docs: create API documentation"]
        Ex4["test: add unit tests"]
        Ex5["chore: configure CI/CD"]
    end
    
    Examples --> Stage[Stage Files]
    Stage --> Commit[Create Commit]
    Commit --> Log[Log Evidence]
    Log --> Push[Push to GitHub]
    
    style Changes fill:#e1f5ff
    style GenMsg fill:#fff4e1
    style Commit fill:#e8f5e9
    style Log fill:#fff9c4
    style Push fill:#f3e5f5
```

---

## 8. Bob Evidence Tracking System

```mermaid
flowchart TB
    Session[Bob Session Starts] --> Mode{Which Mode?}
    
    Mode -->|Plan| PlanMode[Plan Mode Session]
    Mode -->|Code| CodeMode[Code Mode Session]
    Mode -->|Advanced| AdvMode[Advanced Mode Session]
    Mode -->|Ask| AskMode[Ask Mode Session]
    Mode -->|Orchestrator| OrchMode[Orchestrator Mode Session]
    
    PlanMode --> LogSession[Session Logger Captures]
    CodeMode --> LogSession
    AdvMode --> LogSession
    AskMode --> LogSession
    OrchMode --> LogSession
    
    LogSession --> Capture1[Capture Objective]
    LogSession --> Capture2[Capture Decisions]
    LogSession --> Capture3[Capture Outputs]
    LogSession --> Capture4[Capture Prompts]
    
    Capture1 --> SaveMD[Save Session Markdown]
    Capture2 --> SaveMD
    Capture3 --> SaveMD
    Capture4 --> SaveMD
    
    SaveMD --> UpdateIndex[Update Session Index]
    UpdateIndex --> LinkCommits[Link to Commits]
    
    LinkCommits --> CommitMap[Create Commit Mapping]
    CommitMap --> PromptDoc[Document Prompts]
    
    PromptDoc --> Export[Export Evidence]
    
    Export --> SessionFile["sessions/YYYY-MM-DD_mode_NNN.md"]
    Export --> PromptFile["prompts/NNN_description.md"]
    Export --> MapFile["commits/commit_to_session_map.json"]
    
    SessionFile --> Evidence[Evidence Directory]
    PromptFile --> Evidence
    MapFile --> Evidence
    
    Evidence --> Review[Ready for Review]
    
    style Session fill:#e1f5ff
    style LogSession fill:#fff4e1
    style SaveMD fill:#e8f5e9
    style Export fill:#f3e5f5
    style Evidence fill:#fff9c4
    style Review fill:#c8e6c9
```

---

## 9. API Request/Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Express API
    participant Val as Validator
    participant Ctrl as Controller
    participant Orch as Orchestrator
    participant Ana as Analyzers
    participant Score as Scoring
    participant Rep as Reports
    
    Client->>API: POST /api/analyze
    Note over Client,API: Request Body: repoUrl, branch, options
    
    API->>Val: Validate Request
    
    alt Invalid Request
        Val-->>API: Validation Error
        API-->>Client: 400 Bad Request
    else Valid Request
        Val-->>API: Valid
        API->>Ctrl: Process Request
        
        Ctrl->>Orch: Start Analysis
        Orch->>Orch: Clone Repository
        
        Orch->>Ana: Run Security Scan
        Ana-->>Orch: Security Results
        
        Orch->>Ana: Run README Check
        Ana-->>Orch: README Results
        
        Orch->>Ana: Run Prompt Check
        Ana-->>Orch: Prompt Results
        
        Orch->>Score: Calculate Scores
        Score-->>Orch: Final Scores
        
        Orch->>Rep: Generate Reports
        Rep-->>Orch: JSON + Markdown
        
        Orch-->>Ctrl: Analysis Complete
        Ctrl-->>API: Format Response
        API-->>Client: 200 OK + Results
    end
    
    Note over Client,API: Response: scores, issues, recommendations
```

---

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph Development
        DevEnv[Local Development]
        DevTest[Unit Tests]
        DevLint[ESLint]
    end
    
    subgraph Version Control
        Git[Git Repository]
        GitHub[GitHub Remote]
    end
    
    subgraph CI/CD
        Actions[GitHub Actions]
        TestJob[Test Job]
        BuildJob[Build Job]
    end
    
    subgraph Production
        Server[Node.js Server]
        PM2[PM2 Process Manager]
        Logs[Log Files]
    end
    
    subgraph External
        Frontend[Streamlit/Stitch UI]
        GitHubAPI[GitHub API]
    end
    
    DevEnv --> DevTest
    DevEnv --> DevLint
    DevTest --> Git
    DevLint --> Git
    
    Git --> GitHub
    GitHub --> Actions
    
    Actions --> TestJob
    TestJob --> BuildJob
    BuildJob --> Server
    
    Server --> PM2
    PM2 --> Logs
    
    Frontend --> Server
    Server --> GitHubAPI
    
    style Development fill:#e1f5ff
    style Version Control fill:#fff4e1
    style CI/CD fill:#e8f5e9
    style Production fill:#f3e5f5
    style External fill:#fff9c4
```

---

## 11. Security Analysis Process

```mermaid
flowchart TD
    Start[Start Security Scan] --> LoadPatterns[Load Detection Patterns]
    
    LoadPatterns --> Patterns
    subgraph Patterns
        P1[API Key Patterns]
        P2[Token Patterns]
        P3[Password Patterns]
        P4[Secret Patterns]
    end
    
    Patterns --> ScanFiles[Scan All Files]
    
    ScanFiles --> CheckJS[Check JavaScript Files]
    ScanFiles --> CheckPY[Check Python Files]
    ScanFiles --> CheckConfig[Check Config Files]
    ScanFiles --> CheckEnv[Check .env Files]
    
    CheckJS --> Match{Pattern Match?}
    CheckPY --> Match
    CheckConfig --> Match
    CheckEnv --> Match
    
    Match -->|Yes| Severity{Determine Severity}
    Match -->|No| Continue[Continue Scanning]
    
    Severity -->|Hardcoded Secret| High[High Severity]
    Severity -->|Exposed Credential| High
    Severity -->|Weak Config| Medium[Medium Severity]
    Severity -->|Missing Header| Low[Low Severity]
    
    High --> Record[Record Issue]
    Medium --> Record
    Low --> Record
    
    Record --> Location[Capture File + Line]
    Location --> Recommend[Generate Recommendation]
    
    Recommend --> MoreFiles{More Files?}
    MoreFiles -->|Yes| Continue
    MoreFiles -->|No| Calculate[Calculate Security Score]
    
    Calculate --> Deduct["Score = 100 - penalties"]
    Deduct --> Final[Return Security Results]
    
    Continue --> ScanFiles
    
    style Start fill:#e1f5ff
    style Patterns fill:#fff4e1
    style High fill:#ffcdd2
    style Medium fill:#fff9c4
    style Low fill:#c8e6c9
    style Final fill:#b2dfdb
```

---

## 12. Implementation Phases Timeline

```mermaid
gantt
    title PolicyPilot Implementation Roadmap
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Phase 1: Foundation
    Project Init           :p1, 00:00, 1h
    Express Setup          :p2, after p1, 1h
    Git Operations         :p3, after p2, 1h
    
    section Phase 2: Core Analysis
    Security Analyzer      :p4, after p3, 1.5h
    README Validator       :p5, after p4, 1h
    Prompt Verifier        :p6, after p5, 1h
    Scoring Engine         :p7, after p6, 1.5h
    
    section Phase 3: Reporting
    Report Generators      :p8, after p7, 1.5h
    Analysis Orchestrator  :p9, after p8, 1.5h
    
    section Phase 4: Automation
    Git Automation         :p10, after p9, 2h
    Bob Evidence System    :p11, after p10, 2h
    
    section Phase 5: Testing & Docs
    Unit Tests             :p12, after p11, 2h
    Documentation          :p13, after p12, 1.5h
    CI/CD Setup            :p14, after p13, 1h
```

---

*These diagrams provide visual representations of the PolicyPilot architecture, workflows, and implementation strategy.*

*Document Version: 1.0*  
*Last Updated: 2026-05-03*  
*Author: Bob (Plan Mode)*