"""Tests for domain management."""

from pathlib import Path
import tempfile
import shutil

from deepfreeze.domain import Domain, DomainType, ResetPolicy, DomainManager


class TestDomain:
    """Test Domain class."""

    def test_domain_creation(self):
        """Test creating a domain."""
        domain = Domain(
            name="test",
            domain_type=DomainType.SYS,
            path=Path("/test/path"),
            reset_policy=ResetPolicy.DISCARD,
            use_git=False,
            use_overlay=True,
        )

        assert domain.name == "test"
        assert domain.domain_type == DomainType.SYS
        assert domain.reset_policy == ResetPolicy.DISCARD
        assert not domain.use_git
        assert domain.use_overlay

    def test_domain_to_dict(self):
        """Test converting domain to dictionary."""
        domain = Domain(
            name="test",
            domain_type=DomainType.CFG,
            path=Path("/test/path"),
            reset_policy=ResetPolicy.OPTIONAL_COMMIT,
            use_git=True,
            use_overlay=True,
        )

        data = domain.to_dict()

        assert data["name"] == "test"
        assert data["domain_type"] == "cfg"
        assert data["reset_policy"] == "optional"
        assert data["use_git"] is True

    def test_domain_from_dict(self):
        """Test creating domain from dictionary."""
        data = {
            "name": "test",
            "domain_type": "user",
            "path": "/test/path",
            "reset_policy": "persistent",
            "use_git": False,
            "use_overlay": False,
        }

        domain = Domain.from_dict(data)

        assert domain.name == "test"
        assert domain.domain_type == DomainType.USER
        assert domain.reset_policy == ResetPolicy.PERSISTENT


class TestDomainManager:
    """Test DomainManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test domain manager initialization."""
        manager = DomainManager(self.base_path)
        manager.initialize_domains()

        assert len(manager.domains) == 4
        assert "sys" in manager.domains
        assert "cfg" in manager.domains
        assert "user" in manager.domains
        assert "cache" in manager.domains

    def test_save_and_load_config(self):
        """Test saving and loading domain configuration."""
        manager = DomainManager(self.base_path)
        manager.initialize_domains()
        manager.save_config()

        # Create new manager and load config
        manager2 = DomainManager(self.base_path)
        assert manager2.load_config()

        assert len(manager2.domains) == 4
        assert "sys" in manager2.domains

        # Verify domain properties
        sys_domain = manager2.get_domain("sys")
        assert sys_domain is not None
        assert sys_domain.domain_type == DomainType.SYS
        assert sys_domain.reset_policy == ResetPolicy.DISCARD

    def test_get_domain(self):
        """Test getting a domain by name."""
        manager = DomainManager(self.base_path)
        manager.initialize_domains()

        domain = manager.get_domain("cfg")
        assert domain is not None
        assert domain.name == "cfg"
        assert domain.use_git is True

        # Test non-existent domain
        assert manager.get_domain("nonexistent") is None
