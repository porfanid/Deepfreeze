#!/usr/bin/env python3
"""Example usage of Deep Freeze.

This script demonstrates the core functionality of Deep Freeze.
"""

import tempfile
import shutil
from pathlib import Path

from deepfreeze.manager import DeepFreezeManager


def main():
    """Run Deep Freeze example."""
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp(prefix="deepfreeze_example_")
    print(f"Demo directory: {temp_dir}\n")

    try:
        # Initialize Deep Freeze
        print("=" * 60)
        print("1. Initializing Deep Freeze")
        print("=" * 60)
        manager = DeepFreezeManager(Path(temp_dir))
        manager.init()
        print("✓ Deep Freeze initialized\n")

        # Show initial status
        print("=" * 60)
        print("2. Initial Status")
        print("=" * 60)
        status = manager.get_status()
        print(f"Base path: {status['base_path']}")
        print(f"Domains: {len(status['domains'])}")
        for name, info in status["domains"].items():
            print(f"  - {name}: {info['reset_policy']}")
        print()

        # Create some test files in domains
        print("=" * 60)
        print("3. Creating Test Files")
        print("=" * 60)
        sys_domain = manager.domain_manager.get_domain("sys")
        cfg_domain = manager.domain_manager.get_domain("cfg")

        (sys_domain.path / "app.txt").write_text("System application file")
        (cfg_domain.path / "config.yaml").write_text("setting: value")
        print("✓ Created test files in sys and cfg domains\n")

        # Create a snapshot
        print("=" * 60)
        print("4. Creating Snapshot")
        print("=" * 60)
        snapshot = manager.create_snapshot(
            "base", description="Clean system with test files"
        )
        print(f"✓ Snapshot created: {snapshot.name} ({snapshot.snapshot_id})")
        print(f"  Domains: {', '.join(snapshot.domains.keys())}\n")

        # Create another snapshot
        print("=" * 60)
        print("5. Creating Another Snapshot")
        print("=" * 60)
        (cfg_domain.path / "config2.yaml").write_text("another: setting")
        snapshot2 = manager.create_snapshot(
            "modified", description="System with additional config"
        )
        print(f"✓ Snapshot created: {snapshot2.name} ({snapshot2.snapshot_id})\n")

        # List snapshots
        print("=" * 60)
        print("6. Listing Snapshots")
        print("=" * 60)
        snapshots = manager.list_snapshots()
        for snap in snapshots:
            print(f"  - {snap.name} ({snap.snapshot_id[:8]}...)")
            print(f"    Created: {snap.created_at}")
            print(f"    Description: {snap.description}")
        print()

        # Set default snapshot
        print("=" * 60)
        print("7. Setting Default Snapshot")
        print("=" * 60)
        manager.set_default_snapshot(snapshot.snapshot_id)
        print(f"✓ Default snapshot: {snapshot.name}\n")

        # Test thaw/freeze
        print("=" * 60)
        print("8. Testing Thaw/Freeze")
        print("=" * 60)
        print(f"  Currently frozen: {not manager.is_thawed()}")
        manager.thaw()
        print(f"  After thaw: {manager.is_thawed()}")
        manager.freeze()
        print(f"  After freeze: {not manager.is_thawed()}\n")

        # Git status
        print("=" * 60)
        print("9. Git Status")
        print("=" * 60)
        if "cfg" in manager.git_managers:
            git_status = manager.git_managers["cfg"].get_status()
            print(f"  Branch: {git_status.get('branch', 'N/A')}")
            print(f"  Clean: {git_status.get('clean', False)}")
            print(f"  Recent commits: {len(git_status.get('commits', []))}")
        print()

        # Final status
        print("=" * 60)
        print("10. Final Status")
        print("=" * 60)
        final_status = manager.get_status()
        print(f"Snapshots: {final_status['snapshots']['total']}")
        print(f"Default: {final_status['snapshots']['default']}")
        print()

        print("=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    finally:
        # Cleanup
        print(f"\nCleaning up: {temp_dir}")
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
