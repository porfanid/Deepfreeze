# Deep Freeze

[![Tests](https://github.com/porfanid/Deepfreeze/actions/workflows/test.yml/badge.svg)](https://github.com/porfanid/Deepfreeze/actions/workflows/test.yml)
[![Lint](https://github.com/porfanid/Deepfreeze/actions/workflows/lint.yml/badge.svg)](https://github.com/porfanid/Deepfreeze/actions/workflows/lint.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A system state management tool that ensures a computer can always return to a known "clean" state, while allowing selective persistence through domain-based freezing and Git integration.

## 🎯 Overview

Deep Freeze provides a powerful way to manage system state by separating storage into domains with different persistence policies:

- **sys** → OS + apps (frozen, discarded on reboot)
- **cfg** → Configs (versioned with Git, optional commit)
- **user** → Home directories (persistent)
- **cache** → Temp files (always reset)

### Key Features

- ✨ **Domain-based storage separation** with flexible policies
- 📸 **Snapshot management** for frozen domains
- 🔄 **Git integration** for configuration tracking and versioning
- 🔒 **Predictable system behavior** with easy rollback
- 🖥️ **Cross-platform support** (Linux, macOS, Windows)
- 🚀 **Lightweight** - works on existing systems without OS changes
- ⚡ **Performance optimized** - OverlayFS and hardlink-based snapshots
- 🔁 **Auto-restore on boot** - optional system service

### Performance Features (New!)

- **OverlayFS Support (Linux):** Instant freeze/thaw with zero-copy snapshots
- **Hardlink Snapshots:** Efficient storage using hardlinks instead of file copies
- **Windows Junctions:** Fast redirection for Windows systems
- **Minimal Disk Usage:** Multiple snapshots share unchanged files

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/porfanid/Deepfreeze.git
cd Deepfreeze

# Install with pip
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### System Requirements

- Python 3.8 or higher
- Git (for configuration versioning)
- Supported OS: Linux, macOS, Windows

## 🚀 Quick Start

### 1. Initialize Deep Freeze

```bash
freeze init
```

This creates the domain structure and initializes Git for the configuration domain.

### 2. Create a Base Snapshot

```bash
freeze snapshot create base --description "Clean system state"
```

### 3. Check Status

```bash
freeze status
```

### 4. Set Default Snapshot

```bash
freeze set-default base
```

## 📖 Usage

### Basic Commands

#### Initialize System

```bash
freeze init
```

Sets up domains (sys, cfg, user, cache) and initializes the Git repository for the config domain.

#### Create Snapshot

```bash
freeze snapshot create <name> [--description "Description"]
```

Creates a snapshot of frozen domains (sys, cfg).

**Examples:**
```bash
freeze snapshot create base
freeze snapshot create before-update --description "Before system update"
```

#### List Snapshots

```bash
freeze snapshot list
```

Shows all available snapshots with their details.

#### Set Default Snapshot

```bash
freeze set-default <snapshot-id-or-name>
```

Sets which snapshot the system should boot to by default.

#### View Status

```bash
# Human-readable output
freeze status

# JSON output
freeze status --json-output
```

Shows current Deep Freeze state, domain information, snapshots, and Git status.

#### Commit Configuration Changes

```bash
freeze commit "Commit message"
```

Commits changes in the cfg domain to Git.

#### Thaw System

```bash
freeze thaw
```

Temporarily disables freezing to allow persistent changes to frozen domains.

#### Re-enable Freezing

```bash
freeze freeze
```

Re-enables freezing after thawing.

#### Restore Snapshot

```bash
# Restore the default snapshot
freeze restore --default

# Restore a specific snapshot by name or ID
freeze restore base
freeze restore 1babc5f463c1aea8
```

Restores a snapshot to the frozen domains (sys, cfg), returning the system to a known clean state.

### Boot Service Management

#### Install Auto-Restore Service

```bash
freeze service install
```

Installs a system service that automatically restores the default snapshot on every boot. This provides true "reboot-to-restore" functionality.

**Requirements:**
- Deep Freeze must be initialized
- A default snapshot should be set (recommended)
- Root/Administrator privileges required

**Supported Platforms:**
- Linux (systemd)
- Windows (Task Scheduler)
- macOS (manual installation - see services/README.md)

#### Check Service Status

```bash
freeze service status
```

Shows the status of the auto-restore boot service.

#### Uninstall Service

```bash
freeze service uninstall
```

Removes the auto-restore boot service from the system.

### Advanced Usage

#### Custom Base Path

```bash
freeze --base-path /custom/path init
freeze --base-path /custom/path status
```

#### Working with Multiple Snapshots

```bash
# Create snapshots for different purposes
freeze snapshot create dev-environment
freeze snapshot create testing-setup
freeze snapshot create production-ready

# List and choose
freeze snapshot list
freeze set-default production-ready
```

## 🏗️ Architecture

### Domain Types

| Domain | Purpose | Git Tracking | Reset Policy | Storage Type |
|--------|---------|-------------|--------------|--------------|
| **sys** | OS + applications | ❌ | Discard on reboot | Snapshot + Overlay |
| **cfg** | Configuration files | ✅ | Optional commit | Snapshot + Overlay + Git |
| **user** | User data/home dirs | ❌ (optional) | Persistent | Direct storage |
| **cache** | Temporary files | ❌ | Always reset | tmpfs |

### How It Works

1. **Domain Separation**: Different parts of the system are isolated into domains
2. **Snapshots**: Frozen domains (sys, cfg) are captured in snapshots
3. **Overlays**: Runtime changes go to overlays, discarded on reset
4. **Git Control**: Configuration domain tracks changes in Git for auditability
5. **Selective Persistence**: User data remains persistent across reboots
6. **Auto-Restore**: Optional boot service automatically restores default snapshot

Boot → [Auto-Restore Service] → Load Snapshot → Apply Overlays → Runtime Changes → Reboot
                                       ↓
                               Git Commit (optional, for cfg)
```

When the auto-restore service is installed:
- System boots
- Service runs `freeze restore --default`
- Frozen domains (sys, cfg) are restored to snapshot state
- User data in persistent domains remains unchanged
- System is ready in clean state

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=deepfreeze --cov-report=html

# Run specific test file
pytest tests/test_manager.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black src tests

# Lint with Flake8
flake8 src tests --max-line-length=88

# Type check with mypy
mypy src --ignore-missing-imports
```

### Project Structure

```
Deepfreeze/
├── src/
│   └── deepfreeze/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── manager.py          # Main Deep Freeze manager
│       ├── domain.py           # Domain management
│       ├── snapshot.py         # Snapshot management
│       └── git_integration.py  # Git integration
├── tests/
│   ├── test_cli.py
│   ├── test_manager.py
│   ├── test_domain.py
│   ├── test_snapshot.py
│   └── test_git_integration.py
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── lint.yml
├── setup.py
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📋 Roadmap

- [x] **Phase 1: Performance Optimization** (✅ COMPLETED)
  - [x] OverlayFS integration for Linux
  - [x] Windows junction/symlink simulation  
  - [x] Hardlink-based efficient snapshots
- [x] Boot-time integration for automatic snapshot restoration
- [x] CLI restore command
- [ ] **Phase 2: Security & Hardening**
  - [ ] Password-protected CLI commands
  - [ ] Config file encryption
- [ ] **Phase 3: Advanced Boot Integration**
  - [ ] Pre-login restoration (Linux)
  - [ ] macOS LaunchDaemon support
- [ ] **Phase 4: User Experience**
  - [ ] Differential snapshots
  - [ ] Background monitoring daemon
  - [ ] Desktop notifications
- [ ] **Phase 5: Deployment**
  - [ ] Automated cross-platform installer
- [ ] Web UI for management
- [ ] Remote snapshot storage
- [ ] Network domain support

See [ROADMAP_STATUS.md](ROADMAP_STATUS.md) for detailed implementation status.

## 🐛 Known Limitations

- OverlayFS requires root privileges (Linux only)
- Windows junction approach less robust than kernel driver
- Boot service requires manual installation
- Limited to user-space operations (no kernel integration)
- Config encryption not yet implemented

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Deep Freeze commercial software
- Built with Python, Git, and open-source tools
- Community feedback and contributions

## 📞 Support

- 🐛 [Report Issues](https://github.com/porfanid/Deepfreeze/issues)
- 💬 [Discussions](https://github.com/porfanid/Deepfreeze/discussions)
- 📧 Contact maintainers through GitHub

## 🌟 Star History

If you find Deep Freeze useful, please consider starring the repository!

---

Made with ❤️ by the Deep Freeze community
