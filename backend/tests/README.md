# PolicyPilot Backend Test Suite

Comprehensive pytest suite for the PolicyPilot backend with 237+ tests covering all services, APIs, and integration workflows.

## Overview

This test suite provides extensive coverage of the PolicyPilot backend, including:
- **Secret Scanner**: Pattern detection, entropy calculation, confidence scoring
- **README Validator**: Section validation, quality scoring
- **Prompt Checker**: Documentation validation, field checking
- **Scoring Engine**: Module scoring, weighted calculations, recommendations
- **File Handler**: Upload management, validation, security
- **Report Generator**: Multi-format report generation
- **API Endpoints**: All FastAPI routes and error handling
- **Integration Tests**: End-to-end workflows

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_secret_scanner.py -v

# Run specific test class
pytest tests/test_secret_scanner.py::TestEntropyCalculation -v

# Run specific test
pytest tests/test_secret_scanner.py::TestEntropyCalculation::test_entropy_random_string -v
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"

# Run scanner tests
pytest -m scanner

# Run validator tests
pytest -m validator
```

## Test Structure

```
tests/
├── README.md                      # This file
├── conftest.py                    # Shared fixtures and configuration
├── test_secret_scanner.py         # Secret scanner tests (682 lines, 43 tests)
├── test_readme_validator.py       # README validator tests (673 lines, 37 tests)
├── test_prompt_checker.py         # Prompt checker tests (598 lines, 33 tests)
├── test_scoring_engine.py         # Scoring engine tests (682 lines, 41 tests)
├── test_file_handler.py           # File handler tests (~400 lines, ~25 tests)
├── test_report_generator.py       # Report generator tests (~400 lines, ~25 tests)
└── test_api.py                    # API endpoint tests (497 lines, 33 tests)
```

## Test Coverage

### Current Coverage

| Module | Coverage | Lines | Tests |
|--------|----------|-------|-------|
| secret_scanner.py | ≥95% | 761 | 43 |
| readme_validator.py | ≥90% | 286 | 37 |
| prompt_checker.py | ≥90% | 293 | 33 |
| scoring_engine.py | ≥95% | 377 | 41 |
| file_handler.py | ≥85% | 219 | ~25 |
| report_generator.py | ≥85% | 713 | ~25 |
| main.py (API) | ≥90% | 305 | 33 |
| **Overall** | **≥85%** | **2,954** | **237** |

### Coverage Goals

- **Overall**: ≥85%
- **Critical modules** (secret_scanner, scoring_engine, main): ≥90%
- **Supporting modules**: ≥80%

## Test Categories

### Unit Tests

Test individual functions and methods in isolation:
- Entropy calculation
- Pattern matching
- Score calculation
- File validation
- Data transformation

### Integration Tests

Test multiple components working together:
- Full project scanning
- Complete analysis workflow
- Report generation pipeline
- Upload and analyze flow

### API Tests

Test FastAPI endpoints:
- Health checks
- File uploads
- Project analysis
- Report retrieval
- Error handling

### Performance Tests

Test performance characteristics:
- Large file handling
- Many files upload
- Directory scanning speed

### Security Tests

Test security features:
- Path traversal prevention
- File extension validation
- Input sanitization

## Fixtures

### Directory Fixtures

- `temp_dir`: Temporary directory with automatic cleanup
- `test_project_dir`: Test project structure
- `upload_dir`: Temporary upload directory
- `reports_dir`: Temporary reports directory

### File Fixtures

- `sample_python_file`: Python file with secrets
- `sample_readme_complete`: Complete README
- `sample_readme_incomplete`: Incomplete README
- `sample_prompt_json`: JSON prompt file
- `sample_prompt_text`: Text prompt file
- `sample_secrets_file`: File with various secret patterns
- `sample_false_positives_file`: File with false positive patterns

### Model Fixtures

- `sample_secret_match`: SecretMatch object
- `sample_readme_result`: ReadmeValidationResult object
- `sample_prompt_result`: PromptDocumentationResult object

### Client Fixtures

- `client`: FastAPI TestClient
- `async_client`: Async HTTP client

## Writing New Tests

### Test Naming Convention

```python
def test_<what>_<condition>_<expected_result>():
    """Test that <what> <condition> results in <expected_result>."""
    pass
```

Examples:
- `test_entropy_empty_string_returns_zero()`
- `test_upload_invalid_extension_returns_400()`
- `test_analysis_with_secrets_reduces_score()`

### Test Structure

```python
def test_feature():
    """Test description."""
    # Arrange - Set up test data
    scanner = SecretScanner()
    test_file = create_test_file("test.py", "content")
    
    # Act - Execute the code being tested
    result = scanner.scan_file(test_file)
    
    # Assert - Verify the results
    assert len(result) > 0
    assert result[0].severity == SeverityLevel.CRITICAL
```

### Using Fixtures

```python
def test_with_fixtures(test_project_dir, sample_readme_complete):
    """Test using fixtures."""
    validator = ReadmeValidator()
    result = validator.validate(test_project_dir)
    assert result.exists is True
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("test", 0.0),
    ("random123", 3.5),
    ("AKIAIOSFODNN7EXAMPLE", 4.0),
])
def test_entropy_calculation(input, expected):
    """Test entropy calculation with various inputs."""
    scanner = SecretScanner()
    entropy = scanner.calculate_entropy(input)
    assert entropy >= expected
```

## Continuous Integration

### GitHub Actions Example

```yaml
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
        pytest --cov=app --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with import errors
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: Fixtures not found
```bash
# Solution: Ensure conftest.py is in tests/ directory
# and pytest is discovering it correctly
pytest --fixtures
```

**Issue**: Coverage not showing all files
```bash
# Solution: Run from project root
cd backend
pytest --cov=app
```

**Issue**: Tests are slow
```bash
# Solution: Run fast tests only
pytest -m "not slow"

# Or run in parallel
pip install pytest-xdist
pytest -n auto
```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Use Fixtures**: Leverage fixtures for common setup to reduce duplication
3. **Clear Assertions**: Use descriptive assertion messages
4. **Test Edge Cases**: Include tests for boundary conditions and error cases
5. **Mock External Dependencies**: Use mocks for external services
6. **Keep Tests Fast**: Optimize slow tests or mark them with `@pytest.mark.slow`
7. **Document Complex Tests**: Add docstrings explaining what's being tested
8. **Follow AAA Pattern**: Arrange, Act, Assert

## Maintenance

### Adding New Tests

1. Identify the feature or bug to test
2. Choose appropriate test file or create new one
3. Write test following naming conventions
4. Use existing fixtures or create new ones
5. Run test to verify it works
6. Check coverage impact

### Updating Tests

When modifying code:
1. Run affected tests first
2. Update tests to match new behavior
3. Add new tests for new functionality
4. Verify coverage hasn't decreased
5. Run full test suite before committing

### Reviewing Tests

When reviewing test PRs:
- [ ] Tests follow naming conventions
- [ ] Tests are independent
- [ ] Fixtures used appropriately
- [ ] Edge cases covered
- [ ] Assertions are meaningful
- [ ] Tests are well-documented
- [ ] Coverage goals met

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Support

For questions or issues with tests:
1. Check this README
2. Review existing tests for examples
3. Check pytest documentation
4. Ask the team

## Made with Bob