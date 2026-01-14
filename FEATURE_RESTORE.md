# Automated Enforcement & "Reboot-to-Restore" - Feature Summary

## Overview

This feature implements true "reboot-to-restore" functionality for Deep Freeze, allowing the system to automatically return to a clean state on every boot.

## New Commands

### `freeze restore`

Restore a snapshot to frozen domains (sys, cfg).

**Usage:**
```bash
# Restore the default snapshot
freeze restore --default

# Restore a specific snapshot by name
freeze restore base

# Restore a specific snapshot by ID
freeze restore 1babc5f463c1aea8
```

**What it does:**
- Clears the current state of frozen domains (sys, cfg)
- Restores the snapshot content to those domains
- Preserves user data in persistent domains (user)
- Does not affect the cache domain

### `freeze service`

Manage the auto-restore boot service.

**Subcommands:**

#### `freeze service install`
Installs a system service that runs `freeze restore --default` on every boot.

**Requirements:**
- Root/Administrator privileges
- Deep Freeze must be initialized
- A default snapshot should be set

**Supported platforms:**
- Linux (systemd)
- Windows (Task Scheduler)
- macOS (manual - see services/README.md)

#### `freeze service status`
Shows the current status of the auto-restore boot service.

#### `freeze service uninstall`
Removes the auto-restore boot service.

## How It Works

### Manual Restore
1. User runs `freeze restore --default`
2. Deep Freeze loads the default snapshot
3. Frozen domains (sys, cfg) are cleared and replaced with snapshot content
4. System is now in the clean state defined by the snapshot

### Automatic Boot Restore
1. System boots
2. Boot service runs automatically (before user login)
3. Service executes `freeze restore --default`
4. Frozen domains are restored to clean state
5. User logs in to a clean system

## Use Cases

### 1. Public Computers / Kiosks
**Problem:** Users leave files, change settings, install unwanted software
**Solution:** Install auto-restore service
**Result:** Every reboot returns computer to pristine state

### 2. Lab Computers
**Problem:** Students make changes that persist and affect next user
**Solution:** Auto-restore service ensures clean state for each class
**Result:** Consistent experience for all users

### 3. Development Testing
**Problem:** Need to test software installation in clean environment
**Solution:** Create clean snapshot, test, restore manually
**Result:** Quick iteration without VM overhead

### 4. Malware Recovery
**Problem:** System infected with malware
**Solution:** Reboot triggers auto-restore to clean snapshot
**Result:** Malware eliminated (assuming clean snapshot was made before infection)

## Example Workflows

### Setting Up Auto-Restore

```bash
# 1. Initialize Deep Freeze
freeze init

# 2. Configure your system to desired clean state
#    - Install needed software
#    - Configure settings
#    - Remove temporary files

# 3. Create a snapshot of the clean state
freeze snapshot create production --description "Production-ready clean state"

# 4. Set it as default
freeze set-default production

# 5. Install the boot service
sudo freeze service install  # Linux
# OR run as Administrator on Windows

# 6. Verify installation
sudo freeze service status

# 7. Test by rebooting
sudo reboot

# After reboot, any changes made before reboot are gone!
```

### Testing Without Rebooting

```bash
# Make some changes
echo "test" > ~/important-file.txt
# ... make other changes ...

# Manually restore (simulates boot restore)
freeze restore --default

# Your changes are gone - system is clean again!
```

### Updating the Clean State

```bash
# 1. Disable auto-restore temporarily
sudo freeze service uninstall

# 2. Boot into the system
sudo reboot

# 3. Make your updates
#    - Install new software
#    - Update configurations
#    - etc.

# 4. Create new snapshot
freeze snapshot create updated --description "Updated clean state"

# 5. Set as default
freeze set-default updated

# 6. Re-enable auto-restore
sudo freeze service install

# 7. Test
sudo reboot
```

## Architecture

### Service Files

**Linux (systemd):**
- Service file: `services/deepfreeze-restore.service`
- Installation: `services/install-linux.sh`
- Location: `/etc/systemd/system/deepfreeze-restore.service`
- Runs at: `sysinit.target` (early boot)

**Windows (Task Scheduler):**
- Task definition: `services/deepfreeze-restore.xml`
- Installation: `services/install-windows.bat`
- Name: `DeepFreezeAutoRestore`
- Runs at: System startup (as SYSTEM user)

### Code Components

