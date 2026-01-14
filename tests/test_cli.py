"""Tests for Deep Freeze CLI."""

from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil

from deepfreeze.cli import cli


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_init_command(self):
        """Test freeze init command."""
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        assert result.exit_code == 0
        assert "initialized" in result.output.lower()
        assert (self.base_path / "domains.json").exists()

    def test_init_already_initialized(self):
        """Test init when already initialized."""
        # Initialize first time
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Try to initialize again
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        assert result.exit_code == 0
        assert "already initialized" in result.output.lower()

    def test_status_not_initialized(self):
        """Test status when not initialized."""
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "status"])

        assert result.exit_code == 0
        assert "not initialized" in result.output.lower()

    def test_status_initialized(self):
        """Test status when initialized."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Check status
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "status"])

        assert result.exit_code == 0
        assert "Deep Freeze Status" in result.output
        assert "Domains:" in result.output

    def test_snapshot_create(self):
        """Test creating a snapshot."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Create snapshot
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "snapshot", "create", "test_snap"]
        )

        assert result.exit_code == 0
        assert "Snapshot created" in result.output

    def test_snapshot_list(self):
        """Test listing snapshots."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Create snapshot
        self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "snapshot", "create", "test_snap"]
        )

        # List snapshots
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "snapshot", "list"]
        )

        assert result.exit_code == 0
        assert "test_snap" in result.output

    def test_set_default(self):
        """Test setting default snapshot."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Create snapshot
        self.runner.invoke(
            cli,
            ["--base-path", str(self.base_path), "snapshot", "create", "default_snap"],
        )

        # Set as default
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "set-default", "default_snap"]
        )

        assert result.exit_code == 0
        assert "Default snapshot set" in result.output

    def test_thaw_command(self):
        """Test thaw command."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Thaw
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "thaw"])

        assert result.exit_code == 0
        assert "thawed" in result.output.lower()

    def test_freeze_command(self):
        """Test freeze command."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Thaw first
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "thaw"])

        # Then freeze
        result = self.runner.invoke(cli, ["--base-path", str(self.base_path), "freeze"])

        assert result.exit_code == 0
        assert "frozen" in result.output.lower()

    def test_status_json_output(self):
        """Test status with JSON output."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Get status as JSON
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "status", "--json-output"]
        )

        assert result.exit_code == 0
        # Should be valid JSON
        import json

        data = json.loads(result.output)
        assert data["initialized"] is True
