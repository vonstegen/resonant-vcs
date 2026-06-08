"""CLI module for AugmentedVCS."""

from .main import cli, main
from .conversational import ConversationalCLI
from .completions import install_completions

__all__ = ["cli", "main", "ConversationalCLI", "install_completions"]
