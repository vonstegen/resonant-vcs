"""Configuration management for AugmentedVCS."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class UserConfig:
    """User-level configuration."""
    name: str = "user"
    email: str = ""
    ai_provider: str = "ollama"
    ai_model: str = "llama3.2"
    ai_base_url: str = "http://localhost:11434"
    default_branch: str = "main"
    editor: str = ""
    pager: str = ""


@dataclass
class RepoConfig:
    """Repository-level configuration."""
    description: str = ""
    author: str = ""
    default_branch: str = "main"
    ai_enabled: bool = True


class ConfigManager:
    """Manages user and repository configuration."""

    GLOBAL_CONFIG_DIR = Path.home() / ".config" / "avcs"
    GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"
    REPO_CONFIG_FILE = Path(".avcs") / "config.json"

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path
        self.global_config = self._load_global_config()
        self.repo_config = self._load_repo_config() if repo_path else None

    def _load_global_config(self) -> UserConfig:
        """Load global user config."""
        if self.GLOBAL_CONFIG_FILE.exists():
            try:
                data = json.loads(self.GLOBAL_CONFIG_FILE.read_text())
                return UserConfig(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return UserConfig()

    def _load_repo_config(self) -> Optional[RepoConfig]:
        """Load repository config."""
        if self.repo_path:
            repo_config_path = self.repo_path / self.REPO_CONFIG_FILE
            if repo_config_path.exists():
                try:
                    data = json.loads(repo_config_path.read_text())
                    return RepoConfig(**data)
                except (json.JSONDecodeError, TypeError):
                    pass
        return RepoConfig()

    def save_global_config(self) -> None:
        """Save global config to file."""
        self.GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.GLOBAL_CONFIG_FILE.write_text(json.dumps(asdict(self.global_config), indent=2))

    def save_repo_config(self) -> None:
        """Save repo config to file."""
        if self.repo_path and self.repo_config:
            repo_config_path = self.repo_path / self.REPO_CONFIG_FILE
            repo_config_path.parent.mkdir(parents=True, exist_ok=True)
            repo_config_path.write_text(json.dumps(asdict(self.repo_config), indent=2))

    def get_author(self) -> str:
        """Get the author name."""
        if self.repo_config and self.repo_config.author:
            return self.repo_config.author
        return self.global_config.name

    def get_ai_config(self) -> dict:
        """Get AI configuration."""
        return {
            "provider": self.global_config.ai_provider,
            "model": self.global_config.ai_model,
            "base_url": self.global_config.ai_base_url,
        }

    def set_user_name(self, name: str) -> None:
        """Set the user name."""
        self.global_config.name = name
        self.save_global_config()

    def set_user_email(self, email: str) -> None:
        """Set the user email."""
        self.global_config.email = email
        self.save_global_config()

    def set_ai_model(self, model: str) -> None:
        """Set the AI model."""
        self.global_config.ai_model = model
        self.save_global_config()

    def set_ai_base_url(self, url: str) -> None:
        """Set the AI base URL."""
        self.global_config.ai_base_url = url
        self.save_global_config()


def get_config(repo_path: Optional[Path] = None) -> ConfigManager:
    """Get a configuration manager."""
    return ConfigManager(repo_path)


def config_help():
    """Print configuration help."""
    return """
# AugmentedVCS Configuration

## Global Config (~/.config/avcs/config.json)
- name: Your name for commits
- email: Your email (optional)
- ai_provider: AI provider (ollama, openai)
- ai_model: Model to use (llama3.2, gpt-4, etc.)
- ai_base_url: Base URL for AI provider
- default_branch: Default branch name
- editor: Preferred text editor
- pager: Preferred pager for log output

## Repo Config (.avcs/config.json)
- description: Repository description
- author: Override author name
- default_branch: Override default branch
- ai_enabled: Enable/disable AI features

## Usage
avcs config --global user.name "Your Name"
avcs config --global ai.model "llama3.2"
avcs config user.email "you@example.com"
"""