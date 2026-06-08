"""Summarizes changes in plain language."""

from typing import Optional
from ..switcher import AISwitcher


class ChangesSummarizer:
    """Summarizes version changes in plain language."""

    def __init__(self, switcher: Optional[AISwitcher] = None):
        self.switcher = switcher or AISwitcher()

    def summarize(self, changes: list[dict]) -> str:
        """Summarize a list of changes in plain language."""
        if not changes:
            return "No changes to summarize"

        added = [c["path"] for c in changes if c["type"] == "added"]
        modified = [c["path"] for c in changes if c["type"] == "modified"]
        deleted = [c["path"] for c in changes if c["type"] == "deleted"]

        user_prompt = "Summarize these changes in plain language:\n"

        if added:
            user_prompt += f"\nNew files added: {', '.join(added)}"
        if modified:
            user_prompt += f"\nFiles changed: {', '.join(modified)}"
        if deleted:
            user_prompt += f"\nFiles removed: {', '.join(deleted)}"

        user_prompt += "\n\nProvide a brief summary a non-technical person would understand:"

        response = self.switcher.generate(user_prompt)

        if response.error:
            return self._fallback_summarize(added, modified, deleted)

        return response.content.strip()

    def _fallback_summarize(self, added, modified, deleted) -> str:
        """Fallback summary when AI unavailable."""
        parts = []
        if added:
            parts.append(f"Added {len(added)} new file(s)")
        if modified:
            parts.append(f"Changed {len(modified)} file(s)")
        if deleted:
            parts.append(f"Removed {len(deleted)} file(s)")
        return "; ".join(parts) if parts else "No changes"

    def compare_versions(self, version_a: dict, version_b: dict) -> str:
        """Compare two versions in plain language."""
        user_prompt = f"""Compare these two versions and explain what changed:

Version A ({version_a.get('message', 'unknown')}): 
{version_a.get('summary', 'No summary')}

Version B ({version_b.get('message', 'unknown')}): 
{version_b.get('summary', 'No summary')}

Explain the key differences in simple terms:"""

        response = self.switcher.generate(user_prompt)

        if response.error:
            return f"Changes from '{version_a.get('message')}' to '{version_b.get('message')}'"

        return response.content.strip()