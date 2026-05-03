# Secret Scanner Module - Git Commit Strategy

## Overview
This document defines the Git commit strategy for the Secret Scanner module, including commit message format, affected files, and rationale for commit boundaries.

---

## Commit Message

```
feat(security): implement advanced secret scanning engine

Add comprehensive secret detection with entropy analysis and false positive reduction

Features:
- Multi-pattern detection for 20+ secret types (API keys, tokens, AWS, DB strings, private keys)
- Shannon entropy calculation for randomness detection
- Advanced false positive reduction with context analysis
- Confidence scoring system (0.0-1.0)
- Severity classification (CRITICAL, HIGH, MEDIUM, LOW)
- Structured JSON output with detailed statistics

Technical improvements:
- Enhanced SecretMatch model with entropy, confidence, and metadata fields
- Pattern-based detection with configurable thresholds
- Context-aware scanning with line/column precision
- File and path filtering for performance optimization

Breaking changes:
- SecretMatch model now requires additional fields (secret_type, column_start, confidence, entropy, reason)
- Existing code using SecretMatch must be updated to provide new required fields

BREAKING CHANGE: SecretMatch model signature changed
```

---

## Affected Files

### Modified Files
1. **`backend/app/models.py`**
   - Enhanced `SecretMatch` model with new fields:
     - `secret_type`: Type classification of the secret
     - `column_start`: Column position in line
     - `column_end`: End column position (optional)
     - `confidence`: Confidence score (0.0-1.0)
     - `entropy`: Shannon entropy value
     - `reason`: Detection reason/description
     - `is_verified`: Verification status flag

2. **`backend/app/services/secret_scanner.py`**
   - Complete rewrite with advanced detection engine
   - Added `SecretPattern` dataclass for pattern definitions
   - Implemented `calculate_entropy()` for Shannon entropy analysis
   - Implemented `is_false_positive()` with comprehensive checks
   - Implemented `calculate_confidence()` with multi-factor scoring
   - Added 20+ detection patterns for various secret types
   - Enhanced scanning logic with context awareness
   - Added structured JSON output with statistics

### New Files
3. **`backend/test_secret_scanner.py`**
   - Comprehensive test suite for secret scanner
   - Demonstrates detection capabilities
   - Tests entropy calculation
   - Validates false positive reduction
   - Generates JSON output for verification

4. **`backend/SECRET_SCANNER_COMMIT.md`** (this file)
   - Git commit strategy documentation
   - Rationale and implementation details

---

## Rationale for Commit Boundary

### Why These Files Belong Together

#### 1. **Cohesive Feature Implementation**
All changes work together to implement a single, cohesive feature: advanced secret scanning. The model changes, scanner implementation, and tests form a complete, functional unit.

#### 2. **Dependency Chain**
- `models.py` defines the data structure
- `secret_scanner.py` uses the model to return results
- `test_secret_scanner.py` validates the implementation
- All three must be updated together to maintain consistency

#### 3. **Breaking Change Management**
The model changes are breaking changes that affect the scanner implementation. Committing them together ensures:
- No intermediate broken state
- Clear migration path for consumers
- Atomic update of all dependent code

#### 4. **Feature Completeness**
This commit delivers a complete, testable feature:
- ✅ Data models defined
- ✅ Core logic implemented
- ✅ Tests provided
- ✅ Documentation included

### Why NOT Split Into Multiple Commits

#### ❌ **Model-Only Commit**
Would break existing code without providing the implementation that uses the new fields.

#### ❌ **Scanner-Only Commit**
Would fail because the model doesn't have required fields yet.

#### ❌ **Test-Only Commit**
Would fail because neither model nor scanner support the new functionality.

### Alternative Commit Strategy (Not Recommended)

If forced to split, the order would be:
1. **Commit 1**: Model changes (breaking)
2. **Commit 2**: Scanner implementation
3. **Commit 3**: Tests and documentation

**Why this is worse:**
- Commit 1 breaks the build
- Commit 2 is required to fix Commit 1
- Creates unnecessary intermediate states
- Harder to review and revert

