"""
Comprehensive tests for Secret Scanner Service.

Tests cover:
- Pattern detection for various secret types
- Entropy calculation
- False positive filtering
- Confidence scoring
- File scanning
- Directory scanning
- Statistics generation
"""
import pytest
from pathlib import Path
from app.services.secret_scanner import SecretScanner, SecretPattern
from app.models import SeverityLevel


# ============================================================================
# Test Class: SecretScanner Initialization
# ============================================================================

class TestSecretScannerInit:
    """Test SecretScanner initialization."""
    
    def test_scanner_initialization(self):
        """Test scanner initializes with patterns."""
        scanner = SecretScanner()
        assert scanner is not None
        assert len(scanner.patterns) > 0
        assert scanner.false_positive_regex is not None
    
    def test_patterns_have_required_fields(self):
        """Test all patterns have required fields."""
        scanner = SecretScanner()
        for pattern in scanner.patterns:
            assert hasattr(pattern, 'name')
            assert hasattr(pattern, 'pattern')
            assert hasattr(pattern, 'secret_type')
            assert hasattr(pattern, 'severity')
            assert hasattr(pattern, 'description')
            assert hasattr(pattern, 'min_entropy')


# ============================================================================
# Test Class: Entropy Calculation
# ============================================================================

class TestEntropyCalculation:
    """Test Shannon entropy calculation."""
    
    def test_entropy_empty_string(self):
        """Test entropy of empty string."""
        scanner = SecretScanner()
        entropy = scanner.calculate_entropy("")
        assert entropy == 0.0
    
    def test_entropy_single_char(self):
        """Test entropy of single character."""
        scanner = SecretScanner()
        entropy = scanner.calculate_entropy("a")
        assert entropy == 0.0
    
    def test_entropy_repeated_chars(self):
        """Test entropy of repeated characters (low entropy)."""
        scanner = SecretScanner()
        entropy = scanner.calculate_entropy("aaaaaaaaaa")
        assert entropy == 0.0
    
    def test_entropy_random_string(self):
        """Test entropy of random-looking string (high entropy)."""
        scanner = SecretScanner()
        entropy = scanner.calculate_entropy("aB3xK9mP2qL7")
        assert entropy > 3.0  # Should have high entropy
    
    def test_entropy_aws_key(self):
        """Test entropy of AWS-like key."""
        scanner = SecretScanner()
        entropy = scanner.calculate_entropy("AKIAIOSFODNN7EXAMPLE")
        assert entropy > 3.0
    
    def test_entropy_comparison(self):
        """Test that random strings have higher entropy than patterns."""
        scanner = SecretScanner()
        low_entropy = scanner.calculate_entropy("abcdefghij")
        high_entropy = scanner.calculate_entropy("aB3xK9mP2q")
        assert high_entropy > low_entropy


# ============================================================================
# Test Class: False Positive Detection
# ============================================================================

class TestFalsePositiveDetection:
    """Test false positive filtering."""
    
    def test_example_keyword(self):
        """Test detection of 'example' keyword."""
        scanner = SecretScanner()
        result = scanner.is_false_positive(
            "example_key_12345",
            "This is an example",
            "API_KEY = 'example_key_12345'"
        )
        assert result is True
    
    def test_placeholder_keywords(self):
        """Test detection of placeholder keywords."""
        scanner = SecretScanner()
        keywords = ["your_key", "insert_here", "replace_this", "xxx", "placeholder"]
        for keyword in keywords:
            result = scanner.is_false_positive(
                keyword,
                f"Use {keyword} here",
                f"KEY = '{keyword}'"
            )
            assert result is True
    
    def test_env_variable_reference(self):
        """Test detection of environment variable references."""
        scanner = SecretScanner()
        lines = [
            "api_key = os.getenv('API_KEY')",
            "secret = ${SECRET_KEY}",
            "token = process.env.TOKEN"
        ]
        for line in lines:
            result = scanner.is_false_positive("API_KEY", "", line)
            assert result is True
    
    def test_all_caps_short_string(self):
        """Test detection of all-caps placeholder."""
        scanner = SecretScanner()
        result = scanner.is_false_positive(
            "API_KEY",
            "",
            "API_KEY = API_KEY"
        )
        assert result is True
    
    def test_low_diversity_string(self):
        """Test detection of low character diversity."""
        scanner = SecretScanner()
        result = scanner.is_false_positive(
            "aaaaaabbbbbb",
            "",
            "KEY = 'aaaaaabbbbbb'"
        )
        assert result is True
    
    def test_sequential_patterns(self):
        """Test detection of sequential patterns."""
        scanner = SecretScanner()
        patterns = ["abc123", "qwerty", "123456"]
        for pattern in patterns:
            result = scanner.is_false_positive(pattern, "", f"KEY = '{pattern}'")
            assert result is True
    
    def test_real_secret_not_false_positive(self):
        """Test that real secrets are not flagged as false positives."""
        scanner = SecretScanner()
        result = scanner.is_false_positive(
            "AKIAIOSFODNN7EXAMPLE",
            "AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'",
            "AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'"
        )
        assert result is False


