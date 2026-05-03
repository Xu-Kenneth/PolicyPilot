#!/usr/bin/env python3
"""
PolicyPilot Git Automation Script

Automatically detects file changes, groups them into logical commits,
generates commit messages, and executes git operations safely.

Features:
- Intelligent file grouping by module/purpose
- Auto-generated conventional commit messages
- Secret detection before committing
- Dry-run mode for safe testing
- Support for local GitHub repositories
- Detailed logging and error handling
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class FileChange:
    """Represents a file change."""
    path: str
    status: str  # 'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed)
    change_type: str  # Inferred type (e.g., 'backend', 'docs', 'config')


@dataclass
class CommitGroup:
    """Represents a group of related file changes."""
    name: str
    files: List[FileChange]
    commit_type: str  # feat, fix, docs, refactor, test, chore
    scope: Optional[str]
    description: str


class SecretDetector:
    """Detects potential secrets in files before committing."""
    
    SECRET_PATTERNS = {
        'api_key': r'(?i)(api[_-]?key|apikey)[\s]*[=:]\s*[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?',
        'password': r'(?i)(password|passwd|pwd)[\s]*[=:]\s*[\'"]?([^\s\'"]{8,})[\'"]?',
        'token': r'(?i)(token|auth[_-]?token)[\s]*[=:]\s*[\'"]?([a-zA-Z0-9_\-\.]{20,})[\'"]?',
        'secret': r'(?i)(secret|secret[_-]?key)[\s]*[=:]\s*[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?',
        'private_key': r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
        'aws_key': r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)[\s]*[=:]\s*[\'"]?([A-Z0-9]{20,})[\'"]?',
        'github_token': r'(?i)gh[pousr]_[A-Za-z0-9_]{36,}',
        'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}',
    }
    
    SAFE_PATTERNS = [
        'example', 'sample', 'placeholder', 'your_', 'my_', 'test_',
        'dummy', 'fake', 'mock', '<your', '<insert', 'xxx', '***', '...',
        '${', '$('
    ]
    
    def scan_file(self, file_path: str) -> List[Tuple[str, int, str]]:
        """
        Scan a file for potential secrets.
        
        Returns:
            List of (pattern_name, line_number, matched_text) tuples
        """
        secrets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            return secrets
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments
            if self._is_comment(line):
                continue
            
            # Check each pattern
            for pattern_name, pattern in self.SECRET_PATTERNS.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    if not self._is_false_positive(line):
                        secrets.append((pattern_name, line_num, match.group(0)[:50]))
        
        return secrets
    
    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment."""
        stripped = line.strip()
        return any(stripped.startswith(prefix) for prefix in ['#', '//', '/*', '*', '<!--'])
    
    def _is_false_positive(self, line: str) -> bool:
        """Check if match is likely a false positive."""
        line_lower = line.lower()
        return any(pattern in line_lower for pattern in self.SAFE_PATTERNS)


