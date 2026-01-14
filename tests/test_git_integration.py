"""Tests for Git integration."""

import pytest
from pathlib import Path
import tempfile
import shutil

from deepfreeze.git_integration import GitManager


class TestGitManager:
    """Test GitManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.domain_path = Path(self.temp_dir) / "test_domain"
        self.domain_path.mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init_repo(self):
        """Test initializing a Git repository."""
        manager = GitManager(self.domain_path)
        
        assert manager.init_repo()
        assert manager.is_initialized()
        assert (self.domain_path / ".git").exists()
        assert (self.domain_path / ".gitignore").exists()
    
    def test_get_status(self):
        """Test getting repository status."""
        manager = GitManager(self.domain_path)
        manager.init_repo()
        
        status = manager.get_status()
        
        assert status["initialized"] is True
        assert "branch" in status
        assert status["clean"] is True
    
    def test_commit_changes(self):
        """Test committing changes."""
        manager = GitManager(self.domain_path)
        manager.init_repo()
        
        # Create a file
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")
        
        # Commit changes
        assert manager.commit_changes("Test commit")
        
        # Check status
        status = manager.get_status()
        assert status["clean"] is True
    
    def test_get_history(self):
        """Test getting commit history."""
        manager = GitManager(self.domain_path)
        manager.init_repo()
        
        # Create and commit a file
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")
        manager.commit_changes("Test commit")
        
        history = manager.get_history()
        
        assert len(history) >= 1
        assert "sha" in history[0]
        assert "message" in history[0]
        assert "Test commit" in history[0]["message"]
    
    def test_create_tag(self):
        """Test creating a Git tag."""
        manager = GitManager(self.domain_path)
        manager.init_repo()
        
        # Create a file and commit (tags need at least one commit)
        test_file = self.domain_path / "test.txt"
        test_file.write_text("test content")
        manager.commit_changes("Test commit")
        
        # Create a tag
        assert manager.create_tag("v1.0.0", "Version 1.0.0")
        
        # Verify tag exists
        assert manager.repo is not None
        tags = [tag.name for tag in manager.repo.tags]
        assert "v1.0.0" in tags
    
    def test_status_with_changes(self):
        """Test status when there are uncommitted changes."""
        manager = GitManager(self.domain_path)
        manager.init_repo()
        
        # Create a new file
        test_file = self.domain_path / "new_file.txt"
        test_file.write_text("new content")
        
        status = manager.get_status()
        
        assert status["clean"] is False
        assert len(status["untracked_files"]) > 0
