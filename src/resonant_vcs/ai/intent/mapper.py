"""Maps intents to VCS operations."""

from typing import Protocol
from .classifier import ParsedIntent, VCSIntent


class RepositoryProtocol(Protocol):
    """Protocol for repository interface."""
    def add(self, file_path): ...
    def commit(self, message, author="user"): ...
    def log(self, max_count=50): ...
    def status(self): ...
    def checkout_version(self, version_id): ...
    def checkout_branch(self, branch_name): ...
    def branch_create(self, name): ...
    def branch_list(self): ...
    def branch_delete(self, name): ...
    def diff(self, version_a_id, version_b_id): ...
    def diff_staged(self): ...
    def restore(self, file_path): ...
    def unstage(self, file_path): ...


class IntentMapper:
    """Maps parsed intents to repository operations."""

    def __init__(self, repo):
        self.repo: RepositoryProtocol = repo

    def execute(self, parsed: ParsedIntent) -> dict:
        """Execute the intent and return results."""
        intent = parsed.intent
        entities = parsed.entities

        try:
            if intent == VCSIntent.INIT:
                return {"success": True, "message": "Repository already initialized"}

            elif intent == VCSIntent.ADD:
                file = entities.get("file", "test.txt")
                self.repo.add(file)
                return {"success": True, "message": f"Staged: {file}"}

            elif intent == VCSIntent.COMMIT:
                message = entities.get("message", "Auto-saved changes")
                version = self.repo.commit(message)
                return {
                    "success": True,
                    "message": f"Created commit {version.id[:8]}",
                    "version_id": version.id
                }

            elif intent == VCSIntent.LOG:
                versions = self.repo.log()
                return {
                    "success": True,
                    "versions": [
                        {"id": v.id[:8], "message": v.message, "date": str(v.created_at)}
                        for v in versions
                    ]
                }

            elif intent == VCSIntent.STATUS:
                status = self.repo.status()
                return {"success": True, "status": status}

            elif intent == VCSIntent.CHECKOUT:
                version_id = entities.get("version_id")
                if version_id:
                    self.repo.checkout_version(version_id)
                    return {"success": True, "message": f"Checked out {version_id[:8]}"}
                return {"success": False, "message": "No version specified"}

            elif intent == VCSIntent.BRANCH_CREATE:
                name = entities.get("branch_name", "feature")
                self.repo.branch_create(name)
                return {"success": True, "message": f"Created branch: {name}"}

            elif intent == VCSIntent.BRANCH_LIST:
                branches = self.repo.branch_list()
                return {
                    "success": True,
                    "branches": [b.name for b in branches]
                }

            elif intent == VCSIntent.BRANCH_SWITCH:
                name = entities.get("branch_name")
                if name:
                    self.repo.checkout_branch(name)
                    return {"success": True, "message": f"Switched to {name}"}
                return {"success": False, "message": "No branch specified"}

            elif intent == VCSIntent.BRANCH_DELETE:
                name = entities.get("branch_name")
                if name:
                    self.repo.branch_delete(name)
                    return {"success": True, "message": f"Deleted branch: {name}"}
                return {"success": False, "message": "No branch specified"}

            elif intent == VCSIntent.DIFF:
                changes = self.repo.diff_staged()
                return {"success": True, "changes": changes}

            elif intent == VCSIntent.RESTORE:
                file = entities.get("file")
                if file:
                    self.repo.restore(file)
                    return {"success": True, "message": f"Restored: {file}"}
                return {"success": False, "message": "No file specified"}

            elif intent == VCSIntent.UNSTAGE:
                file = entities.get("file")
                if file:
                    self.repo.unstage(file)
                    return {"success": True, "message": f"Unstaged: {file}"}
                return {"success": False, "message": "No file specified"}

            else:
                return {"success": False, "message": "Unknown command"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}