# Deep Freeze Auto-Restore Service

This directory contains service files and installation scripts for automatically restoring Deep Freeze snapshots on system boot.

## Overview

The auto-restore service ensures that your system automatically restores to the default Deep Freeze snapshot on every boot, providing true "reboot-to-restore" functionality.

## Files

- **deepfreeze-restore.service** - systemd service unit for Linux
- **deepfreeze-restore.xml** - Windows Task Scheduler XML template
- **install-linux.sh** - Installation script for Linux (systemd)
- **uninstall-linux.sh** - Uninstallation script for Linux
- **install-windows.bat** - Installation script for Windows
- **uninstall-windows.bat** - Uninstallation script for Windows

## Prerequisites

Before installing the service:

1. **Deep Freeze must be installed** and the `freeze` command must be available in your PATH
2. **Deep Freeze must be initialized**: Run `freeze init`
3. **A default snapshot must be set**: Run `freeze set-default <snapshot-name>`

Example setup:
```bash
# Initialize Deep Freeze
freeze init

# Create a base snapshot
freeze snapshot create base --description "Clean system state"

# Set it as default
freeze set-default base
```

## Installation

### Linux (systemd)

**Requirements:**
- systemd-based Linux distribution
- Root/sudo access

**Install:**
```bash
cd services
sudo ./install-linux.sh
```

The service will be installed to `/etc/systemd/system/deepfreeze-restore.service` and enabled to run on boot.

**Verify installation:**
```bash
sudo systemctl status deepfreeze-restore.service
```

**Test manually (without rebooting):**
```bash
sudo systemctl start deepfreeze-restore.service
```

**View logs:**
```bash
sudo journalctl -u deepfreeze-restore.service
```

**Uninstall:**
```bash
cd services
sudo ./uninstall-linux.sh
```

### Windows

**Requirements:**
- Windows 7 or later
- Administrator privileges

**Install:**
1. Open Command Prompt or PowerShell **as Administrator**
2. Navigate to the `services` directory
3. Run:
   ```cmd
   install-windows.bat
   ```

The scheduled task will be created and enabled to run on system startup.

**Verify installation:**
```cmd
schtasks /Query /TN "DeepFreezeAutoRestore"
```

**Test manually (without rebooting):**
```cmd
schtasks /Run /TN "DeepFreezeAutoRestore"
```

**View task details:**
- Open Task Scheduler (taskschd.msc)
- Look for "DeepFreezeAutoRestore" in the Task Scheduler Library

**Uninstall:**
```cmd
uninstall-windows.bat
```

## How It Works

The service runs the following command on every boot:
```bash
freeze restore --default
```

This command:
1. Loads the Deep Freeze configuration
2. Identifies the default snapshot
3. Restores frozen domains (sys, cfg) to the snapshot state
4. Preserves user data in persistent domains

## Customization

### Custom Base Path

If you're using a custom Deep Freeze base path, you'll need to modify the service files:

**Linux (deepfreeze-restore.service):**
```ini
ExecStart=/usr/local/bin/freeze --base-path /custom/path restore --default
```

**Windows (deepfreeze-restore.xml):**
```xml
<Arguments>--base-path C:\custom\path restore --default</Arguments>
```

### Custom Freeze Command Location

If `freeze` is installed in a non-standard location:

**Linux:** Update the `ExecStart` path in `deepfreeze-restore.service`

**Windows:** Update the `<Command>` path in `deepfreeze-restore.xml`

## Troubleshooting

### Linux

**Service fails to start:**
1. Check service status:
   ```bash
   sudo systemctl status deepfreeze-restore.service
   ```
2. View detailed logs:
   ```bash
   sudo journalctl -u deepfreeze-restore.service -n 50
   ```
3. Verify `freeze` command is in PATH:
   ```bash
   which freeze
   ```
4. Test restore manually:
   ```bash
   freeze restore --default
   ```

**Common issues:**
- No default snapshot set: Run `freeze set-default <snapshot-name>`
- Permission errors: Ensure service runs with appropriate privileges
- Path issues: Verify freeze command location

### Windows

**Scheduled task fails:**
1. Check task status in Task Scheduler (taskschd.msc)
2. View task history in Task Scheduler
3. Verify `freeze` command is in PATH:
   ```cmd
   where freeze
   ```
4. Test restore manually:
   ```cmd
   freeze restore --default
   ```

**Common issues:**
- Task runs but fails: Check that `freeze` is in system PATH (not just user PATH)
- Permission errors: Task should run with highest privileges
- No default snapshot set: Run `freeze set-default <snapshot-name>`

## Security Considerations

- The service runs with elevated privileges (root on Linux, SYSTEM on Windows)
- Ensure your Deep Freeze installation and snapshots are properly secured
- Review service permissions before deploying in production environments
- Consider the security implications of automatic system restoration

## Disabling Without Uninstalling

### Linux
```bash
# Disable (prevents auto-start on boot)
sudo systemctl disable deepfreeze-restore.service

# Re-enable
sudo systemctl enable deepfreeze-restore.service
```

### Windows
```cmd
# Disable
schtasks /Change /TN "DeepFreezeAutoRestore" /DISABLE

# Re-enable
schtasks /Change /TN "DeepFreezeAutoRestore" /ENABLE
```

## Alternative: macOS (launchd)

For macOS systems, you can create a LaunchDaemon. Here's a basic template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.deepfreeze.restore</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/freeze</string>
        <string>restore</string>
        <string>--default</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/deepfreeze-restore.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/deepfreeze-restore.err</string>
</dict>
</plist>
```

Save as `/Library/LaunchDaemons/com.deepfreeze.restore.plist` and load with:
```bash
sudo launchctl load /Library/LaunchDaemons/com.deepfreeze.restore.plist
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/porfanid/Deepfreeze/issues
- Documentation: https://github.com/porfanid/Deepfreeze

---

**Important:** Always test the auto-restore functionality in a non-production environment before deploying to production systems.
