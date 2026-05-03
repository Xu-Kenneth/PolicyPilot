# PyTest Suite Commit Grouping Strategy

This document outlines the strategy for committing the comprehensive pytest suite for PolicyPilot backend.

## Commit Grouping Philosophy

Tests are grouped by:
1. **Functional area** - Tests for related components
2. **Dependency order** - Foundation tests before integration tests
3. **Logical cohesion** - Related test functionality together
4. **Review size** - Manageable chunks for code review

## Commit Groups

### Group 1: Test Infrastructure & Configuration
**Files:**
- `pytest.ini`
- `requirements-test.txt`
- `tests/conftest.py`
- `tests/__init__.py`

**Rationale:** Foundation for all tests. Must be committed first as other tests depend on fixtures and configuration.

**Size:** ~500 lines
**Review Time:** 15-20 minutes

---

### Group 2: Core Service Tests - Secret Scanner
**Files:**
- `tests/test_secret_scanner.py`

**Rationale:** Secret scanner is a critical security component with complex logic (entropy calculation, pattern matching, false positive filtering). Deserves dedicated commit for thorough review.

**Size:** ~680 lines
**Review Time:** 30-40 minutes

---

### Group 3: Core Service Tests - Validators
**Files:**
- `tests/test_readme_validator.py`
- `tests/test_prompt_checker.py`

**Rationale:** Both validators follow similar patterns (file detection, content validation, scoring). Logical to group together.

**Size:** ~1,270 lines combined
**Review Time:** 40-50 minutes

---

### Group 4: Core Service Tests - Scoring & Integration
**Files:**
- `tests/test_scoring_engine.py`

**Rationale:** Scoring engine integrates all other services. Should be reviewed after understanding individual service tests.

**Size:** ~680 lines
**Review Time:** 30-40 minutes

---

### Group 5: Infrastructure Tests - File Handling & Reports
**Files:**
- `tests/test_file_handler.py`
- `tests/test_report_generator.py`

**Rationale:** Supporting infrastructure for file operations and report generation. Can be reviewed together as they're less complex than core logic.

**Size:** ~800 lines combined (estimated)
**Review Time:** 30-40 minutes

---

### Group 6: API & Integration Tests
**Files:**
- `tests/test_api.py`

**Rationale:** API tests verify end-to-end functionality. Should be last as they depend on all other components working correctly.

**Size:** ~500 lines
**Review Time:** 25-30 minutes

---

## Commit Order

```
1. test: Add pytest infrastructure and configuration
2. test: Add comprehensive secret scanner tests
3. test: Add README and prompt validator tests
4. test: Add scoring engine tests
5. test: Add file handler and report generator tests
6. test: Add API endpoint and integration tests
```

## Alternative Grouping Strategy

If smaller commits are preferred:

### Micro-Commit Strategy
1. Test infrastructure (pytest.ini, conftest.py)
2. Secret scanner - pattern detection tests
3. Secret scanner - entropy and confidence tests
4. Secret scanner - integration tests
5. README validator tests
6. Prompt checker tests
7. Scoring engine - calculation tests
8. Scoring engine - integration tests
9. File handler tests
10. Report generator tests
11. API - health and upload tests
12. API - analysis and report tests
13. API - integration tests

## Testing the Tests

Before committing, ensure:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test groups
pytest tests/test_secret_scanner.py -v
pytest tests/test_readme_validator.py -v
pytest tests/test_prompt_checker.py -v
pytest tests/test_scoring_engine.py -v
pytest tests/test_api.py -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run fast tests only (skip slow)
pytest -m "not slow"
```

## Coverage Goals

- **Overall Coverage:** ≥ 85%
- **Critical Modules:** ≥ 90%
  - secret_scanner.py
  - scoring_engine.py
  - main.py (API endpoints)
- **Supporting Modules:** ≥ 80%
  - readme_validator.py
  - prompt_checker.py
  - file_handler.py
  - report_generator.py

## Review Checklist

For each commit, reviewers should verify:

- [ ] Tests follow pytest conventions
- [ ] Test names are descriptive
- [ ] Tests are independent (no order dependency)
- [ ] Fixtures are used appropriately
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Integration tests verify end-to-end flows
- [ ] Tests are well-documented
- [ ] No test code duplication
- [ ] Assertions are meaningful
- [ ] Test data is realistic

## CI/CD Integration

Tests should be integrated into CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Maintenance Strategy

- **Add tests** for new features before implementation (TDD)
- **Update tests** when modifying existing functionality
- **Review coverage** monthly and add tests for uncovered code
- **Refactor tests** when they become brittle or hard to maintain
- **Document** complex test scenarios

## Made with Bob