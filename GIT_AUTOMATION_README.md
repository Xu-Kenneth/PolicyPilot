# PolicyPilot Git Automation Script

Production-ready Python script for intelligent, safe Git commit management with automatic change detection, smart grouping, and secret scanning.

## Features

✅ **Automatic Change Detection** - Detects all modified, added, and deleted files  
✅ **Smart Commit Grouping** - Groups changes by module and feature  
✅ **Auto-Generated Messages** - Creates semantic commit messages following Conventional Commits  
✅ **Secret Scanning** - Validates commits don't contain secrets (integrates with PolicyPilot scanner)  
✅ **Safety Validation** - Multiple validation layers prevent accidents  
✅ **Dry-Run Mode** - Preview changes without executing  
✅ **GitHub Push** - Automated push with error handling  

## Installation

### Prerequisites

- Python 3.10+
- Git installed and configured
- GitHub repository with push access

### Setup

```bash
# No installation needed - it's a standalone script
# Just ensure you have Python 3.10+

# Make executable (optional)
chmod +x git_automation.py
```

## Usage

### Basic Usage

```bash
# Preview changes (safe - no commits made)
python git_automation.py --dry-run

# Execute commits and push to GitHub
python git_automation.py

# Commit but don't push
python git_automation.py --no-push

# Use specific repository
python git_automation.py --repo /path/to/repo
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without executing (safe mode) |
| `--no-push` | Create commits but don't push to remote |
| `--repo PATH` | Path to git repository (default: current directory) |
| `--help` | Show help message |

## How It Works

### Workflow Steps

1. **Change Detection** - Scans repository for modified files using `git status`
2. **Safety Validation** - Runs multiple safety checks:
   - Blocks sensitive files (.env, .pem, .key, etc.)
   - Scans for secrets using PolicyPilot's secret scanner
   - Validates commit size limits
3. **Smart Grouping** - Groups changes into logical commits by:
   - Module (security, api, docs, etc.)
   - Commit type (feat, fix, docs, test, etc.)
   - File relationships
4. **Message Generation** - Creates semantic commit messages:
   - Follows Conventional Commits format
   - Includes file lists and statistics
   - Adds metadata footer
5. **Preview** - Shows all commits that will be created
6. **Confirmation** - Asks user to confirm before executing
7. **Execution** - Stages files, creates commits, pushes to GitHub

### Commit Classification

#### Commit Types

- `feat` - New features or enhancements
- `fix` - Bug fixes
- `docs` - Documentation changes only
- `test` - Test additions or modifications
- `refactor` - Code restructuring without behavior change
- `style` - Code style/formatting changes
- `chore` - Maintenance tasks (config, dependencies)
- `perf` - Performance improvements
- `ci` - CI/CD pipeline changes
- `build` - Build system changes

#### Module Scopes

- `security` - Secret scanner module
- `readme` - README validator
- `prompts` - Prompt checker
- `scoring` - Scoring engine
- `reporting` - Report generator
- `api` - API endpoints and models
- `config` - Configuration files
- `tests` - Test files
- `docs` - Documentation
- `ci` - CI/CD workflows
- `core` - Cross-cutting changes

### Commit Message Format

```
type(scope): subject line

Body with details:
- File changes
- Statistics

Generated-by: PolicyPilot Git Automation
```

**Example:**
```
feat(security): add secret scanning

Files changed:
- + app/services/secret_scanner.py
- ~ app/models.py
- + test_secret_scanner.py

Changes: +761, -50

Generated-by: PolicyPilot Git Automation
```

## Safety Features

### 1. Blocked File Patterns

The script automatically blocks commits containing:
- Environment files: `.env`, `.env.local`, `.env.production`
- Private keys: `.pem`, `.key`, `.p12`, `.pfx`
- SSH keys: `id_rsa`, `id_dsa`
- Certificates: `*.crt`, `*.cer`

### 2. Secret Scanning

If PolicyPilot's secret scanner is available, the script:
- Scans all changed files for secrets
- Blocks commits with high-confidence secrets (≥80%)
- Shows detected secrets with file locations
- Provides remediation guidance

### 3. Size Limits

- Warns if >50 files changed (suggests splitting)
- Warns if >2000 lines added (suggests splitting)
- Automatically splits large commits into smaller groups

### 4. Dry-Run Mode

Always test with `--dry-run` first:
```bash
python git_automation.py --dry-run
```

This shows exactly what will happen without making any changes.

## Examples

### Example 1: Preview Changes

```bash
$ python git_automation.py --dry-run

🚀 PolicyPilot Git Automation
============================================================
⚠️  DRY RUN MODE - No changes will be made

📊 Step 1: Detecting changes...
   Found 4 changed files

🔒 Step 2: Running safety validation...
   ✅ All safety checks passed

📦 Step 3: Grouping changes into commits...
   Created 2 commit groups

✍️  Step 4: Generating commit messages...

👀 Step 5: Preview commits
------------------------------------------------------------

Commit 1/2:
  Type: feat(security)
  Subject: add secret scanning
  Files: 3
  Changes: +761, -50
  Files:
    - app/services/secret_scanner.py
    - app/models.py
    - test_secret_scanner.py

Commit 2/2:
  Type: docs
  Subject: update documentation
  Files: 1
  Changes: +417, -0
  Files:
    - SECRET_SCANNER_COMMIT.md

✅ Dry run complete - no changes made
```

### Example 2: Execute Commits

```bash
$ python git_automation.py

