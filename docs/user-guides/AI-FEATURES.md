# AI Features Guide

Learn how AI makes AugmentedVCS accessible for everyone.

---

## Overview

AugmentedVCS uses AI (via Ollama) to make version control easier:

- **Smart commit messages** — AI suggests meaningful messages
- **Plain language explanations** — Understand changes without technical knowledge
- **Story mode** — See your history as a narrative
- **Natural language commands** — Speak to the VCS in plain English

---

## Requirements

### Ollama Installation

AI features require Ollama running locally:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Verify
ollama list
```

### Check AI Status

```bash
avcs ai-status
```

Should show:
```
┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Provider ┃ Available ┃ Model    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ ollama   │ ✓         │ llama3.2 │
└──────────┴───────────┴──────────┘
```

---

## Smart Commit Messages

### Problem
What do you write for a commit message?

### Solution
Let AI suggest one for you:

```bash
# Make some changes
echo "new content" >> notes.txt
avcs add notes.txt

# Get a suggestion
avcs suggest
# Output: "Update notes.txt with additional content"
```

### In the Web UI

1. Make changes and stage files
2. Click **Suggest Message**
3. AI suggests a commit message
4. Click to use it or write your own

### How It Works

1. AI looks at your changed files
2. Analyzes the content of changes
3. Suggests a clear, concise message
4. Follows commit message best practices

---

## Plain Language Explanations

### Problem
Technical diffs are hard to understand.

### Solution
AI explains in plain English:

```bash
# Make some changes
echo "new content" >> notes.txt
avcs add notes.txt

# Get explanation
avcs explain
# Output: "You added 1 new line to notes.txt. 
#          It's a shopping list with an item added."
```

### In the Web UI

1. Make changes
2. Click **Explain Changes**
3. AI explains what changed in simple terms

---

## Story Mode

### Problem
Version history is just a list of commits.

### Solution
AI tells your project story:

```bash
avcs story
```

Output:
```
Your project started on January 15th when you 
created the initial structure. You then added 
your main content, and most recently updated 
your shopping list with fresh items. 

Your project is steadily growing, with regular 
updates that build on each other...
```

### In the Web UI

1. Click **Tell Me the Story**
2. AI narrates your project history

---

## Natural Language Commands

### Problem
Remembering CLI commands is hard.

### Solution
Just say what you want:

```bash
avcs chat

# Then type:
> show me the history
> create a new branch for vacation
> save my changes
> what changed
```

### Available Commands in Chat

| What You Say | What Happens |
|--------------|--------------|
| "save this" | Stages and commits |
| "show history" | Shows version log |
| "what changed" | Shows status |
| "create branch [name]" | Creates a branch |
| "switch to [branch]" | Changes branch |
| "explain these changes" | Plain language diff |

---

## AI-Powered Intent Parser

### How It Works

When you say something like "save my work", the AI:

1. **Understands** — Converts natural language to intent
2. **Maps** — Connects intent to VCS action
3. **Executes** — Runs the appropriate command
4. **Explains** — Tells you what happened

### Examples

| Input | Intent | Action |
|-------|--------|--------|
| "save this" | COMMIT | `avcs commit` |
| "show me history" | LOG | `avcs log` |
| "what changed" | STATUS | `avcs status` |
| "new branch vacation" | BRANCH_CREATE | `avcs branch vacation` |
| "restore my file" | RESTORE | `avcs restore` |

---

## Offline Mode

### What If Ollama Isn't Available?

AugmentedVCS works without AI:

```bash
# Falls back gracefully
avcs suggest
# Output: "Update 3 files" (simple fallback)
```

You can still:
- Use all CLI commands
- Track versions
- Create branches
- View history

AI features just show simple fallback messages.

---

## Configuration

### Change AI Model

```bash
# List available models
ollama list

# Pull a different model
ollama pull llama3.3

# Set in config
avcs config ai.model llama3.3
```

### Change Ollama URL

```bash
avcs config ai.base_url http://localhost:11434
```

---

## Troubleshooting

### "AI provider not available"

1. Is Ollama running?
```bash
ollama list
```

2. Start Ollama:
```bash
ollama serve
```

3. Check status:
```bash
avcs ai-status
```

### Slow AI Responses

- Smaller models are faster (llama3.2 vs llama3.3)
- Close other Ollama processes
- More RAM helps

### Wrong Suggestions

- AI works better with more context
- Stage more files for better suggestions
- Write manual messages if needed

---

## Next Steps

- [CLI Reference](./CLI-REFERENCE.md)
- [Web UI Guide](./WEB-UI.md)
- [Developer Guide](../developer/DEVELOPER-GUIDE.md)