# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-14

### Added
- Initial MVP release of Deep Freeze
- Core domain management system (sys, cfg, user, cache)
- Snapshot creation and management
- Git integration for configuration tracking
- Full CLI interface with commands:
  - `freeze init` - Initialize Deep Freeze system
  - `freeze snapshot create` - Create snapshots
  - `freeze snapshot list` - List all snapshots
  - `freeze set-default` - Set default snapshot
  - `freeze status` - Show system status
  - `freeze commit` - Commit config changes
  - `freeze thaw` - Temporarily disable freezing
  - `freeze freeze` - Re-enable freezing
- Cross-platform support (Linux, macOS, Windows)
- Comprehensive test suite (41 tests, 80% coverage)
- CI/CD workflows for testing and linting
- Complete documentation (README, CONTRIBUTING, GitHub Copilot instructions)
- MIT License

### Technical Details
- Python 3.8+ support
- Uses GitPython for version control
- Click for CLI interface
- Pytest for testing
- Black, Flake8, and mypy for code quality

[0.1.0]: https://github.com/porfanid/Deepfreeze/releases/tag/v0.1.0