---

## Implementation Details

### Secret Detection Capabilities

#### Supported Secret Types (20+)
1. **AWS Credentials**
   - Access Key ID (AKIA*, ASIA*, etc.)
   - Secret Access Key (40-character base64)
   - Session Token (100+ character base64)

2. **API Keys**
   - Generic API keys (20+ characters)
   - Google Cloud API keys (AIza prefix)
   - Stripe keys (sk_live, pk_test)
   - Twilio keys (SK prefix)
   - SendGrid keys (SG. prefix)

3. **Version Control Tokens**
   - GitHub Personal Access Tokens (ghp_)
   - GitHub OAuth Tokens (gho_)
   - GitHub App Tokens (ghu_)
   - GitHub Refresh Tokens (ghr_)

4. **Communication Platform Tokens**
   - Slack tokens (xoxb-, xoxp-, xoxs-)
   - Slack webhooks (hooks.slack.com URLs)

5. **Database Connection Strings**
   - PostgreSQL (postgres://)
   - MySQL (mysql://)
   - MongoDB (mongodb://, mongodb+srv://)
   - Redis (redis://)

6. **Cryptographic Keys**
   - RSA Private Keys
   - EC Private Keys
   - DSA Private Keys
   - OpenSSH Private Keys
   - SSH Private Keys

7. **Authentication Tokens**
   - JWT tokens (eyJ prefix)
   - OAuth tokens
   - Bearer tokens
   - Generic access tokens

8. **Cloud Provider Keys**
   - Azure Storage Keys (88-character base64)
   - PayPal/Braintree tokens

9. **Generic Secrets**
   - Hardcoded passwords
   - Generic secrets
   - Generic tokens

### False Positive Reduction

#### Pattern-Based Filtering
- Example/sample/test/dummy/fake/mock indicators
- Placeholder patterns (your_key, insert_here, xxx, 000)
- Environment variable references (${}, $(), %, os.getenv)
- Sequential patterns (012, 123, abc, qwerty)
- Documentation indicators

#### Entropy-Based Filtering
- Shannon entropy calculation
- Minimum entropy thresholds per pattern type
- Low diversity detection (repeated characters)
- Character type analysis (upper, lower, digit, special)

#### Context-Based Filtering
- Comment line detection
- Production vs. test environment indicators
- Confidence scoring based on context clues

### Confidence Scoring Algorithm

Multi-factor scoring (0.0 to 1.0):

1. **Entropy Contribution (40%)**
   - Higher entropy = higher confidence
   - Normalized to 0-1 scale

2. **Length Contribution (20%)**
   - Longer secrets = higher confidence
   - Thresholds: 40+ chars (0.2), 32+ chars (0.15), 20+ chars (0.1)

3. **Context Clues (20%)**
   - Positive: prod, production, live, secret, private (+0.05 each)
   - Negative: test, dev, local, example, sample (-0.05 each)

4. **Character Diversity (20%)**
   - Presence of uppercase, lowercase, digits, special chars
   - Maximum 0.2 for all four types present

5. **Pattern-Specific Adjustments**
   - High-confidence patterns (AWS, GitHub, Stripe) get +0.1 bonus

### Severity Classification

- **CRITICAL**: AWS keys, private keys, database URLs, production API keys
- **HIGH**: Generic API keys, OAuth tokens, Slack tokens, JWT tokens
- **MEDIUM**: Generic secrets, generic tokens
- **LOW**: (Reserved for future use)

### Performance Optimizations

#### File Filtering
- Skip binary files (images, videos, executables, archives)
- Skip dependency directories (node_modules, vendor, venv)
- Skip build artifacts (dist, build, target)
- Skip large files (>1MB)

#### Path Filtering
- Skip version control directories (.git, .svn, .hg)
- Skip cache directories (__pycache__, .pytest_cache)
- Skip coverage directories

---

## Testing Strategy

### Test Coverage

The test file (`test_secret_scanner.py`) validates:

1. **Detection Accuracy**
   - Correctly identifies real secrets
   - Correctly ignores false positives
   - Handles various secret formats

2. **Entropy Calculation**
   - Validates Shannon entropy algorithm
   - Tests with various string patterns

3. **Confidence Scoring**
   - Verifies multi-factor scoring
   - Tests edge cases

4. **JSON Output**
   - Validates structured output format
   - Verifies statistics calculation

### Manual Testing

To test the scanner:

```bash
# Run the test suite
python backend/test_secret_scanner.py

# Expected output:
# - List of detected secrets with metadata
# - Statistics by severity, type, and confidence
# - JSON output file (scan_results.json)
# - Entropy analysis for sample strings
```

---

## Migration Guide

### For Existing Code Using SecretMatch

**Before:**
```python
secret = SecretMatch(
    pattern_name="API Key",
    file_path="config.py",
    line_number=10,
    matched_text="sk_****",
    context="api_key = sk_live_...",
    severity=SeverityLevel.HIGH
)
```

**After:**
```python
secret = SecretMatch(
    pattern_name="API Key",
    secret_type="api_key",              # NEW: Required
    file_path="config.py",
    line_number=10,
    column_start=12,                     # NEW: Required
    column_end=52,                       # NEW: Optional
    matched_text="sk_****",
    context="api_key = sk_live_...",
    severity=SeverityLevel.HIGH,
    confidence=0.85,                     # NEW: Required (0.0-1.0)
    entropy=4.2,                         # NEW: Required
    reason="Stripe API key detected",   # NEW: Required
    is_verified=False                    # NEW: Optional (default False)
)
```

### For Code Scanning Files

**Before:**
```python
from app.services.secret_scanner import secret_scanner

secrets = secret_scanner.scan_file(Path("myfile.py"))
for secret in secrets:
    print(f"{secret.pattern_name}: {secret.matched_text}")
```

**After (No Changes Required):**
```python
from app.services.secret_scanner import secret_scanner

secrets = secret_scanner.scan_file(Path("myfile.py"))
for secret in secrets:
    print(f"{secret.pattern_name}: {secret.matched_text}")
    print(f"Confidence: {secret.confidence:.2%}")
    print(f"Entropy: {secret.entropy:.2f}")
```

---

## Future Enhancements

### Planned Features
1. **Secret Verification**
   - API calls to verify if secrets are valid
   - Integration with secret scanning services

2. **Custom Patterns**
   - User-defined regex patterns
   - Pattern configuration via YAML/JSON

3. **Remediation Suggestions**
   - Automated fix suggestions
   - Environment variable migration

4. **Integration**
   - Git hooks for pre-commit scanning
   - CI/CD pipeline integration
   - IDE plugins

5. **Reporting**
   - HTML/PDF report generation
   - Trend analysis over time
   - Compliance reporting

### Technical Debt
- Add unit tests for individual methods
- Add integration tests with real repositories
- Performance benchmarking
- Memory optimization for large files

---

## Review Checklist

Before merging, verify:

- [ ] All files compile without errors
- [ ] Model changes are backward-incompatible (documented)
- [ ] Scanner detects all 20+ secret types
- [ ] False positive rate is acceptable (<5%)
- [ ] Confidence scoring is accurate
- [ ] JSON output is well-formed
- [ ] Test file runs successfully
- [ ] Documentation is complete
- [ ] Breaking changes are clearly marked
- [ ] Migration guide is provided

---

## Commit Metadata

- **Type**: `feat` (new feature)
- **Scope**: `security` (security-related changes)
- **Breaking Change**: Yes (model signature changed)
- **Ticket**: N/A (internal improvement)
- **Reviewers**: Security team, Backend team
- **Estimated Review Time**: 30-45 minutes

---

## Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [API_EXAMPLES.md](API_EXAMPLES.md) - API usage examples
- [README.md](README.md) - Project overview

---

**Last Updated**: 2026-05-03  
**Author**: Bob (AI Assistant)  
**Version**: 1.0.0