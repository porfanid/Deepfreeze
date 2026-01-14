"""Domain management for Deep Freeze.

This module provides the core domain abstraction for managing different
storage domains (sys, cfg, user, cache) with different persistence policies.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path
import json


class DomainType(Enum):
    """Types of storage domains."""

    SYS = "sys"  # OS + apps (frozen)
    CFG = "cfg"  # Configs (versioned)
    USER = "user"  # Home directories (persistent)
    CACHE = "cache"  # Temp files (always reset)


class ResetPolicy(Enum):
    """Reset policies for domains."""

    DISCARD = "discard"  # Discard on reboot
    OPTIONAL_COMMIT = "optional"  # Can commit or discard
    PERSISTENT = "persistent"  # Never reset
    ALWAYS_RESET = "always"  # Always reset (tmpfs)


class Domain:
    """Represents a storage domain with its configuration."""

    def __init__(
        self,
        name: str,
        domain_type: DomainType,
        path: Path,
        reset_policy: ResetPolicy,
        use_git: bool = False,
        use_overlay: bool = False,
    ):
        """Initialize a domain.

        Args:
            name: Domain name
            domain_type: Type of domain
            path: Path to domain storage
            reset_policy: How to handle resets
            use_git: Whether to track with Git
            use_overlay: Whether to use overlay filesystem
        """
        self.name = name
        self.domain_type = domain_type
        self.path = Path(path)
        self.reset_policy = reset_policy
        self.use_git = use_git
        self.use_overlay = use_overlay

    def to_dict(self) -> Dict[str, Any]:
        """Convert domain to dictionary representation."""
        return {
            "name": self.name,
            "domain_type": self.domain_type.value,
            "path": str(self.path),
            "reset_policy": self.reset_policy.value,
            "use_git": self.use_git,
            "use_overlay": self.use_overlay,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Domain":
        """Create domain from dictionary representation."""
        return cls(
            name=data["name"],
            domain_type=DomainType(data["domain_type"]),
            path=Path(data["path"]),
            reset_policy=ResetPolicy(data["reset_policy"]),
            use_git=data.get("use_git", False),
            use_overlay=data.get("use_overlay", False),
        )


class DomainManager:
    """Manages all storage domains."""

    DEFAULT_DOMAINS = {
        DomainType.SYS: {
            "reset_policy": ResetPolicy.DISCARD,
            "use_git": False,
            "use_overlay": True,
        },
        DomainType.CFG: {
            "reset_policy": ResetPolicy.OPTIONAL_COMMIT,
            "use_git": True,
            "use_overlay": True,
        },
        DomainType.USER: {
            "reset_policy": ResetPolicy.PERSISTENT,
            "use_git": False,
            "use_overlay": False,
        },
        DomainType.CACHE: {
            "reset_policy": ResetPolicy.ALWAYS_RESET,
            "use_git": False,
            "use_overlay": False,
        },
    }

    def __init__(self, base_path: Path):
        """Initialize domain manager.

        Args:
            base_path: Base path for Deep Freeze storage
        """
        self.base_path = Path(base_path)
        self.domains: Dict[str, Domain] = {}
        self.config_file = self.base_path / "domains.json"

    def initialize_domains(self) -> None:
        """Initialize default domains."""
        for domain_type, config in self.DEFAULT_DOMAINS.items():
            domain_path = self.base_path / "domains" / domain_type.value
            domain = Domain(
                name=domain_type.value,
                domain_type=domain_type,
                path=domain_path,
                **config,
            )
            self.domains[domain_type.value] = domain

            # Create domain directory
            domain_path.mkdir(parents=True, exist_ok=True)

    def save_config(self) -> None:
        """Save domain configuration to file."""
        config = {
            "domains": {name: domain.to_dict() for name, domain in self.domains.items()}
        }
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def load_config(self) -> bool:
        """Load domain configuration from file.

        Returns:
            True if config was loaded, False if not found
        """
        if not self.config_file.exists():
            return False

        with open(self.config_file, "r") as f:
            config = json.load(f)

        self.domains = {
            name: Domain.from_dict(data) for name, data in config["domains"].items()
        }
        return True

    def get_domain(self, name: str) -> Optional[Domain]:
        """Get a domain by name.

        Args:
            name: Domain name

        Returns:
            Domain if found, None otherwise
        """
        return self.domains.get(name)
