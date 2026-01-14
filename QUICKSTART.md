# Deep Freeze - Quick Start Guide

Get up and running with Deep Freeze in 5 minutes!

## Step 1: Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/porfanid/Deepfreeze.git
cd Deepfreeze

# Install Deep Freeze
pip install -e .

# Verify installation
freeze --help
```

## Step 2: Initialize (30 seconds)

```bash
# Initialize Deep Freeze (uses ~/.deepfreeze by default)
freeze init
```

**What this does:**
- Creates 4 domains: sys, cfg, user, cache
- Initializes Git for the cfg domain
- Sets up configuration files

## Step 3: Create Your First Snapshot (30 seconds)

```bash
# Create a base snapshot of your system
freeze snapshot create base --description "Clean system state"
```

**What this does:**
- Captures current state of sys and cfg domains
- Creates a snapshot with a unique ID
- Commits cfg to Git

## Step 4: Check Status (10 seconds)

```bash
# View current system status
freeze status
```

You'll see:
- Domain information
- Snapshot count
- Git status
- Current freeze state

## Step 5: Set Default Snapshot (10 seconds)

```bash
# Set the base snapshot as default
freeze set-default base
```

Now your system knows which snapshot to restore to!

---

## Common Operations

### List All Snapshots

```bash
freeze snapshot list
```

### Create a New Snapshot

```bash
# Before making system changes
freeze snapshot create before-update --description "Before installing X"

# Make your changes...

# Create another snapshot after changes
freeze snapshot create after-update --description "After installing X"
```

### Commit Configuration Changes

```bash
# Make changes to config files in cfg domain
# Then commit them to Git
freeze commit "Updated network settings"
```

### Temporarily Disable Freezing

```bash
# Thaw to make permanent changes
freeze thaw

# Make your changes...

# Re-enable freezing
freeze freeze
```

### View Status as JSON

```bash
freeze status --json-output
```

---

## Example Workflow

### Scenario: Testing a new application

```bash
# 1. Create a snapshot before installing
freeze snapshot create before-new-app --description "Before installing MyApp"

# 2. Install and test the application
# ... installation steps ...

# 3. If you like it, create a new snapshot
freeze snapshot create with-myapp --description "System with MyApp installed"
freeze set-default with-myapp

# 4. If you don't like it, just reboot (in full implementation)
#    The system will restore to the last default snapshot
```

### Scenario: Managing configuration changes

```bash
# 1. Edit config files
vim ~/.deepfreeze/domains/cfg/myconfig.yaml

# 2. Test your changes
# ...

# 3. Commit them to Git
freeze commit "Updated myconfig with new settings"

# 4. Create a snapshot
freeze snapshot create updated-config
```

---

## Useful Commands Cheat Sheet

```bash
# Initialization
freeze init                           # Initialize Deep Freeze

# Snapshots
freeze snapshot create <name>         # Create snapshot
freeze snapshot list                  # List all snapshots
freeze set-default <snapshot>         # Set default snapshot

# Restore
freeze restore --default              # Restore default snapshot
freeze restore <snapshot>             # Restore specific snapshot

# Status
freeze status                         # Human-readable status
freeze status --json-output           # JSON status

# Configuration Management
freeze commit "message"               # Commit cfg changes

# System Control
freeze thaw                           # Disable freezing
freeze freeze                         # Enable freezing

# Boot Service
freeze service install                # Install auto-restore service
freeze service status                 # Check service status
freeze service uninstall              # Uninstall service

# Help
freeze --help                         # Main help
freeze snapshot --help                # Snapshot help
```

---

## Enable Auto-Restore on Boot (Optional)

For true "reboot-to-restore" functionality, install the boot service:

```bash
# Install the auto-restore service
freeze service install

# Check that it's installed correctly
freeze service status
```

Now every time your system boots, it will automatically restore to the default snapshot!

**Test it:**
1. Make some changes to frozen domains
2. Reboot your system
3. Changes are gone - system is back to the clean state

**Important:** Make sure you have a default snapshot set before installing the service.

For more details, see `services/README.md`.

---

## Run the Demo

See Deep Freeze in action:

```bash
python examples/demo.py
```

This demonstrates:
1. Initialization
2. Domain management
3. Creating snapshots
4. Git integration
5. Status checking

---

## Troubleshooting

### Problem: "Deep Freeze is not initialized"

**Solution:**
```bash
freeze init
```

### Problem: Snapshot creation fails

**Solution:**
- Check disk space
- Ensure domains directory exists
- Check permissions

### Problem: Git commands fail

**Solution:**
- Ensure Git is installed: `git --version`
- Check Git configuration in cfg domain

---

## Next Steps

1. **Read the full README**: `cat README.md`
2. **Explore examples**: `python examples/demo.py`
3. **Run tests**: `make test`
4. **Read contributing guide**: `cat CONTRIBUTING.md`

---

## Getting Help

- **CLI Help**: `freeze --help`
- **Issues**: https://github.com/porfanid/Deepfreeze/issues
- **Discussions**: https://github.com/porfanid/Deepfreeze/discussions

---

**Happy Freezing! 🧊**
