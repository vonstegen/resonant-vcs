# Web UI Guide

Guide to using the AugmentedVCS web interface.

---

## Accessing the Web UI

### 1. Start the API Server

```bash
avcs serve
```

### 2. Start the Web UI

```bash
npm run dev
# or
npm run start
```

### 3. Open Browser

Navigate to: **http://localhost:3000**

---

## Interface Overview

### Mode Toggle

The UI has two modes:

| Mode | Best For |
|------|----------|
| **Simple** | Non-technical users, beginners |
| **Advanced** | Developers, technical users |

Toggle between modes using the buttons in the header.

---

## Simple Mode

Designed for **non-technical users** who want easy version control.

### Features

#### Status Panel
Shows quick stats at the top:
- **Versions** — How many saves you've made
- **Changes** — How many files changed
- **Staged** — Files ready to save

#### Quick Actions
Big, friendly buttons:

| Button | What It Does |
|--------|-------------|
| **Save Current Version** | Stages all files and opens commit form |
| **Explain Changes** | Tells you what changed in plain English |
| **Tell Me the Story** | Shows your project history as a story |

#### Save Your Changes
1. Click **Save Current Version**
2. Type a description like "Updated my shopping list"
3. Click **Save Version**
4. Done! 🎉

#### AI-Powered Features
- **Suggest Message** — Click to get an AI-written commit message
- **Explain Changes** — AI explains what you changed in simple terms
- **Story Mode** — AI tells your project history as a narrative

---

## Advanced Mode

For **developers** who want more control.

### Features

#### Files Panel
Shows all tracked files with status:
- `+` New files
- `~` Modified files
- `-` Deleted files

#### Branches Panel
Shows all branches. Click to switch.

#### Commit Form
Standard commit message input with:
- Manual message entry
- Show full technical details

#### Timeline
Visual commit history with:
- Commit hashes
- Timestamps
- Full messages

---

## File Management

### Stage Files

1. **Simple Mode**: Click "Save Current Version" to stage all
2. **Advanced Mode**: Click "Add All" in the Files panel

### View Changes

Click on any file in the Files panel to see what changed.

### Commit

1. Write a message (or click "Suggest Message")
2. Click "Save Version"
3. Your save appears in the timeline

---

## Using AI Features

### Get Commit Suggestions

1. Make some changes
2. Click "Suggest Message"
3. AI suggests a commit message
4. Click the suggestion to use it

### Explain Changes

1. Make some changes
2. Click "Explain Changes"
3. AI explains what you changed in plain English
4. Great for understanding what was done

### Story Mode

1. Click "Tell Me the Story"
2. AI tells your project history as a narrative
3. Great for presentations or understanding project evolution

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Open commit form |
| `Escape` | Close dialogs |

---

## Mobile Support

The UI is responsive and works on mobile devices.

### On Mobile
- Sidebar collapses to hamburger menu
- Touch-friendly buttons
- Simplified layout

---

## Troubleshooting

### UI Not Loading

1. Is the API server running?
```bash
avcs serve
```

2. Is the UI dev server running?
```bash
npm run dev
```

3. Check browser console for errors

### Changes Not Appearing

1. Click the refresh button in the UI
2. Or press `F5` to reload

### API Errors

Check the terminal running `avcs serve` for error messages.

---

## API Documentation

The API is available at **http://localhost:8000/docs**

Interactive API docs let you:
- Try all endpoints
- See request/response formats
- Test from the browser

---

## Next Steps

- [Quick Start Guide](./QUICK-START.md)
- [Installation Guide](./INSTALLATION.md)
- [AI Features](./AI-FEATURES.md)
