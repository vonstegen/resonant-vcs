# Installation Guide

Complete installation instructions for AugmentedVCS.

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 8 GB |
| Disk Space | 100 MB | 500 MB |
| Ollama RAM | 4 GB (optional) | 8 GB |

---

## Method 1: pip (Recommended)

```bash
# Install latest release
pip install resonant-vcs

# Install with all extras (AI, web UI)
pip install resonant-vcs[all]
```

---

## Method 2: Development Install

```bash
# Clone the repository
git clone https://github.com/vonstegen/resonant-vcs.git
cd resonant-vcs

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[all]"

# Install frontend dependencies
npm install
```

---

## Verify Installation

```bash
avcs --version
# Should show: AugmentedVCS 0.1.0

avcs --help
# Shows all available commands
```

---

## Install Ollama (For AI Features)

AI features like smart commit messages, plain-language explanations, and story mode require Ollama.

### macOS / Linux

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version

# Pull the model
ollama pull llama3.2
```

### Windows

1. Download from https://ollama.com/download
2. Install and run Ollama
3. Open terminal and run:
```bash
ollama pull llama3.2
```

### Verify Ollama

```bash
ollama list
# Should show: llama3.2 ready to use
```

### Check AI Status in AugmentedVCS

```bash
avcs ai-status
```

Expected output:
```
┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Provider ┃ Available ┃ Model    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ ollama   │ ✓         │ llama3.2 │
└──────────┴───────────┴──────────┘
```

---

## Running the Web UI

### 1. Start the API Server

```bash
# In one terminal
avcs serve
```

### 2. Start the Web UI

```bash
# In another terminal
cd resonant-vcs
npm run dev
```

### 3. Open in Browser

Navigate to: http://localhost:3000

---

## Shell Completions

### Bash

```bash
avcs completions --shell bash
# Add to ~/.bashrc:
source ~/.bash_completion.d/avcs
```

### Zsh

```bash
avcs completions --shell zsh
```

### Fish

```bash
avcs completions --shell fish
```

---

## Configuration

### Global Config

```bash
# View config
avcs config

# Set your name
avcs config user.name "Your Name"

# Set AI model
avcs config ai.model llama3.2
```

Config file location: `~/.config/avcs/config.json`

### Repository Config

```bash
# Configure inside a repo
cd my-project
avcs config user.email "you@example.com"
```

---

## Troubleshooting

### "command not found: avcs"

Make sure the virtual environment is activated:
```bash
source .venv/bin/activate
```

### "Cannot connect to Ollama"

1. Is Ollama running?
```bash
ollama list
```

2. Start Ollama:
```bash
ollama serve
```

3. Check port:
```bash
curl http://localhost:11434
```

### Port 8000 already in use

Use a different port:
```bash
avcs serve --port 8001
```

---

## Uninstall

```bash
pip uninstall resonant-vcs

# Remove config
rm -rf ~/.config/avcs

# Remove Ollama (optional)
ollama uninstall
```

---

## Next Steps

- [Quick Start Guide](./QUICK-START.md)
- [CLI Reference](./CLI-REFERENCE.md)
- [Web UI Guide](./WEB-UI.md)
