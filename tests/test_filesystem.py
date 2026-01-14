"""Tests for filesystem operations."""

from pathlib import Path
import tempfile
import shutil
import os
import stat
import platform

from deepfreeze.filesystem import FilesystemManager


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


class TestFilesystemManager:
    """Test FilesystemManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.fs_manager = FilesystemManager()

    def teardown_method(self):
        """Clean up test fixtures."""
        import time
        import gc

        gc.collect()
        time.sleep(0.1)
        shutil.rmtree(self.temp_dir, onerror=remove_readonly)

    def test_platform_detection(self):
        """Test platform detection."""
        assert self.fs_manager.platform in ["Linux", "Windows", "Darwin"]
        assert (
            self.fs_manager.is_linux
            or self.fs_manager.is_windows
            or self.fs_manager.is_macos
        )

    def test_copy_with_hardlinks(self):
        """Test copying with hardlinks."""
        # Create source directory with files
        source = self.base_path / "source"
        source.mkdir()
        (source / "file1.txt").write_text("content1")
        (source / "file2.txt").write_text("content2")

        # Create subdirectory
        subdir = source / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        # Copy with hardlinks
        target = self.base_path / "target"
        files_linked = self.fs_manager.copy_with_hardlinks(source, target)

        # Verify target exists and has same structure
        assert target.exists()
        assert (target / "file1.txt").exists()
        assert (target / "file2.txt").exists()
        assert (target / "subdir" / "file3.txt").exists()

        # Verify content
        assert (target / "file1.txt").read_text() == "content1"
        assert (target / "subdir" / "file3.txt").read_text() == "content3"

        # On systems that support hardlinks, verify they are hardlinked
        if platform.system() != "Windows":
            source_stat = (source / "file1.txt").stat()
            target_stat = (target / "file1.txt").stat()
            # Check if inodes match (same file)
            assert source_stat.st_ino == target_stat.st_ino
            assert source_stat.st_nlink >= 2  # At least 2 links

    def test_copy_with_hardlinks_skip_git(self):
        """Test hardlink copying skips .git directories."""
        # Create source with .git directory
        source = self.base_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")

        git_dir = source / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        # Copy with skip_git=True (default)
        target = self.base_path / "target"
        self.fs_manager.copy_with_hardlinks(source, target, skip_git=True)

        # Verify file copied but .git skipped
        assert (target / "file.txt").exists()
        assert not (target / ".git").exists()

    def test_is_same_filesystem(self):
        """Test filesystem detection."""
        path1 = self.base_path / "path1"
        path2 = self.base_path / "path2"
        path1.mkdir()
        path2.mkdir()

        # Paths in same temp directory should be on same filesystem
        assert self.fs_manager.is_same_filesystem(path1, path2)

    def test_get_disk_usage(self):
        """Test disk usage calculation."""
        path = self.base_path
        total, used, free = self.fs_manager.get_disk_usage(path)

        # Should return non-zero values
        assert total > 0
        assert used >= 0
        assert free >= 0
        assert total >= used + free  # Allow for filesystem overhead

    def test_get_disk_usage_nonexistent(self):
        """Test disk usage for non-existent path."""
        path = self.base_path / "nonexistent"
        total, used, free = self.fs_manager.get_disk_usage(path)

        # Should return zeros for non-existent path
        assert total == 0
        assert used == 0
        assert free == 0

    def test_supports_overlayfs(self):
        """Test OverlayFS support detection."""
        # Just verify it returns a boolean
        result = self.fs_manager.supports_overlayfs()
        assert isinstance(result, bool)

        # OverlayFS should only be supported on Linux
        if self.fs_manager.is_linux:
            # May or may not be supported depending on system
            pass
        else:
            assert result is False

    def test_create_remove_junction_unix(self):
        """Test junction/symlink creation on Unix-like systems."""
        if self.fs_manager.is_windows:
            # Skip on Windows (requires admin privileges)
            return

        source = self.base_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")

        target = self.base_path / "link"

        # Create symlink
        assert self.fs_manager.create_junction(source, target)
        assert target.exists()
        assert target.is_symlink()

        # Verify link works
        assert (target / "file.txt").read_text() == "content"

        # Remove symlink
        assert self.fs_manager.remove_junction(target)
        assert not target.exists()

    def test_create_junction_source_not_exist(self):
        """Test junction creation with non-existent source."""
        source = self.base_path / "nonexistent"
        target = self.base_path / "link"

        # Should fail
        assert not self.fs_manager.create_junction(source, target)

    def test_remove_junction_not_exist(self):
        """Test removing non-existent junction."""
        path = self.base_path / "nonexistent"

        # Should succeed (no-op)
        assert self.fs_manager.remove_junction(path)


class TestFilesystemManagerOverlay:
    """Test OverlayFS functionality (Linux only)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.fs_manager = FilesystemManager()

    def teardown_method(self):
        """Clean up test fixtures."""
        import time
        import gc

        gc.collect()
        time.sleep(0.1)
        shutil.rmtree(self.temp_dir, onerror=remove_readonly)

    def test_is_mount_point(self):
        """Test mount point detection."""
        # Regular directory should not be a mount point
        path = self.base_path / "notmount"
        path.mkdir()
        assert not self.fs_manager.is_mount_point(path)

        # Root should be a mount point on Unix systems
        if not self.fs_manager.is_windows:
            root = Path("/")
            # Root may or may not be a mount point depending on system
            # Just verify it returns a boolean
            result = self.fs_manager.is_mount_point(root)
            assert isinstance(result, bool)
