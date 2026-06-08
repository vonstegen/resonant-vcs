"""AI-powered commit message suggestion."""

from typing import Optional
from ..switcher import AISwitcher, AIConfig


SYSTEM_PROMPT = """You are a helpful assistant that suggests clear, concise commit messages.
Follow these conventions:
- Use imperative mood ("Add", "Fix", "Update" not "Added", "Fixed")
- Keep messages under 72 characters
- Start with a capital letter
- No period at the end
- Be specific about what changed

Examples:
- "Add user authentication"
- "Fix null pointer in login handler"
- "Update README with installation steps"
- "Remove deprecated API endpoints"

Just respond with the commit message, nothing else."""


class CommitSuggester:
    """Suggests commit messages based on changed files."""

    def __init__(self, switcher: Optional[AISwitcher] = None):
        self.switcher = switcher or AISwitcher()
        self.system_prompt = SYSTEM_PROMPT

    def suggest(self, staged_files: list[tuple[str, str]], diff_content: str = "") -> str:
        """Suggest a commit message based on staged files and diff."""
        if not staged_files:
            return "No files staged for commit"

        # Build context about what changed
        file_names = [path for path, _ in staged_files]
        file_summary = ", ".join(file_names)

        user_prompt = f"Suggest a commit message for changes to these files:\n{file_summary}"

        if diff_content:
            user_prompt += f"\n\nHere are the changes:\n{diff_content[:500]}"

        response = self.switcher.generate(
            f"{self.system_prompt}\n\n{user_prompt}"
        )

        if response.error:
            return self._fallback_suggest(file_names)

        return response.content.strip()

    def _fallback_suggest(self, file_names: list[str]) -> str:
        """Fallback suggestion when AI is unavailable."""
        if len(file_names) == 1:
            return f"Update {file_names[0]}"
        elif len(file_names) <= 3:
            return f"Update {', '.join(file_names[:-1])} and {file_names[-1]}"
        else:
            return f"Update {len(file_names)} files"

    def explain_change(self, file_path: str, diff: str) -> str:
        """Explain what a file change means in plain language."""
        user_prompt = f"""Explain this code change in simple terms for a non-technical person.
Focus on WHY this change was made, not technical details.

File: {file_path}
Changes:
{diff[:1000]}

Explain in 1-2 sentences:"""

        response = self.switcher.generate(user_prompt)

        if response.error:
            return f"Changed {file_path}"

        return response.content.strip()