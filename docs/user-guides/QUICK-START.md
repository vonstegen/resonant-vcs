# Quick Start Guide

> **Get started with AugmentedVCS in 5 minutes**

AugmentedVCS is a version control system that uses AI to make tracking changes easy for everyone — from beginners to developers.

---

## Step 1: Install

### Requirements
- Python 3.11+
- Ollama (for AI features, optional but recommended)
- Node.js 18+ (for web UI)

### Install AugmentedVCS

```bash
pip install resonant-vcs
```

### Install Ollama (Optional but Recommended)

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows - Download from https://ollama.com/download

# Pull a model
ollama pull llama3.2
```

---

## Step 2: Initialize a Project

```bash
# Create a new folder for your project
mkdir my-project
cd my-project

# Initialize AugmentedVCS
avcs init
```

You'll see:
```
Initialized empty repository at /path/to/my-project
Run 'avcs add <file>' to stage files
```

---

## Step 3: Add and Save Your First Version

```bash
# Create a file
echo "My shopping list" > notes.txt

# Stage the file
avcs add notes.txt

# Save your version
avcs commit -m "Add initial shopping list"
```

---

## Step 4: View Your History

```bash
avcs log
```

Shows:
```
a1b2c3d4 2024-01-15 10:30
Add initial shopping list
```

---

## That's It! 🎉

You just learned the basics:
- `avcs init` — Start tracking a project
- `avcs add <file>` — Stage files for saving
- `avcs commit -m "message"` — Save a version
- `avcs log` — See your history

---

## Next Steps

### For Non-Technical Users
- Try the **Web UI** at http://localhost:3000
- Use the **chat mode**: `avcs chat` (speaks plain English!)
- Click "Suggest Message" for AI-powered commit messages

### For Developers
- Try branch commands: `avcs branch feature-login`
- Use diff: `avcs diff`
- Configure: `avcs config`

### Learn More
- [Installation Guide](./INSTALLATION.md)
- [CLI Reference](./CLI-REFERENCE.md)
- [Web UI Guide](./WEB-UI.md)
- [AI Features](./AI-FEATURES.md)
