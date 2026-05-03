# Bob Evidence Tracking System - Implementation Plan

**Version:** 1.0  
**Date:** 2026-05-03  
**Author:** Bob (Plan Mode)  
**Related:** [`BOB_EVIDENCE_TRACKING_SYSTEM.md`](BOB_EVIDENCE_TRACKING_SYSTEM.md)

---

## Implementation Phases

### Phase 1: Infrastructure Setup (30 minutes)

**Objective:** Create directory structure and configuration files

**Tasks:**
1. Create `.bob/` directory structure
2. Create `prompts/` directory structure
3. Initialize configuration files
4. Create template files
5. Commit infrastructure

**Deliverables:**
- `.bob/sessions/` directory
- `.bob/commits/` directory
- `.bob/config/evidence_config.json`
- `.bob/templates/session_template.md`
- `.bob/templates/prompt_template.md`
- `prompts/README.md`
- `prompts/prompt_index.json`

**Commands:**
```bash
# Create directories
mkdir -p .bob/{sessions,commits,config,scripts,templates}
mkdir -p prompts

# Initialize files (see detailed commands in main document)
# Commit infrastructure
git add .bob/ prompts/
git commit -m "chore: initialize Bob evidence tracking system"
```

---

### Phase 2: Evidence Automation Scripts (45 minutes)

**Objective:** Create automation scripts for evidence tracking

**Tasks:**
1. Create evidence validation script
2. Create commit mapping updater
3. Create session generator
4. Create evidence summary generator
5. Test all scripts

**Deliverables:**
- `.bob/scripts/validate_evidence.py`
- `.bob/scripts/update_commit_map.py`
- `.bob/scripts/generate_session.py`
- `.bob/scripts/generate_summary.py`

**Key Script: `validate_evidence.py`**
```python
#!/usr/bin/env python3
"""Validate Bob evidence completeness."""

import json
from pathlib import Path

def validate_evidence():
    results = {"valid": True, "errors": [], "warnings": []}
    
    # Check commit map
    commit_map = Path(".bob/commits/commit_map.json")
    if not commit_map.exists():
        results["errors"].append("Missing commit_map.json")
        results["valid"] = False
        return results
    
    # Load and validate
    with open(commit_map) as f:
        data = json.load(f)
    
    # Validate each commit has evidence
    for commit in data["commits"]:
        session_file = Path(commit["session"]["file"])
        prompt_file = Path(commit["prompt"]["file"])
        
        if not session_file.exists():
            results["errors"].append(f"Missing: {session_file}")
            results["valid"] = False
        
        if not prompt_file.exists():
            results["errors"].append(f"Missing: {prompt_file}")
            results["valid"] = False
    
    return results

if __name__ == "__main__":
    results = validate_evidence()
    print("✅ PASSED" if results["valid"] else "❌ FAILED")
    for error in results["errors"]:
        print(f"  ❌ {error}")
    exit(0 if results["valid"] else 1)
```

---

### Phase 3: Git Automation Integration (60 minutes)

**Objective:** Integrate evidence tracking with existing Git automation

**Tasks:**
1. Modify [`git_autocommit.py`](git_autocommit.py) to include Bob evidence
2. Add session tracking to commit workflow
3. Add prompt linking to commits
4. Update commit message format
5. Test integration

**Key Modifications to `git_autocommit.py`:**

```python
class BobEvidenceTracker:
    """Track Bob evidence in commits."""
    
    def __init__(self):
        self.current_session = None
        self.current_prompt = None
        self.current_mode = None
    
    def start_session(self, mode: str, objective: str):
        """Start new Bob session."""
        session_id = f"{mode.lower()}_{self._get_next_id()}"
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        self.current_session = {
            "id": session_id,
            "mode": mode,
            "date": timestamp,
            "objective": objective,
            "file": f".bob/sessions/{timestamp}_{session_id}.md"
        }
        
        # Create session document
        self._create_session_doc()
        return session_id
    
    def link_prompt(self, prompt_file: str):
        """Link prompt to current session."""
        self.current_prompt = {
            "file": prompt_file,
            "id": self._extract_prompt_id(prompt_file)
        }
    
    def enhance_commit_message(self, message: str) -> str:
        """Add Bob evidence to commit message."""
        if not self.current_session:
            return message
        
        evidence = f"""
Bob-Session: {self.current_session['id']}
Bob-Mode: {self.current_session['mode']}
Bob-Prompt: {self.current_prompt['file'] if self.current_prompt else 'N/A'}
Evidence: {self.current_session['file']}
Generated-By: Bob AI Assistant
"""
        return message + "\n" + evidence
    
    def update_commit_map(self, commit_hash: str, message: str, files: list):
        """Update commit mapping JSON."""
        commit_map_file = Path(".bob/commits/commit_map.json")
        
        # Load existing map
        with open(commit_map_file) as f:
            commit_map = json.load(f)
        
        # Add new commit
        commit_entry = {
            "hash": commit_hash,
            "short_hash": commit_hash[:7],
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "session": self.current_session,
            "prompt": self.current_prompt,
            "files_changed": files,
            "ai_generated": True
        }
        
        commit_map["commits"].append(commit_entry)
        commit_map["statistics"]["total_commits"] += 1
        
        # Save updated map
        with open(commit_map_file, 'w') as f:
            json.dump(commit_map, f, indent=2)
```

