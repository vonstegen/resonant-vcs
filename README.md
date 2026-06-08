# AugmentedVCS

> **Version Control for Everyone — Built by AI, Managed by AI**

[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-yellow.svg)](https://github.com/vonstegen/resonant-vcs)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-20%20passing-green.svg)](#tests)

**AugmentedVCS** is a next-generation Version Control System designed for both **experienced software developers** and **non-technical users**. Unlike traditional VCS tools, AugmentedVCS leverages AI to provide intuitive interfaces, intelligent content management, and seamless collaboration.

## ✨ What Makes It Different

| Traditional VCS | AugmentedVCS |
|----------------|--------------|
| CLI-first, developer-centric | AI-guided UI for all skill levels |
| Code-focused | Multi-content: notes, images, documents |
| Manual conflict resolution | AI-mediated suggestions |
| Steep learning curve | Natural language commands |

## 🚀 Quick Start

### Install

```bash
pip install resonant-vcs
```

### Initialize a Project

```bash
mkdir my-project && cd my-project
avcs init
```

### Save Your First Version

```bash
echo "My shopping list" > notes.txt
avcs add notes.txt
avcs commit -m "Add initial notes"
```

### View History

```bash
avcs log
```

**That's it!** 🎉

## 🖥️ Web UI

For non-technical users, AugmentedVCS has a beautiful web interface:

```bash
# Terminal 1: Start API server
avcs serve

# Terminal 2: Start web UI
npm run dev
```

Then open **http://localhost:3000** in your browser.

![Web UI](docs/images/ui-screenshot.png)

## 🤖 AI Features

AugmentedVCS uses AI (via Ollama) to make version control accessible:

### Smart Commit Messages
```bash
avcs suggest
# Output: "Update shopping list with fresh items"
```

### Plain Language Explanations
```bash
avcs explain
# Output: "You added 2 files and modified 1 file..."
```

### Story Mode
```bash
avcs story
# Output: "Your project began on January 15th..."
```

### Natural Language Commands
```bash
avcs chat
> save my changes
> show me the history
> create a new branch for vacation
```

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Quick Start](docs/user-guides/QUICK-START.md) | Get started in 5 minutes |
| [Installation](docs/user-guides/INSTALLATION.md) | Complete install instructions |
| [CLI Reference](docs/user-guides/CLI-REFERENCE.md) | All CLI commands |
| [Web UI Guide](docs/user-guides/WEB-UI.md) | Using the web interface |
| [AI Features](docs/user-guides/AI-FEATURES.md) | AI-powered capabilities |
| [Architecture](docs/developer/ARCHITECTURE.md) | Technical design |
| [Developer Guide](docs/developer/DEVELOPER-GUIDE.md) | Contributing |
| [API Reference](docs/api/API-REFERENCE.md) | REST API docs |

## 🔧 CLI Commands

```bash
avcs init              # Initialize repository
avcs add <files>       # Stage files
avcs commit -m "msg"   # Create version
avcs log               # View history
avcs status            # Current status
avcs branch            # List branches
avcs checkout <ref>    # Switch versions
avcs diff              # Show changes
avcs ai "command"      # Natural language
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  User Interface (Simple/Advanced/AI CLI) │
├─────────────────────────────────────────┤
│         AI Orchestration Layer          │
│  (Intent Parser • Features • Switcher)  │
├─────────────────────────────────────────┤
│           Core VCS Engine               │
│  (Branch • Commit • Merge • Diff)       │
├─────────────────────────────────────────┤
│        Storage (SQLite + Files)         │
└─────────────────────────────────────────┘
```

## 🧪 Tests

```bash
pytest
```

**20 tests passing** with coverage:
- Intent Classifier: 97%
- Database: 89%
- Repository: 83%

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI |
| Database | SQLite |
| AI | Ollama (local) |
| CLI | Click |
| UI | React 18, TypeScript, Vite |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Make changes with tests
4. Ensure tests pass (`pytest`)
5. Update documentation
6. Submit Pull Request

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

## 👥 Team

- **Founder:** Andre VonStegen
- **DAO:** [ResonantDAO](https://resonantdao.com/)
- **Interface Partner:** [ResonantClaw](https://hub.resonantclaw.com/)

---

**Status:** 🟡 Alpha — Ready for community testing!

[![GitHub](https://img.shields.io/badge/GitHub-vonstegen/resonant-vcs-blue.svg)](https://github.com/vonstegen/resonant-vcs)