"""Core Deep Freeze manager.

This module provides the main interface for Deep Freeze operations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import os
import platform

from .domain import DomainManager, DomainType, Domain
from .snapshot import SnapshotManager, Snapshot
from .git_integration import GitManager


class DeepFreezeManager:
    """Main manager for Deep Freeze operations."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize Deep Freeze manager.
        
        Args:
            base_path: Base path for Deep Freeze storage (default: ~/.deepfreeze)
        """
        if base_path is None:
            base_path = Path.home() / ".deepfreeze"
        
        self.base_path = Path(base_path)
        self.domain_manager = DomainManager(self.base_path)
        self.snapshot_manager = SnapshotManager(self.base_path)
        self.git_managers: Dict[str, GitManager] = {}
        self.initialized = False
        
    def init(self) -> bool:
        """Initialize Deep Freeze system.
        
        Returns:
            True if successful
        """
        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize domains
        self.domain_manager.initialize_domains()
        self.domain_manager.save_config()
        
        # Initialize Git for cfg domain
        cfg_domain = self.domain_manager.get_domain("cfg")
        if cfg_domain and cfg_domain.use_git:
            git_manager = GitManager(cfg_domain.path)
            git_manager.init_repo()
            self.git_managers["cfg"] = git_manager
        
        # Load snapshot configuration
        self.snapshot_manager.load_config()
        
        self.initialized = True
        return True
    
    def load(self) -> bool:
        """Load existing Deep Freeze configuration.
        
        Returns:
            True if configuration was loaded
        """
        if not self.base_path.exists():
            return False
        
        # Load domain configuration
        if not self.domain_manager.load_config():
            return False
        
        # Load snapshot configuration
        self.snapshot_manager.load_config()
        
        # Initialize Git managers for domains that use Git
        for domain in self.domain_manager.domains.values():
            if domain.use_git:
                git_manager = GitManager(domain.path)
                if git_manager.is_initialized():
                    self.git_managers[domain.name] = git_manager
        
        self.initialized = True
        return True
    
    def is_initialized(self) -> bool:
        """Check if Deep Freeze is initialized.
        
        Returns:
            True if initialized
        """
        return (self.base_path / "domains.json").exists()
    
    def create_snapshot(self, name: str, description: str = "") -> Optional[Snapshot]:
        """Create a new snapshot.
        
        Args:
            name: Snapshot name
            description: Optional description
            
        Returns:
            Created snapshot or None if failed
        """
        if not self.initialized:
            return None
        
        # Get paths of domains to snapshot (frozen domains only)
        domain_paths = {}
        for domain in self.domain_manager.domains.values():
            if domain.use_overlay:  # Frozen domains
                domain_paths[domain.name] = domain.path
        
        # Create snapshot
        snapshot = self.snapshot_manager.create_snapshot(
            name=name,
            domain_paths=domain_paths,
            description=description
        )
        
        # Commit cfg domain to Git if it uses Git
        if "cfg" in self.git_managers:
            self.git_managers["cfg"].commit_changes(
                f"Snapshot: {name}",
                add_all=True
            )
        
        return snapshot
    
    def list_snapshots(self) -> List[Snapshot]:
        """List all snapshots.
        
        Returns:
            List of snapshots
        """
        return self.snapshot_manager.list_snapshots()
    
    def set_default_snapshot(self, snapshot_id: str) -> bool:
        """Set the default snapshot.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            True if successful
        """
        return self.snapshot_manager.set_default_snapshot(snapshot_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Deep Freeze status.
        
        Returns:
            Status information
        """
        status = {
            "initialized": self.initialized,
            "base_path": str(self.base_path),
            "platform": platform.system(),
            "domains": {},
            "snapshots": {
                "total": len(self.snapshot_manager.snapshots),
                "default": self.snapshot_manager.default_snapshot
            },
            "git_status": {}
        }
        
        if not self.initialized:
            return status
        
        # Domain status
        for name, domain in self.domain_manager.domains.items():
            status["domains"][name] = {
                "type": domain.domain_type.value,
                "path": str(domain.path),
                "reset_policy": domain.reset_policy.value,
                "use_git": domain.use_git,
                "use_overlay": domain.use_overlay,
                "exists": domain.path.exists()
            }
        
        # Git status for domains with Git
        for name, git_manager in self.git_managers.items():
            status["git_status"][name] = git_manager.get_status()
        
        # List recent snapshots
        snapshots = self.snapshot_manager.list_snapshots()
        status["snapshots"]["recent"] = [
            {
                "id": s.snapshot_id,
                "name": s.name,
                "created_at": s.created_at,
                "description": s.description
            }
            for s in sorted(snapshots, key=lambda x: x.created_at, reverse=True)[:5]
        ]
        
        return status
    
    def commit_config(self, message: str) -> bool:
        """Commit configuration changes to Git.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        if "cfg" not in self.git_managers:
            return False
        
        return self.git_managers["cfg"].commit_changes(message, add_all=True)
    
    def thaw(self) -> bool:
        """Temporarily disable freezing.
        
        This is a placeholder for the MVP. In a full implementation,
        this would modify boot configurations to disable overlay mounts.
        
        Returns:
            True if successful
        """
        # For MVP, we just mark a flag file
        thaw_file = self.base_path / ".thawed"
        thaw_file.touch()
        return True
    
    def freeze(self) -> bool:
        """Re-enable freezing after thaw.
        
        Returns:
            True if successful
        """
        thaw_file = self.base_path / ".thawed"
        if thaw_file.exists():
            thaw_file.unlink()
        return True
    
    def is_thawed(self) -> bool:
        """Check if system is currently thawed.
        
        Returns:
            True if thawed
        """
        return (self.base_path / ".thawed").exists()
