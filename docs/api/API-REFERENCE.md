# API Reference

REST API documentation for AugmentedVCS.

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

Currently no authentication required. Future versions will include OAuth.

---

## Response Format

All responses are JSON.

### Success Response

```json
{
  "message": "Operation completed",
  "data": {}
}
```

### Error Response

```json
{
  "detail": "Error description"
}
```

---

## Endpoints

### Health Check

**GET** `/`

Check API status.

**Response:**
```json
{
  "name": "AugmentedVCS API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

### Initialize Repository

**POST** `/repositories`

Create a new repository.

**Request:**
```json
{
  "path": "/path/to/project",
  "description": "Optional description"
}
```

**Response:**
```json
{
  "message": "Repository initialized",
  "path": "/path/to/project"
}
```

---

### Get Repository Info

**GET** `/repositories/{path}`

Get repository information.

**Parameters:**
- `path` (string) — URL-encoded repository path

**Response:**
```json
{
  "path": "/path/to/project",
  "branch": "main",
  "branches": ["main", "feature-login"],
  "staged_count": 3,
  "has_commits": true
}
```

---

### Get Repository Status

**GET** `/repositories/{path}/status`

Get current repository status.

**Response:**
```json
{
  "initialized": true,
  "branch": "main",
  "staged": [["notes.txt", "abc123..."]],
  "modified": ["notes.txt"],
  "new_staged": [],
  "deleted": []
}
```

---

### Stage Files

**POST** `/repositories/{path}/add`

Stage files for commit.

**Request:**
```json
{
  "files": ["notes.txt", "README.md"]
}
```

**Response:**
```json
{
  "staged": ["notes.txt", "README.md"],
  "count": 2
}
```

---

### Unstage File

**DELETE** `/repositories/{path}/unstage/{file}`

Remove file from staging.

**Parameters:**
- `path` — URL-encoded repository path
- `file` — URL-encoded file path

**Response:**
```json
{
  "message": "Unstaged: notes.txt"
}
```

---

### Create Commit

**POST** `/repositories/{path}/commit`

Create a new version/commit.

**Request:**
```json
{
  "message": "Add initial files",
  "author": "user"
}
```

**Response:**
```json
{
  "id": "abc12345",
  "message": "Add initial files",
  "created_at": "2024-01-15T10:30:00",
  "author": "user"
}
```

---

### Get Commit History

**GET** `/repositories/{path}/log`

Get version history.

**Parameters:**
- `count` (int, optional) — Number of commits to return (default: 50)

**Response:**
```json
[
  {
    "id": "abc12345",
    "message": "Add initial files",
    "created_at": "2024-01-15T10:30:00",
    "author": "user"
  }
]
```

---

### Checkout

**POST** `/repositories/{path}/checkout`

Switch to a version or branch.

**Request (version):**
```json
{
  "version": "abc12345"
}
```

**Request (branch):**
```json
{
  "branch": "feature-login"
}
```

**Response:**
```json
{
  "message": "Switched to branch: feature-login"
}
```

---

### List Branches

**GET** `/repositories/{path}/branches`

Get all branches.

**Response:**
```json
[
  {
    "name": "main",
    "head_version_id": "abc12345"
  },
  {
    "name": "feature-login",
    "head_version_id": "def67890"
  }
]
```

---

### Create Branch

**POST** `/repositories/{path}/branches`

Create a new branch.

**Request:**
```json
{
  "name": "feature-new"
}
```

**Response:**
```json
{
  "message": "Created branch: feature-new"
}
```

---

### Delete Branch

**DELETE** `/repositories/{path}/branches/{name}`

Delete a branch.

**Parameters:**
- `name` — Branch name

**Response:**
```json
{
  "message": "Deleted branch: feature-old"
}
```

---

### Get Staged Changes

**GET** `/repositories/{path}/diff`

Get diff of staged changes.

**Response:**
```json
{
  "changes": [
    {"path": "notes.txt", "type": "modified"},
    {"path": "newfile.md", "type": "added"}
  ]
}
```

---

### Compare Versions

**GET** `/repositories/{path}/diff/{v1}/{v2}`

Compare two versions.

**Parameters:**
- `v1` — First version ID
- `v2` — Second version ID

**Response:**
```json
{
  "changes": [
    {"path": "notes.txt", "type": "modified"}
  ]
}
```

---

### AI Status

**GET** `/repositories/{path}/ai/status`

Check AI provider status.

**Response:**
```json
{
  "ollama": {
    "available": true,
    "model": "llama3.2"
  }
}
```

---

### Suggest Commit Message

**POST** `/repositories/{path}/ai/suggest`

Get AI-powered commit message suggestion.

**Response:**
```json
{
  "suggestion": "Add user authentication module"
}
```

---

### Explain Changes

**POST** `/repositories/{path}/ai/explain`

Get plain language explanation of changes.

**Response:**
```json
{
  "explanation": "You added 2 new files and modified 1 existing file. The main change is updating the shopping list with new items."
}
```

---

### Generate Story

**POST** `/repositories/{path}/ai/story`

Get narrative version history.

**Request:**
```json
{
  "count": 10
}
```

**Response:**
```json
{
  "story": "Your project began with the initial setup on January 15th..."
}
```

---

## WebSocket (Future)

Future versions may include WebSocket for real-time updates.

---

## Rate Limiting

Currently no rate limiting. Future versions will include rate limits.

---

## Errors

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request |
| 404 | Not found |
| 409 | Conflict (e.g., repo exists) |
| 500 | Server error |

---

## Interactive Docs

Visit **http://localhost:8000/docs** for interactive API documentation powered by Swagger UI.

---

## Client Libraries

### Python

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")
response = client.get("/")
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/");
const data = await response.json();
```

---

## Next Steps

- [Architecture Overview](../developer/ARCHITECTURE.md)
- [Developer Guide](../developer/DEVELOPER-GUIDE.md)