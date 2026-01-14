# Deep Freeze - GitHub Copilot Instructions

## Project Overview
Deep Freeze is a system state management tool that ensures computers can return to a known "clean" state while allowing selective persistence through domain-based freezing and Git integration.

## Code Style and Conventions

### Python Style
- Follow PEP 8 with 88-character line length (Black default)
- Use type hints for function parameters and return values
- Use Google-style docstrings for all public functions and classes
- Organize imports: standard library, third-party, local
- Use meaningful, descriptive variable and function names

### Naming Conventions
- Classes: PascalCase (e.g., `SnapshotManager`, `DomainType`)
- Functions/methods: snake_case (e.g., `create_snapshot`, `get_domain`)
- Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_DOMAINS`)
- Private methods: prefix with underscore (e.g., `_calculate_hash`)

### Documentation
- Every public class, method, and function must have a docstring
- Include Args, Returns, Raises, and Examples sections where appropriate
- Keep comments focused on "why", not "what"
- Update README.md when adding user-facing features

## Architecture Patterns

### Domain Model
- Four core domains: sys (frozen OS/apps), cfg (versioned configs), user (persistent data), cache (temporary)
- Each domain has a type, path, reset policy, and optional Git tracking
- Use enums for domain types and reset policies

### Manager Pattern
- Use manager classes for coordinating operations (e.g., `DomainManager`, `SnapshotManager`)
- Managers handle initialization, configuration persistence, and high-level operations
- Separate concerns: domain logic, snapshot logic, Git integration

### Error Handling
- Use try-except blocks for I/O operations and external calls
- Return boolean success indicators for simple operations
- Return None for failures in object retrieval methods
- Log errors appropriately but don't expose sensitive information

## Testing Requirements

### Test Structure
- Use pytest for all tests
- Create test classes that mirror production classes
- Use setup_method and teardown_method for test fixtures
- Use temporary directories for file system tests

### Coverage Goals
- Aim for >80% code coverage
- Test both success and failure paths
- Include edge cases and boundary conditions
- Mock external dependencies (Git, file system) when appropriate

### Test Naming
- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<specific_behavior>`

## Common Patterns

### Path Handling
```python
from pathlib import Path

# Always use Path objects for file paths
path = Path(base_path) / "subdir" / "file.txt"
path.mkdir(parents=True, exist_ok=True)
```

### Configuration Persistence
```python
# Use JSON for configuration files
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)
```

### CLI Commands
```python
# Use Click for CLI with clear help text
@click.command()
@click.argument('name')
@click.option('--description', '-d', help='Optional description')
def command(name: str, description: str):
    """Clear, user-friendly command description."""
    ...
```

### Git Operations
```python
# Always check if repo is initialized before operations
if not git_manager.is_initialized():
    return False

# Use try-except for Git operations
try:
    repo.index.commit(message)
    return True
except GitCommandError:
    return False
```

## Security Considerations

- Never expose sensitive paths or data in logs or error messages
- Validate user inputs before file system operations
- Use secure hash algorithms (SHA256) for integrity checks
- Be cautious with file permissions on created directories

## Performance Guidelines

- Use generators for large file iterations
- Avoid loading entire files into memory when possible
- Use efficient data structures (sets for membership, dicts for lookups)
- Consider lazy loading for large operations

## Specific Module Guidelines

### deepfreeze/domain.py
- Domain represents a storage area with specific policies
- DomainManager coordinates all domains
- Use enums for domain types and reset policies
- Persist configuration as JSON

### deepfreeze/snapshot.py
- Snapshots capture state of frozen domains
- Calculate hashes for integrity verification
- Use snapshot IDs for unique identification
- Support both ID and name-based lookups

### deepfreeze/git_integration.py
- GitManager wraps GitPython operations
- Always check initialization status first
- Provide both detailed and summary status
- Handle GitCommandError exceptions

### deepfreeze/manager.py
- DeepFreezeManager orchestrates all components
- Separate init and load operations
- Provide comprehensive status information
- Use thaw/freeze for temporary policy changes

### deepfreeze/cli.py
- Use Click for command-line interface
- Provide both human-readable and JSON output options
- Clear error messages with exit codes
- Consistent command structure and naming

## When Adding New Features

1. **Design First**: Consider how it fits into existing architecture
2. **Write Tests**: Create tests before or alongside implementation
3. **Update Docs**: Update README.md and relevant docstrings
4. **Consider Cross-Platform**: Ensure Windows, macOS, and Linux support
5. **Error Handling**: Handle failures gracefully with clear messages
6. **Configuration**: Persist configuration if state needs to survive restarts

## Common Tasks

### Adding a New CLI Command
1. Add command function in cli.py with Click decorators
2. Add corresponding manager method if needed
3. Write integration test in test_cli.py
4. Update README.md with command documentation

### Adding a New Domain Type
1. Add enum value to DomainType in domain.py
2. Update DEFAULT_DOMAINS in DomainManager
3. Update documentation and tests
4. Consider Git integration needs

### Extending Snapshot Functionality
1. Update Snapshot class in snapshot.py
2. Modify SnapshotManager methods
3. Update serialization (to_dict/from_dict)
4. Add tests for new functionality

## Avoid These Common Mistakes

- ❌ Using string paths instead of Path objects
- ❌ Forgetting to handle file/directory existence checks
- ❌ Not using context managers for file operations
- ❌ Missing error handling for external operations (Git, file I/O)
- ❌ Hardcoding paths instead of using base_path
- ❌ Not writing tests for new features
- ❌ Exposing implementation details in public APIs

## Best Practices

- ✅ Use type hints consistently
- ✅ Write descriptive docstrings
- ✅ Keep functions small and focused
- ✅ Use meaningful variable names
- ✅ Handle errors explicitly
- ✅ Write tests for all new code
- ✅ Update documentation with changes
- ✅ Use enums for fixed sets of values
- ✅ Prefer composition over inheritance
- ✅ Return early to reduce nesting

## Example Code Patterns

### Creating a New Manager Method
```python
def create_something(self, name: str, options: Dict[str, Any]) -> Optional[Something]:
    """Create a new something.
    
    Args:
        name: Name of the something
        options: Configuration options
        
    Returns:
        Created something or None if failed
    """
    if not self.initialized:
        return None
    
    try:
        something = Something(name, **options)
        self.things[name] = something
        self.save_config()
        return something
    except Exception as e:
        logger.error(f"Failed to create something: {e}")
        return None
```

### Adding a CLI Command
```python
@cli.command()
@click.argument('name')
@click.option('--flag', is_flag=True, help='Optional flag')
@click.pass_context
def my_command(ctx, name: str, flag: bool):
    """Command description for help text."""
    manager = DeepFreezeManager(ctx.obj['base_path'])
    
    if not manager.is_initialized():
        click.echo("✗ Not initialized", err=True)
        sys.exit(1)
    
    manager.load()
    
    if manager.do_something(name, flag):
        click.echo(f"✓ Success: {name}")
    else:
        click.echo("✗ Failed", err=True)
        sys.exit(1)
```

---

This guidance helps GitHub Copilot understand Deep Freeze's architecture, coding standards, and best practices to generate consistent, high-quality code suggestions.
