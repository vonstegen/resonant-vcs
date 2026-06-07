# AugmentedVCS Building Blocks — Todo List

> **Master Todo List | Updated: 2026-06-05**

---

## 🎯 Priority Order

> **"A working VCS that saves versions comes BEFORE fancy AI features."**

---

## 🔲 BLOCK A: Project Foundation

**Why:** Everything else depends on this

### A1: Project Setup
- [ ] Initialize Python project (`pyproject.toml`)
- [ ] Create virtual environment
- [ ] Install core dependencies (FastAPI, Click, SQLite)
- [ ] Set up Git repo with `main`, `develop` branches
- [ ] Create `.gitignore` for Python + `.avcs/`

### A2: Directory Structure
```
AugmentedVCS/
├── src/
│   ├── __init__.py
│   ├── core/          # VCS engine
│   ├── ai/            # AI layer
│   ├── cli/           # Command line
│   └── api/           # Web API
├── tests/
├── config/
└── .avcs/             # Created on init
    ├── objects/       # Content-addressed storage
    ├── refs/          # Branches and tags
    └── db/            # SQLite database
```

### A3: Configuration
- [ ] Create `config/defaults.yaml`
- [ ] Create `config/ai_providers.yaml`
- [ ] Implement config loader

---

## 🔲 BLOCK B: Core VCS Engine

**Why:** This IS the VCS. No AI, no UI — just version control.

### B1: Database Schema
```sql
-- Repositories
CREATE TABLE repositories (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    created_at TIMESTAMP,
    description TEXT
);

-- Files (tracked)
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    repo_id TEXT,
    path TEXT NOT NULL,
    hash TEXT NOT NULL,
    FOREIGN KEY (repo_id) REFERENCES repositories(id)
);

-- Versions (commits)
CREATE TABLE versions (
    id TEXT PRIMARY KEY,
    repo_id TEXT,
    message TEXT,
    parent_id TEXT,
    created_at TIMESTAMP,
    author TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories(id),
    FOREIGN KEY (parent_id) REFERENCES versions(id)
);

-- Branches
CREATE TABLE branches (
    id TEXT PRIMARY KEY,
    repo_id TEXT,
    name TEXT NOT NULL,
    head_version_id TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories(id),
    FOREIGN KEY (head_version_id) REFERENCES versions(id)
);
```

### B2: Core Classes
- [ ] `Repository` class — manages repo lifecycle
- [ ] `Version` class — represents a commit
- [ ] `Branch` class — manages branches
- [ ] `FileReference` class — tracks files in versions

### B3: Core Operations
- [ ] `init()` — Create new repository
- [ ] `add(path)` — Stage file
- [ ] `commit(message)` — Save version
- [ ] `log()` — Show history
- [ ] `checkout(version_id)` — Switch version
- [ ] `branch_create(name)` — New branch
- [ ] `branch_switch(name)` — Switch branch
- [ ] `merge(branch_name)` — Combine branches
- [ ] `diff(version_a, version_b)` — Show changes

### B4: Content Storage
- [ ] Implement content-addressed storage (hash → file)
- [ ] Store compressed content in `.avcs/objects/`
- [ ] Implement deduplication
- [ ] Handle large files gracefully

---

## 🔲 BLOCK C: CLI Interface

**Why:** Developers need command-line. Also validates core engine works.

### C1: Basic Commands
```bash
avcs init                      # Create repo
avcs add <file>               # Stage file
avcs commit "message"         # Save version
avcs log                       # Show history
avcs checkout <version>       # Restore version
avcs branch                    # List branches
avcs branch <name>            # Create branch
avcs checkout -b <name>       # Create + switch
avcs merge <branch>           # Merge branch
avcs diff <v1> <v2>           # Compare versions
```

### C2: Advanced Commands
```bash
avcs status                   # What's staged
avcs reset <file>             # Unstage
avcs rm <file>                # Remove from tracking
avcs restore <file>          # Restore from last commit
avcs config                   # Show/set config
```

### C3: Help System
- [ ] `avcs --help` — Global help
- [ ] `avcs <command> --help` — Command help
- [ ] `avcs help` — Interactive help mode

