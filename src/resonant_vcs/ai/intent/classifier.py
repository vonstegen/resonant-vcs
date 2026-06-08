"""Intent classification for natural language VCS commands."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class VCSIntent(Enum):
    """Possible VCS intents."""
    INIT = "init"
    ADD = "add"
    COMMIT = "commit"
    LOG = "log"
    STATUS = "status"
    CHECKOUT = "checkout"
    BRANCH_CREATE = "branch_create"
    BRANCH_LIST = "branch_list"
    BRANCH_SWITCH = "branch_switch"
    BRANCH_DELETE = "branch_delete"
    DIFF = "diff"
    RESTORE = "restore"
    UNSTAGE = "unstage"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """A parsed user intent."""
    intent: VCSIntent
    confidence: float
    entities: dict
    raw_text: str
    suggestion: Optional[str] = None


# Keywords that indicate each intent
INTENT_KEYWORDS = {
    VCSIntent.INIT: ["init", "initialize", "new repo", "start", "create repo"],
    VCSIntent.ADD: ["add", "stage", "track", "include", "save for commit"],
    VCSIntent.COMMIT: ["commit", "save", "save version", "save changes", "checkpoint"],
    VCSIntent.LOG: ["log", "history", "commits", "versions", "what happened", "show history"],
    VCSIntent.STATUS: ["status", "what's changed", "changed", "pending", "staged"],
    VCSIntent.CHECKOUT: ["checkout", "switch to", "go to", "restore version"],
    VCSIntent.BRANCH_CREATE: ["new branch", "create branch", "branch", "start feature"],
    VCSIntent.BRANCH_LIST: ["branches", "list branches", "show branches", "what branches"],
    VCSIntent.BRANCH_SWITCH: ["switch branch", "change branch", "go to branch"],
    VCSIntent.BRANCH_DELETE: ["delete branch", "remove branch"],
    VCSIntent.DIFF: ["diff", "compare", "changes", "difference", "what changed"],
    VCSIntent.RESTORE: ["restore", "revert", "undo", "get back"],
    VCSIntent.UNSTAGE: ["unstage", "remove from staging", "untrack"],
    VCSIntent.HELP: ["help", "what can i do", "commands", "how do i"],
}


class IntentClassifier:
    """Classifies natural language into VCS intents."""

    def __init__(self):
        self.intents = INTENT_KEYWORDS

    def classify(self, text: str) -> ParsedIntent:
        """Classify user text into a VCS intent."""
        text = text.lower().strip()

        scores = {}
        for intent, keywords in self.intents.items():
            scores[intent] = 0
            for keyword in keywords:
                if keyword in text:
                    scores[intent] += 1

        # Find highest scoring intent
        if max(scores.values()) > 0:
            best_intent = max(scores, key=scores.get)
            confidence = scores[best_intent] / max(sum(scores.values()), 1)
        else:
            best_intent = VCSIntent.UNKNOWN
            confidence = 0.0

        entities = self._extract_entities(text, best_intent)
        suggestion = self._get_suggestion(best_intent, entities)

        return ParsedIntent(
            intent=best_intent,
            confidence=confidence,
            entities=entities,
            raw_text=text,
            suggestion=suggestion
        )

    def _extract_entities(self, text: str, intent: VCSIntent) -> dict:
        """Extract relevant entities from the text."""
        entities = {}

        # Extract branch names (look for pattern like "branch <name>" or "new <name> branch")
        import re
        branch_patterns = [
            r'(?:new|create|to)?\s*branch\s+([a-zA-Z0-9_-]+)',
            r'([a-zA-Z0-9_-]+)\s*branch',
            r'feature[-_]?([a-zA-Z0-9_-]+)',
        ]
        for pattern in branch_patterns:
            match = re.search(pattern, text)
            if match:
                entities["branch_name"] = match.group(1)
                break

        # Extract version/commit ID (short hash)
        import re
        hash_pattern = r'[a-f0-9]{7,40}'
        hashes = re.findall(hash_pattern, text)
        if hashes:
            entities["version_id"] = hashes[0]

        # Extract file paths
        file_pattern = r'[\w\-./\\]+\.\w+'
        files = re.findall(file_pattern, text)
        if files:
            entities["file"] = files[0]

        # Extract commit message keywords
        if "message" in text or "commit" in text:
            msg_match = re.search(r'["\'](.+?)["\']', text)
            if msg_match:
                entities["message"] = msg_match.group(1)

        return entities

    def _get_suggestion(self, intent: VCSIntent, entities: dict) -> Optional[str]:
        """Get a suggestion for how to execute this intent."""
        suggestions = {
            VCSIntent.INIT: "avcs init",
            VCSIntent.ADD: "avcs add <file>",
            VCSIntent.COMMIT: "avcs commit -m 'message'",
            VCSIntent.LOG: "avcs log",
            VCSIntent.STATUS: "avcs status",
            VCSIntent.CHECKOUT: f'avcs checkout {entities.get("version_id", "<version>")}',
            VCSIntent.BRANCH_CREATE: f'avcs branch {entities.get("branch_name", "<name>")}',
            VCSIntent.BRANCH_LIST: "avcs branch",
            VCSIntent.BRANCH_SWITCH: f'avcs checkout -b {entities.get("branch_name", "<name>")}',
            VCSIntent.DIFF: "avcs diff",
            VCSIntent.RESTORE: f'avcs restore {entities.get("file", "<file>")}',
            VCSIntent.UNSTAGE: "avcs unstage <file>",
        }
        return suggestions.get(intent)