# ============================================================================
# Test Class: Confidence Scoring
# ============================================================================

class TestConfidenceScoring:
    """Test confidence score calculation."""
    
    def test_high_entropy_increases_confidence(self):
        """Test that high entropy increases confidence."""
        scanner = SecretScanner()
        confidence = scanner.calculate_confidence(
            "aB3xK9mP2qL7wN5tY8",
            "production key",
            4.5,
            3.0,
            "AWS Access Key"
        )
        assert confidence > 0.7
    
    def test_low_entropy_decreases_confidence(self):
        """Test that low entropy decreases confidence."""
        scanner = SecretScanner()
        confidence = scanner.calculate_confidence(
            "test_key_123",
            "test environment",
            2.0,
            3.0,
            "API Key"
        )
        assert confidence < 0.5
    
    def test_production_context_increases_confidence(self):
        """Test that production context increases confidence."""
        scanner = SecretScanner()
        prod_confidence = scanner.calculate_confidence(
            "secret_key_abc123",
            "production secret key",
            3.5,
            3.0,
            "Secret Key"
        )
        test_confidence = scanner.calculate_confidence(
            "secret_key_abc123",
            "test secret key",
            3.5,
            3.0,
            "Secret Key"
        )
        assert prod_confidence > test_confidence
    
    def test_long_string_increases_confidence(self):
        """Test that longer strings increase confidence."""
        scanner = SecretScanner()
        long_confidence = scanner.calculate_confidence(
            "a" * 50,
            "",
            3.5,
            3.0,
            "Token"
        )
        short_confidence = scanner.calculate_confidence(
            "a" * 15,
            "",
            3.5,
            3.0,
            "Token"
        )
        assert long_confidence > short_confidence
    
    def test_high_confidence_patterns(self):
        """Test that specific patterns get confidence boost."""
        scanner = SecretScanner()
        confidence = scanner.calculate_confidence(
            "AKIAIOSFODNN7EXAMPLE",
            "",
            4.0,
            3.5,
            "AWS Access Key ID"
        )
        assert confidence >= 0.6


# ============================================================================
# Test Class: File Scanning
# ============================================================================

class TestFileScanning:
    """Test file scanning functionality."""
    
    def test_scan_file_with_secrets(self, sample_secrets_file):
        """Test scanning file with multiple secrets."""
        scanner = SecretScanner()
        secrets = scanner.scan_file(sample_secrets_file)
        assert len(secrets) > 0
        assert any(s.secret_type == "aws_access_key" for s in secrets)
    
    def test_scan_file_without_secrets(self, test_project_dir):
        """Test scanning file without secrets."""
        clean_file = test_project_dir / "clean.py"
        clean_file.write_text("print('Hello World')\nx = 1 + 1")
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(clean_file)
        assert len(secrets) == 0
    
    def test_scan_file_with_false_positives(self, sample_false_positives_file):
        """Test that false positives are filtered."""
        scanner = SecretScanner()
        secrets = scanner.scan_file(sample_false_positives_file)
        # Should have very few or no secrets due to false positive filtering
        assert len(secrets) < 3
    
    def test_skip_binary_files(self, test_project_dir):
        """Test that binary files are skipped."""
        binary_file = test_project_dir / "image.png"
        binary_file.write_bytes(b'\x89PNG\r\n\x1a\n')
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(binary_file)
        assert len(secrets) == 0
    
    def test_skip_large_files(self, test_project_dir):
        """Test that large files are skipped."""
        large_file = test_project_dir / "large.txt"
        # Create file > 1MB
        large_file.write_text("x" * (1024 * 1024 + 1))
        
        scanner = SecretScanner()
        result = scanner.should_skip_file(large_file)
        assert result is True
    
    def test_secret_location_accuracy(self, test_project_dir):
        """Test that secret locations are accurate."""
        test_file = test_project_dir / "test.py"
        content = '''line 1
line 2
API_KEY = "AKIAIOSFODNN7EXAMPLE"
line 4'''
        test_file.write_text(content)
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        if secrets:
            secret = secrets[0]
            assert secret.line_number == 3
            assert secret.column_start >= 0


