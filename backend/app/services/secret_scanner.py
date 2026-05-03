"""
Secret Scanner Service - Advanced Detection Engine
Detects sensitive information in code repositories including API keys, tokens,
credentials, and private keys with false positive reduction and entropy analysis.
"""

import re
import math
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass

from app.config import settings
from app.models import SecretMatch, SeverityLevel


@dataclass
class SecretPattern:
    """Defines a pattern for detecting secrets with metadata."""
    name: str
    pattern: str
    secret_type: str
    severity: SeverityLevel
    description: str
    min_entropy: float = 3.0
    requires_context: bool = False


class SecretScanner:
    """
    Advanced secret scanner with entropy analysis and false positive reduction.
    
    Features:
    - Multiple secret type detection (API keys, tokens, AWS, DB strings, private keys)
    - Shannon entropy calculation for randomness detection
    - False positive reduction with context analysis
    - Confidence scoring (0.0-1.0)
    - Severity classification (CRITICAL, HIGH, MEDIUM, LOW)
    - Structured JSON output
    """
    
    # False positive indicators
    FALSE_POSITIVE_PATTERNS = [
        r'example',
        r'sample',
        r'test',
        r'dummy',
        r'fake',
        r'mock',
        r'placeholder',
        r'your[_-]?key',
        r'your[_-]?token',
        r'your[_-]?secret',
        r'insert[_-]?here',
        r'replace[_-]?this',
        r'<your',
        r'<insert',
        r'xxx+',
        r'000+',
        r'111+',
        r'aaa+',
        r'abc+',
        r'123+',
        r'\*\*\*+',
        r'\.\.\.+',
    ]
    
    # File extensions to skip
    SKIP_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.pyc', '.pyo', '.class', '.o', '.obj',
        '.woff', '.woff2', '.ttf', '.eot', '.otf'
    }
    
    # Paths to skip
    SKIP_PATHS = {
        'node_modules', 'vendor', 'venv', 'env', '.venv',
        '.git', '.svn', '.hg',
        'dist', 'build', 'target', 'out',
        '__pycache__', '.pytest_cache', '.mypy_cache',
        'coverage', '.coverage', 'htmlcov',
        '.next', '.nuxt', '.cache',
        'bower_components', 'jspm_packages'
    }
    
    def __init__(self):
        """Initialize the secret scanner with detection patterns."""
        self.patterns = self._initialize_patterns()
        self.false_positive_regex = re.compile(
            '|'.join(self.FALSE_POSITIVE_PATTERNS),
            re.IGNORECASE
        )
    
    def _initialize_patterns(self) -> List[SecretPattern]:
        """Initialize comprehensive secret detection patterns."""
        return [
            # AWS Credentials
            SecretPattern(
                name="AWS Access Key ID",
                pattern=r'\b((?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16})\b',
                secret_type="aws_access_key",
                severity=SeverityLevel.CRITICAL,
                description="AWS Access Key ID detected",
                min_entropy=3.5
            ),
            SecretPattern(
                name="AWS Secret Access Key",
                pattern=r'(?i)(?:aws[_-]?secret[_-]?access[_-]?key|aws[_-]?secret)["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
                secret_type="aws_secret_key",
                severity=SeverityLevel.CRITICAL,
                description="AWS Secret Access Key detected",
                min_entropy=4.0,
                requires_context=True
            ),
            SecretPattern(
                name="AWS Session Token",
                pattern=r'(?i)(?:aws[_-]?session[_-]?token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{100,})["\']?',
                secret_type="aws_session_token",
                severity=SeverityLevel.HIGH,
                description="AWS Session Token detected",
                min_entropy=4.0,
                requires_context=True
            ),
            
            # API Keys
            SecretPattern(
                name="Generic API Key",
                pattern=r'(?i)(?:api[_-]?key|apikey|api[_-]?secret)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
                secret_type="api_key",
                severity=SeverityLevel.HIGH,
                description="Generic API key detected",
                min_entropy=3.5,
                requires_context=True
            ),
            
            # GitHub Tokens
            SecretPattern(
                name="GitHub Personal Access Token",
                pattern=r'\b(ghp_[A-Za-z0-9_]{36,})\b',
                secret_type="github_token",
                severity=SeverityLevel.CRITICAL,
                description="GitHub personal access token detected",
                min_entropy=4.0
            ),
            SecretPattern(
                name="GitHub OAuth Token",
                pattern=r'\b(gho_[A-Za-z0-9_]{36,})\b',
                secret_type="github_oauth",
                severity=SeverityLevel.CRITICAL,
                description="GitHub OAuth token detected",
                min_entropy=4.0
            ),
            SecretPattern(
                name="GitHub App Token",
                pattern=r'\b(ghu_[A-Za-z0-9_]{36,})\b',
                secret_type="github_app",
                severity=SeverityLevel.CRITICAL,
                description="GitHub App token detected",
                min_entropy=4.0
            ),
            SecretPattern(
                name="GitHub Refresh Token",
                pattern=r'\b(ghr_[A-Za-z0-9_]{36,})\b',
                secret_type="github_refresh",
                severity=SeverityLevel.CRITICAL,
                description="GitHub refresh token detected",
                min_entropy=4.0
            ),
            
            # Slack Tokens
            SecretPattern(
                name="Slack Token",
                pattern=r'\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,})\b',
                secret_type="slack_token",
                severity=SeverityLevel.HIGH,
                description="Slack token detected",
                min_entropy=4.0
            ),
            SecretPattern(
                name="Slack Webhook",
                pattern=r'https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24,}',
                secret_type="slack_webhook",
                severity=SeverityLevel.HIGH,
                description="Slack webhook URL detected",
                min_entropy=3.5
            ),
            
            # Stripe Keys
            SecretPattern(
                name="Stripe API Key",
                pattern=r'\b((?:sk|pk)_(?:live|test)_[A-Za-z0-9]{24,})\b',
                secret_type="stripe_key",
                severity=SeverityLevel.CRITICAL,
                description="Stripe API key detected",
                min_entropy=4.0
            ),
            
            # Private Keys
            SecretPattern(
                name="RSA Private Key",
                pattern=r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
                secret_type="private_key",
                severity=SeverityLevel.CRITICAL,
                description="Private key detected",
                min_entropy=2.0
            ),
            
            # Database Connection Strings
            SecretPattern(
                name="PostgreSQL Connection String",
                pattern=r'(?i)postgres(?:ql)?://[^\s:]+:[^\s@]+@[^\s/]+(?:/[^\s]*)?',
                secret_type="database_url",
                severity=SeverityLevel.CRITICAL,
                description="PostgreSQL connection string with credentials detected",
                min_entropy=3.0
            ),
            SecretPattern(
                name="MySQL Connection String",
                pattern=r'(?i)mysql://[^\s:]+:[^\s@]+@[^\s/]+(?:/[^\s]*)?',
                secret_type="database_url",
                severity=SeverityLevel.CRITICAL,
                description="MySQL connection string with credentials detected",
                min_entropy=3.0
            ),
            SecretPattern(
                name="MongoDB Connection String",
                pattern=r'(?i)mongodb(?:\+srv)?://[^\s:]+:[^\s@]+@[^\s/]+(?:/[^\s]*)?',
                secret_type="database_url",
                severity=SeverityLevel.CRITICAL,
                description="MongoDB connection string with credentials detected",
                min_entropy=3.0
            ),
            SecretPattern(
                name="Redis Connection String",
                pattern=r'(?i)redis://[^\s:]*:[^\s@]+@[^\s/]+(?:/[^\s]*)?',
                secret_type="database_url",
                severity=SeverityLevel.CRITICAL,
                description="Redis connection string with credentials detected",
                min_entropy=3.0
            ),
            
            # JWT Tokens
            SecretPattern(
                name="JWT Token",
                pattern=r'\b(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b',
                secret_type="jwt_token",
                severity=SeverityLevel.HIGH,
                description="JWT token detected",
                min_entropy=4.0
            ),
            
            # OAuth Tokens
            SecretPattern(
                name="OAuth Token",
                pattern=r'(?i)(?:oauth[_-]?token|access[_-]?token|bearer[_-]?token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{20,})["\']?',
                secret_type="oauth_token",
                severity=SeverityLevel.HIGH,
                description="OAuth/Access token detected",
                min_entropy=3.5,
                requires_context=True
            ),
            
            # Passwords
            SecretPattern(
                name="Password in Code",
                pattern=r'(?i)(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\'\s]{8,})["\']',
                secret_type="password",
                severity=SeverityLevel.HIGH,
                description="Hardcoded password detected",
                min_entropy=2.5,
                requires_context=True
            ),
            
            # Generic Secrets
            SecretPattern(
                name="Generic Secret",
                pattern=r'(?i)(?:secret|secret[_-]?key)["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']',
                secret_type="generic_secret",
                severity=SeverityLevel.MEDIUM,
                description="Generic secret detected",
                min_entropy=3.0,
                requires_context=True
            ),
            SecretPattern(
                name="Generic Token",
                pattern=r'(?i)(?:token|auth[_-]?token)["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']',
                secret_type="generic_token",
                severity=SeverityLevel.MEDIUM,
                description="Generic token detected",
                min_entropy=3.0,
                requires_context=True
            ),
            
            # Cloud Provider Keys
            SecretPattern(
                name="Google Cloud API Key",
                pattern=r'\b(AIza[A-Za-z0-9_\-]{35})\b',
                secret_type="google_api_key",
                severity=SeverityLevel.CRITICAL,
                description="Google Cloud API key detected",
                min_entropy=3.5
            ),
            SecretPattern(
                name="Azure Storage Key",
                pattern=r'(?i)(?:azure[_-]?storage[_-]?key|azure[_-]?key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{88})["\']?',
                secret_type="azure_key",
                severity=SeverityLevel.CRITICAL,
                description="Azure storage key detected",
                min_entropy=4.0,
                requires_context=True
            ),
            
            # Messaging/Communication
            SecretPattern(
                name="Twilio API Key",
                pattern=r'\b(SK[a-z0-9]{32})\b',
                secret_type="twilio_key",
                severity=SeverityLevel.HIGH,
                description="Twilio API key detected",
                min_entropy=3.5
            ),
            SecretPattern(
                name="SendGrid API Key",
                pattern=r'\b(SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43})\b',
                secret_type="sendgrid_key",
                severity=SeverityLevel.HIGH,
                description="SendGrid API key detected",
                min_entropy=4.0
            ),
            
            # Payment Processors
            SecretPattern(
                name="PayPal/Braintree Access Token",
                pattern=r'access_token\$production\$[a-z0-9]{16}\$[a-f0-9]{32}',
                secret_type="paypal_token",
                severity=SeverityLevel.CRITICAL,
                description="PayPal/Braintree access token detected",
                min_entropy=4.0
            ),
            
            # SSH Keys
            SecretPattern(
                name="SSH Private Key",
                pattern=r'-----BEGIN OPENSSH PRIVATE KEY-----',
                secret_type="ssh_key",
                severity=SeverityLevel.CRITICAL,
                description="SSH private key detected",
                min_entropy=2.0
            ),
        ]
    
    def calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string.
        Higher entropy indicates more randomness (likely a real secret).
        
        Args:
            string: The string to analyze
            
        Returns:
            Shannon entropy value
        """
        if not string or len(string) < 2:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in string:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(string)
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def is_false_positive(self, matched_string: str, context: str, line: str) -> bool:
        """
        Check if the matched string is likely a false positive.
        
        Args:
            matched_string: The matched secret string
            context: Surrounding context
            line: The line containing the match
            
        Returns:
            True if likely a false positive
        """
        # Check against false positive patterns
        if self.false_positive_regex.search(matched_string):
            return True
        
        if self.false_positive_regex.search(context):
            return True
        
        # Check for environment variable references
        if any(indicator in line for indicator in ['${', '$(', '%', 'os.getenv', 'process.env', 'ENV[']):
            return True
        
        # Check for common placeholder patterns
        if re.match(r'^[A-Z_]+$', matched_string) and len(matched_string) < 15:
            return True
        
        # Check for repeated characters (low diversity)
        if len(set(matched_string)) < len(matched_string) * 0.3:
            return True
        
        # Check for sequential patterns
        sequential_patterns = [
            r'(012|123|234|345|456|567|678|789)',
            r'(abc|bcd|cde|def|efg|fgh)',
            r'(qwerty|asdfgh|zxcvbn)'
        ]
        for pattern in sequential_patterns:
            if re.search(pattern, matched_string.lower()):
                return True
        
        # Check for documentation/comment indicators
        doc_indicators = ['example', 'documentation', 'readme', 'comment', 'note:', 'todo:']
        if any(indicator in context.lower() for indicator in doc_indicators):
            return True
        
        return False
    
    def calculate_confidence(
        self,
        matched_string: str,
        context: str,
        entropy: float,
        min_entropy: float,
        pattern_name: str
    ) -> float:
        """
        Calculate confidence score (0.0 to 1.0) for a detected secret.
        
        Args:
            matched_string: The matched secret string
            context: Surrounding context
            entropy: Calculated entropy
            min_entropy: Minimum required entropy
            pattern_name: Name of the pattern that matched
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Entropy contribution (40% weight)
        if entropy >= min_entropy:
            entropy_score = min(entropy / 5.0, 1.0)
            confidence += entropy_score * 0.4
        else:
            confidence -= 0.2
        
        # Length contribution (20% weight)
        if len(matched_string) >= 40:
            confidence += 0.2
        elif len(matched_string) >= 32:
            confidence += 0.15
        elif len(matched_string) >= 20:
            confidence += 0.1
        
        # Context clues (20% weight)
        context_lower = context.lower()
        
        # Positive indicators
        positive_indicators = ['prod', 'production', 'live', 'secret', 'private', 'credential', 'key']
        positive_count = sum(1 for indicator in positive_indicators if indicator in context_lower)
        confidence += min(positive_count * 0.05, 0.15)
        
        # Negative indicators
        negative_indicators = ['test', 'dev', 'local', 'example', 'sample']
        negative_count = sum(1 for indicator in negative_indicators if indicator in context_lower)
        confidence -= min(negative_count * 0.05, 0.1)
        
        # Character diversity (20% weight)
        char_types = sum([
            any(c.isupper() for c in matched_string),
            any(c.islower() for c in matched_string),
            any(c.isdigit() for c in matched_string),
            any(not c.isalnum() for c in matched_string)
        ])
        confidence += (char_types / 4.0) * 0.2
        
        # Pattern-specific adjustments
        if pattern_name in ['AWS Access Key ID', 'GitHub Personal Access Token', 'Stripe API Key']:
            confidence += 0.1  # High-confidence patterns
        
        return min(max(confidence, 0.0), 1.0)
    
    def should_skip_file(self, file_path: Path) -> bool:
        """
        Check if file should be skipped.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be skipped
        """
        # Check extension
        if file_path.suffix.lower() in self.SKIP_EXTENSIONS:
            return True
        
        # Check path components
        path_parts = set(file_path.parts)
        if path_parts & self.SKIP_PATHS:
            return True
        
        # Check file size (skip files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True
        
        return False
    
    def get_context(self, lines: List[str], line_number: int, context_size: int = 2) -> str:
        """
        Get surrounding context for a match.
        
        Args:
            lines: All lines in the file
            line_number: Line number (1-based)
            context_size: Number of lines before/after
            
        Returns:
            Context string
        """
        start = max(0, line_number - context_size - 1)
        end = min(len(lines), line_number + context_size)
        return ''.join(lines[start:end]).strip()
    
    def is_comment_line(self, line: str) -> bool:
        """
        Check if a line is a comment.
        
        Args:
            line: Line of code
            
        Returns:
            True if line is a comment
        """
        stripped = line.strip()
        comment_prefixes = ('#', '//', '/*', '*', '<!--', '--', ';', '%')
        return any(stripped.startswith(prefix) for prefix in comment_prefixes)
    
    def scan_file(self, file_path: Path) -> List[SecretMatch]:
        """
        Scan a single file for secrets.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of detected secrets
        """
        if self.should_skip_file(file_path):
            return []
        
        secrets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError, OSError):
            return secrets
        
        content = ''.join(lines)
        
        for pattern in self.patterns:
            compiled_pattern = re.compile(pattern.pattern, re.IGNORECASE | re.MULTILINE)
            
            for match in compiled_pattern.finditer(content):
                # Extract the actual secret value
                matched_string = match.group(1) if match.groups() else match.group(0)
                
                # Calculate line and column
                line_number = content[:match.start()].count('\n') + 1
                line_start = content[:match.start()].rfind('\n') + 1
                column_start = match.start() - line_start
                column_end = column_start + len(matched_string)
                
                # Get the actual line
                line = lines[line_number - 1] if line_number <= len(lines) else ""
                
                # Skip comments unless it's a private key
                if self.is_comment_line(line) and pattern.secret_type != "private_key":
                    continue
                
                # Get context
                context = self.get_context(lines, line_number)
                
                # Calculate entropy
                entropy = self.calculate_entropy(matched_string)
                
                # Check for false positives
                if self.is_false_positive(matched_string, context, line):
                    continue
                
                # Check minimum entropy
                if entropy < pattern.min_entropy:
                    continue
                
                # Calculate confidence
                confidence = self.calculate_confidence(
                    matched_string,
                    context,
                    entropy,
                    pattern.min_entropy,
                    pattern.name
                )
                
                # Skip low confidence matches for context-dependent patterns
                if pattern.requires_context and confidence < 0.5:
                    continue
                
                # Mask the secret for display
                masked_text = self._mask_secret(matched_string)
                
                # Create secret match
                secret = SecretMatch(
                    pattern_name=pattern.name,
                    secret_type=pattern.secret_type,
                    file_path=str(file_path),
                    line_number=line_number,
                    column_start=column_start,
                    column_end=column_end,
                    matched_text=masked_text,
                    context=context,
                    severity=pattern.severity,
                    confidence=confidence,
                    entropy=entropy,
                    reason=pattern.description
                )
                secrets.append(secret)
        
        return secrets
    
    def scan_directory(self, directory: Path) -> List[SecretMatch]:
        """
        Scan all files in a directory recursively.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of all detected secrets
        """
        all_secrets = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                secrets = self.scan_file(file_path)
                all_secrets.extend(secrets)
        
        return all_secrets
    
    def _mask_secret(self, text: str, visible_chars: int = 4) -> str:
        """
        Mask a secret for display.
        
        Args:
            text: Secret text
            visible_chars: Number of characters to show
            
        Returns:
            Masked secret
        """
        if len(text) <= visible_chars:
            return '*' * len(text)
        return text[:visible_chars] + '*' * (len(text) - visible_chars)
    
    def get_statistics(self, secrets: List[SecretMatch]) -> Dict[str, Any]:
        """
        Get statistics about detected secrets.
        
        Args:
            secrets: List of detected secrets
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total': len(secrets),
            'by_severity': {},
            'by_type': {},
            'by_pattern': {},
            'unique_files': len(set(s.file_path for s in secrets)),
            'high_confidence': len([s for s in secrets if s.confidence >= 0.8]),
            'medium_confidence': len([s for s in secrets if 0.5 <= s.confidence < 0.8]),
            'low_confidence': len([s for s in secrets if s.confidence < 0.5]),
            'average_confidence': sum(s.confidence for s in secrets) / len(secrets) if secrets else 0.0,
            'average_entropy': sum(s.entropy for s in secrets) / len(secrets) if secrets else 0.0
        }
        
        for secret in secrets:
            # Count by severity
            severity = secret.severity.value
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # Count by type
            secret_type = secret.secret_type
            stats['by_type'][secret_type] = stats['by_type'].get(secret_type, 0) + 1
            
            # Count by pattern
            pattern = secret.pattern_name
            stats['by_pattern'][pattern] = stats['by_pattern'].get(pattern, 0) + 1
        
        return stats
    
    def to_json(self, secrets: List[SecretMatch]) -> str:
        """
        Convert secrets to structured JSON output.
        
        Args:
            secrets: List of detected secrets
            
        Returns:
            JSON string
        """
        output = {
            'scan_results': {
                'secrets': [
                    {
                        'pattern_name': s.pattern_name,
                        'secret_type': s.secret_type,
                        'file_path': s.file_path,
                        'line_number': s.line_number,
                        'column_start': s.column_start,
                        'column_end': s.column_end,
                        'matched_text': s.matched_text,
                        'context': s.context,
                        'severity': s.severity.value,
                        'confidence': round(s.confidence, 3),
                        'entropy': round(s.entropy, 3),
                        'reason': s.reason,
                        'is_verified': s.is_verified
                    }
                    for s in secrets
                ],
                'statistics': self.get_statistics(secrets)
            }
        }
        return json.dumps(output, indent=2)


# Global instance
secret_scanner = SecretScanner()

# Made with Bob
