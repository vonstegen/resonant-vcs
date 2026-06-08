"""Database schema and operations for AugmentedVCS."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid


@dataclass
class Repository:
    """Represents a VCS repository."""
    id: str
    path: Path
    created_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None


@dataclass
class FileReference:
    """Tracks a file at a specific version."""
    id: str
    repo_id: str
    path: str
    hash: str


@dataclass
class Version:
    """Represents a commit/snapshot."""
    id: str
    repo_id: str
    message: str
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    author: str = "user"


@dataclass
class Branch:
    """Represents a branch."""
    id: str
    repo_id: str
    name: str
    head_version_id: Optional[str] = None


class Database:
    """SQLite database for AugmentedVCS."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS repositories (
        id TEXT PRIMARY KEY,
        path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        repo_id TEXT NOT NULL,
        path TEXT NOT NULL,
        hash TEXT NOT NULL,
        FOREIGN KEY (repo_id) REFERENCES repositories(id)
    );

    CREATE TABLE IF NOT EXISTS versions (
        id TEXT PRIMARY KEY,
        repo_id TEXT NOT NULL,
        message TEXT NOT NULL,
        parent_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        author TEXT DEFAULT 'user',
        FOREIGN KEY (repo_id) REFERENCES repositories(id),
        FOREIGN KEY (parent_id) REFERENCES versions(id)
    );

    CREATE TABLE IF NOT EXISTS branches (
        id TEXT PRIMARY KEY,
        repo_id TEXT NOT NULL,
        name TEXT NOT NULL UNIQUE,
        head_version_id TEXT,
        FOREIGN KEY (repo_id) REFERENCES repositories(id),
        FOREIGN KEY (head_version_id) REFERENCES versions(id)
    );

    CREATE TABLE IF NOT EXISTS staged_files (
        id TEXT PRIMARY KEY,
        repo_id TEXT NOT NULL,
        path TEXT NOT NULL,
        hash TEXT NOT NULL,
        FOREIGN KEY (repo_id) REFERENCES repositories(id)
    );

    CREATE TABLE IF NOT EXISTS version_files (
        version_id TEXT NOT NULL,
        path TEXT NOT NULL,
        hash TEXT NOT NULL,
        PRIMARY KEY (version_id, path),
        FOREIGN KEY (version_id) REFERENCES versions(id)
    );

    CREATE INDEX IF NOT EXISTS idx_files_repo ON files(repo_id);
    CREATE INDEX IF NOT EXISTS idx_versions_repo ON versions(repo_id);
    CREATE INDEX IF NOT EXISTS idx_branches_repo ON branches(repo_id);
    CREATE INDEX IF NOT EXISTS idx_staged_repo ON staged_files(repo_id);
    CREATE INDEX IF NOT EXISTS idx_version_files ON version_files(version_id);
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to the database."""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def initialize(self) -> None:
        """Create all tables."""
        if not self._conn:
            self.connect()
        self._conn.executescript(self.SCHEMA)
        self._conn.commit()

    @property
    def conn(self) -> sqlite3.Connection:
        """Get the connection, connecting if necessary."""
        if not self._conn:
            self.connect()
        return self._conn

    def create_repository(self, path: Path, description: str = None) -> Repository:
        """Create a new repository record."""
        repo = Repository(
            id=str(uuid.uuid4()),
            path=path,
            description=description
        )
        self.conn.execute(
            "INSERT INTO repositories (id, path, description) VALUES (?, ?, ?)",
            (repo.id, str(path), repo.description)
        )
        self.conn.commit()
        return repo

    def get_repository(self, path: Path) -> Optional[Repository]:
        """Get repository by path."""
        row = self.conn.execute(
            "SELECT * FROM repositories WHERE path = ?",
            (str(path),)
        ).fetchone()
        if row:
            return Repository(
                id=row["id"],
                path=Path(row["path"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                description=row["description"]
            )
        return None

    def get_repository_by_id(self, repo_id: str) -> Optional[Repository]:
        """Get repository by ID."""
        row = self.conn.execute(
            "SELECT * FROM repositories WHERE id = ?",
            (repo_id,)
        ).fetchone()
        if row:
            return Repository(
                id=row["id"],
                path=Path(row["path"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                description=row["description"]
            )
        return None

    def stage_file(self, repo_id: str, path: str, file_hash: str) -> None:
        """Stage a file for commit."""
        # Remove if already staged
        self.conn.execute(
            "DELETE FROM staged_files WHERE repo_id = ? AND path = ?",
            (repo_id, path)
        )
        self.conn.execute(
            "INSERT INTO staged_files (id, repo_id, path, hash) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), repo_id, path, file_hash)
        )
        self.conn.commit()

    def unstage_file(self, repo_id: str, path: str) -> None:
        """Unstage a file."""
        self.conn.execute(
            "DELETE FROM staged_files WHERE repo_id = ? AND path = ?",
            (repo_id, path)
        )
        self.conn.commit()

    def get_staged_files(self, repo_id: str) -> list[tuple[str, str]]:
        """Get all staged files as (path, hash) tuples."""
        rows = self.conn.execute(
            "SELECT path, hash FROM staged_files WHERE repo_id = ?",
            (repo_id,)
        ).fetchall()
        return [(r["path"], r["hash"]) for r in rows]

    def clear_staging(self, repo_id: str) -> None:
        """Clear all staged files."""
        self.conn.execute(
            "DELETE FROM staged_files WHERE repo_id = ?",
            (repo_id,)
        )
        self.conn.commit()

    def create_version(
        self,
        repo_id: str,
        message: str,
        parent_id: Optional[str] = None,
        author: str = "user"
    ) -> Version:
        """Create a new version (commit)."""
        version = Version(
            id=str(uuid.uuid4()),
            repo_id=repo_id,
            message=message,
            parent_id=parent_id,
            author=author
        )
        self.conn.execute(
            """INSERT INTO versions (id, repo_id, message, parent_id, author)
               VALUES (?, ?, ?, ?, ?)""",
            (version.id, repo_id, message, parent_id, author)
        )
        self.conn.commit()
        return version

    def get_versions(self, repo_id: str) -> list[Version]:
        """Get all versions for a repository, newest first."""
        rows = self.conn.execute(
            "SELECT * FROM versions WHERE repo_id = ? ORDER BY created_at DESC",
            (repo_id,)
        ).fetchall()
        return [
            Version(
                id=row["id"],
                repo_id=row["repo_id"],
                message=row["message"],
                parent_id=row["parent_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                author=row["author"]
            )
            for row in rows
        ]

    def get_version_by_id(self, version_id: str) -> Optional[Version]:
        """Get a version by ID."""
        row = self.conn.execute(
            "SELECT * FROM versions WHERE id = ?",
            (version_id,)
        ).fetchone()
        if row:
            return Version(
                id=row["id"],
                repo_id=row["repo_id"],
                message=row["message"],
                parent_id=row["parent_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                author=row["author"]
            )
        return None

    def get_files_at_version(self, version_id: str) -> list[FileReference]:
        """Get all files tracked at a specific version."""
        rows = self.conn.execute(
            "SELECT * FROM version_files WHERE version_id = ?",
            (version_id,)
        ).fetchall()
        repo = self.conn.execute("SELECT repo_id FROM versions WHERE id = ?", (version_id,)).fetchone()
        repo_id = repo["repo_id"] if repo else ""
        return [
            FileReference(
                id=str(uuid.uuid4()),
                repo_id=repo_id,
                path=row["path"],
                hash=row["hash"]
            )
            for row in rows
        ]

    def track_files_for_version(self, version_id: str, files: list[tuple[str, str]]) -> None:
        """"Track which files were part of a version snapshot."""
        for path, file_hash in files:
            self.conn.execute(
                "INSERT OR REPLACE INTO version_files (version_id, path, hash) VALUES (?, ?, ?)",
                (version_id, path, file_hash)
            )
        self.conn.commit()

    def track_file(self, repo_id: str, path: str, file_hash: str) -> None:
        """Track a file at the current version."""
        # Remove old entry for this path
        self.conn.execute(
            "DELETE FROM files WHERE repo_id = ? AND path = ?",
            (repo_id, path)
        )
        self.conn.execute(
            "INSERT INTO files (id, repo_id, path, hash) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), repo_id, path, file_hash)
        )
        self.conn.commit()

    def get_tracked_files(self, repo_id: str) -> list[FileReference]:
        """Get all currently tracked files."""
        rows = self.conn.execute(
            "SELECT * FROM files WHERE repo_id = ?",
            (repo_id,)
        ).fetchall()
        return [
            FileReference(
                id=row["id"],
                repo_id=row["repo_id"],
                path=row["path"],
                hash=row["hash"]
            )
            for row in rows
        ]

    def create_branch(
        self,
        repo_id: str,
        name: str,
        head_version_id: Optional[str] = None
    ) -> Branch:
        """Create a new branch."""
        branch = Branch(
            id=str(uuid.uuid4()),
            repo_id=repo_id,
            name=name,
            head_version_id=head_version_id
        )
        self.conn.execute(
            "INSERT INTO branches (id, repo_id, name, head_version_id) VALUES (?, ?, ?, ?)",
            (branch.id, repo_id, name, head_version_id)
        )
        self.conn.commit()
        return branch

    def get_branch(self, repo_id: str, name: str) -> Optional[Branch]:
        """Get a branch by name."""
        row = self.conn.execute(
            "SELECT * FROM branches WHERE repo_id = ? AND name = ?",
            (repo_id, name)
        ).fetchone()
        if row:
            return Branch(
                id=row["id"],
                repo_id=row["repo_id"],
                name=row["name"],
                head_version_id=row["head_version_id"]
            )
        return None

    def get_branches(self, repo_id: str) -> list[Branch]:
        """Get all branches for a repository."""
        rows = self.conn.execute(
            "SELECT * FROM branches WHERE repo_id = ?",
            (repo_id,)
        ).fetchall()
        return [
            Branch(
                id=row["id"],
                repo_id=row["repo_id"],
                name=row["name"],
                head_version_id=row["head_version_id"]
            )
            for row in rows
        ]

    def update_branch_head(self, branch_name: str, repo_id: str, version_id: str) -> None:
        """Update the HEAD of a branch."""
        self.conn.execute(
            "UPDATE branches SET head_version_id = ? WHERE repo_id = ? AND name = ?",
            (version_id, repo_id, branch_name)
        )
        self.conn.commit()

    def delete_branch(self, repo_id: str, name: str) -> None:
        """Delete a branch."""
        self.conn.execute(
            "DELETE FROM branches WHERE repo_id = ? AND name = ?",
            (repo_id, name)
        )
        self.conn.commit()

    def get_current_branch(self, repo_id: str) -> Optional[str]:
        """Get the current branch name."""
        row = self.conn.execute(
            "SELECT value FROM repository_meta WHERE repo_id = ? AND key = 'current_branch'",
            (repo_id,)
        ).fetchone()
        return row["value"] if row else None

    def set_current_branch(self, repo_id: str, branch_name: str) -> None:
        """Set the current branch."""
        # Ensure meta table exists
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS repository_meta (
               repo_id TEXT, key TEXT, value TEXT,
               PRIMARY KEY (repo_id, key))"""
        )
        self.conn.execute(
            """INSERT OR REPLACE INTO repository_meta (repo_id, key, value)
               VALUES (?, 'current_branch', ?)""",
            (repo_id, branch_name)
        )
        self.conn.commit()
