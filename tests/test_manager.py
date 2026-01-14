"""Tests for Deep Freeze manager."""

from pathlib import Path
import tempfile
import shutil
import os
import stat

from deepfreeze.manager import DeepFreezeManager


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files.

    This function is called when shutil.rmtree encounters a permission error.
    It attempts to change the file permissions and retry the operation.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


class TestDeepFreezeManager:
    """Test DeepFreezeManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.manager = None

    def teardown_method(self):
        """Clean up test fixtures."""
        # Close Git managers to release file handles on Windows
        if self.manager is not None and hasattr(self.manager, "close"):
            self.manager.close()
        # Small delay to ensure handles are released on Windows
        import time

        time.sleep(0.1)
        shutil.rmtree(self.temp_dir, onerror=remove_readonly)

    def test_initialization(self):
        """Test Deep Freeze initialization."""
        self.manager = DeepFreezeManager(self.base_path)

        assert self.manager.init()
        assert self.manager.initialized
        assert self.manager.base_path.exists()
        assert (self.manager.base_path / "domains.json").exists()

    def test_is_initialized(self):
        """Test checking if Deep Freeze is initialized."""
        self.manager = DeepFreezeManager(self.base_path)

        assert not self.manager.is_initialized()

        self.manager.init()

        assert self.manager.is_initialized()

    def test_load(self):
        """Test loading existing configuration."""
        # Initialize first
        manager1 = DeepFreezeManager(self.base_path)
        manager1.init()
        manager1.close()

        # Create new manager and load
        self.manager = DeepFreezeManager(self.base_path)
        assert self.manager.load()
        assert self.manager.initialized

    def test_create_snapshot(self):
        """Test creating a snapshot."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Create some test files in domains
        sys_domain = self.manager.domain_manager.get_domain("sys")
        (sys_domain.path / "test.txt").write_text("test content")

        snapshot = self.manager.create_snapshot("test_snapshot", "Test description")

        assert snapshot is not None
        assert snapshot.name == "test_snapshot"
        assert snapshot.description == "Test description"

    def test_list_snapshots(self):
        """Test listing snapshots."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Create snapshots
        self.manager.create_snapshot("snap1")
        self.manager.create_snapshot("snap2")

        snapshots = self.manager.list_snapshots()

        assert len(snapshots) == 2
        snapshot_names = [s.name for s in snapshots]
        assert "snap1" in snapshot_names
        assert "snap2" in snapshot_names

    def test_set_default_snapshot(self):
        """Test setting default snapshot."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        snapshot = self.manager.create_snapshot("default")

        assert self.manager.set_default_snapshot(snapshot.snapshot_id)
        assert self.manager.snapshot_manager.default_snapshot == snapshot.snapshot_id

    def test_get_status(self):
        """Test getting Deep Freeze status."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        status = self.manager.get_status()

        assert status["initialized"] is True
        assert "base_path" in status
        assert "domains" in status
        assert "snapshots" in status
        assert len(status["domains"]) == 4

    def test_commit_config(self):
        """Test committing config changes."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Create a file in cfg domain
        cfg_domain = self.manager.domain_manager.get_domain("cfg")
        (cfg_domain.path / "config.txt").write_text("config content")

        assert self.manager.commit_config("Test config commit")

    def test_thaw_and_freeze(self):
        """Test thawing and freezing system."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        assert not self.manager.is_thawed()

        assert self.manager.thaw()
        assert self.manager.is_thawed()

        assert self.manager.freeze()
        assert not self.manager.is_thawed()

    def test_restore_snapshot(self):
        """Test restoring a snapshot."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Create a snapshot
        snapshot = self.manager.create_snapshot("restore_test", "Test restore")
        self.manager.set_default_snapshot(snapshot.snapshot_id)

        # Modify sys domain
        sys_domain = self.manager.domain_manager.get_domain("sys")
        test_file = sys_domain.path / "test_file.txt"
        test_file.write_text("new content")

        assert test_file.exists()

        # Restore the snapshot
        assert self.manager.restore_snapshot(snapshot.snapshot_id)

        # Verify file was removed
        assert not test_file.exists()

    def test_restore_default_snapshot(self):
        """Test restoring the default snapshot."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Create and set default snapshot
        snapshot = self.manager.create_snapshot("default_restore", "Test default restore")
        self.manager.set_default_snapshot(snapshot.snapshot_id)

        # Modify sys domain
        sys_domain = self.manager.domain_manager.get_domain("sys")
        test_file = sys_domain.path / "default_test.txt"
        test_file.write_text("content to remove")

        assert test_file.exists()

        # Restore using default
        assert self.manager.restore_snapshot(use_default=True)

        # Verify file was removed
        assert not test_file.exists()

    def test_restore_snapshot_not_found(self):
        """Test restoring a non-existent snapshot."""
        self.manager = DeepFreezeManager(self.base_path)
        self.manager.init()

        # Try to restore non-existent snapshot
        assert not self.manager.restore_snapshot("nonexistent")
