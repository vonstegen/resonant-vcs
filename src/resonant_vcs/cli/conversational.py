"""Natural language conversational CLI for AugmentedVCS."""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown

from ..core.repository import open
from ..ai.intent import IntentClassifier, IntentMapper
from ..ai.features import CommitSuggester, ChangesSummarizer, VersionNarrator
from .main import find_repo, get_repo


console = Console()


class ConversationalCLI:
    """Natural language interface for AugmentedVCS."""

    WELCOME = """
# 🎉 Welcome to AugmentedVCS Assistant

I'm here to help you track your work using simple, plain English commands.

**Try saying things like:**
- "I worked on the recipe notes today — save it"
- "Show me what changed"
- "Create a branch for vacation planning"
- "Show me the history as a story"

Type `help` for all available commands or `quit` to exit.
"""

    HELP_TEXT = """
## Available Commands

### Version Control
- **"save this"** or **"commit"** — Save current changes
- **"show history"** or **"log"** — See version history
- **"what changed"** or **"status"** — See pending changes
- **"compare"** or **"diff"** — Compare versions

### Branches
- **"new branch [name]"** — Create a branch
- **"switch to [branch]"** — Switch branches
- **"show branches"** — List branches

### Files
- **"add [file]"** — Stage a file
- **"restore [file]"** — Restore from last version
- **"unstage [file]"** — Remove from staging

### AI Features
- **"suggest commit message"** — Get AI suggestion
- **"explain in plain language"** — Plain English changes
- **"tell me the story"** — Narrative history

### General
- **"help"** — Show this help
- **"quit"** or **"exit"** — Exit

Just speak naturally — I'll figure out what you need!
"""

    def __init__(self, repo_path: Optional[Path] = None):
        if repo_path is None:
            repo_path = find_repo()
            if not repo_path:
                console.print("[red]No repository found. Run 'avcs init' first.[/red]")
                sys.exit(1)

        self.repo = open(repo_path)
        self.classifier = IntentClassifier()
        self.mapper = IntentMapper(self.repo)
        self.commit_suggester = CommitSuggester()
        self.summarizer = ChangesSummarizer()
        self.narrator = VersionNarrator()
        self.context = {}
        self.running = True

    def run(self):
        """Run the conversational interface."""
        console.print(Markdown(self.WELCOME))

        while self.running:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
                if not user_input.strip():
                    continue

                response = self._process_input(user_input)
                console.print(f"\n[bold green]Assistant:[/bold green] {response}")

            except KeyboardInterrupt:
                console.print("\n[dim]Goodbye![/dim]")
                break
            except EOFError:
                break

    def _process_input(self, text: str) -> str:
        """Process natural language input."""
        text = text.strip().lower()

        # Handle special commands
        if text in ["quit", "exit", "bye"]:
            self.running = False
            return "Goodbye! Your work is safe."

        if text in ["help", "commands", "?"]:
            console.print(Markdown(self.HELP_TEXT))
            return "See the help above!"

        # Check for AI-specific commands first
        if "suggest commit" in text or "commit message" in text:
            return self._suggest_commit_message()

        if "plain language" in text or "explain" in text or "simple" in text:
            return self._explain_changes()

        if "story" in text or "narrative" in text or "tell me" in text:
            return self._tell_story()

        if "history as story" in text:
            return self._tell_full_story()

        # Use intent classifier for VCS commands
        parsed = self.classifier.classify(text)

        if parsed.confidence < 0.3:
            return (
                f"I'm not sure what you mean by '{text}'. "
                f"Try 'help' to see available commands, or rephrase your request."
            )

        # Execute the intent
        result = self.mapper.execute(parsed)

        if result["success"]:
            return self._format_success(result)
        else:
            return f"Oops! {result.get('message', 'Something went wrong')}"

    def _suggest_commit_message(self) -> str:
        """Suggest a commit message."""
        status = self.repo.status()
        staged = status.get("staged", [])

        if not staged:
            return "No files staged yet. Use 'add [file]' to stage files first."

        suggestion = self.commit_suggester.suggest(staged)
        return f"💡 Suggested commit message: *{suggestion}*"

    def _explain_changes(self) -> str:
        """Explain changes in plain language."""
        changes = self.repo.diff_staged()

        if not changes:
            return "No pending changes to explain."

        return self.summarizer.summarize(changes)

    def _tell_story(self) -> str:
        """Tell recent commits as a story."""
        versions = self.repo.log(max_count=5)
        version_dicts = [
            {
                "id": v.id[:8],
                "message": v.message,
                "date": v.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for v in versions
        ]

        return self.narrator.narrate_versions(version_dicts)

    def _tell_full_story(self) -> str:
        """Tell the complete project story."""
        versions = self.repo.log(max_count=20)
        version_dicts = [
            {
                "id": v.id[:8],
                "message": v.message,
                "date": v.created_at.strftime("%Y-%m-%d")
            }
            for v in versions
        ]

        return self.narrator.narrate_versions(version_dicts, max_count=20)

    def _format_success(self, result: dict) -> str:
        """Format a success result for display."""
        msg = result.get("message", "Done!")

        # Add extra info if available
        if "versions" in result:
            versions = result["versions"]
            if versions:
                lines = ["**Recent versions:**"]
                for v in versions[:5]:
                    lines.append(f"- {v['id']}: {v['message']}")
                return msg + "\n" + "\n".join(lines)

        if "branches" in result:
            branches = result["branches"]
            if branches:
                return msg + f"\nBranches: {', '.join(branches)}"

        if "status" in result:
            status = result["status"]
            staged_count = len(status.get("staged", []))
            if staged_count:
                return msg + f" ({staged_count} file(s) staged)"
            return msg + " (no pending changes)"

        return msg


def run_conversational(repo_path: Optional[Path] = None):
    """Run the conversational CLI."""
    cli = ConversationalCLI(repo_path)
    cli.run()