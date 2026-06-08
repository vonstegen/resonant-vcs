"""Integration tests for full workflow."""

import pytest
import tempfile
from pathlib import Path

from resonant_vcs.core.repository import init, open
from resonant_vcs.ai.intent import IntentClassifier, IntentMapper, VCSIntent


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test_repo"
        repo_path.mkdir()
        yield repo_path


@pytest.fixture
def initialized_repo(temp_repo):
    """Create an initialized repository."""
    repo = init(temp_repo, "Test repository")
    yield repo
    repo.close()


def test_full_workflow(initialized_repo):
    """Test complete workflow: add, commit, branch, merge."""
    repo = initialized_repo
    repo_path = repo.path

    # Create first file
    file1 = repo_path / "README.md"
    file1.write_text("# Project\n\nMy awesome project.")
    repo.add(file1)
    v1 = repo.commit("Add README")

    assert v1 is not None
    assert v1.message == "Add README"

    # Create second file
    file2 = repo_path / "main.py"
    file2.write_text("print('hello')")
    repo.add(file2)
    v2 = repo.commit("Add main script")

    assert len(repo.log()) == 2

    # Create branch
    repo.branch_create("feature")
    branches = repo.branch_list()
    assert len(branches) == 2

    # Switch branch and make changes
    repo.checkout_branch("feature")
    file2.write_text("print('hello world')")
    repo.add(file2)
    v3 = repo.commit("Update main script")

    # All versions exist in repo (log shows all versions)
    assert len(repo.log()) == 3

    # Switch back to main
    repo.checkout_branch("main")
    # Check branch heads
    main_branch = repo.db.get_branch(repo.get_repo_record().id, "main")
    feature_branch = repo.db.get_branch(repo.get_repo_record().id, "feature")
    assert main_branch.head_version_id == v2.id  # Main ends at v2
    assert feature_branch.head_version_id == v3.id  # Feature ends at v3


def test_ai_intent_workflow(temp_repo):
    """Test AI intent classification workflow."""
    repo = init(temp_repo)

    # Create a test file
    file1 = temp_repo / "test.txt"
    file1.write_text("Hello")
    repo.add(file1)
    repo.commit("Initial")

    # Test intent classifier
    classifier = IntentClassifier()
    mapper = IntentMapper(repo)

    # Test various intents
    test_cases = [
        ("add test.txt", VCSIntent.ADD),
        ("commit my changes", VCSIntent.COMMIT),
        ("show me the history", VCSIntent.LOG),
        ("what changed", VCSIntent.STATUS),
        ("create new branch", VCSIntent.BRANCH_CREATE),
    ]

    for text, expected_intent in test_cases:
        parsed = classifier.classify(text)
        assert parsed.intent == expected_intent, f"Expected {expected_intent} for '{text}'"


def test_status_accurate(initialized_repo):
    """Test that status accurately reflects state."""
    repo = initialized_repo
    repo_path = repo.path

    # Initial status
    status = repo.status()
    assert status["initialized"]
    assert status["branch"] == "main"
    assert len(status["staged"]) == 0

    # Add a file
    file1 = repo_path / "test.txt"
    file1.write_text("Hello")
    repo.add(file1)

    status = repo.status()
    assert len(status["staged"]) == 1
    assert status["staged"][0][0] == "test.txt"

    # Commit and check status again
    repo.commit("Add test file")
    status = repo.status()
    assert len(status["staged"]) == 0  # Cleared after commit


def test_diff_between_versions(initialized_repo):
    """Test diff between versions."""
    repo = initialized_repo
    repo_path = repo.path

    # Create version 1
    file1 = repo_path / "file.txt"
    file1.write_text("Version 1")
    repo.add(file1)
    v1 = repo.commit("Version 1")

    # Modify and create version 2
    file1.write_text("Version 2")
    repo.add(file1)
    v2 = repo.commit("Version 2")

    # Diff between versions
    changes = repo.diff(v1.id, v2.id)
    assert len(changes) == 1
    assert changes[0]["type"] == "modified"
    assert changes[0]["path"] == "file.txt"


def test_unstage_and_restore(initialized_repo):
    """Test unstage and restore functionality."""
    repo = initialized_repo
    repo_path = repo.path

    # Create and commit initial file
    file1 = repo_path / "test.txt"
    file1.write_text("Original content")
    repo.add(file1)
    repo.commit("Initial")

    # Modify but don't commit yet
    file1.write_text("Modified content")
    repo.add(file1)

    # Check status shows modified
    status = repo.status()
    assert "modified" in status
    assert "test.txt" in status["modified"]

    # Unstage
    repo.unstage(file1)
    status = repo.status()
    assert "test.txt" not in status.get("modified", [])

    # Restore from last commit
    repo.restore(file1)
    assert file1.read_text() == "Original content"


def test_checkout_version_restores_files(initialized_repo):
    """Test that checkout restores files correctly."""
    repo = initialized_repo
    repo_path = repo.path

    # Version 1
    file1 = repo_path / "file.txt"
    file1.write_text("Version 1 content")
    repo.add(file1)
    v1 = repo.commit("Version 1")

    # Version 2 (modify file)
    file1.write_text("Version 2 content")
    repo.add(file1)
    repo.commit("Version 2")

    # Checkout version 1
    repo.checkout_version(v1.id)
    assert file1.read_text() == "Version 1 content"