**Manager (`src/deepfreeze/manager.py`):**
- `restore_snapshot(snapshot_id, use_default)` - Core restore logic
- Handles both ID-based and default snapshot restoration

**CLI (`src/deepfreeze/cli.py`):**
- `restore` command - User-facing restore interface
- `service` command group - Service management

**Snapshot Manager (`src/deepfreeze/snapshot.py`):**
- `restore_snapshot()` - Low-level restore implementation (already existed)

## Testing

### Unit Tests
- 3 new tests in `tests/test_manager.py`
- 4 new tests in `tests/test_cli.py`
- All 48 tests passing

### Manual Testing
```bash
# Quick test
cd /tmp
freeze --base-path /tmp/test init
freeze --base-path /tmp/test snapshot create clean
freeze --base-path /tmp/test set-default clean
echo "test" > /tmp/test/domains/sys/file.txt
freeze --base-path /tmp/test restore --default
ls /tmp/test/domains/sys/file.txt  # Should not exist
```

## Security Considerations

1. **Service runs with elevated privileges** (root/SYSTEM)
   - Necessary to modify system files
   - Audit installation scripts before running

2. **Snapshot integrity**
   - Snapshots are stored in plaintext
   - Protect the Deep Freeze directory with appropriate permissions
   - Consider encrypting the base path directory

3. **Boot process**
   - Service runs early in boot
   - Failure to restore may leave system in inconsistent state
   - Always test in non-production environment first

4. **Malware considerations**
   - If malware infects the default snapshot, it will persist across reboots
   - Always create snapshots from known-clean states
   - Consider multiple snapshots for rollback options

## Troubleshooting

### "No default snapshot set" Error
**Cause:** Restore called but no default snapshot configured
**Solution:** Run `freeze set-default <snapshot-name>`

### Service Fails to Start (Linux)
**Check logs:** `sudo journalctl -u deepfreeze-restore.service`
**Common issues:**
- `freeze` command not in PATH
- Permissions issues
- No default snapshot set

### Service Fails (Windows)
**Check logs:** Task Scheduler → DeepFreezeAutoRestore → History
**Common issues:**
- `freeze` not in system PATH (check SYSTEM user PATH)
- Administrator privileges not configured
- No default snapshot set

### Restore Succeeds But Changes Persist
**Possible causes:**
- Changes were made to persistent domains (user)
- Snapshot was taken after changes were made
- Wrong snapshot restored
**Solution:** Verify which domains are frozen with `freeze status`

## Performance Considerations

### MVP Implementation
Current implementation uses file copying for snapshots:
- **Snapshot creation:** Linear time with domain size
- **Restore operation:** Linear time with domain size
- **Boot time impact:** Depends on snapshot size

### Production Considerations
For production use, consider:
- **OverlayFS/UnionFS:** Use filesystem-level snapshots instead of copies
- **Incremental snapshots:** Only store differences between snapshots
- **Compression:** Compress snapshot data
- **Hardlinks:** Use hardlinks for unchanged files

## Limitations

1. **Manual installation required:** Service not installed automatically with package
2. **User-space only:** Cannot freeze actual OS files (e.g., /etc, /usr)
3. **No atomic restore:** If restore fails mid-process, system may be inconsistent
4. **Single snapshot restore:** Cannot selectively restore individual domains
5. **No rollback:** If restored snapshot is bad, must manually fix or restore different snapshot

## Future Enhancements

- [ ] Atomic restore operations
- [ ] Selective domain restore
- [ ] Pre-boot environment integration (like actual Deep Freeze)
- [ ] Remote snapshot management
- [ ] Scheduled automatic snapshots
- [ ] Snapshot verification/integrity checks
- [ ] Multi-snapshot restore (merge domains from different snapshots)
- [ ] Encrypted snapshots
- [ ] Automatic service installation during package install

## References

- Main documentation: `README.md`
- Quick start guide: `QUICKSTART.md`
- Service installation guide: `services/README.md`
- Test suite: `tests/test_manager.py`, `tests/test_cli.py`

## Support

For issues or questions:
- GitHub Issues: https://github.com/porfanid/Deepfreeze/issues
- Documentation: See README.md and services/README.md

---

**Status:** ✅ Feature Complete (v0.1.0)
**Tested on:** Linux (Ubuntu), Python 3.8+
**Service Templates:** Linux (systemd), Windows (Task Scheduler)
