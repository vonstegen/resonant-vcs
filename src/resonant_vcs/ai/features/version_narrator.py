"""Version history narrator - tells version history as a story."""

from typing import Optional
from ..switcher import AISwitcher


class VersionNarrator:
    """Tells version history as an engaging narrative."""

    def __init__(self, switcher: Optional[AISwitcher] = None):
        self.switcher = switcher or AISwitcher()

    def narrate_versions(self, versions: list[dict], max_count: int = 10) -> str:
        """Tell the version history as a story."""
        if not versions:
            return "This project has no history yet. Start by creating your first version!"

        versions = versions[:max_count]

        # Build version list for context
        version_list = []
        for i, v in enumerate(versions):
            msg = v.get("message", "No message")
            date = v.get("date", "unknown date")
            version_list.append(f"{i+1}. {msg} ({date})")

        versions_text = "\n".join(version_list)

        user_prompt = f"""Tell the history of this project as a compelling story:

{versions_text}

Weave these into a narrative that explains the project's journey.
Make it engaging but concise (2-3 paragraphs):"""

        response = self.switcher.generate(user_prompt)

        if response.error:
            return self._fallback_narrate(versions)

        return response.content.strip()

    def _fallback_narrate(self, versions: list[dict]) -> str:
        """Fallback when AI unavailable."""
        if len(versions) == 1:
            return f"Started with: '{versions[0].get('message')}'"

        summary = [f"- {v.get('message')}" for v in versions[:5]]
        return "Project history:\n" + "\n".join(summary)

    def narrate_commit(self, version: dict, previous_version: Optional[dict] = None) -> str:
        """Tell a single commit as a mini-story."""
        msg = version.get("message", "No message")
        date = version.get("date", "unknown")

        if previous_version:
            user_prompt = f"""Tell this change as a brief story:

"{msg}" on {date}

This follows "{previous_version.get('message', 'unknown')}"

Explain what happened in 1-2 sentences:"""
        else:
            user_prompt = f"""Tell this as a story opening:

"{msg}" on {date}

This is the first version. Explain what started in 1-2 sentences:"""

        response = self.switcher.generate(user_prompt)

        if response.error:
            return msg

        return response.content.strip()
