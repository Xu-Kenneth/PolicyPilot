# Git Autocommit Script - Usage Guide

Production-ready Python script for intelligent Git automation with safety features.

## Features

✅ **Intelligent File Grouping** - Automatically groups related files into logical commits
✅ **Auto-Generated Commit Messages** - Creates conventional commit messages
✅ **Secret Detection** - Scans files for hardcoded secrets before committing
✅ **Dry-Run Mode** - Preview changes without making commits
✅ **Safe Execution** - Requires confirmation when secrets are detected
✅ **GitHub Support** - Works with local GitHub repositories
✅ **Verbose Logging** - Detailed output for debugging

## Installation

No additional dependencies required - uses Python standard library only!

```bash
# Make script executable (Linux/Mac)
chmod +x git_autocommit.py

# Or run with Python
python git_autocommit.py
```

## Quick Start

### 1. Preview Changes (Dry Run)

```bash
python git_autocommit.py --dry-run
```

**Output:**
```
[10:30:45] 🔍 DRY RUN MODE - No changes will be made
[10:30:45] ✓ Repository: /path/to/PolicyPilot
[10:30:45] ✓ Detecting file changes...
[10:30:45] ✓ Found 12 changed file(s)
[10:30:45] ✓ Grouping changes into logical commits...
[10:30:45] ✓ Created 3 commit group(s)

--- Commit Group 1/3: backend_service ---
[10:30:45] 🔍 Would commit 4 file(s):
[10:30:45] 🔍 Message: feat(services): add 4 new files
[10:30:45] 🔍   A backend/app/services/secret_scanner.py
[10:30:45] 🔍   A backend/app/services/readme_validator.py
[10:30:45] 🔍   A backend/app/services/prompt_checker.py
[10:30:45] 🔍   A backend/app/services/scoring_engine.py
```

### 2. Commit Changes

```bash
python git_autocommit.py
```

### 3. Commit and Push

```bash
python git_autocommit.py --push
```

### 4. Commit and Push to Specific Branch

