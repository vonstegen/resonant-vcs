# Agent Instructions for AugmentedVCS

## Project Context

AugmentedVCS is a next-generation Version Control System designed for both developers and non-technical users. It leverages AI to provide intuitive version tracking for notes, images, and creative content. The project integrates with ResonantDAO for decentralized governance.

**Key Documents:**
- `project.md` — Full project specification
- `docs/architecture/` — Technical architecture
- `docs/user-guides/` — User-facing documentation

## Working Directory

```
/mnt/c/Users/andre/Documents/VonStegen-Master-Vault/Projects/AI/Augmented-Projects/AugmentedVCS/
```

**Windows Path:** `C:\Users\andre\Documents\VonStegen-Master-Vault\Projects\AI\Augmented-Projects\AugmentedVCS\`

## Architecture Principles

1. **Local-first** — All data stored locally, sync is optional
2. **AI-native** — AI assists every interaction, from commits to conflict resolution
3. **Accessibility-first** — Simple mode for non-technical users, advanced for developers
4. **DAO-integrated** — ResonantDAO governance for project ownership

## Tech Stack Conventions

| Component | Language/Tool | Notes |
|-----------|---------------|-------|
| Backend | Python 3.11+ | FastAPI, async |
| Database | SQLite | Local storage |
| Vector DB | Qdrant | Semantic search |
| AI | Ollama (local) + Cloud APIs | Flexible inference |
| Frontend | React/TypeScript | Web UI |
| CLI | Python (Click/Typer) | Developer tools |

## Code Conventions

### Python
- Type hints required
- Async/await for I/O
- PEP 8 style with Black formatting
- Docstrings for all public functions

### TypeScript/React
- Functional components only
- TypeScript strict mode
- Hooks for state management

## Branch Strategy

- `main` — Stable releases
- `develop` — Integration branch
- `feature/*` — Feature development
- `ai/*` — AI-specific features
- `dao/*` — DAO integration features

## Testing Requirements

- Unit tests for core VCS operations
- Integration tests for AI layer
- E2E tests for user interfaces
- Minimum 80% code coverage for core modules

## Commit Conventions

Format: `type(scope): description`

Types:
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code restructuring
- `ai` — AI-related changes
- `dao` — DAO integration

## Important Notes

1. **Privacy-first** — Never send user content to cloud without explicit consent
2. **Offline-capable** — All core features work without internet
3. **Graceful degradation** — AI features fall back to traditional methods when unavailable
4. **Accessibility** — WCAG 2.1 AA compliance for all UIs

## Available Scripts

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Start development server
python -m src.api.main

# CLI help
python -m src.cli --help
```

## Related Projects

- [ResonantDAO](https://resonantdao.com/) — Governance
- [ResonantClaw](https://hub.resonantclaw.com/) — Interface hub