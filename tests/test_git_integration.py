"""Tests for Git integration."""

from pathlib import Path
import tempfile
import shutil
import os
import stat

from deepfreeze.git_integration import GitManager


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files.

    This function is called when shutil.rmtree encounters a permission error.
    It attempts to change the file permissions and retry the operation.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


class TestGitManager:
    """Test GitManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.domain_path = Path(self.temp_dir) / "test_domain"
        self.domain_path.mkdir(parents=True)
        self.manager = None

    def teardown_method(self):
        """Clean up test fixtures."""
        # Close Git repository to release file handles on Windows
        if self.manager is not None and hasattr(self.manager, "close"):
            self.manager.close()
        # Small delay to ensure handles are released on Windows
        import time

        time.sleep(0.1)
        shutil.rmtree(self.temp_dir, onerror=remove_readonly)

    def test_init_repo(self):
        """Test initializing a Git repository."""
        self.manager = GitManager(self.domain_path)

        assert self.manager.init_repo()
        assert self.manager.is_initialized()
        assert (self.domain_path / ".git").exists()
        assert (self.domain_path / ".gitignore").exists()

    def test_get_status(self):
        """Test getting repository status."""
        self.manager = GitManager(self.domain_path)
        self.manager.init_repo()

        status = self.manager.get_status()

        assert status["initialized"] is True
        assert "branch" in status
        assert status["clean"] is True

    def test_commit_changes(self):
        """Test committing changes."""
        self.manager = GitManager(self.domain_path)
        self.manager.init_repo()

        # Create a file
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")

        # Commit changes
        assert self.manager.commit_changes("Test commit")

        # Check status
        status = self.manager.get_status()
        assert status["clean"] is True

    def test_get_history(self):
        """Test getting commit history."""
        self.manager = GitManager(self.domain_path)
        self.manager.init_repo()

        # Create and commit a file
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")
        self.manager.commit_changes("Test commit")

        history = self.manager.get_history()

        assert len(history) >= 1
        assert "sha" in history[0]
        assert "message" in history[0]
        assert "Test commit" in history[0]["message"]

    def test_create_tag(self):
        """Test creating a Git tag."""
        self.manager = GitManager(self.domain_path)
        self.manager.init_repo()

        # Create a file and commit (tags need at least one commit)
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")
        self.manager.commit_changes("Test commit")

        # Create a tag
        assert self.manager.create_tag("v1.0.0", "Version 1.0.0")

        # Verify tag exists
        assert self.manager.repo is not None
        tags = [tag.name for tag in self.manager.repo.tags]
        assert "v1.0.0" in tags

    def test_status_with_changes(self):
        """Test status when there are uncommitted changes."""
        self.manager = GitManager(self.domain_path)
        self.manager.init_repo()

        # Create a new file
        test_file = self.domain_path / "new_file.txt"
        test_file.write_text("new content")

        status = self.manager.get_status()

        assert status["clean"] is False
        assert len(status["untracked_files"]) > 0