class GitAutomation:
    """Main Git automation class."""
    
    def __init__(self, repo_path: str = ".", dry_run: bool = False, verbose: bool = False):
        self.repo_path = Path(repo_path).resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.secret_detector = SecretDetector()
        
        # File grouping patterns
        self.file_patterns = {
            'backend_service': r'^backend/app/services/.*\.py$',
            'backend_core': r'^backend/app/(main|config|models)\.py$',
            'backend_test': r'^backend/test_.*\.py$',
            'backend_docs': r'^backend/.*\.(md|txt)$',
            'backend_config': r'^backend/(requirements\.txt|\.env.*|\.gitignore|run\.py)$',
            'docs': r'^[^/]+\.(md|txt)$',
            'config': r'^\..*|.*\.(json|yaml|yml|toml)$',
            'scripts': r'^.*\.(py|sh|bat)$',
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "🔍" if self.dry_run else "✓"
        if level == "ERROR":
            prefix = "❌"
        elif level == "WARNING":
            prefix = "⚠️"
        elif level == "DRY_RUN":
            prefix = "🔍"
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def run_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """
        Run a shell command.
        
        Returns:
            Tuple of (success, output)
        """
        try:
            if self.verbose:
                self.log(f"Running: {' '.join(command)}", "INFO")
            
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        
        except Exception as e:
            return False, str(e)
    
    def check_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        success, _ = self.run_command(['git', 'rev-parse', '--git-dir'])
        return success
    
    def get_changed_files(self) -> List[FileChange]:
        """Get list of changed files."""
        # Get staged and unstaged changes
        success, output = self.run_command(['git', 'status', '--porcelain'])
        
        if not success:
            self.log("Failed to get git status", "ERROR")
            return []
        
        changes = []
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            # Parse git status output
            status = line[0:2].strip()
            file_path = line[3:].strip()
            
            # Skip renamed files (handle separately)
            if '->' in file_path:
                file_path = file_path.split('->')[-1].strip()
            
            # Determine status
            if status in ['A', 'AM']:
                file_status = 'A'
            elif status in ['M', 'MM', ' M']:
                file_status = 'M'
            elif status in ['D', ' D']:
                file_status = 'D'
            elif status in ['R', 'RM']:
                file_status = 'R'
            else:
                file_status = 'M'  # Default to modified
            
            # Determine change type
            change_type = self._classify_file(file_path)
            
            changes.append(FileChange(
                path=file_path,
                status=file_status,
                change_type=change_type
            ))
        
        return changes
    
    def _classify_file(self, file_path: str) -> str:
        """Classify a file based on its path."""
        for pattern_name, pattern in self.file_patterns.items():
            if re.match(pattern, file_path):
                return pattern_name
        return 'other'
    
    def group_changes(self, changes: List[FileChange]) -> List[CommitGroup]:
        """Group file changes into logical commits."""
        groups: Dict[str, List[FileChange]] = {}
        
        # Group by change type
        for change in changes:
            if change.change_type not in groups:
                groups[change.change_type] = []
            groups[change.change_type].append(change)
        
        # Create commit groups
        commit_groups = []
        
        for group_name, files in groups.items():
            commit_type, scope, description = self._generate_commit_info(group_name, files)
            
            commit_groups.append(CommitGroup(
                name=group_name,
                files=files,
                commit_type=commit_type,
                scope=scope,
                description=description
            ))
        
        return commit_groups
    
    def _generate_commit_info(self, group_name: str, files: List[FileChange]) -> Tuple[str, Optional[str], str]:
        """Generate commit type, scope, and description."""
        # Determine commit type
        has_new = any(f.status == 'A' for f in files)
        has_deleted = any(f.status == 'D' for f in files)
        
        if 'test' in group_name:
            commit_type = 'test'
        elif 'docs' in group_name or group_name == 'backend_docs':
            commit_type = 'docs'
        elif 'config' in group_name or group_name == 'backend_config':
            commit_type = 'chore'
        elif has_new:
            commit_type = 'feat'
        else:
            commit_type = 'refactor'
        
        # Determine scope
        if 'backend' in group_name:
            if 'service' in group_name:
                scope = 'services'
            elif 'core' in group_name:
                scope = 'core'
            elif 'test' in group_name:
                scope = 'tests'
            else:
                scope = 'backend'
        else:
            scope = None
        
        # Generate description
        if len(files) == 1:
            file_name = Path(files[0].path).name
            if files[0].status == 'A':
                description = f"add {file_name}"
            elif files[0].status == 'D':
                description = f"remove {file_name}"
            else:
                description = f"update {file_name}"
        else:
            if has_new and has_deleted:
                description = f"update {len(files)} files"
            elif has_new:
                description = f"add {len(files)} new files"
            elif has_deleted:
                description = f"remove {len(files)} files"
            else:
                description = f"update {len(files)} files"
        
        return commit_type, scope, description
    
    def generate_commit_message(self, group: CommitGroup) -> str:
        """Generate a conventional commit message."""
        # Format: <type>(<scope>): <description>
        if group.scope:
            header = f"{group.commit_type}({group.scope}): {group.description}"
        else:
            header = f"{group.commit_type}: {group.description}"
        
        # Add body with file list
        body_lines = ["\n"]
        for file in group.files:
            status_symbol = {
                'A': '+',
                'M': '~',
                'D': '-',
                'R': '→'
            }.get(file.status, '~')
            body_lines.append(f"  {status_symbol} {file.path}")
        
        return header + '\n'.join(body_lines)
    
    def scan_for_secrets(self, files: List[FileChange]) -> Dict[str, List[Tuple[str, int, str]]]:
        """Scan files for potential secrets."""
        secrets_found = {}
        
        for file in files:
            if file.status == 'D':  # Skip deleted files
                continue
            
            file_path = self.repo_path / file.path
            if not file_path.exists():
                continue
            
            secrets = self.secret_detector.scan_file(str(file_path))
            if secrets:
                secrets_found[file.path] = secrets
        
        return secrets_found
    
    def commit_group(self, group: CommitGroup) -> bool:
        """Commit a group of changes."""
        # Check for secrets
        secrets = self.scan_for_secrets(group.files)
        if secrets:
            self.log(f"⚠️  Secrets detected in {len(secrets)} file(s):", "WARNING")
            for file_path, file_secrets in secrets.items():
                self.log(f"  {file_path}:", "WARNING")
                for pattern, line, text in file_secrets:
                    self.log(f"    Line {line}: {pattern} - {text}", "WARNING")
            
            if not self.dry_run:
                response = input("\n⚠️  Continue with commit? (yes/no): ")
                if response.lower() != 'yes':
                    self.log("Commit aborted by user", "WARNING")
                    return False
        
        # Generate commit message
        commit_message = self.generate_commit_message(group)
        
        if self.dry_run:
            self.log(f"Would commit {len(group.files)} file(s):", "DRY_RUN")
            self.log(f"Message: {commit_message.split(chr(10))[0]}", "DRY_RUN")
            for file in group.files:
                self.log(f"  {file.status} {file.path}", "DRY_RUN")
            return True
        
        # Stage files
        for file in group.files:
            success, output = self.run_command(['git', 'add', file.path])
            if not success:
                self.log(f"Failed to stage {file.path}: {output}", "ERROR")
                return False
        
        # Commit
        success, output = self.run_command(['git', 'commit', '-m', commit_message])
        if not success:
            self.log(f"Failed to commit: {output}", "ERROR")
            return False
        
        self.log(f"✓ Committed {len(group.files)} file(s): {commit_message.split(chr(10))[0]}")
        return True
    
    def push_changes(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """Push commits to remote repository."""
        if self.dry_run:
            self.log(f"Would push to {remote}/{branch or 'current branch'}", "DRY_RUN")
            return True
        
        # Get current branch if not specified
        if not branch:
            success, branch = self.run_command(['git', 'branch', '--show-current'])
            if not success:
                self.log("Failed to get current branch", "ERROR")
                return False
        
        # Push
        self.log(f"Pushing to {remote}/{branch}...")
        success, output = self.run_command(['git', 'push', remote, branch])
        
        if not success:
            self.log(f"Failed to push: {output}", "ERROR")
            return False
        
        self.log(f"✓ Successfully pushed to {remote}/{branch}")
        return True
    
    def run(self, push: bool = False, remote: str = "origin", branch: Optional[str] = None):
        """Run the complete automation workflow."""
        self.log("=" * 60)
        self.log("PolicyPilot Git Automation")
        self.log("=" * 60)
        
        if self.dry_run:
            self.log("🔍 DRY RUN MODE - No changes will be made", "DRY_RUN")
        
        # Check if git repo
        if not self.check_git_repo():
            self.log("Not a git repository!", "ERROR")
            return False
        
        self.log(f"Repository: {self.repo_path}")
        
        # Get changed files
        self.log("Detecting file changes...")
        changes = self.get_changed_files()
        
        if not changes:
            self.log("No changes detected")
            return True
        
        self.log(f"Found {len(changes)} changed file(s)")
        
        # Group changes
        self.log("Grouping changes into logical commits...")
        groups = self.group_changes(changes)
        self.log(f"Created {len(groups)} commit group(s)")
        
        # Commit each group
        success_count = 0
        for i, group in enumerate(groups, 1):
            self.log(f"\n--- Commit Group {i}/{len(groups)}: {group.name} ---")
            if self.commit_group(group):
                success_count += 1
        
        self.log(f"\n✓ Successfully processed {success_count}/{len(groups)} commit group(s)")
        
        # Push if requested
        if push and success_count > 0:
            self.log("\n--- Pushing Changes ---")
            self.push_changes(remote, branch)
        
        self.log("\n" + "=" * 60)
        self.log("Automation complete!")
        self.log("=" * 60)
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PolicyPilot Git Automation - Intelligent commit grouping and automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes without committing)
  python git_autocommit.py --dry-run

  # Commit changes
  python git_autocommit.py

  # Commit and push
  python git_autocommit.py --push

  # Commit and push to specific remote/branch
  python git_autocommit.py --push --remote origin --branch main

  # Verbose output
  python git_autocommit.py --verbose
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually committing'
    )
    
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push commits after committing'
    )
    
    parser.add_argument(
        '--remote',
        default='origin',
        help='Remote repository name (default: origin)'
    )
    
    parser.add_argument(
        '--branch',
        help='Branch to push to (default: current branch)'
    )
    
    parser.add_argument(
        '--repo-path',
        default='.',
        help='Path to git repository (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = GitAutomation(
        repo_path=args.repo_path,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Run automation
    try:
        success = automation.run(
            push=args.push,
            remote=args.remote,
            branch=args.branch
        )
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