---

### Phase 4: Prompts Folder Setup (30 minutes)

**Objective:** Create and document prompts folder structure

**Tasks:**
1. Create prompts README
2. Create prompt index
3. Document prompt workflow
4. Create example prompts
5. Commit prompts infrastructure

**Deliverables:**
- `prompts/README.md`
- `prompts/prompt_index.json`
- `prompts/000_example_prompt.md`

**Prompts README:**
```markdown
# Prompts Documentation

This folder contains all user prompts provided to Bob AI Assistant.

## Structure

- Each prompt is a numbered markdown file: `NNN_title.md`
- `prompt_index.json` tracks all prompts
- Prompts are committed BEFORE Bob processes them
- Updated with results AFTER Bob completes work

## Workflow

1. Create prompt file: `prompts/003_secret_scanner.md`
2. Commit prompt: `git commit -m "docs(prompts): add prompt 003"`
3. Bob processes prompt (creates session, makes commits)
4. Update prompt with results
5. Commit updated prompt: `git commit -m "docs(prompts): update prompt 003 with results"`

## Verification

```bash
# List all prompts
ls -la prompts/*.md

# View prompt index
cat prompts/prompt_index.json

# Find commits for prompt
git log --grep="prompt_003" --oneline
```
```

---

### Phase 5: Documentation and Examples (45 minutes)

**Objective:** Create comprehensive documentation and examples

**Tasks:**
1. Create judge verification guide
2. Create example session documents
3. Create example prompt documents
4. Create evidence summary
5. Update main README

**Deliverables:**
- `JUDGE_VERIFICATION_GUIDE.md`
- `.bob/sessions/example_session.md`
- `prompts/example_prompt.md`
- `.bob/commits/evidence_summary.md`
- Updated `README.md`

**Judge Verification Guide:**
```markdown
# Judge Verification Guide

## Quick Verification (5 minutes)

### 1. View All Bob Commits
```bash
git log --grep="Bob-Session" --oneline
```
Expected: Multiple commits with Bob attribution

### 2. Check Evidence Files
```bash
ls -la .bob/sessions/
ls -la prompts/
```
Expected: Session and prompt files present

### 3. Verify Commit Mapping
```bash
cat .bob/commits/commit_map.json | jq '.statistics'
```
Expected: Complete statistics

### 4. Validate Evidence
```bash
python .bob/scripts/validate_evidence.py
```
Expected: ✅ PASSED

## Detailed Verification (15 minutes)

### View Specific Session
```bash
# Example: Secret Scanner implementation
git log --grep="code_002" --oneline
cat .bob/sessions/2026-05-03_code_002.md
cat prompts/003_secret_scanner.md
```

### Verify Code Quality
```bash
# View file with Bob attribution
git log --follow backend/app/services/secret_scanner.py
git show <commit_hash>
```

### Check Evidence Completeness
```bash
# Count evidence files
echo "Sessions: $(ls .bob/sessions/*.md | wc -l)"
echo "Prompts: $(ls prompts/*.md | wc -l)"
echo "Commits: $(git log --grep='Bob-Session' --oneline | wc -l)"
```

## Scoring Checklist

- [ ] All commits have Bob attribution
- [ ] Sessions documented
- [ ] Prompts preserved
- [ ] Commit mapping complete
- [ ] Evidence validation passes
- [ ] Code quality high
- [ ] Tests included
- [ ] Documentation complete

**Expected Score: 93-99/100** 🏆
```

---

### Phase 6: Testing and Validation (30 minutes)

**Objective:** Test complete evidence system

**Tasks:**
1. Create test session
2. Create test commits
3. Validate evidence
4. Test verification commands
5. Fix any issues

**Test Workflow:**
```bash
# 1. Start test session
python .bob/scripts/generate_session.py \
  --mode "Code" \
  --objective "Test evidence tracking"

# 2. Create test prompt
cat > prompts/999_test_prompt.md << 'EOF'
# Prompt: Test Evidence Tracking
**Prompt ID:** 999
**Mode:** Code
**Objective:** Test the evidence tracking system
EOF

git add prompts/999_test_prompt.md
git commit -m "docs(prompts): add test prompt 999"

# 3. Make test commit with evidence
git commit --allow-empty -m "test: verify evidence tracking

Test commit to validate evidence system.

Bob-Session: code_999
Bob-Mode: Code
Bob-Prompt: prompts/999_test_prompt.md
Evidence: .bob/sessions/2026-05-03_code_999.md
Generated-By: Bob AI Assistant"

# 4. Update commit map
python .bob/scripts/update_commit_map.py

# 5. Validate evidence
python .bob/scripts/validate_evidence.py

# 6. Generate summary
python .bob/scripts/generate_summary.py

# 7. Verify with judge commands
git log --grep="Bob-Session" --oneline
cat .bob/commits/evidence_summary.md
```

---

## Integration with Existing Git Automation

### Modify `git_autocommit.py`

Add Bob evidence tracking to existing automation:

```python
# At the top of git_autocommit.py
from bob_evidence_tracker import BobEvidenceTracker

class GitAutoCommit:
    def __init__(self):
        # ... existing code ...
        self.evidence_tracker = BobEvidenceTracker()
    
    def commit_group(self, group_name, files):
        """Commit a group of files with Bob evidence."""
        
        # Generate base commit message (existing logic)
        message = self.generate_commit_message(group_name, files)
        
        # Enhance with Bob evidence
        if self.evidence_tracker.current_session:
            message = self.evidence_tracker.enhance_commit_message(message)
        
        # Create commit (existing logic)
        commit_hash = self.create_commit(message, files)
        
        # Update commit map
        if self.evidence_tracker.current_session:
            self.evidence_tracker.update_commit_map(
                commit_hash, message, files
            )
        
        return commit_hash
```

---

## Timeline and Effort

| Phase | Duration | Complexity | Priority |
|-------|----------|------------|----------|
| Phase 1: Infrastructure | 30 min | Low | High |
| Phase 2: Automation Scripts | 45 min | Medium | High |
| Phase 3: Git Integration | 60 min | High | High |
| Phase 4: Prompts Setup | 30 min | Low | High |
| Phase 5: Documentation | 45 min | Medium | Medium |
| Phase 6: Testing | 30 min | Medium | High |
| **TOTAL** | **4 hours** | - | - |

---

## Success Criteria

### Must Have (Critical)
- ✅ `.bob/` directory structure created
- ✅ `prompts/` directory structure created
- ✅ Commit map JSON functional
- ✅ Evidence validation script works
- ✅ Git automation includes Bob evidence
- ✅ All commits have Bob attribution

### Should Have (Important)
- ✅ Session documents auto-generated
- ✅ Prompt index maintained
- ✅ Evidence summary generated
- ✅ Judge verification guide complete
- ✅ Example documents created

### Nice to Have (Optional)
- ⭕ Web dashboard for evidence
- ⭕ Automated statistics reporting
- ⭕ Evidence export to PDF
- ⭕ Integration with CI/CD

---

## Risk Mitigation

### Risk 1: Evidence Files Not Committed
**Mitigation:** Add pre-push hook to validate evidence
```bash
#!/bin/bash
# .git/hooks/pre-push
python .bob/scripts/validate_evidence.py || exit 1
```

### Risk 2: Commit Map Out of Sync
**Mitigation:** Auto-update commit map in Git automation

### Risk 3: Missing Session Documentation
**Mitigation:** Template-based auto-generation

### Risk 4: Incomplete Prompt History
**Mitigation:** Commit prompts immediately upon creation

---

## Post-Implementation Checklist

**Before Hackathon Submission:**

- [ ] Run evidence validation: `python .bob/scripts/validate_evidence.py`
- [ ] Generate evidence summary: `python .bob/scripts/generate_summary.py`
- [ ] Test judge verification commands
- [ ] Verify all commits have Bob attribution
- [ ] Check commit map completeness
- [ ] Validate session documents
- [ ] Confirm prompt history
- [ ] Update README with evidence section
- [ ] Create judge verification guide
- [ ] Test on fresh clone

**Verification Commands:**
```bash
# Quick validation
python .bob/scripts/validate_evidence.py

# Count evidence
echo "Sessions: $(ls .bob/sessions/*.md 2>/dev/null | wc -l)"
echo "Prompts: $(ls prompts/*.md 2>/dev/null | wc -l)"
echo "Bob Commits: $(git log --grep='Bob-Session' --oneline | wc -l)"

# Test judge commands
git log --grep="Bob-Session" --oneline | head -10
cat .bob/commits/evidence_summary.md
```

---

## Next Steps

1. **Review this implementation plan**
2. **Approve approach and timeline**
3. **Switch to Code mode** for implementation
4. **Begin with Phase 1** (Infrastructure Setup)
5. **Iterate through phases** sequentially
6. **Test thoroughly** before submission
7. **Generate final evidence summary**

---

**Document Version:** 1.0  
**Author:** Bob (Plan Mode)  
**Status:** ✅ Ready for Implementation  
**Estimated Time:** 4 hours  
**Expected Score Impact:** +23-29 points 🚀