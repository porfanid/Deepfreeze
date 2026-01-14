"""Git integration for Deep Freeze.

This module provides Git-based version control for configuration domains.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from git import Repo, GitCommandError


class GitManager:
    """Manages Git repositories for configuration domains."""

    def __init__(self, domain_path: Path):
        """Initialize Git manager.

        Args:
            domain_path: Path to domain directory
        """
        self.domain_path = Path(domain_path)
        self.repo: Optional[Repo] = None

    def init_repo(self) -> bool:
        """Initialize a Git repository.

        Returns:
            True if successful
        """
        try:
            if (self.domain_path / ".git").exists():
                self.repo = Repo(self.domain_path)
                return True

            self.repo = Repo.init(self.domain_path)

            # Configure Git user if not already set
            try:
                config_writer = self.repo.config_writer()
                # Only set if not already configured
                try:
                    self.repo.config_reader().get_value("user", "name")
                except Exception:
                    config_writer.set_value("user", "name", "Deep Freeze")
                try:
                    self.repo.config_reader().get_value("user", "email")
                except Exception:
                    config_writer.set_value("user", "email", "deepfreeze@localhost")
                config_writer.release()
            except Exception:
                pass  # Ignore config errors, use global config

            # Create initial .gitignore
            gitignore_path = self.domain_path / ".gitignore"
            if not gitignore_path.exists():
                with open(gitignore_path, "w") as f:
                    f.write("# Deep Freeze managed repository\n")
                    f.write("*.tmp\n")
                    f.write("*.log\n")

            # Create initial commit
            self.repo.index.add([".gitignore"])
            self.repo.index.commit("Initial commit by Deep Freeze")

            return True
        except Exception:
            return False

    def is_initialized(self) -> bool:
        """Check if Git repository is initialized.

        Returns:
            True if initialized
        """
        return (self.domain_path / ".git").exists()

    def get_status(self) -> Dict[str, Any]:
        """Get repository status.

        Returns:
            Dictionary with status information
        """
        if not self.repo:
            if not self.is_initialized():
                return {"initialized": False}
            self.repo = Repo(self.domain_path)

        try:
            # Get current branch
            current_branch = self.repo.active_branch.name

            # Get changed files
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            untracked_files = self.repo.untracked_files
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]

            # Get recent commits
            commits = []
            try:
                for commit in list(self.repo.iter_commits(max_count=5)):
                    commits.append(
                        {
                            "sha": commit.hexsha[:8],
                            "message": commit.message.strip(),
                            "author": str(commit.author),
                            "date": commit.committed_datetime.isoformat(),
                        }
                    )
            except ValueError:
                # No commits yet
                pass

            return {
                "initialized": True,
                "branch": current_branch,
                "changed_files": changed_files,
                "untracked_files": untracked_files,
                "staged_files": staged_files,
                "commits": commits,
                "clean": len(changed_files) == 0 and len(untracked_files) == 0,
            }
        except Exception as e:
            return {"initialized": True, "error": str(e)}

    def commit_changes(self, message: str, add_all: bool = True) -> bool:
        """Commit changes to repository.

        Args:
            message: Commit message
            add_all: Whether to add all changes

        Returns:
            True if successful
        """
        if not self.repo:
            if not self.is_initialized():
                return False
            self.repo = Repo(self.domain_path)

        try:
            if add_all:
                # Add all changed and new files
                self.repo.git.add(A=True)

            # Check if there's anything to commit
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                return True  # Nothing to commit, but not an error

            self.repo.index.commit(message)
            return True
        except GitCommandError:
            return False

    def get_history(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """Get commit history.

        Args:
            max_count: Maximum number of commits to return

        Returns:
            List of commit information
        """
        if not self.repo:
            if not self.is_initialized():
                return []
            self.repo = Repo(self.domain_path)

        commits = []
        try:
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append(
                    {
                        "sha": commit.hexsha[:8],
                        "full_sha": commit.hexsha,
                        "message": commit.message.strip(),
                        "author": str(commit.author),
                        "date": commit.committed_datetime.isoformat(),
                    }
                )
        except ValueError:
            # No commits yet
            pass

        return commits

    def create_tag(self, tag_name: str, message: str = "") -> bool:
        """Create a Git tag.

        Args:
            tag_name: Name of the tag
            message: Optional tag message (creates annotated tag)

        Returns:
            True if successful
        """
        if not self.repo:
            if not self.is_initialized():
                return False
            self.repo = Repo(self.domain_path)

        try:
            # Use git command directly for annotated tags
            if message:
                self.repo.git.tag("-a", tag_name, "-m", message)
            else:
                self.repo.create_tag(tag_name)
            return True
        except (GitCommandError, Exception):
            return False

    def checkout(self, ref: str) -> bool:
        """Checkout a specific commit or branch.

        Args:
            ref: Commit SHA, branch name, or tag

        Returns:
            True if successful
        """
        if not self.repo:
            if not self.is_initialized():
                return False
            self.repo = Repo(self.domain_path)

        try:
            self.repo.git.checkout(ref)
            return True
        except GitCommandError:
            return False