---

## 🔲 BLOCK D: AI Layer (Phase 2)

**Why:** Makes the VCS accessible to non-technical users.

### D1: AI Infrastructure
- [ ] Create `ai/base.py` — Abstract AI provider
- [ ] Create `ai/ollama.py` — Ollama implementation
- [ ] Create `ai/openai.py` — OpenAI fallback
- [ ] Implement `ai/switcher.py` — Provider selection

### D2: Intent Parser
- [ ] `ai/intent/classifier.py` — Classify user intent
- [ ] `ai/intent/mapper.py` — Map intent → VCS operation
- [ ] Train/test with sample phrases

### D3: AI Features
- [ ] `ai/features/commit_suggester.py` — Smart commit messages
- [ ] `ai/features/changes_summarizer.py` — Plain language diffs
- [ ] `ai/features/version_narrator.py` — Story-style history

### D4: Natural Language CLI
- [ ] `cli/conversational.py` — Multi-turn interface
- [ ] `cli/context_keeper.py` — Conversation context

---

## 🔲 BLOCK E: Web UI (Phase 3)

**Why:** Non-technical users need visual interface.

### E1: Frontend Setup
- [ ] Initialize React app with TypeScript
- [ ] Set up routing (React Router)
- [ ] Create component library
- [ ] Set up state management (Zustand/Redux)

### E2: Core UI Components
- [ ] `RepoSelector` — Choose repository
- [ ] `FileExplorer` — Browse files
- [ ] `VersionTimeline` — Visual history
- [ ] `DiffViewer` — Show changes
- [ ] `CommitForm` — Save versions

### E3: AI-Powered Components
- [ ] `SmartCommitMessage` — AI-suggested message
- [ ] `PlainLanguageDiff` — Human-readable changes
- [ ] `VersionStory` — Narrative version history

### E4: Responsive Design
- [ ] Mobile-first CSS
- [ ] Touch-friendly controls
- [ ] Offline indicator

---

## 🔲 BLOCK F: Testing & QA

**Why:** Ensure reliability for all users.

### F1: Unit Tests
- [ ] Core VCS operations (>80% coverage)
- [ ] AI intent classification
- [ ] CLI commands

### F2: Integration Tests
- [ ] Full workflow: init → add → commit → log → checkout
- [ ] Branch creation and merging
- [ ] File restoration

### F3: User Testing
- [ ] Non-technical user walkthrough
- [ ] Developer CLI evaluation
- [ ] Accessibility audit (WCAG 2.1 AA)

---

## 🔲 BLOCK G: Documentation

**Why:** "If it's not documented, it doesn't exist."

### G1: Developer Docs
- [ ] Architecture overview
- [ ] API reference
- [ ] CLI command reference
- [ ] Contributing guide

### G2: User Docs
- [ ] Quick start guide (5 minutes to first commit)
- [ ] Video tutorials
- [ ] Example workflows
- [ ] Troubleshooting FAQ

### G3: Community Docs
- [ ] How to report bugs
- [ ] How to request features
- [ ] How to contribute

---

## 📊 Progress Tracking

| Block | Status | Notes |
|-------|--------|-------|
| **A: Project Foundation** | 🟡 Not Started | |
| **B: Core VCS Engine** | 🟡 Not Started | **Most Critical** |
| **C: CLI Interface** | 🟡 Not Started | Validates Block B |
| **D: AI Layer** | ⚪ Future | Phase 2 |
| **E: Web UI** | ⚪ Future | Phase 3 |
| **F: Testing & QA** | ⚪ Future | Ongoing |
| **G: Documentation** | ⚪ Future | Ongoing |

---

## 🚀 Quick Start Checklist

To start building BLOCK B (Core VCS), you need:

- [ ] Python 3.11+
- [ ] `pip install click sqlalchemy pyyaml`
- [ ] Initialize Git repo
- [ ] Create `src/core/` directory
- [ ] Write first test

**Then:** Implement one operation at a time, starting with `init()` and `commit()`.

---

**Legend:**
- 🟢 Complete
- 🟡 In Progress
- ⚪ Not Started
- 🔴 Blocked