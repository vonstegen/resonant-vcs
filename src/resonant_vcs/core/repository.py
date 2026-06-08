"""Core repository operations for AugmentedVCS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .database import Database, Version, Branch
from .storage import Storage


class Repository:
    """The main repository class managing a VCS repository."""

    AVCS_DIR = Path(".avcs")
    DB_FILE = Path("repo.db")
    HEAD_FILE = Path("HEAD")
    CONFIG_FILE = Path("config.json")

    def __init__(self, path: Path):
        self.path = path
        self.avcs_path = path / self.AVCS_DIR
        self.db_path = self.avcs_path / "repo.db"
        self.storage = Storage(path)
        self._db: Optional[Database] = None

    @property
    def db(self) -> Database:
        """Lazy database connection."""
        if self._db is None:
            self._db = Database(self.db_path)
            self._db.connect()
        return self._db

    def exists(self) -> bool:
        """Check if this is a valid AugmentedVCS repository."""
        return self.avcs_path.exists() and self.db_path.exists()

    def initialize(self, description: str = None) -> None:
        """Initialize a new repository."""
        self.avcs_path.mkdir(parents=True, exist_ok=True)
        self.storage.initialize()
        self.db.initialize()
        self.db.create_repository(self.path, description)
        # Create default branch
        self.db.create_branch(self.db.get_repository(self.path).id, "main")
        self._write_head("main")

    def is_initialized(self) -> bool:
        """Check if repository is initialized."""
        return self.avcs_path.exists() and self.db_path.exists()

    def get_repo_record(self):
        """Get the repository database record."""
        return self.db.get_repository(self.path)

    def add(self, file_path: Path | str) -> None:
        """Stage a file for the next commit."""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Resolve relative to repo root
        if not file_path.is_absolute():
            file_path = self.path / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.is_dir():
            raise IsADirectoryError(f"Cannot add directory: {file_path}")

        # Compute hash and store
        file_hash = self.storage.store_file(file_path)

        # Get relative path
        rel_path = str(file_path.relative_to(self.path))

        # Stage in database
        repo = self.db.get_repository(self.path)
        if not repo:
            raise RuntimeError("Repository not initialized")
        self.db.stage_file(repo.id, rel_path, file_hash)

    def unstage(self, file_path: Path | str) -> None:
        """Unstage a file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.is_absolute():
            file_path = self.path / file_path

        rel_path = str(file_path.relative_to(self.path))
        repo = self.db.get_repository(self.path)
        if repo:
            self.db.unstage_file(repo.id, rel_path)

    def status(self) -> dict:
        """Get the current status of the repository."""
        repo = self.db.get_repository(self.path)
        if not repo:
            return {"initialized": False}

        staged = self.db.get_staged_files(repo.id)
        tracked = self.db.get_tracked_files(repo.id)

        # Find modified and new files
        staged_paths = {p for p, _ in staged}
        tracked_dict = {f.path: f.hash for f in tracked}
        tracked_paths = set(tracked_dict.keys())

        modified = []
        new_staged = []
        deleted = []

        # Check staged files against tracked
        for path, file_hash in staged:
            if path in tracked_paths:
                if file_hash != tracked_dict[path]:
                    modified.append(path)
            else:
                new_staged.append(path)

        # Find deleted files
        for path in tracked_paths:
            if path not in staged_paths:
                deleted.append(path)

        current_branch = self._read_head()
        return {
            "initialized": True,
            "branch": current_branch,
            "staged": staged,
            "modified": modified,
            "new_staged": new_staged,
            "deleted": deleted,
            "tracked": tracked_paths
        }

    def commit(self, message: str, author: str = "user") -> Version:
        """Create a new version (commit)."""
        repo = self.db.get_repository(self.path)
        if not repo:
            raise RuntimeError("Repository not initialized")

        staged = self.db.get_staged_files(repo.id)
        if not staged:
            raise ValueError("No files staged for commit")

        # Get parent version
        current_branch = self._read_head()
        branch = self.db.get_branch(repo.id, current_branch)
        parent_id = branch.head_version_id if branch else None

        # Create version
        version = self.db.create_version(repo.id, message, parent_id, author)

        # Track all staged files (both for the repo and for this version)
        for path, file_hash in staged:
            self.db.track_file(repo.id, path, file_hash)
        
        # Track files for this specific version snapshot
        self.db.track_files_for_version(version.id, staged)

        # Update branch head
        self.db.update_branch_head(current_branch, repo.id, version.id)

        # Clear staging
        self.db.clear_staging(repo.id)

        return version

    def log(self, max_count: int = 50) -> list[Version]:
        """Get version history."""
        repo = self.db.get_repository(self.path)
        if not repo:
            return []
        return self.db.get_versions(repo.id)[:max_count]

    def checkout_version(self, version_id: str) -> None:
        """Checkout a specific version, restoring files."""
        version = self.db.get_version_by_id(version_id)
        if not version:
            raise ValueError(f"Version not found: {version_id}")

        files = self.db.get_files_at_version(version_id)

        for file_ref in files:
            content = self.storage.retrieve(file_ref.hash)
            if content is None:
                print(f"Warning: Content missing for {file_ref.path}")
                continue

            file_path = self.path / file_ref.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)

    def checkout_branch(self, branch_name: str) -> None:
        """Switch to a branch."""
        repo = self.db.get_repository(self.path)
        if not repo:
            raise RuntimeError("Repository not initialized")

        branch = self.db.get_branch(repo.id, branch_name)
        if not branch:
            raise ValueError(f"Branch not found: {branch_name}")

        self._write_head(branch_name)

        # If branch has a head, checkout those files
        if branch.head_version_id:
            self.checkout_version(branch.head_version_id)

    def branch_create(self, name: str) -> Branch:
        """Create a new branch."""
        repo = self.db.get_repository(self.path)
        if not repo:
            raise RuntimeError("Repository not initialized")

        existing = self.db.get_branch(repo.id, name)
        if existing:
            raise ValueError(f"Branch already exists: {name}")

        # Get current branch head
        current = self._read_head()
        current_branch = self.db.get_branch(repo.id, current)
        head_id = current_branch.head_version_id if current_branch else None

        return self.db.create_branch(repo.id, name, head_id)

    def branch_delete(self, name: str) -> None:
        """Delete a branch."""
        if name == "main":
            raise ValueError("Cannot delete the main branch")

        repo = self.db.get_repository(self.path)
        if repo:
            self.db.delete_branch(repo.id, name)

    def branch_list(self) -> list[Branch]:
        """List all branches."""
        repo = self.db.get_repository(self.path)
        if not repo:
            return []
        return self.db.get_branches(repo.id)

    def diff(self, version_a_id: str, version_b_id: str) -> list[dict]:
        """Compare two versions. Returns list of changes."""
        files_a = {f.path: f.hash for f in self.db.get_files_at_version(version_a_id)}
        files_b = {f.path: f.hash for f in self.db.get_files_at_version(version_b_id)}

        all_paths = set(files_a.keys()) | set(files_b.keys())
        changes = []

        for path in sorted(all_paths):
            hash_a = files_a.get(path)
            hash_b = files_b.get(path)

            if hash_a and not hash_b:
                changes.append({"path": path, "type": "deleted"})
            elif not hash_a and hash_b:
                changes.append({"path": path, "type": "added"})
            elif hash_a != hash_b:
                changes.append({"path": path, "type": "modified"})
            # else: unchanged, skip

        return changes

    def diff_staged(self) -> list[dict]:
        """Diff staged files against tracked files."""
        repo = self.db.get_repository(self.path)
        if not repo:
            return []

        staged = dict(self.db.get_staged_files(repo.id))
        tracked = {f.path: f.hash for f in self.db.get_tracked_files(repo.id)}

        all_paths = set(staged.keys()) | set(tracked.keys())
        changes = []

        for path in sorted(all_paths):
            hash_staged = staged.get(path)
            hash_tracked = tracked.get(path)

            if hash_staged and not hash_tracked:
                changes.append({"path": path, "type": "added"})
            elif hash_staged != hash_tracked:
                changes.append({"path": path, "type": "modified"})

        return changes

    def restore(self, file_path: Path | str) -> None:
        """Restore a file from the last commit."""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.is_absolute():
            file_path = self.path / file_path

        rel_path = str(file_path.relative_to(self.path))
        current_branch = self._read_head()
        repo = self.db.get_repository(self.path)

        branch = self.db.get_branch(repo.id, current_branch)
        if not branch or not branch.head_version_id:
            raise ValueError("No commits to restore from")

        files = self.db.get_files_at_version(branch.head_version_id)
        file_ref = next((f for f in files if f.path == rel_path), None)

        if not file_ref:
            raise ValueError(f"File not tracked: {rel_path}")

        content = self.storage.retrieve(file_ref.hash)
        if content:
            file_path.write_bytes(content)

    def _write_head(self, branch_name: str) -> None:
        """Write the current branch to HEAD file."""
        head_path = self.avcs_path / self.HEAD_FILE
        head_path.write_text(f"ref: {branch_name}\n")

    def _read_head(self) -> str:
        """Read the current branch from HEAD file."""
        head_path = self.avcs_path / self.HEAD_FILE
        if head_path.exists():
            content = head_path.read_text().strip()
            if content.startswith("ref: "):
                return content[5:].strip()
        return "main"

    def close(self) -> None:
        """Close database connection."""
        if self._db:
            self._db.close()
            self._db = None


def init(path: Path, description: str = None) -> Repository:
    """Initialize a new repository."""
    repo = Repository(path)
    if repo.exists():
        raise RuntimeError(f"Repository already exists at {path}")
    repo.initialize(description)
    return repo


def open(path: Path) -> Repository:
    """Open an existing repository."""
    repo = Repository(path)
    if not repo.exists():
        raise RuntimeError(f"Not a repository: {path}")
    return repo
