"""Filesystem operations for Deep Freeze.

This module provides platform-specific filesystem operations including
OverlayFS mounting (Linux), junction/symlink redirection (Windows),
and efficient snapshot creation using hardlinks.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List
import shutil
import logging

logger = logging.getLogger(__name__)


class FilesystemManager:
    """Manages platform-specific filesystem operations."""

    def __init__(self):
        """Initialize filesystem manager with platform detection."""
        self.platform = platform.system()
        self.is_linux = self.platform == "Linux"
        self.is_windows = self.platform == "Windows"
        self.is_macos = self.platform == "Darwin"

    def supports_overlayfs(self) -> bool:
        """Check if OverlayFS is supported.

        Returns:
            True if OverlayFS is available
        """
        if not self.is_linux:
            return False

        # Check if overlayfs module is available
        try:
            result = subprocess.run(
                ["modprobe", "-n", "-q", "overlay"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def mount_overlay(
        self,
        lower_dir: Path,
        upper_dir: Path,
        work_dir: Path,
        mount_point: Path,
    ) -> bool:
        """Mount an OverlayFS.

        Args:
            lower_dir: Read-only base layer (snapshot)
            upper_dir: Writable upper layer
            work_dir: Work directory for overlay
            mount_point: Where to mount the overlay

        Returns:
            True if mount successful
        """
        if not self.supports_overlayfs():
            logger.warning("OverlayFS not supported on this system")
            return False

        # Ensure directories exist
        lower_dir.mkdir(parents=True, exist_ok=True)
        upper_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        mount_point.mkdir(parents=True, exist_ok=True)

        # Build overlay mount command
        options = (
            f"lowerdir={lower_dir},"
            f"upperdir={upper_dir},"
            f"workdir={work_dir}"
        )

        try:
            subprocess.run(
                [
                    "mount",
                    "-t",
                    "overlay",
                    "overlay",
                    "-o",
                    options,
                    str(mount_point),
                ],
                check=True,
                capture_output=True,
            )
            logger.info(f"Mounted overlay at {mount_point}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount overlay: {e.stderr.decode()}")
            return False
        except FileNotFoundError:
            logger.error("mount command not found")
            return False

    def unmount_overlay(self, mount_point: Path) -> bool:
        """Unmount an OverlayFS.

        Args:
            mount_point: Path to unmount

        Returns:
            True if unmount successful
        """
        if not mount_point.exists():
            return True

        try:
            subprocess.run(
                ["umount", str(mount_point)],
                check=True,
                capture_output=True,
            )
            logger.info(f"Unmounted overlay at {mount_point}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount overlay: {e.stderr.decode()}")
            return False
        except FileNotFoundError:
            logger.error("umount command not found")
            return False

    def is_mount_point(self, path: Path) -> bool:
        """Check if path is a mount point.

        Args:
            path: Path to check

        Returns:
            True if path is a mount point
        """
        if not path.exists():
            return False

        if self.is_linux:
            try:
                result = subprocess.run(
                    ["mountpoint", "-q", str(path)],
                    check=False,
                )
                return result.returncode == 0
            except FileNotFoundError:
                # Fallback to checking if parent differs
                return os.stat(str(path)).st_dev != os.stat(
                    str(path.parent)
                ).st_dev

        return False

    def create_junction(self, source: Path, target: Path) -> bool:
        """Create a junction (Windows) or symlink (Unix).

        Args:
            source: Source path
            target: Target path (will be created)

        Returns:
            True if junction/symlink created
        """
        if not source.exists():
            logger.error(f"Source path does not exist: {source}")
            return False

        if target.exists():
            logger.warning(f"Target already exists: {target}")
            return False

        try:
            if self.is_windows:
                # Use mklink /J for junction on Windows
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(target), str(source)],
                    check=True,
                    capture_output=True,
                )
            else:
                # Use symlink on Unix-like systems
                target.symlink_to(source, target_is_directory=source.is_dir())

            logger.info(f"Created junction/symlink: {target} -> {source}")
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error(f"Failed to create junction/symlink: {e}")
            return False

    def remove_junction(self, path: Path) -> bool:
        """Remove a junction or symlink.

        Args:
            path: Junction/symlink path to remove

        Returns:
            True if removed successfully
        """
        if not path.exists():
            return True

        try:
            if self.is_windows and path.is_dir():
                # Use rmdir for junctions on Windows
                subprocess.run(
                    ["cmd", "/c", "rmdir", str(path)],
                    check=True,
                    capture_output=True,
                )
            else:
                path.unlink()

            logger.info(f"Removed junction/symlink: {path}")
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error(f"Failed to remove junction/symlink: {e}")
            return False

    def copy_with_hardlinks(
        self, source: Path, target: Path, skip_git: bool = True
    ) -> int:
        """Copy directory tree using hardlinks for files.

        Args:
            source: Source directory
            target: Target directory
            skip_git: Skip .git directories

        Returns:
            Number of files linked
        """
        if not source.exists():
            logger.error(f"Source does not exist: {source}")
            return 0

        target.mkdir(parents=True, exist_ok=True)
        files_linked = 0

        for root, dirs, files in os.walk(source):
            # Skip .git directories if requested
            if skip_git and ".git" in dirs:
                dirs.remove(".git")

            root_path = Path(root)
            relative = root_path.relative_to(source)
            target_root = target / relative

            # Create directories
            target_root.mkdir(parents=True, exist_ok=True)

            # Hardlink files
            for filename in files:
                source_file = root_path / filename
                target_file = target_root / filename

                try:
                    # Try hardlink first
                    if source_file.is_file():
                        os.link(source_file, target_file)
                        files_linked += 1
                except (OSError, PermissionError):
                    # Fall back to copy if hardlink fails
                    shutil.copy2(source_file, target_file)

        logger.info(f"Linked {files_linked} files from {source} to {target}")
        return files_linked

    def get_disk_usage(self, path: Path) -> tuple[int, int, int]:
        """Get disk usage statistics.

        Args:
            path: Path to check

        Returns:
            Tuple of (total, used, free) in bytes
        """
        if not path.exists():
            return (0, 0, 0)

        stat = shutil.disk_usage(path)
        return (stat.total, stat.used, stat.free)

    def is_same_filesystem(self, path1: Path, path2: Path) -> bool:
        """Check if two paths are on the same filesystem.

        Args:
            path1: First path
            path2: Second path

        Returns:
            True if on same filesystem
        """
        if not path1.exists() or not path2.exists():
            return False

        return os.stat(str(path1)).st_dev == os.stat(str(path2)).st_dev
