# Changelog

All notable changes to AugmentedVCS.

## [0.1.0] - 2024-06-08 - Alpha

### Added

#### Core VCS Engine
- SQLite database schema (repositories, files, versions, branches)
- Content-addressed storage with SHA-256 hashing
- Core operations: init, add, commit, log, checkout, branch, diff
- Version file tracking for proper snapshot support

#### AI Layer
- Ollama provider with sync/async support
- AI provider switcher with fallback
- Intent classifier for natural language parsing
- Intent mapper to execute VCS operations
- CommitSuggester - AI-powered commit messages
- ChangesSummarizer - Plain language explanations
- VersionNarrator - Story-style history

#### User Interfaces
- FastAPI REST API with full VCS operations
- React web UI with Simple/Advanced modes
- Shell completions (bash, zsh, fish)
- Configuration management (global + repo level)
- Conversational AI CLI mode

#### CLI Commands
- `avcs init` - Initialize repository
- `avcs add` - Stage files
- `avcs commit` - Create version
- `avcs log` - View history
- `avcs status` - Current status
- `avcs branch` - Manage branches
- `avcs checkout` - Switch versions
- `avcs diff` - Show changes
- `avcs ai` - Natural language commands
- `avcs ai-status` - Check AI provider
- `avcs suggest` - AI commit suggestion
- `avcs explain` - Plain language changes
- `avcs story` - Narrative history
- `avcs chat` - Conversational mode
- `avcs config` - Configuration
- `avcs completions` - Shell completions
- `avcs serve` - API server
- `avcs ui` - Web UI

### Fixed
- Path concatenation in config.py
- is_hidden() compatibility for Python < 3.13
- Version file tracking for proper diff support

### Documentation
- Quick Start Guide
- Installation Guide
- CLI Reference
- Web UI Guide
- AI Features Guide
- Architecture Overview
- Developer Guide
- API Reference
- Testing Guide

---

## [Unreleased]

### Planned
- Community testing
- User feedback integration
- Bug fixes and improvements

### Future
- Phase 4: Community Testing & Approval
- Phase 5: DAO Integration (ResonantDAO governance)