# Testing Guide

How to test AugmentedVCS.

---

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=resonant_vcs --cov-report=html
# View: open htmlcov/index.html
```

### Watch Mode

```bash
pytest --watch
```

---

## Test Structure

```
tests/
├── test_core.py        # Core VCS operations
├── test_ai.py          # AI/intent parsing
└── test_integration.py # Full workflows
```

---

## Writing Tests

### Basic Test

```python
# tests/test_example.py
import pytest
from resonant_vcs.core.repository import init

def test_example():
    # Arrange
    # Act
    # Assert
    assert True
```

### Using Fixtures

```python
@pytest.fixture
def temp_repo():
    """Create a temporary repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test_repo"
        path.mkdir()
        yield path

def test_init(temp_repo):
    repo = init(temp_repo)
    assert repo.exists()
```

---

## Test Categories

### Unit Tests
- Test individual functions
- Fast, isolated
- `tests/test_core.py`

### Integration Tests
- Test full workflows
- Slower, but comprehensive
- `tests/test_integration.py`

### AI Tests
- Test intent parsing
- Mock or use real Ollama
- `tests/test_ai.py`

---

## Coverage Requirements

| Module | Target |
|--------|--------|
| Database | 80%+ |
| Repository | 70%+ |
| Intent Classifier | 90%+ |

---

## CI/CD

Tests run on every push via GitHub Actions.

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest
```

---

## Debugging Failed Tests

```bash
# Run single test
pytest tests/test_core.py::test_init -v

# Show print output
pytest -s

# Drop into debugger on failure
pytest --pdb
```