# Developer Guide

Guide for contributing to AugmentedVCS development.

---

## Setting Up Development Environment

### 1. Clone Repository

```bash
git clone https://github.com/vonstegen/resonant-vcs.git
cd resonant-vcs
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -e ".[all]"
npm install
```

### 4. Verify Installation

```bash
pytest
avcs --version
```

---

## Project Structure

```
src/resonant_vcs/
├── core/           # VCS engine (database, storage, repository)
├── ai/             # AI layer (providers, intent, features)
├── cli/            # Command-line interface
├── api/            # FastAPI REST API
└── utils/          # Utilities (config, etc.)

src/ui/             # React frontend
tests/              # Python tests
docs/               # Documentation
```

---

## Running Development Servers

### Backend (CLI)

```bash
# From .venv
avcs --help

# Or run directly
python -m resonant_vcs.cli.main --help
```

### API Server

```bash
avcs serve
# or
python -m resonant_vcs.api.main
```

### Web UI (Frontend)

```bash
npm run dev
```

---

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=resonant_vcs --cov-report=html

# Watch mode
pytest --watch

# Specific test file
pytest tests/test_core.py

# Specific test
pytest tests/test_core.py::test_init
```

---

## Code Style

### Python

- Type hints required
- Async/await for I/O
- PEP 8 with Black formatting
- Docstrings for public functions

```bash
# Format code
black src/

# Lint
ruff src/

# Type check
mypy src/
```

### TypeScript/React

- Functional components only
- TypeScript strict mode
- Hooks for state management

```bash
# Format
npm run format

# Lint
npm run lint
```

---

## Adding New Commands

### CLI Commands

Add to `src/resonant_vcs/cli/main.py`:

```python
@cli.command()
@click.argument("arg")
@click.option("-o", "--option", help="Option description")
def newcommand(arg: str, option: str | None):
    """Description of command."""
    # Implementation
    pass
```

### API Endpoints

Add to `src/resonant_vcs/api/main.py`:

```python
@app.get("/path/{param}")
async def endpoint(param: str):
    """Endpoint description."""
    return {"result": "value"}
```

---

## Adding AI Features

### 1. Create Provider (if needed)

```python
# src/resonant_vcs/ai/my_provider.py
from .base import AIProvider, AIResponse

class MyProvider(AIProvider):
    def is_available(self) -> bool:
        # Check if provider is running
        pass
    
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        # Call provider API
        pass
```

### 2. Register in Switcher

Edit `src/resonant_vcs/ai/switcher.py`:

```python
def _initialize_providers(self):
    # Add your provider
    if MyProvider().is_available():
        self._providers["my"] = MyProvider()
```

### 3. Create Feature

```python
# src/resonant_vcs/ai/features/my_feature.py
class MyFeature:
    def __init__(self, switcher: AISwitcher):
        self.switcher = switcher
    
    def run(self, context: dict) -> str:
        # AI-powered feature logic
        pass
```

---

## Database Changes

### Schema Updates

Edit `src/resonant_vcs/core/database.py`:

```python
SCHEMA = """
-- Add new tables or columns
CREATE TABLE IF NOT EXISTS new_table (
    id TEXT PRIMARY KEY,
    ...
);
"""
```

### Migrations

For now, database is recreated on `avcs init`. Future versions will include migration support.

---

## Commit Guidelines

### Format

```
type(scope): description

[optional body]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code restructure |
| `test` | Tests |
| `ai` | AI-related changes |

### Examples

```bash
git commit -m "feat: add branch delete command"
git commit -m "fix: correct file path handling"
git commit -m "docs: add API reference"
```

---

## Branch Strategy

- `main` — Stable releases
- `develop` — Integration branch (future)
- `feature/*` — Feature development
- `fix/*` — Bug fixes

### Creating Feature Branch

```bash
git checkout -b feature/my-feature
# Make changes
git commit -m "feat: implement my feature"
git push origin feature/my-feature
```

---

## Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Update documentation if needed
6. Submit PR with description

---

## Debugging

### CLI Debugging

```bash
# Add print statements
print(f"Debug: {variable}")

# Use rich console
from rich.console import Console
console = Console()
console.print(f"[red]Error: {error}[/red]")
```

### API Debugging

```bash
# Run with verbose logging
LOG_LEVEL=debug avcs serve

# Check API docs
curl http://localhost:8000/docs
```

### Python Debugging

```bash
# Use pdb
python -m pdb -c continue -m resonant_vcs.cli.main

# Or in code
import pdb; pdb.set_trace()
```

---

## Performance Profiling

```bash
# Profile Python code
python -m cProfile -s cumulative -m resonant_vcs.cli.main

# Memory profiling
python -m memory_profiler script.py
```

---

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag
4. Build package
5. Publish to PyPI

---

## Getting Help

- GitHub Issues: https://github.com/vonstegen/resonant-vcs/issues
- Documentation: `/docs`
- Code: Well-commented, self-documenting

---

## Next Steps

- [Architecture Overview](./ARCHITECTURE.md)
- [API Reference](../api/API-REFERENCE.md)
- [Testing Guide](./TESTING.md)