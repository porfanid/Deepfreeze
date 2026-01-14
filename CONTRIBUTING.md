# Contributing to Deep Freeze

Thank you for your interest in contributing to Deep Freeze! This document provides guidelines and best practices for contributing to the project.

## 🌟 Code of Conduct

Be respectful, inclusive, and collaborative. We're all here to build something great together.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Setting Up Development Environment

1. **Fork and Clone**

```bash
git clone https://github.com/YOUR_USERNAME/Deepfreeze.git
cd Deepfreeze
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Development Dependencies**

```bash
pip install -e ".[dev]"
```

4. **Verify Setup**

```bash
# Run tests
pytest

# Check code style
black --check src tests
flake8 src tests
```

## 📝 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### 2. Make Your Changes

Follow the coding standards outlined below.

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=deepfreeze --cov-report=term

# Run specific test
pytest tests/test_manager.py -v
```

### 4. Format and Lint

```bash
# Format code
black src tests

# Check linting
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Type checking (optional but recommended)
mypy src --ignore-missing-imports
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: snapshot compression support"
```

Good commit message format:
```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat: Add snapshot compression support

Implement gzip compression for snapshots to reduce storage space.
Adds --compress flag to snapshot create command.

Closes #123
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear title and description
- Reference related issues
- Screenshots for UI changes
- Test results

## 💻 Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black default)
- **Imports**: Organized and sorted
- **Docstrings**: Google style for all public functions and classes
- **Type Hints**: Use where beneficial for clarity

### Code Organization

```python
"""Module docstring.

Detailed description of module purpose.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import click
from git import Repo

# Local imports
from .domain import Domain
from .snapshot import Snapshot


class MyClass:
    """Class docstring.
    
    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2
    """
    
    def __init__(self, param1: str, param2: int):
        """Initialize MyClass.
        
        Args:
            param1: Description of param1
            param2: Description of param2
        """
        self.attr1 = param1
        self.attr2 = param2
    
    def my_method(self, arg: str) -> bool:
        """Method docstring.
        
        Args:
            arg: Description of argument
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When arg is invalid
        """
        if not arg:
            raise ValueError("arg cannot be empty")
        return True
```

### Best Practices

#### 1. **Write Clear, Self-Documenting Code**

```python
# Good
def calculate_snapshot_hash(domain_path: Path) -> str:
    """Calculate SHA256 hash of domain contents."""
    ...

# Avoid
def calc_hash(p):
    """Hash."""
    ...
```

#### 2. **Use Type Hints**

```python
from typing import List, Dict, Optional

def get_snapshots(limit: Optional[int] = None) -> List[Snapshot]:
    """Get list of snapshots."""
    ...
```

#### 3. **Handle Errors Gracefully**

```python
try:
    snapshot = manager.create_snapshot(name)
except SnapshotError as e:
    logger.error(f"Failed to create snapshot: {e}")
    return False
```

#### 4. **Write Tests for New Features**

```python
def test_snapshot_creation():
    """Test that snapshots are created correctly."""
    manager = SnapshotManager(temp_path)
    snapshot = manager.create_snapshot("test")
    
    assert snapshot is not None
    assert snapshot.name == "test"
```

#### 5. **Keep Functions Small and Focused**

Each function should do one thing well.

#### 6. **Use Meaningful Variable Names**

```python
# Good
snapshot_manager = SnapshotManager(base_path)
domain_paths = get_domain_paths()

# Avoid
sm = SnapshotManager(bp)
dp = get_paths()
```

### Documentation Standards

#### Docstrings

Use Google-style docstrings:

```python
def function_with_types_in_docstring(param1: str, param2: int) -> bool:
    """Summary line.

    Extended description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is empty
        
    Example:
        >>> function_with_types_in_docstring("test", 42)
        True
    """
    ...
```

#### Comments

- Use comments sparingly - code should be self-explanatory
- Explain **why**, not **what**
- Keep comments up-to-date with code changes

```python
# Good: Explains why
# Use SHA256 for security and to detect any bit-level corruption
hash_algo = hashlib.sha256()

# Avoid: States the obvious
# Create a SHA256 hash object
hash_algo = hashlib.sha256()
```

## 🧪 Testing Guidelines

### Test Structure

```python
class TestFeatureName:
    """Test FeatureName functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = Manager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        result = self.manager.do_something()
        assert result is True
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Include integration tests for CLI commands
- Mock external dependencies when appropriate

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_manager.py

# Specific test
pytest tests/test_manager.py::TestManager::test_init

# With coverage
pytest --cov=deepfreeze --cov-report=html
```

## 📚 Documentation

### When to Update Documentation

- New features added
- API changes
- Configuration changes
- New dependencies
- Installation steps modified

### Documentation Locations

- **README.md**: User-facing documentation
- **CONTRIBUTING.md**: This file
- **Docstrings**: In-code documentation
- **GitHub Wiki**: Extended guides and tutorials

## 🔍 Code Review Process

### For Contributors

- Ensure all tests pass
- Format code with Black
- Update documentation
- Respond to review feedback promptly

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates

## 🐛 Reporting Bugs

Use GitHub Issues with:

1. **Clear title**: Summarize the problem
2. **Description**: Detailed explanation
3. **Steps to reproduce**: Numbered list
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Environment**: OS, Python version, Deep Freeze version
7. **Logs/screenshots**: If applicable

## 💡 Feature Requests

Submit feature requests via GitHub Issues:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: How you envision it working
3. **Alternatives**: Other approaches you've considered
4. **Additional Context**: Any other relevant information

## 📖 GitHub Copilot Instructions

When using GitHub Copilot with this project:

### Code Generation Guidelines

- Follow the existing code style and patterns
- Use type hints for function parameters and return values
- Include docstrings for all public functions and classes
- Write self-documenting code with clear variable names
- Keep functions focused and small (single responsibility)
- Handle errors explicitly rather than silently failing

### Testing Guidelines

- Generate tests that match the existing test structure
- Include setup and teardown methods
- Test both success and failure cases
- Use descriptive test names that explain what is being tested
- Mock external dependencies appropriately

### Documentation Guidelines

- Keep documentation concise but complete
- Use code examples where helpful
- Follow the existing documentation structure
- Update related docs when adding features

## 🎯 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts
- [ ] CI checks pass

## 🏆 Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Mentioned in project announcements

## 📞 Getting Help

- **Questions**: Use GitHub Discussions
- **Issues**: Create a GitHub Issue
- **Chat**: Join our community (link TBD)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Deep Freeze! 🎉
