"""Tests for Deep Freeze manager."""

import pytest
from pathlib import Path
import tempfile
import shutil

from deepfreeze.manager import DeepFreezeManager


class TestDeepFreezeManager:
    """Test DeepFreezeManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test Deep Freeze initialization."""
        manager = DeepFreezeManager(self.base_path)
        
        assert manager.init()
        assert manager.initialized
        assert manager.base_path.exists()
        assert (manager.base_path / "domains.json").exists()
    
    def test_is_initialized(self):
        """Test checking if Deep Freeze is initialized."""
        manager = DeepFreezeManager(self.base_path)
        
        assert not manager.is_initialized()
        
        manager.init()
        
        assert manager.is_initialized()
    
    def test_load(self):
        """Test loading existing configuration."""
        # Initialize first
        manager1 = DeepFreezeManager(self.base_path)
        manager1.init()
        
        # Create new manager and load
        manager2 = DeepFreezeManager(self.base_path)
        assert manager2.load()
        assert manager2.initialized
    
    def test_create_snapshot(self):
        """Test creating a snapshot."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        # Create some test files in domains
        sys_domain = manager.domain_manager.get_domain("sys")
        (sys_domain.path / "test.txt").write_text("test content")
        
        snapshot = manager.create_snapshot("test_snapshot", "Test description")
        
        assert snapshot is not None
        assert snapshot.name == "test_snapshot"
        assert snapshot.description == "Test description"
    
    def test_list_snapshots(self):
        """Test listing snapshots."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        # Create snapshots
        manager.create_snapshot("snap1")
        manager.create_snapshot("snap2")
        
        snapshots = manager.list_snapshots()
        
        assert len(snapshots) == 2
        snapshot_names = [s.name for s in snapshots]
        assert "snap1" in snapshot_names
        assert "snap2" in snapshot_names
    
    def test_set_default_snapshot(self):
        """Test setting default snapshot."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        snapshot = manager.create_snapshot("default")
        
        assert manager.set_default_snapshot(snapshot.snapshot_id)
        assert manager.snapshot_manager.default_snapshot == snapshot.snapshot_id
    
    def test_get_status(self):
        """Test getting Deep Freeze status."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        status = manager.get_status()
        
        assert status["initialized"] is True
        assert "base_path" in status
        assert "domains" in status
        assert "snapshots" in status
        assert len(status["domains"]) == 4
    
    def test_commit_config(self):
        """Test committing config changes."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        # Create a file in cfg domain
        cfg_domain = manager.domain_manager.get_domain("cfg")
        (cfg_domain.path / "config.txt").write_text("config content")
        
        assert manager.commit_config("Test config commit")
    
    def test_thaw_and_freeze(self):
        """Test thawing and freezing system."""
        manager = DeepFreezeManager(self.base_path)
        manager.init()
        
        assert not manager.is_thawed()
        
        assert manager.thaw()
        assert manager.is_thawed()
        
        assert manager.freeze()
        assert not manager.is_thawed()
