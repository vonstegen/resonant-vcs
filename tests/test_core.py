"""Tests for core VCS operations."""

import pytest
import tempfile
from pathlib import Path

from resonant_vcs.core.repository import init, open
from resonant_vcs.core.database import Database


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test_repo"
        repo_path.mkdir()
        yield repo_path


def test_init(temp_repo):
    """Test repository initialization."""
    repo = init(temp_repo, "Test repository")

    assert repo.exists()
    assert repo.db_path.exists()
    assert (temp_repo / ".avcs").exists()


def test_add_and_commit(temp_repo):
    """Test adding and committing files."""
    repo = init(temp_repo)

    # Create a test file
    test_file = temp_repo / "test.txt"
    test_file.write_text("Hello, World!")

    # Stage and commit
    repo.add(test_file)
    version = repo.commit("Initial commit")

    assert version is not None
    assert version.message == "Initial commit"


def test_log(temp_repo):
    """Test version history."""
    repo = init(temp_repo)

    # Create multiple commits
    for i in range(3):
        test_file = temp_repo / f"file{i}.txt"
        test_file.write_text(f"Content {i}")
        repo.add(test_file)
        repo.commit(f"Commit {i}")

    versions = repo.log()
    assert len(versions) == 3


def test_branch(temp_repo):
    """Test branch operations."""
    repo = init(temp_repo)

    repo.branch_create("feature")
    branches = repo.branch_list()

    assert len(branches) == 2  # main + feature
    assert any(b.name == "feature" for b in branches)


def test_status(temp_repo):
    """Test status command."""
    repo = init(temp_repo)

    # Check status before any changes
    status = repo.status()
    assert status["initialized"]
    assert status["branch"] == "main"


def test_diff(temp_repo):
    """Test diff functionality."""
    repo = init(temp_repo)

    # Create initial file
    test_file = temp_repo / "test.txt"
    test_file.write_text("Hello")
    repo.add(test_file)
    repo.commit("Initial")

    # Modify the file
    test_file.write_text("Hello, World!")
    repo.add(test_file)

    changes = repo.diff_staged()
    assert len(changes) == 1
    assert changes[0]["type"] == "modified"
