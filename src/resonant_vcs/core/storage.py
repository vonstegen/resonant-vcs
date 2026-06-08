"""Content-addressed storage for AugmentedVCS."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import BinaryIO


class Storage:
    """Content-addressed file storage using SHA-256 hashing."""

    OBJECTS_DIR = Path(".avcs") / "objects"

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.objects_dir = repo_path / self.OBJECTS_DIR

    def initialize(self) -> None:
        """Create the storage directory structure."""
        self.objects_dir.mkdir(parents=True, exist_ok=True)

    def _hash_content(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    def _get_object_path(self, file_hash: str) -> Path:
        """Get the path for storing an object with this hash."""
        # Use first 2 chars as subdirectory for fan-out
        subdir = self.objects_dir / file_hash[:2]
        return subdir / file_hash[2:]

    def store(self, content: bytes) -> str:
        """Store content and return its hash."""
        file_hash = self._hash_content(content)
        object_path = self._get_object_path(file_hash)

        if not object_path.exists():
            object_path.parent.mkdir(parents=True, exist_ok=True)
            object_path.write_bytes(content)

        return file_hash

    def store_file(self, file_path: Path) -> str:
        """Store a file and return its hash."""
        content = file_path.read_bytes()
        return self.store(content)

    def retrieve(self, file_hash: str) -> bytes | None:
        """Retrieve content by hash, or None if not found."""
        object_path = self._get_object_path(file_hash)
        if object_path.exists():
            return object_path.read_bytes()
        return None

    def exists(self, file_hash: str) -> bool:
        """Check if an object exists."""
        return self._get_object_path(file_hash).exists()

    def delete(self, file_hash: str) -> bool:
        """Delete an object by hash."""
        object_path = self._get_object_path(file_hash)
        if object_path.exists():
            object_path.unlink()
            return True
        return False

    def list_objects(self) -> list[str]:
        """List all stored object hashes."""
        hashes = []
        if self.objects_dir.exists():
            for subdir in self.objects_dir.iterdir():
                if subdir.is_dir():
                    for obj_file in subdir.iterdir():
                        if obj_file.is_file():
                            # Reconstruct hash: subdir name + filename
                            hashes.append(subdir.name + obj_file.name)
        return hashes

    def get_size(self, file_hash: str) -> int:
        """Get the size of a stored object in bytes."""
        object_path = self._get_object_path(file_hash)
        if object_path.exists():
            return object_path.stat().st_size
        return 0

    def garbage_collect(self, valid_hashes: set[str]) -> int:
        """Remove orphaned objects not in valid_hashes. Returns count deleted."""
        deleted = 0
        for obj_hash in self.list_objects():
            if obj_hash not in valid_hashes:
                if self.delete(obj_hash):
                    deleted += 1
        return deleted