```bash
python git_autocommit.py --push --remote origin --branch main
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Preview without committing | False |
| `--push` | Push after committing | False |
| `--remote` | Remote repository name | origin |
| `--branch` | Branch to push to | current branch |
| `--repo-path` | Path to git repository | current directory |
| `--verbose` | Enable verbose output | False |

## File Grouping Logic

The script automatically groups files into logical commits based on patterns:

### Backend Service Files
**Pattern:** `backend/app/services/*.py`
**Commit Type:** `feat(services)` or `refactor(services)`
**Example:**
```
feat(services): add secret_scanner.py

  + backend/app/services/secret_scanner.py
```

### Backend Core Files
**Pattern:** `backend/app/(main|config|models).py`
**Commit Type:** `feat(core)` or `refactor(core)`
**Example:**
```
feat(core): add main.py

  + backend/app/main.py
```

### Backend Tests
**Pattern:** `backend/test_*.py`
**Commit Type:** `test(tests)`
**Example:**
```
test(tests): add test_secret_scanner.py

  + backend/test_secret_scanner.py
```

### Backend Documentation
**Pattern:** `backend/*.md`
**Commit Type:** `docs(backend)`
**Example:**
```
docs(backend): add README.md

  + backend/README.md
```

### Backend Configuration
**Pattern:** `backend/(requirements.txt|.env*|.gitignore|run.py)`
**Commit Type:** `chore(backend)`
**Example:**
```
chore(backend): update requirements.txt

  ~ backend/requirements.txt
```

### Root Documentation
**Pattern:** `*.md` (root level)
**Commit Type:** `docs`
**Example:**
```
docs: add ARCHITECTURE.md

  + ARCHITECTURE.md
```

### Scripts
**Pattern:** `*.py`, `*.sh`, `*.bat`
**Commit Type:** `feat` or `chore`
**Example:**
```
feat: add git_autocommit.py

  + git_autocommit.py
```

## Secret Detection

The script scans for 8 types of secrets:

1. **API Keys** - `api_key`, `apikey`
2. **Passwords** - `password`, `passwd`, `pwd`
3. **Tokens** - `token`, `auth_token`
4. **Secret Keys** - `secret`, `secret_key`
5. **Private Keys** - RSA/SSH private keys
6. **AWS Credentials** - AWS access keys
7. **GitHub Tokens** - `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
8. **Slack Tokens** - `xoxb-`, `xoxa-`, `xoxp-`, `xoxr-`, `xoxs-`

### False Positive Detection

The script ignores common false positives:
- Example values (`example`, `sample`, `placeholder`)
- Test values (`test_`, `dummy`, `fake`, `mock`)
- Template values (`your_`, `my_`, `<your`, `<insert`)
- Masked values (`xxx`, `***`, `...`)
- Environment variables (`${`, `$(`)

### When Secrets Are Detected

```
⚠️  Secrets detected in 1 file(s):
  config.py:
    Line 15: api_key - api_key = "sk-1234567890abcdef"

⚠️  Continue with commit? (yes/no):
```

Type `yes` to proceed or `no` to abort.

## Commit Message Format

The script follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

  <file changes>
```

### Commit Types

- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Test additions/changes
- `chore` - Maintenance tasks

### File Change Symbols

- `+` - Added file
- `~` - Modified file
- `-` - Deleted file
- `→` - Renamed file

## Examples

### Example 1: Adding New Backend Services

**Files Changed:**
- `backend/app/services/secret_scanner.py` (new)
- `backend/app/services/readme_validator.py` (new)
- `backend/app/services/prompt_checker.py` (new)

**Generated Commit:**
```
feat(services): add 3 new files

  + backend/app/services/secret_scanner.py
  + backend/app/services/readme_validator.py
  + backend/app/services/prompt_checker.py
```

### Example 2: Updating Documentation

**Files Changed:**
- `README.md` (modified)
- `ARCHITECTURE.md` (modified)

**Generated Commits:**
```
docs: update README.md

  ~ README.md

docs: update ARCHITECTURE.md

  ~ ARCHITECTURE.md
```

### Example 3: Mixed Changes

**Files Changed:**
- `backend/app/main.py` (modified)
- `backend/requirements.txt` (modified)
- `backend/README.md` (new)

**Generated Commits:**
```
refactor(core): update main.py

  ~ backend/app/main.py

chore(backend): update requirements.txt

  ~ backend/requirements.txt

docs(backend): add README.md

  + backend/README.md
```

## Safety Features

### 1. Dry Run Mode
Always test with `--dry-run` first to preview changes.

### 2. Secret Detection
Automatically scans for hardcoded secrets before committing.

### 3. User Confirmation
Requires explicit confirmation when secrets are detected.

### 4. No Destructive Operations
Never modifies or deletes files - only stages and commits.

### 5. Error Handling
Graceful error handling with clear error messages.

## Troubleshooting

### "Not a git repository!"

**Solution:** Run the script from within a git repository or use `--repo-path`:
```bash
python git_autocommit.py --repo-path /path/to/repo
```

### "No changes detected"

**Solution:** Make sure you have uncommitted changes:
```bash
git status
```

### "Failed to stage file"

**Solution:** Check file permissions and git status:
```bash
git status
git add <file>  # Test manually
```

### "Failed to push"

**Solution:** Check remote configuration and authentication:
```bash
git remote -v
git push origin main  # Test manually
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Auto Commit
on: [push]
jobs:
  commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Git Automation
        run: python git_autocommit.py --dry-run
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python git_autocommit.py --dry-run
```

## Best Practices

1. **Always use dry-run first** to preview changes
2. **Review generated commit messages** before pushing
3. **Keep commits atomic** - one logical change per commit
4. **Use meaningful branch names** for better organization
5. **Test secret detection** with known test secrets
6. **Run regularly** to keep commits small and manageable

## Advanced Usage

### Custom File Patterns

Edit the `file_patterns` dictionary in the script:

```python
self.file_patterns = {
    'frontend': r'^frontend/.*\.(js|jsx|ts|tsx)$',
    'backend_api': r'^backend/api/.*\.py$',
    # Add your patterns here
}
```

### Custom Secret Patterns

Edit the `SECRET_PATTERNS` dictionary:

```python
SECRET_PATTERNS = {
    'custom_token': r'CUSTOM_TOKEN[\s]*=[\s]*[\'"]?([a-zA-Z0-9]+)[\'"]?',
    # Add your patterns here
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review the script's verbose output (`--verbose`)
3. Test with `--dry-run` first
4. Check git status manually

## License

Part of PolicyPilot - IBM watsonx Policy Compliance Checker