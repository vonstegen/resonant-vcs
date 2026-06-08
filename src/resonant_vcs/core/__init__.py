"""Core VCS module for AugmentedVCS."""

from .database import Database, Repository, Version, Branch, FileReference
from .storage import Storage
from .repository import init, open, Repository

__all__ = [
    "Database",
    "Repository",
    "Version", 
    "Branch",
    "FileReference",
    "Storage",
    "init",
    "open",
]