# ============================================================================
# Test Class: Directory Scanning
# ============================================================================

class TestDirectoryScanning:
    """Test directory scanning functionality."""
    
    def test_scan_directory_recursive(self, test_project_dir):
        """Test recursive directory scanning."""
        # Create files in subdirectories
        (test_project_dir / "src").mkdir(exist_ok=True)
        (test_project_dir / "src" / "config.py").write_text(
            'API_KEY = "AKIAIOSFODNN7EXAMPLE"'
        )
        (test_project_dir / "tests").mkdir(exist_ok=True)
        (test_project_dir / "tests" / "test.py").write_text(
            'TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"'
        )
        
        scanner = SecretScanner()
        secrets = scanner.scan_directory(test_project_dir)
        
        assert len(secrets) >= 2
        files = set(s.file_path for s in secrets)
        assert len(files) >= 2
    
    def test_scan_empty_directory(self, test_project_dir):
        """Test scanning empty directory."""
        scanner = SecretScanner()
        secrets = scanner.scan_directory(test_project_dir)
        assert len(secrets) == 0
    
    def test_skip_excluded_directories(self, test_project_dir):
        """Test that excluded directories are skipped."""
        # Create node_modules with secrets
        node_modules = test_project_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").write_text(
            'const key = "AKIAIOSFODNN7EXAMPLE";'
        )
        
        scanner = SecretScanner()
        secrets = scanner.scan_directory(test_project_dir)
        
        # Should skip node_modules
        assert not any("node_modules" in s.file_path for s in secrets)


# ============================================================================
# Test Class: Pattern Detection
# ============================================================================

