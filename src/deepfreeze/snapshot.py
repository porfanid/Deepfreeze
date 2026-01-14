"""Snapshot management for Deep Freeze.

This module handles creating, managing, and restoring snapshots of frozen domains.
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import os


class Snapshot:
    """Represents a snapshot of system state."""
    
    def __init__(
        self,
        name: str,
        snapshot_id: str,
        created_at: str,
        domains: Dict[str, str],
        description: str = ""
    ):
        """Initialize a snapshot.
        
        Args:
            name: Snapshot name
            snapshot_id: Unique snapshot identifier
            created_at: ISO format timestamp
            domains: Map of domain name to hash/reference
            description: Optional description
        """
        self.name = name
        self.snapshot_id = snapshot_id
        self.created_at = created_at
        self.domains = domains
        self.description = description
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "domains": self.domains,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        """Create snapshot from dictionary."""
        return cls(
            name=data["name"],
            snapshot_id=data["snapshot_id"],
            created_at=data["created_at"],
            domains=data["domains"],
            description=data.get("description", "")
        )


class SnapshotManager:
    """Manages snapshots of frozen domains."""
    
    def __init__(self, base_path: Path):
        """Initialize snapshot manager.
        
        Args:
            base_path: Base path for Deep Freeze storage
        """
        self.base_path = Path(base_path)
        self.snapshots_path = self.base_path / "snapshots"
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        self.config_file = self.base_path / "snapshots.json"
        self.snapshots: Dict[str, Snapshot] = {}
        self.default_snapshot: Optional[str] = None
        
    def create_snapshot(
        self,
        name: str,
        domain_paths: Dict[str, Path],
        description: str = ""
    ) -> Snapshot:
        """Create a new snapshot of specified domains.
        
        Args:
            name: Snapshot name
            domain_paths: Map of domain name to path
            description: Optional description
            
        Returns:
            Created snapshot
        """
        # Generate snapshot ID
        timestamp = datetime.now().isoformat()
        snapshot_id = hashlib.sha256(f"{name}{timestamp}".encode()).hexdigest()[:16]
        
        # Create snapshot directory
        snapshot_dir = self.snapshots_path / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy domain contents and calculate hashes
        domain_hashes = {}
        for domain_name, domain_path in domain_paths.items():
            if domain_path.exists():
                # Create domain snapshot directory
                domain_snapshot_dir = snapshot_dir / domain_name
                domain_snapshot_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy contents (for MVP, we copy files; production would use more efficient methods)
                if domain_path.is_dir():
                    for item in domain_path.iterdir():
                        if item.is_file():
                            shutil.copy2(item, domain_snapshot_dir / item.name)
                        elif item.is_dir():
                            shutil.copytree(item, domain_snapshot_dir / item.name, dirs_exist_ok=True)
                
                # Calculate hash
                domain_hash = self._calculate_directory_hash(domain_path)
                domain_hashes[domain_name] = domain_hash
        
        # Create snapshot object
        snapshot = Snapshot(
            name=name,
            snapshot_id=snapshot_id,
            created_at=timestamp,
            domains=domain_hashes,
            description=description
        )
        
        self.snapshots[snapshot_id] = snapshot
        self.save_config()
        
        return snapshot
    
    def _calculate_directory_hash(self, path: Path) -> str:
        """Calculate hash of directory contents.
        
        Args:
            path: Directory path
            
        Returns:
            SHA256 hash of contents
        """
        hasher = hashlib.sha256()
        
        if not path.exists():
            return hasher.hexdigest()
        
        # Sort files for consistent hashing
        for root, dirs, files in os.walk(path):
            dirs.sort()
            for filename in sorted(files):
                filepath = Path(root) / filename
                try:
                    hasher.update(filepath.name.encode())
                    with open(filepath, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b''):
                            hasher.update(chunk)
                except (IOError, OSError):
                    # Skip files we can't read
                    pass
        
        return hasher.hexdigest()
    
    def list_snapshots(self) -> List[Snapshot]:
        """List all snapshots.
        
        Returns:
            List of snapshots
        """
        return list(self.snapshots.values())
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get a snapshot by ID.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Snapshot if found, None otherwise
        """
        return self.snapshots.get(snapshot_id)
    
    def get_snapshot_by_name(self, name: str) -> Optional[Snapshot]:
        """Get a snapshot by name.
        
        Args:
            name: Snapshot name
            
        Returns:
            Snapshot if found, None otherwise
        """
        for snapshot in self.snapshots.values():
            if snapshot.name == name:
                return snapshot
        return None
    
    def set_default_snapshot(self, snapshot_id: str) -> bool:
        """Set the default snapshot to boot.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            True if successful, False if snapshot not found
        """
        if snapshot_id not in self.snapshots:
            return False
        
        self.default_snapshot = snapshot_id
        self.save_config()
        return True
    
    def restore_snapshot(self, snapshot_id: str, target_paths: Dict[str, Path]) -> bool:
        """Restore a snapshot to specified paths.
        
        Args:
            snapshot_id: Snapshot ID
            target_paths: Map of domain name to target path
            
        Returns:
            True if successful
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return False
        
        snapshot_dir = self.snapshots_path / snapshot_id
        if not snapshot_dir.exists():
            return False
        
        # Restore each domain
        for domain_name in snapshot.domains.keys():
            if domain_name in target_paths:
                source = snapshot_dir / domain_name
                target = target_paths[domain_name]
                
                if source.exists():
                    # Clear target directory
                    if target.exists():
                        shutil.rmtree(target)
                    
                    # Copy snapshot contents
                    shutil.copytree(source, target)
        
        return True
    
    def save_config(self) -> None:
        """Save snapshot configuration to file."""
        config = {
            "snapshots": {
                sid: snapshot.to_dict()
                for sid, snapshot in self.snapshots.items()
            },
            "default_snapshot": self.default_snapshot
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> bool:
        """Load snapshot configuration from file.
        
        Returns:
            True if config was loaded, False if not found
        """
        if not self.config_file.exists():
            return False
        
        with open(self.config_file, "r") as f:
            config = json.load(f)
        
        self.snapshots = {
            sid: Snapshot.from_dict(data)
            for sid, data in config.get("snapshots", {}).items()
        }
        self.default_snapshot = config.get("default_snapshot")
        
        return True
