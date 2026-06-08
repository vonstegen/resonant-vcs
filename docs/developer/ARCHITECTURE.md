# Architecture Overview

Technical architecture of AugmentedVCS.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                           │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐│
│  │   Web UI        │    │   CLI           │    │  Chat Mode   ││
│  │  (React/Vite)   │    │  (Click)        │    │  (Natural)   ││
│  └────────┬────────┘    └────────┬────────┘    └──────┬───────┘│
└───────────┼─────────────────────┼─────────────────────┼────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                        API Layer (FastAPI)                       │
│  ┌──────────────────────────────┴──────────────────────────────┐│
│  │  Repositories • Commits • Branches • Diff • AI Endpoints    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                        Core Engine (Python)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Database  │  │Storage   │  │Repository│  │Operations│         │
│  │(SQLite)  │  │(Files)   │  │(VCS API) │  │(Logic)   │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                        AI Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Providers │  │Intent    │  │Features  │  │Switcher  │         │
│  │(Ollama)  │  │(Parse)   │  │(Suggest) │  │(Config)  │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
resonant-vcs/
├── src/
│   └── resonant_vcs/
│       ├── core/           # VCS engine
│       │   ├── database.py # SQLite operations
│       │   ├── repository.py
│       │   └── storage.py  # Content-addressed storage
│       ├── ai/             # AI layer
│       │   ├── base.py     # Provider interface
│       │   ├── ollama_provider.py
│       │   ├── switcher.py # Provider selection
│       │   ├── intent/     # Intent parsing
│       │   │   ├── classifier.py
│       │   │   └── mapper.py
│       │   └── features/   # AI features
│       │       ├── commit_suggester.py
│       │       ├── changes_summarizer.py
│       │       └── version_narrator.py
│       ├── cli/            # CLI interface
│       │   ├── main.py     # Click commands
│       │   ├── conversational.py
│       │   └── completions.py
│       ├── api/            # FastAPI
│       │   └── main.py
│       └── utils/
│           └── config.py   # Configuration
├── src/ui/                 # React frontend
│   ├── App.tsx
│   ├── api.ts
│   └── styles.css
├── tests/                  # Python tests
├── docs/                   # Documentation
└── package.json
```

---

## Core Components

### 1. Database (`core/database.py`)

SQLite database for VCS metadata.

**Tables:**
- `repositories` — Repository info
- `versions` — Commits/snapshots
- `branches` — Branch pointers
- `files` — Currently tracked files
- `staged_files` — Pending commit files
- `version_files` — Files at each version

### 2. Storage (`core/storage.py`)

Content-addressed file storage.

- Files stored by SHA-256 hash
- Automatic deduplication
- Located in `.avcs/objects/`

### 3. Repository (`core/repository.py`)

Main VCS interface.

- `init()` — Create repository
- `add()` — Stage files
- `commit()` — Create version
- `log()` — History
- `checkout()` — Switch versions
- `branch()` — Manage branches

### 4. AI Layer

**Providers:**
- Ollama (local, default)
- Configurable for others

**Features:**
- Intent classification
- Commit suggestions
- Plain language explanations
- Story narration

---

## Data Flow

### Commit Flow

```
User: avcs commit -m "message"
  │
  ▼
CLI: Parse command
  │
  ▼
Repository: Get staged files
  │
  ▼
Storage: Hash files, store content
  │
  ▼
Database: Create version record
  │
  ▼
Result: Commit created ✓
```

### AI Suggestion Flow

```
User: avcs suggest
  │
  ▼
Repository: Get staged files
  │
  ▼
AI: Format prompt with file names
  │
  ▼
Ollama: Generate suggestion
  │
  ▼
Result: "Add user authentication" ✓
```

---

## Configuration

### Global Config (`~/.config/avcs/config.json`)

```json
{
  "name": "user",
  "ai_provider": "ollama",
  "ai_model": "llama3.2",
  "default_branch": "main"
}
```

### Repository Config (`.avcs/config.json`)

```json
{
  "description": "My project",
  "author": "Your Name"
}
```

---

## API Design

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/repositories` | Init repo |
| GET | `/repositories/{path}` | Repo info |
| GET | `/repositories/{path}/status` | Current status |
| POST | `/repositories/{path}/add` | Stage files |
| POST | `/repositories/{path}/commit` | Create commit |
| GET | `/repositories/{path}/log` | Version history |
| GET | `/repositories/{path}/branches` | List branches |
| POST | `/repositories/{path}/branches` | Create branch |
| GET | `/repositories/{path}/diff` | Staged changes |
| POST | `/repositories/{path}/ai/suggest` | AI suggestion |
| POST | `/repositories/{path}/ai/explain` | Plain explanation |
| POST | `/repositories/{path}/ai/story` | Version story |

---

## Future Architecture Considerations

### Phase 4: Community Testing
- Add user authentication
- Add project sharing

### Phase 5: DAO Integration
- Add ResonantDAO governance
- Add token-based permissions
- Add ResonantClaw integration

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=resonant_vcs

# Run specific test
pytest tests/test_core.py
```

---

## Next Steps

- [Developer Guide](./DEVELOPER-GUIDE.md)
- [API Reference](../api/API-REFERENCE.md)