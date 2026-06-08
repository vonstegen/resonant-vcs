# CLI Reference

Complete reference for all `avcs` commands.

---

## Core Commands

### avcs init [path]

Initialize a new repository.

```bash
avcs init                    # Initialize current directory
avcs init /path/to/project   # Initialize specific path
avcs init -d "My project"    # With description
```

---

### avcs add [files...]

Stage files for commit.

```bash
avcs add file.txt            # Stage single file
avcs add file1.txt file2.py # Stage multiple files
avcs add -A                  # Stage all files
```

---

### avcs commit [-m "message"]

Create a new version.

```bash
avcs commit -m "Add new feature"
avcs commit                 # Opens editor for message
```

---

### avcs status

Show working tree status.

```bash
avcs status
```

Output:
```
Branch: main

Staged for commit:
  + notes.txt

Modified:
  ~ notes.txt
```

---

### avcs log [-n count]

Show version history.

```bash
avcs log                    # Show all commits
avcs log -n 10              # Show last 10 commits
```

---

### avcs diff [version_a] [version_b]

Show changes.

```bash
avcs diff                   # Show staged changes
avcs diff abc123 def456      # Compare versions
```

---

## Branch Commands

### avcs branch

List branches.

```bash
avcs branch
```

---

### avcs branch [name]

Create a new branch.

```bash
avcs branch feature-login
```

---

### avcs checkout [-b|-branch] [target]

Switch versions or branches.

```bash
avcs checkout abc123         # Checkout specific version
avcs checkout -b new-branch  # Create and switch to new branch
avcs checkout --branch main  # Switch to existing branch
```

---

### avcs checkout -b [branch-name]

Create and switch to a new branch.

```bash
avcs checkout -b feature-shopping
```

---

### avcs restore [file]

Restore a file from the last commit.

```bash
avcs restore notes.txt
avcs restore -a              # Restore all files
```

---

### avcs unstage [file]

Remove a file from staging.

```bash
avcs unstage notes.txt
```

---

## AI Commands

### avcs ai-status

Check AI provider status.

```bash
avcs ai-status
```

---

### avcs ai [text]

Process natural language command.

```bash
avcs ai "show me the history"
avcs ai "create a new branch for vacation"
avcs ai "save my changes"
```

---

### avcs suggest

Get AI-powered commit message suggestion.

```bash
avcs suggest
# Output: "Add user authentication module"
```

---

### avcs explain

Explain changes in plain language.

```bash
avcs explain
# Output: "You added 3 files and modified 1 file..."
```

---

### avcs story [-n count]

Tell version history as a narrative.

```bash
avcs story
avcs story -n 20
```

---

### avcs chat

Start conversational AI assistant.

```bash
avcs chat
# Then type: "save this" or "show history" or "help"
```

---

## Configuration Commands

### avcs config [--global] [key] [value]

View or set configuration.

```bash
avcs config                    # Show all config
avcs config --global           # Show global config
avcs config user.name "Name"   # Set value
avcs config ai.model llama3.2  # Set AI model
```

---

### avcs completions [--shell bash|zsh|fish]

Install shell completions.

```bash
avcs completions --shell bash
```

---

## Server Commands

### avcs serve [--host host] [--port port]

Start the API server.

```bash
avcs serve                    # Default: 127.0.0.1:8000
avcs serve --port 8080        # Custom port
avcs serve --host 0.0.0.0    # Accessible externally
```

---

### avcs ui [--api-port port] [--ui-port port]

Start the full web UI.

```bash
avcs ui                       # Start both API and UI
avcs ui --ui-port 3000        # Custom UI port
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version |
| `--help` | Show help |

---

## Keyboard Shortcuts (in chat mode)

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit chat |
| `Ctrl+D` | Exit chat |

---

## Exit Codes

| Code | Meaning |
|------|--------|
| 0 | Success |
| 1 | Error |
| 2 | Invalid usage |

---

## Examples

### Complete Workflow

```bash
# Initialize
avcs init
avcs config user.name "Your Name"

# Make changes
echo "content" > file.txt
avcs add file.txt
avcs status

# Get AI suggestion
avcs suggest
# Or explain
avcs explain

# Commit
avcs commit -m "Add initial file"

# View history
avcs log

# Create branch for new feature
avcs branch feature-new
avcs checkout feature-new
```

### Using AI Features

```bash
# Natural language commands
avcs ai "show me what changed"
avcs ai "create a new branch called vacation"
avcs ai "save my work"

# Story mode
avcs story

# Conversational
avcs chat
# > I worked on the notes today
# > save this
# > show me the history
```