class TestPatternDetection:
    """Test detection of specific secret patterns."""
    
    def test_aws_access_key_detection(self, test_project_dir):
        """Test AWS access key detection."""
        test_file = test_project_dir / "aws.py"
        test_file.write_text('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        assert len(secrets) > 0
        assert any(s.secret_type == "aws_access_key" for s in secrets)
    
    def test_github_token_detection(self, test_project_dir):
        """Test GitHub token detection."""
        test_file = test_project_dir / "github.py"
        test_file.write_text('TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"')
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        assert len(secrets) > 0
        assert any(s.secret_type == "github_token" for s in secrets)
    
    def test_database_url_detection(self, test_project_dir):
        """Test database URL detection."""
        test_file = test_project_dir / "db.py"
        test_file.write_text(
            'DB_URL = "postgresql://user:password123@localhost/db"'
        )
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        assert len(secrets) > 0
        assert any(s.secret_type == "database_url" for s in secrets)
    
    def test_jwt_token_detection(self, test_project_dir):
        """Test JWT token detection."""
        test_file = test_project_dir / "jwt.py"
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        test_file.write_text(f'JWT = "{jwt}"')
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        assert len(secrets) > 0
        assert any(s.secret_type == "jwt_token" for s in secrets)
    
    def test_private_key_detection(self, test_project_dir):
        """Test private key detection."""
        test_file = test_project_dir / "key.pem"
        test_file.write_text('''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890
-----END RSA PRIVATE KEY-----''')
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(test_file)
        
        assert len(secrets) > 0
        assert any(s.secret_type == "private_key" for s in secrets)


# ============================================================================
# Test Class: Statistics Generation
# ============================================================================

class TestStatisticsGeneration:
    """Test statistics generation."""
    
    def test_statistics_empty_list(self):
        """Test statistics with empty secrets list."""
        scanner = SecretScanner()
        stats = scanner.get_statistics([])
        
        assert stats['total'] == 0
        assert stats['unique_files'] == 0
        assert stats['average_confidence'] == 0.0
    
    def test_statistics_with_secrets(self, sample_secret_match):
        """Test statistics with secrets."""
        scanner = SecretScanner()
        secrets = [sample_secret_match]
        stats = scanner.get_statistics(secrets)
        
        assert stats['total'] == 1
        assert stats['unique_files'] == 1
        assert 'by_severity' in stats
        assert 'by_type' in stats
        assert stats['average_confidence'] > 0
    
    def test_statistics_grouping(self, sample_secret_match):
        """Test statistics grouping by severity and type."""
        scanner = SecretScanner()
        
        # Create multiple secrets
        secret1 = sample_secret_match
        secret2 = SecretMatch(
            pattern_name="GitHub Token",
            secret_type="github_token",
            file_path="src/app.py",
            line_number=5,
            column_start=10,
            matched_text="ghp_****",
            context="TOKEN = 'ghp_1234567890'",
            severity=SeverityLevel.CRITICAL,
            confidence=0.9,
            entropy=4.0,
            reason="GitHub token detected"
        )
        
        stats = scanner.get_statistics([secret1, secret2])
        
        assert stats['total'] == 2
        assert stats['by_severity']['critical'] == 2
        assert len(stats['by_type']) == 2


# ============================================================================
# Test Class: JSON Output
# ============================================================================

class TestJSONOutput:
    """Test JSON output generation."""
    
    def test_json_output_structure(self, sample_secret_match):
        """Test JSON output has correct structure."""
        scanner = SecretScanner()
        json_output = scanner.to_json([sample_secret_match])
        
        import json
        data = json.loads(json_output)
        
        assert 'scan_results' in data
        assert 'secrets' in data['scan_results']
        assert 'statistics' in data['scan_results']
    
    def test_json_output_secret_fields(self, sample_secret_match):
        """Test JSON output contains all secret fields."""
        scanner = SecretScanner()
        json_output = scanner.to_json([sample_secret_match])
        
        import json
        data = json.loads(json_output)
        secret = data['scan_results']['secrets'][0]
        
        required_fields = [
            'pattern_name', 'secret_type', 'file_path', 'line_number',
            'severity', 'confidence', 'entropy', 'reason'
        ]
        for field in required_fields:
            assert field in secret


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_nonexistent_file(self, test_project_dir):
        """Test scanning nonexistent file."""
        scanner = SecretScanner()
        fake_file = test_project_dir / "nonexistent.py"
        secrets = scanner.scan_file(fake_file)
        assert len(secrets) == 0
    
    def test_empty_file(self, test_project_dir):
        """Test scanning empty file."""
        empty_file = test_project_dir / "empty.py"
        empty_file.write_text("")
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(empty_file)
        assert len(secrets) == 0
    
    def test_unicode_content(self, test_project_dir):
        """Test scanning file with unicode content."""
        unicode_file = test_project_dir / "unicode.py"
        unicode_file.write_text("# 日本語コメント\nAPI_KEY = 'AKIAIOSFODNN7EXAMPLE'")
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(unicode_file)
        # Should still detect secrets despite unicode
        assert len(secrets) > 0
    
    def test_very_long_line(self, test_project_dir):
        """Test scanning file with very long lines."""
        long_file = test_project_dir / "long.py"
        long_line = "x = '" + "a" * 10000 + "AKIAIOSFODNN7EXAMPLE" + "b" * 10000 + "'"
        long_file.write_text(long_line)
        
        scanner = SecretScanner()
        secrets = scanner.scan_file(long_file)
        # Should handle long lines
        assert isinstance(secrets, list)


# ============================================================================
# Test Class: Integration Tests
# ============================================================================

@pytest.mark.integration
class TestSecretScannerIntegration:
    """Integration tests for secret scanner."""
    
    def test_full_project_scan(self, test_project_dir):
        """Test scanning a complete project structure."""
        # Create realistic project structure
        structure = {
            "src/app.py": 'API_KEY = "AKIAIOSFODNN7EXAMPLE"',
            "src/config.py": 'DB_URL = "postgresql://user:pass@localhost/db"',
            "tests/test.py": 'print("test")',
            "README.md": "# Project",
            ".env.example": "API_KEY=your_key_here"
        }
        
        for path, content in structure.items():
            file_path = test_project_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        scanner = SecretScanner()
        secrets = scanner.scan_directory(test_project_dir)
        
        # Should find secrets but filter false positives
        assert len(secrets) >= 1
        assert not any(".env.example" in s.file_path for s in secrets)
    
    def test_performance_large_directory(self, test_project_dir):
        """Test performance with many files."""
        import time
        
        # Create 50 files
        for i in range(50):
            file_path = test_project_dir / f"file_{i}.py"
            file_path.write_text(f"# File {i}\nprint('hello')")
        
        scanner = SecretScanner()
        start_time = time.time()
        secrets = scanner.scan_directory(test_project_dir)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0


# Made with Bob