🚀 PolicyPilot Git Automation
============================================================

📊 Step 1: Detecting changes...
   Found 4 changed files

🔒 Step 2: Running safety validation...
   ✅ All safety checks passed

📦 Step 3: Grouping changes into commits...
   Created 2 commit groups

✍️  Step 4: Generating commit messages...

👀 Step 5: Preview commits
------------------------------------------------------------
[... preview output ...]

============================================================
Ready to create 2 commits
============================================================

Proceed with commits? [y/N]: y

💾 Step 6: Executing commits...
   Creating commit 1/2...
   Creating commit 2/2...
   ✅ All commits created successfully

📤 Step 7: Pushing to GitHub...
   ✅ Successfully pushed to remote

============================================================
✅ Git automation complete!
```

### Example 3: Secret Detection

```bash
$ python git_automation.py

🚀 PolicyPilot Git Automation
============================================================

📊 Step 1: Detecting changes...
   Found 2 changed files

🔒 Step 2: Running safety validation...
   ❌ Found 2 high-confidence secrets:
      - AWS Access Key ID in config.py:15
        Confidence: 95%
      - GitHub Personal Access Token in settings.py:42
        Confidence: 88%

   Please remove secrets before committing.
   Use environment variables or .env files (add to .gitignore)

❌ Safety validation failed
```

## Integration with PolicyPilot

### Secret Scanner Integration

The script automatically uses PolicyPilot's secret scanner if available:

```python
from backend.app.services.secret_scanner import secret_scanner

# Scans all changed files
secrets = secret_scanner.scan_file(filepath)

# Blocks high-confidence secrets
high_conf_secrets = [s for s in secrets if s.confidence >= 0.8]
```

### Module Detection

The script understands PolicyPilot's module structure:

```python
MODULE_PATTERNS = {
    ModuleScope.SECURITY: [r'secret_scanner\.py'],
    ModuleScope.README: [r'readme_validator\.py'],
    ModuleScope.PROMPTS: [r'prompt_checker\.py'],
    ModuleScope.SCORING: [r'scoring_engine\.py'],
    ModuleScope.REPORTING: [r'report_generator\.py'],
    # ... more modules
}
```

## Troubleshooting

### Issue: "Not a git repository"

**Solution:** Run from within a git repository or use `--repo` flag:
```bash
python git_automation.py --repo /path/to/repo
```

### Issue: "Secret scanner not available"

**Solution:** The script will skip secret scanning but still work. To enable:
```bash
# Ensure PolicyPilot backend is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/policypilot"
```

### Issue: "Push failed"

**Solution:** Commits are saved locally. Push manually:
```bash
git push origin main
```

Or check:
- GitHub authentication (token/SSH key)
- Network connectivity
- Branch permissions

### Issue: "Too many files changed"

**Solution:** The script will automatically split into multiple commits. Or commit in stages:
```bash
# Commit specific files first
git add specific_files
git commit -m "message"

# Then run automation for remaining files
python git_automation.py
```

## Best Practices

### 1. Always Use Dry-Run First

```bash
# Preview before executing
python git_automation.py --dry-run

# If looks good, execute
python git_automation.py
```

### 2. Review Generated Messages

The script generates good messages, but you can always:
- Run with `--no-push`
- Review commits with `git log`
- Amend if needed: `git commit --amend`
- Then push manually: `git push`

### 3. Keep Changes Focused

For best results:
- Work on one feature at a time
- Commit frequently
- Let the script group related changes

### 4. Handle Secrets Properly

Never commit secrets. Instead:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore

# Use environment variables
export API_KEY="your_key_here"

# Or use .env files (gitignored)
echo "API_KEY=your_key_here" > .env
```

## Advanced Usage

### Custom Repository Path

```bash
# Work with different repository
python git_automation.py --repo ~/projects/other-repo
```

### Commit Without Push

```bash
# Create commits locally, push later
python git_automation.py --no-push

# Review commits
git log --oneline -5

# Push when ready
git push origin main
```

### Integration with CI/CD

```yaml
# .github/workflows/auto-commit.yml
name: Auto Commit

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  auto-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Run Git Automation
        run: python git_automation.py --dry-run
```

## Configuration

### Environment Variables

```bash
# Git configuration
export GIT_AUTHOR_NAME="Bob AI Assistant"
export GIT_AUTHOR_EMAIL="bob@policypilot.ai"

# GitHub token (for push)
export GITHUB_TOKEN="ghp_your_token_here"
```

### Customization

To customize behavior, edit the script:

```python
# Change size limits
MAX_FILES_PER_COMMIT = 20  # Default: 20
MAX_LINES_PER_COMMIT = 1000  # Default: 1000

# Add custom module patterns
MODULE_PATTERNS = {
    ModuleScope.CUSTOM: [r'custom_pattern\.py'],
    # ... existing patterns
}

# Add custom blocked patterns
BLOCKED_PATTERNS = {
    '.custom_secret',
    # ... existing patterns
}
```

## Contributing

To improve the script:

1. Test changes with `--dry-run`
2. Ensure safety features remain intact
3. Add tests for new features
4. Update documentation

## License

Part of PolicyPilot project.

## Support

For issues or questions:
- Check troubleshooting section above
- Review PolicyPilot documentation
- Check git automation design document

---

**Version:** 1.0  
**Last Updated:** 2026-05-03  
**Author:** Bob (Code Mode)