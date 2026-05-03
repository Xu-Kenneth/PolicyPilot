#!/usr/bin/env python3
"""
PolicyPilot Git Automation Script
Production-ready script for intelligent commit management with safety validation.

Features:
- Automatic change detection
- Smart commit grouping by module/feature
- Auto-generated semantic commit messages
- Secret scanning validation
- Dry-run mode for safe testing
- GitHub push automation

Usage:
    python git_automation.py --dry-run          # Preview changes without committing
    python git_automation.py                    # Execute commits and push
    python git_automation.py --no-push          # Commit but don't push
    python git_automation.py --help             # Show help
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum


class CommitType(Enum):
    """Conventional commit types."""
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    TEST = "test"
    REFACTOR = "refactor"
    STYLE = "style"
    CHORE = "chore"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"
    REVERT = "revert"


class ModuleScope(Enum):
    """PolicyPilot module scopes."""
    SECURITY = "security"
    README = "readme"
    PROMPTS = "prompts"
    SCORING = "scoring"
    REPORTING = "reporting"
    API = "api"
    CONFIG = "config"
    TESTS = "tests"
    DOCS = "docs"
    CI = "ci"
    CORE = "core"


@dataclass
class FileChange:
    """Represents a file change."""
    path: Path
    status: str  # 'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed)
    additions: int = 0
    deletions: int = 0


@dataclass
class CommitGroup:
    """Represents a group of related changes for a single commit."""
    commit_type: CommitType
    scope: ModuleScope
    files: List[FileChange] = field(default_factory=list)
    subject: str = ""
    body: List[str] = field(default_factory=list)
    
    @property
    def total_changes(self) -> int:
        """Total lines changed."""
        return sum(f.additions + f.deletions for f in self.files)
    
    @property
    def file_count(self) -> int:
        """Number of files in group."""
        return len(self.files)


class GitAutomation:
    """Main Git automation class."""
    
    # File patterns to skip
    SKIP_PATTERNS = {
        '__pycache__', '.pyc', '.pyo', '.pytest_cache',
        'node_modules', 'venv', '.venv', 'env',
        '.git', '.DS_Store', 'Thumbs.db',
        '.coverage', 'htmlcov', '.mypy_cache',
        'dist', 'build', '*.egg-info'
    }
    
    # Blocked file patterns (secrets/sensitive)
    BLOCKED_PATTERNS = {
        '.env', '.env.local', '.env.production',
        '.pem', '.key', '.p12', '.pfx',
        'id_rsa', 'id_dsa', '*.crt', '*.cer'
    }
    
    # Module mapping patterns
    MODULE_PATTERNS = {
        ModuleScope.SECURITY: [r'secret_scanner\.py'],
        ModuleScope.README: [r'readme_validator\.py'],
        ModuleScope.PROMPTS: [r'prompt_checker\.py'],
        ModuleScope.SCORING: [r'scoring_engine\.py'],
        ModuleScope.REPORTING: [r'report_generator\.py'],
        ModuleScope.API: [r'main\.py', r'models\.py', r'file_handler\.py'],
        ModuleScope.CONFIG: [r'config\.py', r'\.env\.example', r'settings'],
        ModuleScope.TESTS: [r'^test_', r'_test\.py'],
        ModuleScope.DOCS: [r'\.md$', r'\.rst$', r'\.txt$'],
        ModuleScope.CI: [r'\.github/workflows/', r'\.gitlab-ci'],
    }
    
    def __init__(self, repo_path: Path = Path.cwd(), dry_run: bool = False):
        """
        Initialize Git automation.
        
        Args:
            repo_path: Path to git repository
            dry_run: If True, preview changes without executing
        """
        self.repo_path = repo_path
        self.dry_run = dry_run
        self.changes: List[FileChange] = []
        self.commit_groups: List[CommitGroup] = []
        
    def run(self, push: bool = True) -> bool:
        """
        Run the complete automation workflow.
        
        Args:
            push: Whether to push to remote after committing
            
        Returns:
            True if successful, False otherwise
        """
        print("🚀 PolicyPilot Git Automation")
        print("=" * 60)
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made")
            print()
        
        # Step 1: Detect changes
        print("📊 Step 1: Detecting changes...")
        if not self.detect_changes():
            print("✅ No changes detected")
            return True
        
        print(f"   Found {len(self.changes)} changed files")
        print()
        
        # Step 2: Validate safety
        print("🔒 Step 2: Running safety validation...")
        if not self.validate_safety():
            print("❌ Safety validation failed")
            return False
        print("   ✅ All safety checks passed")
        print()
        
        # Step 3: Group changes
        print("📦 Step 3: Grouping changes into commits...")
        self.group_changes()
        print(f"   Created {len(self.commit_groups)} commit groups")
        print()
        
        # Step 4: Generate commit messages
        print("✍️  Step 4: Generating commit messages...")
        self.generate_messages()
        print()
        
        # Step 5: Preview commits
        print("👀 Step 5: Preview commits")
        print("-" * 60)
        self.preview_commits()
        print()
        
        if self.dry_run:
            print("✅ Dry run complete - no changes made")
            return True
        
        # Step 6: Confirm execution
        if not self.confirm_execution():
            print("❌ Execution cancelled by user")
            return False
        
        # Step 7: Execute commits
        print("\n💾 Step 6: Executing commits...")
        if not self.execute_commits():
            print("❌ Commit execution failed")
            return False
        print("   ✅ All commits created successfully")
        print()
        
        # Step 8: Push to remote
        if push:
            print("📤 Step 7: Pushing to GitHub...")
            if not self.push_to_remote():
                print("⚠️  Push failed - commits are local only")
                return False
            print("   ✅ Successfully pushed to remote")
        else:
            print("⏭️  Skipping push (--no-push flag)")
        
        print()
        print("=" * 60)
        print("✅ Git automation complete!")
        return True
    
    def detect_changes(self) -> bool:
        """
        Detect changed files using git status.
        
        Returns:
            True if changes found, False otherwise
        """
        try:
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                return False
            
            # Parse git status output
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                status = line[0:2].strip()
                filepath = line[3:].strip()
                
                # Skip if matches skip patterns
                if self.should_skip_file(filepath):
                    continue
                
                # Get file stats
                additions, deletions = self.get_file_stats(filepath, status)
                
                self.changes.append(FileChange(
                    path=Path(filepath),
                    status=status,
                    additions=additions,
                    deletions=deletions
                ))
            
            return len(self.changes) > 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error detecting changes: {e}")
            return False
    
    def should_skip_file(self, filepath: str) -> bool:
        """Check if file should be skipped."""
        path = Path(filepath)
        
        # Check skip patterns
        for pattern in self.SKIP_PATTERNS:
            if pattern in str(path):
                return True
        
        return False
    
    def get_file_stats(self, filepath: str, status: str) -> Tuple[int, int]:
        """
        Get additions and deletions for a file.
        
        Returns:
            Tuple of (additions, deletions)
        """
        if status == 'D':
            return (0, 0)  # Deleted file
        
        if status == 'A' or status == '??':
            # New file - count all lines as additions
            try:
                path = self.repo_path / filepath
                if path.exists() and path.is_file():
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    return (lines, 0)
            except Exception:
                pass
            return (0, 0)
        
        # Modified file - get diff stats
        try:
            result = subprocess.run(
                ['git', 'diff', '--numstat', 'HEAD', filepath],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2:
                    additions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    return (additions, deletions)
        except Exception:
            pass
        
        return (0, 0)
    
    def validate_safety(self) -> bool:
        """
        Run safety validation checks.
        
        Returns:
            True if all checks pass, False otherwise
        """
        # Check 1: Blocked file patterns
        for change in self.changes:
            filepath = str(change.path)
            for pattern in self.BLOCKED_PATTERNS:
                if pattern in filepath or filepath.endswith(pattern.replace('*', '')):
                    print(f"   ❌ Blocked file detected: {filepath}")
                    print(f"      This file type should not be committed")
                    return False
        
        # Check 2: Secret scanning (if secret_scanner is available)
        try:
            from backend.app.services.secret_scanner import secret_scanner
            
            secrets_found = []
            for change in self.changes:
                if change.status == 'D':
                    continue  # Skip deleted files
                
                filepath = self.repo_path / change.path
                if filepath.exists() and filepath.is_file():
                    secrets = secret_scanner.scan_file(filepath)
                    
                    # Filter high-confidence secrets
                    high_conf_secrets = [s for s in secrets if s.confidence >= 0.8]
                    if high_conf_secrets:
                        secrets_found.extend(high_conf_secrets)
            
            if secrets_found:
                print(f"   ❌ Found {len(secrets_found)} high-confidence secrets:")
                for secret in secrets_found[:5]:  # Show first 5
                    print(f"      - {secret.pattern_name} in {secret.file_path}:{secret.line_number}")
                    print(f"        Confidence: {secret.confidence:.0%}")
                if len(secrets_found) > 5:
                    print(f"      ... and {len(secrets_found) - 5} more")
                print()
                print("   Please remove secrets before committing.")
                print("   Use environment variables or .env files (add to .gitignore)")
                return False
                
        except ImportError:
            print("   ⚠️  Secret scanner not available - skipping secret detection")
        except Exception as e:
            print(f"   ⚠️  Secret scanning error: {e}")
        
        # Check 3: Commit size limits
        total_files = len(self.changes)
        total_additions = sum(c.additions for c in self.changes)
        
        if total_files > 50:
            print(f"   ⚠️  Warning: {total_files} files changed (consider splitting)")
        
        if total_additions > 2000:
            print(f"   ⚠️  Warning: {total_additions} lines added (consider splitting)")
        
        return True
    
    def group_changes(self):
        """Group changes into logical commits."""
        # Group by module
        module_groups: Dict[ModuleScope, List[FileChange]] = {}
        
        for change in self.changes:
            module = self.detect_module(change.path)
            if module not in module_groups:
                module_groups[module] = []
            module_groups[module].append(change)
        
        # Create commit groups
        for module, files in module_groups.items():
            # Determine commit type
            commit_type = self.detect_commit_type(files)
            
            # Split large groups if needed
            if len(files) > 20:
                # Split by file type
                for chunk in self.chunk_files(files, 15):
                    group = CommitGroup(
                        commit_type=commit_type,
                        scope=module,
                        files=chunk
                    )
                    self.commit_groups.append(group)
            else:
                group = CommitGroup(
                    commit_type=commit_type,
                    scope=module,
                    files=files
                )
                self.commit_groups.append(group)
    
    def detect_module(self, filepath: Path) -> ModuleScope:
        """Detect module scope from filepath."""
        filepath_str = str(filepath)
        
        for module, patterns in self.MODULE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, filepath_str):
                    return module
        
        return ModuleScope.CORE
    
    def detect_commit_type(self, files: List[FileChange]) -> CommitType:
        """Detect commit type from files."""
        # All docs → docs
        if all(str(f.path).endswith(('.md', '.rst', '.txt')) for f in files):
            return CommitType.DOCS
        
        # All tests → test
        if all('test' in str(f.path).lower() for f in files):
            return CommitType.TEST
        
        # All config → chore
        if all(any(p in str(f.path) for p in ['config', '.env', 'settings']) for f in files):
            return CommitType.CHORE
        
        # CI files → ci
        if all('.github' in str(f.path) or '.gitlab' in str(f.path) for f in files):
            return CommitType.CI
        
        # New files → feat
        if any(f.status in ('A', '??') for f in files):
            return CommitType.FEAT
        
        # Default to feat for modifications
        return CommitType.FEAT
    
    def chunk_files(self, files: List[FileChange], chunk_size: int) -> List[List[FileChange]]:
        """Split files into chunks."""
        chunks = []
        for i in range(0, len(files), chunk_size):
            chunks.append(files[i:i + chunk_size])
        return chunks
    
    def generate_messages(self):
        """Generate commit messages for all groups."""
        for group in self.commit_groups:
            # Generate subject
            subject = self.generate_subject(group)
            group.subject = subject
            
            # Generate body
            body = self.generate_body(group)
            group.body = body
    
    def generate_subject(self, group: CommitGroup) -> str:
        """Generate commit subject line."""
        # Get action verb based on files
        if any(f.status in ('A', '??') for f in group.files):
            action = "add" if group.commit_type == CommitType.FEAT else "implement"
        elif any(f.status == 'D' for f in group.files):
            action = "remove"
        else:
            action = "update" if group.commit_type == CommitType.FEAT else "fix"
        
        # Get module description
        module_desc = {
            ModuleScope.SECURITY: "secret scanning",
            ModuleScope.README: "README validation",
            ModuleScope.PROMPTS: "prompt documentation",
            ModuleScope.SCORING: "scoring engine",
            ModuleScope.REPORTING: "report generation",
            ModuleScope.API: "API endpoints",
            ModuleScope.CONFIG: "configuration",
            ModuleScope.TESTS: "tests",
            ModuleScope.DOCS: "documentation",
            ModuleScope.CI: "CI/CD pipeline",
            ModuleScope.CORE: "core functionality",
        }.get(group.scope, "module")
        
        return f"{action} {module_desc}"
    
    def generate_body(self, group: CommitGroup) -> List[str]:
        """Generate commit message body."""
        body = []
        
        # Add file list
        if len(group.files) <= 10:
            body.append("Files changed:")
            for file in group.files:
                status_symbol = {
                    'A': '+', '??': '+', 'M': '~', 'D': '-', 'R': '→'
                }.get(file.status, '~')
                body.append(f"- {status_symbol} {file.path}")
        else:
            body.append(f"Modified {len(group.files)} files")
        
        # Add statistics
        total_additions = sum(f.additions for f in group.files)
        total_deletions = sum(f.deletions for f in group.files)
        
        if total_additions > 0 or total_deletions > 0:
            body.append("")
            body.append(f"Changes: +{total_additions}, -{total_deletions}")
        
        return body
    
    def preview_commits(self):
        """Preview all commits that will be created."""
        for i, group in enumerate(self.commit_groups, 1):
            print(f"\nCommit {i}/{len(self.commit_groups)}:")
            print(f"  Type: {group.commit_type.value}({group.scope.value})")
            print(f"  Subject: {group.subject}")
            print(f"  Files: {group.file_count}")
            print(f"  Changes: +{sum(f.additions for f in group.files)}, -{sum(f.deletions for f in group.files)}")
            
            if len(group.files) <= 5:
                print("  Files:")
                for file in group.files:
                    print(f"    - {file.path}")
    
    def confirm_execution(self) -> bool:
        """Ask user to confirm execution."""
        print("\n" + "=" * 60)
        print(f"Ready to create {len(self.commit_groups)} commits")
        print("=" * 60)
        
        response = input("\nProceed with commits? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def execute_commits(self) -> bool:
        """Execute all commits."""
        for i, group in enumerate(self.commit_groups, 1):
            print(f"   Creating commit {i}/{len(self.commit_groups)}...")
            
            # Stage files
            for file in group.files:
                try:
                    subprocess.run(
                        ['git', 'add', str(file.path)],
                        cwd=self.repo_path,
                        check=True,
                        capture_output=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ Failed to stage {file.path}: {e}")
                    return False
            
            # Create commit message
            message = f"{group.commit_type.value}({group.scope.value}): {group.subject}\n\n"
            message += "\n".join(group.body)
            message += "\n\nGenerated-by: PolicyPilot Git Automation"
            
            # Commit
            try:
                subprocess.run(
                    ['git', 'commit', '-m', message],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to create commit: {e}")
                return False
        
        return True
    
    def push_to_remote(self) -> bool:
        """Push commits to remote repository."""
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            
            # Push to remote
            subprocess.run(
                ['git', 'push', 'origin', branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Push failed: {e}")
            print("   Commits are saved locally. You can push manually later.")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PolicyPilot Git Automation - Intelligent commit management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python git_automation.py --dry-run          Preview changes without committing
  python git_automation.py                    Execute commits and push
  python git_automation.py --no-push          Commit but don't push
  python git_automation.py --repo /path/to/repo  Use specific repository
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing (safe mode)'
    )
    
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Create commits but do not push to remote'
    )
    
    parser.add_argument(
        '--repo',
        type=Path,
        default=Path.cwd(),
        help='Path to git repository (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate repository
    if not (args.repo / '.git').exists():
        print(f"❌ Error: {args.repo} is not a git repository")
        sys.exit(1)
    
    # Run automation
    automation = GitAutomation(
        repo_path=args.repo,
        dry_run=args.dry_run
    )
    
    success = automation.run(push=not args.no_push)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

# Made with Bob
