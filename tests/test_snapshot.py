"""Tests for snapshot management."""

import pytest
from pathlib import Path
import tempfile
import shutil

from deepfreeze.snapshot import Snapshot, SnapshotManager


class TestSnapshot:
    """Test Snapshot class."""
    
    def test_snapshot_creation(self):
        """Test creating a snapshot."""
        snapshot = Snapshot(
            name="base",
            snapshot_id="abc123",
            created_at="2024-01-01T00:00:00",
            domains={"sys": "hash1", "cfg": "hash2"},
            description="Base snapshot"
        )
        
        assert snapshot.name == "base"
        assert snapshot.snapshot_id == "abc123"
        assert len(snapshot.domains) == 2
        assert snapshot.description == "Base snapshot"
    
    def test_snapshot_to_dict(self):
        """Test converting snapshot to dictionary."""
        snapshot = Snapshot(
            name="test",
            snapshot_id="xyz789",
            created_at="2024-01-01T00:00:00",
            domains={"sys": "hash1"},
            description="Test"
        )
        
        data = snapshot.to_dict()
        
        assert data["name"] == "test"
        assert data["snapshot_id"] == "xyz789"
        assert "domains" in data
    
    def test_snapshot_from_dict(self):
        """Test creating snapshot from dictionary."""
        data = {
            "name": "test",
            "snapshot_id": "xyz789",
            "created_at": "2024-01-01T00:00:00",
            "domains": {"sys": "hash1"},
            "description": "Test"
        }
        
        snapshot = Snapshot.from_dict(data)
        
        assert snapshot.name == "test"
        assert snapshot.snapshot_id == "xyz789"


class TestSnapshotManager:
    """Test SnapshotManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test snapshot manager initialization."""
        manager = SnapshotManager(self.base_path)
        
        assert manager.base_path == self.base_path
        assert manager.snapshots_path.exists()
    
    def test_create_snapshot(self):
        """Test creating a snapshot."""
        manager = SnapshotManager(self.base_path)
        
        # Create test domain directories
        domain1 = self.base_path / "domain1"
        domain1.mkdir(parents=True)
        (domain1 / "file1.txt").write_text("content1")
        
        domain2 = self.base_path / "domain2"
        domain2.mkdir(parents=True)
        (domain2 / "file2.txt").write_text("content2")
        
        # Create snapshot
        snapshot = manager.create_snapshot(
            name="test_snapshot",
            domain_paths={"domain1": domain1, "domain2": domain2},
            description="Test snapshot"
        )
        
        assert snapshot is not None
        assert snapshot.name == "test_snapshot"
        assert len(snapshot.domains) == 2
        assert "domain1" in snapshot.domains
        assert "domain2" in snapshot.domains
    
    def test_list_snapshots(self):
        """Test listing snapshots."""
        manager = SnapshotManager(self.base_path)
        
        # Create test domain
        domain = self.base_path / "domain"
        domain.mkdir(parents=True)
        (domain / "file.txt").write_text("content")
        
        # Create multiple snapshots
        snapshot1 = manager.create_snapshot("snap1", {"domain": domain})
        snapshot2 = manager.create_snapshot("snap2", {"domain": domain})
        
        snapshots = manager.list_snapshots()
        
        assert len(snapshots) == 2
        snapshot_ids = [s.snapshot_id for s in snapshots]
        assert snapshot1.snapshot_id in snapshot_ids
        assert snapshot2.snapshot_id in snapshot_ids
    
    def test_get_snapshot(self):
        """Test getting a snapshot by ID."""
        manager = SnapshotManager(self.base_path)
        
        domain = self.base_path / "domain"
        domain.mkdir(parents=True)
        
        snapshot = manager.create_snapshot("test", {"domain": domain})
        
        retrieved = manager.get_snapshot(snapshot.snapshot_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id
    
    def test_get_snapshot_by_name(self):
        """Test getting a snapshot by name."""
        manager = SnapshotManager(self.base_path)
        
        domain = self.base_path / "domain"
        domain.mkdir(parents=True)
        
        snapshot = manager.create_snapshot("my_snapshot", {"domain": domain})
        
        retrieved = manager.get_snapshot_by_name("my_snapshot")
        assert retrieved is not None
        assert retrieved.name == "my_snapshot"
    
    def test_set_default_snapshot(self):
        """Test setting default snapshot."""
        manager = SnapshotManager(self.base_path)
        
        domain = self.base_path / "domain"
        domain.mkdir(parents=True)
        
        snapshot = manager.create_snapshot("default", {"domain": domain})
        
        assert manager.set_default_snapshot(snapshot.snapshot_id)
        assert manager.default_snapshot == snapshot.snapshot_id
        
        # Test invalid snapshot
        assert not manager.set_default_snapshot("invalid_id")
    
    def test_save_and_load_config(self):
        """Test saving and loading snapshot configuration."""
        manager = SnapshotManager(self.base_path)
        
        domain = self.base_path / "domain"
        domain.mkdir(parents=True)
        
        snapshot = manager.create_snapshot("test", {"domain": domain})
        manager.set_default_snapshot(snapshot.snapshot_id)
        manager.save_config()
        
        # Create new manager and load config
        manager2 = SnapshotManager(self.base_path)
        assert manager2.load_config()
        
        assert len(manager2.snapshots) == 1
        assert snapshot.snapshot_id in manager2.snapshots
        assert manager2.default_snapshot == snapshot.snapshot_id
