"""
Test file for Secret Scanner
Demonstrates detection capabilities with various secret types
"""

from pathlib import Path
from app.services.secret_scanner import secret_scanner
import json


def create_test_file_with_secrets():
    """Create a test file with various types of secrets"""
    test_content = """
# Test File with Various Secrets

# AWS Credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub Token (FAKE - for testing only)
GITHUB_TOKEN = "ghp_FAKE1234567890abcdefghijklmnopqrstuvwxyz"

# API Keys (FAKE - for testing only)
api_key = "sk_test_FAKE51H8K2jL3m4n5o6p7q8r9s0t1u2v3w4x5y6z"
STRIPE_KEY = "pk_test_FAKE51H8K2jL3m4n5o6p7q8r9s0t1u2v3w4x5y6z"

# Database Connection Strings (FAKE - for testing only)
DATABASE_URL = "postgresql://testuser:testpass123@localhost:5432/testdb"
MONGO_URI = "mongodb://testadmin:testpass@localhost:27017/testdb"

# Slack Token (FAKE - for testing only)
SLACK_TOKEN = "xoxb-FAKE-1234567890-1234567890-abcdefghijklmnopqrstuvwx"

# JWT Token (FAKE - for testing only)
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.FAKE.FAKE"

# Private Key
private_key = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz
-----END RSA PRIVATE KEY-----
'''

# Google Cloud API Key
GOOGLE_API_KEY = "AIzaSyD1234567890abcdefghijklmnopqrstuvw"

# False Positives (should NOT be detected)
api_key_example = "your_api_key_here"
password = "test123"  # Too short
token = "example_token"
secret = "placeholder_secret"
dummy_key = "XXXXXXXXXXXXXXXX"

# Environment Variables (should NOT be detected)
api_key = os.getenv("API_KEY")
secret_key = ${SECRET_KEY}
"""
    
    test_file = Path("test_secrets.py")
    test_file.write_text(test_content)
    return test_file


def test_secret_scanner():
    """Test the secret scanner functionality"""
    print("=" * 80)
    print("SECRET SCANNER TEST")
    print("=" * 80)
    
    # Create test file
    test_file = create_test_file_with_secrets()
    print(f"\n✓ Created test file: {test_file}")
    
    try:
        # Scan the test file
        print(f"\n🔍 Scanning {test_file}...")
        secrets = secret_scanner.scan_file(test_file)
        
        print(f"\n📊 SCAN RESULTS")
        print("-" * 80)
        print(f"Total secrets detected: {len(secrets)}")
        
        if secrets:
            print("\n🚨 DETECTED SECRETS:\n")
            
            for i, secret in enumerate(secrets, 1):
                print(f"{i}. {secret.pattern_name}")
                print(f"   Type: {secret.secret_type}")
                print(f"   Severity: {secret.severity.value.upper()}")
                print(f"   Location: Line {secret.line_number}, Column {secret.column_start}")
                print(f"   Matched: {secret.matched_text}")
                print(f"   Confidence: {secret.confidence:.2%}")
                print(f"   Entropy: {secret.entropy:.2f}")
                print(f"   Reason: {secret.reason}")
                print()
        
        # Get statistics
        stats = secret_scanner.get_statistics(secrets)
        print("\n📈 STATISTICS")
        print("-" * 80)
        print(f"Total Secrets: {stats['total']}")
        print(f"Unique Files: {stats['unique_files']}")
        print(f"Average Confidence: {stats['average_confidence']:.2%}")
        print(f"Average Entropy: {stats['average_entropy']:.2f}")
        
        print("\n🎯 By Severity:")
        for severity, count in sorted(stats['by_severity'].items()):
            print(f"  {severity.upper()}: {count}")
        
        print("\n🔑 By Type:")
        for secret_type, count in sorted(stats['by_type'].items()):
            print(f"  {secret_type}: {count}")
        
        print("\n📊 Confidence Distribution:")
        print(f"  High (≥80%): {stats['high_confidence']}")
        print(f"  Medium (50-80%): {stats['medium_confidence']}")
        print(f"  Low (<50%): {stats['low_confidence']}")
        
        # Generate JSON output
        json_output = secret_scanner.to_json(secrets)
        json_file = Path("scan_results.json")
        json_file.write_text(json_output)
        print(f"\n✓ JSON output saved to: {json_file}")
        
        # Test entropy calculation
        print("\n🧮 ENTROPY ANALYSIS")
        print("-" * 80)
        test_strings = [
            ("AKIAIOSFODNN7EXAMPLE", "AWS Key"),
            ("password123", "Weak Password"),
            ("XXXXXXXXXXXXXXXX", "Placeholder"),
            ("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "AWS Secret"),
        ]
        
        for string, label in test_strings:
            entropy = secret_scanner.calculate_entropy(string)
            print(f"{label:20} | Entropy: {entropy:.2f} | String: {string[:20]}...")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print(f"\n🧹 Cleaned up test file: {test_file}")
        
        json_file = Path("scan_results.json")
        if json_file.exists():
            print(f"📄 JSON results available at: {json_file}")


if __name__ == "__main__":
    test_secret_scanner()

# Made with Bob
