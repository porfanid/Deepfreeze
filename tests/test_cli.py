"""Tests for Deep Freeze CLI."""

from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil
import os
import stat

from deepfreeze.cli import cli


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files.

    This function is called when shutil.rmtree encounters a permission error.
    It attempts to change the file permissions and retry the operation.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up test fixtures."""
        # Longer delay for CLI tests since managers are created internally
        # and we can't close them directly
        import time
        import gc

        # Force garbage collection to close file handles
        gc.collect()
        time.sleep(0.2)
        shutil.rmtree(self.temp_dir, onerror=remove_readonly)

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

    def test_restore_command_with_default_flag(self):
        """Test restore command with --default flag."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Create snapshot
        self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "snapshot", "create", "test_snap"]
        )

        # Set as default
        self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "set-default", "test_snap"]
        )

        # Restore
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "restore", "--default"]
        )

        assert result.exit_code == 0
        assert "restored successfully" in result.output.lower()

    def test_restore_command_by_name(self):
        """Test restore command by snapshot name."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Create snapshot
        self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "snapshot", "create", "restore_by_name"]
        )

        # Restore by name
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "restore", "restore_by_name"]
        )

        assert result.exit_code == 0
        assert "restored successfully" in result.output.lower()

    def test_restore_command_no_default(self):
        """Test restore command without default snapshot set."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Try to restore without setting default
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "restore", "--default"]
        )

        assert result.exit_code != 0
        assert "no default snapshot" in result.output.lower()

    def test_restore_command_missing_args(self):
        """Test restore command without snapshot ID or --default flag."""
        # Initialize
        self.runner.invoke(cli, ["--base-path", str(self.base_path), "init"])

        # Try to restore without arguments
        result = self.runner.invoke(
            cli, ["--base-path", str(self.base_path), "restore"]
        )

        assert result.exit_code != 0
        assert "specify a snapshot" in result.output.lower()
