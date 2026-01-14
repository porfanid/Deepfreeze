"""Command-line interface for Deep Freeze."""

import sys
import click
from pathlib import Path
from typing import Optional
import json

from .manager import DeepFreezeManager


@click.group()
@click.option(
    '--base-path',
    type=click.Path(),
    default=None,
    help='Base path for Deep Freeze storage (default: ~/.deepfreeze)'
)
@click.pass_context
def cli(ctx, base_path: Optional[str]):
    """Deep Freeze - System state management with domain-based freezing.
    
    Ensure a computer can always return to a known "clean" state,
    while allowing selective persistence.
    """
    ctx.ensure_object(dict)
    
    if base_path:
        ctx.obj['base_path'] = Path(base_path)
    else:
        ctx.obj['base_path'] = None


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize Deep Freeze system.
    
    Sets up domains: sys, cfg, user, cache
    Initializes Git repo for cfg domain
    """
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if manager.is_initialized():
        click.echo("Deep Freeze is already initialized.")
        click.echo(f"Base path: {manager.base_path}")
        return
    
    click.echo("Initializing Deep Freeze...")
    
    if manager.init():
        click.echo(f"✓ Deep Freeze initialized at {manager.base_path}")
        click.echo("\nDomains created:")
        for name, domain in manager.domain_manager.domains.items():
            click.echo(f"  • {name}: {domain.path} ({domain.reset_policy.value})")
        
        click.echo("\nNext steps:")
        click.echo("  1. Run 'freeze snapshot create base' to create initial snapshot")
        click.echo("  2. Run 'freeze status' to view system state")
    else:
        click.echo("✗ Failed to initialize Deep Freeze", err=True)
        sys.exit(1)


@cli.group()
def snapshot():
    """Manage snapshots."""
    pass


@snapshot.command('create')
@click.argument('name')
@click.option('--description', '-d', default='', help='Snapshot description')
@click.pass_context
def snapshot_create(ctx, name: str, description: str):
    """Create a new snapshot.
    
    NAME is the snapshot name (e.g., 'base', 'before-update')
    """
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    click.echo(f"Creating snapshot '{name}'...")
    
    snapshot = manager.create_snapshot(name, description)
    
    if snapshot:
        click.echo(f"✓ Snapshot created: {snapshot.snapshot_id}")
        click.echo(f"  Name: {snapshot.name}")
        click.echo(f"  Created: {snapshot.created_at}")
        if snapshot.description:
            click.echo(f"  Description: {snapshot.description}")
        click.echo(f"\nDomains captured:")
        for domain_name in snapshot.domains:
            click.echo(f"  • {domain_name}")
    else:
        click.echo("✗ Failed to create snapshot", err=True)
        sys.exit(1)


@snapshot.command('list')
@click.pass_context
def snapshot_list(ctx):
    """List all snapshots."""
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    snapshots = manager.list_snapshots()
    
    if not snapshots:
        click.echo("No snapshots found.")
        return
    
    click.echo(f"Snapshots ({len(snapshots)}):\n")
    
    default_id = manager.snapshot_manager.default_snapshot
    
    for snap in sorted(snapshots, key=lambda x: x.created_at, reverse=True):
        marker = "→" if snap.snapshot_id == default_id else " "
        click.echo(f"{marker} {snap.name} ({snap.snapshot_id})")
        click.echo(f"    Created: {snap.created_at}")
        if snap.description:
            click.echo(f"    Description: {snap.description}")
        click.echo(f"    Domains: {', '.join(snap.domains.keys())}")
        click.echo()


@cli.command('set-default')
@click.argument('snapshot_id')
@click.pass_context
def set_default(ctx, snapshot_id: str):
    """Set the default snapshot to boot.
    
    SNAPSHOT_ID is the snapshot identifier (or name)
    """
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    # Try to find snapshot by ID or name
    snapshot = manager.snapshot_manager.get_snapshot(snapshot_id)
    if not snapshot:
        snapshot = manager.snapshot_manager.get_snapshot_by_name(snapshot_id)
    
    if not snapshot:
        click.echo(f"✗ Snapshot not found: {snapshot_id}", err=True)
        sys.exit(1)
    
    if manager.set_default_snapshot(snapshot.snapshot_id):
        click.echo(f"✓ Default snapshot set to: {snapshot.name} ({snapshot.snapshot_id})")
    else:
        click.echo("✗ Failed to set default snapshot", err=True)
        sys.exit(1)


@cli.command()
@click.option('--json-output', '-j', is_flag=True, help='Output as JSON')
@click.pass_context
def status(ctx, json_output: bool):
    """Show current Deep Freeze status."""
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        if json_output:
            click.echo(json.dumps({"initialized": False}))
        else:
            click.echo("Deep Freeze is not initialized.")
            click.echo("Run 'freeze init' to get started.")
        return
    
    manager.load()
    status = manager.get_status()
    
    if json_output:
        click.echo(json.dumps(status, indent=2))
        return
    
    # Human-readable output
    click.echo("═" * 60)
    click.echo(" Deep Freeze Status")
    click.echo("═" * 60)
    click.echo()
    
    click.echo(f"Base path: {status['base_path']}")
    click.echo(f"Platform: {status['platform']}")
    click.echo(f"Status: {'Thawed' if manager.is_thawed() else 'Frozen'}")
    click.echo()
    
    # Domains
    click.echo("Domains:")
    for name, domain_info in status['domains'].items():
        exists = "✓" if domain_info['exists'] else "✗"
        click.echo(f"  {exists} {name}")
        click.echo(f"      Type: {domain_info['type']}")
        click.echo(f"      Policy: {domain_info['reset_policy']}")
        click.echo(f"      Git: {'Yes' if domain_info['use_git'] else 'No'}")
        click.echo(f"      Path: {domain_info['path']}")
    
    click.echo()
    
    # Snapshots
    snap_info = status['snapshots']
    click.echo(f"Snapshots: {snap_info['total']} total")
    if snap_info['default']:
        default_snap = manager.snapshot_manager.get_snapshot(snap_info['default'])
        if default_snap:
            click.echo(f"  Default: {default_snap.name} ({snap_info['default']})")
    
    if snap_info.get('recent'):
        click.echo("\n  Recent:")
        for snap in snap_info['recent'][:3]:
            click.echo(f"    • {snap['name']} ({snap['id']})")
            click.echo(f"      Created: {snap['created_at']}")
    
    click.echo()
    
    # Git status
    if status['git_status']:
        click.echo("Git Status:")
        for domain_name, git_status in status['git_status'].items():
            if git_status.get('initialized'):
                clean = "✓ clean" if git_status.get('clean') else "⚠ has changes"
                click.echo(f"  {domain_name}: {clean}")
                if not git_status.get('clean'):
                    if git_status.get('changed_files'):
                        click.echo(f"    Changed: {len(git_status['changed_files'])} files")
                    if git_status.get('untracked_files'):
                        click.echo(f"    Untracked: {len(git_status['untracked_files'])} files")
    
    click.echo()


@cli.command()
@click.argument('message')
@click.pass_context
def commit(ctx, message: str):
    """Commit selective changes (cfg domain).
    
    MESSAGE is the commit message
    """
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    if manager.commit_config(message):
        click.echo(f"✓ Changes committed to cfg domain")
    else:
        click.echo("✗ Failed to commit changes (or no changes to commit)", err=True)


@cli.command()
@click.pass_context
def thaw(ctx):
    """Temporarily disable freezing.
    
    This allows making persistent changes to frozen domains.
    Re-enable with 'freeze freeze' command.
    """
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    if manager.thaw():
        click.echo("✓ System thawed - freezing temporarily disabled")
        click.echo("  Run 'freeze freeze' to re-enable")
    else:
        click.echo("✗ Failed to thaw system", err=True)
        sys.exit(1)


@cli.command('freeze')
@click.pass_context
def freeze_cmd(ctx):
    """Re-enable freezing after thaw."""
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Deep Freeze is not initialized. Run 'freeze init' first.", err=True)
        sys.exit(1)
    
    manager.load()
    
    if manager.freeze():
        click.echo("✓ System frozen - protection enabled")
    else:
        click.echo("✗ Failed to freeze system", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == '__main__':
    main()
