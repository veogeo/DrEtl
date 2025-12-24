# Contributing to DRETL

Thank you for your interest in contributing to DRETL! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/veogeo/DrEtl.git
cd DrEtl
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## Project Structure

```
DrEtl/
├── dretl/              # Main package
│   ├── handlers/       # Data source handlers (read-only)
│   ├── targets/        # Data targets (write-only)
│   ├── models.py       # Core data models
│   ├── handler.py      # Handler base class
│   ├── target.py       # Target base class
│   ├── pipeline.py     # ETL pipeline orchestrator
│   └── cli.py          # Command-line interface
├── tests/              # Test suite
├── examples/           # Example files and scripts
└── pyproject.toml      # Project configuration
```

## Adding a New Handler

Handlers are READ-ONLY components that inspect data sources and produce `DatasetReport` objects.

Example:

```python
from dretl.handler import Handler
from dretl.models import DatasetReport

class MyFormatHandler(Handler):
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        """Check if this handler can process the source."""
        return source_path.endswith('.myformat')
    
    @classmethod
    def get_source_type(cls) -> str:
        """Return the source type identifier."""
        return "myformat"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        """Inspect the data source and generate a report."""
        # Implementation here
        report = DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type()
        )
        # ... populate layers, fields, etc.
        return report
```

Register the handler:

```python
from dretl.handler import HandlerRegistry
HandlerRegistry.register(MyFormatHandler)
```

## Adding a New Target

Targets are WRITE-ONLY components that consume `RewritePlan` objects and load data to backends.

Example:

```python
from dretl.target import Target
from dretl.models import RewritePlan

class MyBackendTarget(Target):
    @classmethod
    def get_target_type(cls) -> str:
        """Return the target type identifier."""
        return "mybackend"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        """Execute the rewrite plan and load data."""
        results = {
            "target_path": plan.target_path,
            "layers_written": [],
            "errors": [],
            "warnings": []
        }
        
        for layer in plan.layers_to_process:
            # Implementation here
            # ... write data
            results["layers_written"].append(layer.name)
        
        return results
```

Register the target:

```python
from dretl.target import TargetRegistry
TargetRegistry.register(MyBackendTarget)
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use pytest fixtures for common setup
- Follow existing test patterns

Example:

```python
import pytest
from dretl.handler import Handler, HandlerRegistry

def test_my_handler():
    handler = MyFormatHandler()
    report = handler.inspect("test.myformat")
    
    assert report.source_type == "myformat"
    assert report.is_valid
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=dretl
```

Run specific test file:
```bash
pytest tests/test_handler.py
```

## Code Style

We follow PEP 8 style guidelines with a few modifications:

- Line length: 88 characters (Black default)
- Use type hints where appropriate
- Write descriptive docstrings

Format code with Black:
```bash
black dretl/
```

Lint with Ruff:
```bash
ruff dretl/
```

## Documentation

- Update README.md for major features
- Add docstrings to all public classes and methods
- Include examples for new functionality
- Update type hints

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Format code with Black
7. Commit with clear messages
8. Push to your fork
9. Create a Pull Request

### PR Checklist

- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Code formatted with Black
- [ ] Documentation updated
- [ ] Examples added if relevant
- [ ] No breaking changes (or clearly documented)

## Design Principles

When contributing, keep these principles in mind:

1. **Separation of Concerns**: Handlers only read, targets only write
2. **Framework Agnostic**: No Django, GeoNode, or framework dependencies
3. **Extensible**: Easy plugin system for handlers and targets
4. **Type Safety**: Use dataclasses and enums for clear data structures
5. **Clean API**: Simple, intuitive interfaces for both CLI and Python

## Questions?

- Open an issue for bug reports or feature requests
- Use discussions for questions and ideas
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
