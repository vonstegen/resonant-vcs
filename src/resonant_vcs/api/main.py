"""FastAPI REST API for AugmentedVCS."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich.console import Console

from ..core.repository import init, open
from ..ai.switcher import AISwitcher, AIConfig
from ..ai.features import CommitSuggester, ChangesSummarizer, VersionNarrator

console = Console()

# Request/Response Models
class InitRequest(BaseModel):
    path: str
    description: Optional[str] = None

class AddRequest(BaseModel):
    files: list[str]

class CommitRequest(BaseModel):
    message: str
    author: str = "user"

class BranchRequest(BaseModel):
    name: str

class CheckoutRequest(BaseModel):
    version: Optional[str] = None
    branch: Optional[str] = None

class VersionResponse(BaseModel):
    id: str
    message: str
    created_at: str
    author: str

class BranchResponse(BaseModel):
    name: str
    head_version_id: Optional[str] = None

class StatusResponse(BaseModel):
    initialized: bool
    branch: Optional[str] = None
    staged: list = []
    modified: list = []

class DiffItem(BaseModel):
    path: str
    type: str

class AIRequest(BaseModel):
    prompt: str
    action: str = "suggest"  # suggest, explain, story

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield
    # Cleanup on shutdown
    pass

app = FastAPI(
    title="AugmentedVCS API",
    description="REST API for AugmentedVCS - AI-powered Version Control",
    version="0.1.0",
    lifespan=lifespan
)

# CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper ---

def get_repo(path: str) -> Path:
    """Get and validate repo path."""
    p = Path(path)
    if not (p / ".avcs").exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    return open(p)

# --- Repository Operations ---

@app.post("/repositories", response_model=dict)
async def init_repo(req: InitRequest):
    """Initialize a new repository."""
    path = Path(req.path).resolve()
    if (path / ".avcs").exists():
        raise HTTPException(status_code=409, detail="Repository already exists")
    
    try:
        repo = init(path, req.description)
        return {"message": "Repository initialized", "path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/repositories/{path}")
async def get_repo_info(path: str):
    """Get repository information."""
    repo = get_repo(path)
    status = repo.status()
    branches = repo.branch_list()
    
    return {
        "path": str(repo.path),
        "branch": status.get("branch"),
        "branches": [b.name for b in branches],
        "staged_count": len(status.get("staged", [])),
        "has_commits": len(repo.log()) > 0
    }

# --- Status & File Operations ---

@app.get("/repositories/{path}/status", response_model=StatusResponse)
async def get_status(path: str):
    """Get repository status."""
    repo = get_repo(path)
    status = repo.status()
    return StatusResponse(**status)

class FileItem(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'folder'
    size: Optional[int] = None

@app.get("/repositories/{path}/files")
async def list_files(path: str):
    """List all files in the repository."""
    repo = get_repo(path)
    repo_path = repo.path
    files = []
    
    try:
        for item in repo_path.iterdir():
            if item.name.startswith('.') and item.name != '.avcs':
                continue
            if item.name == '.avcs':
                continue
            
            stat = item.stat()
            files.append({
                "name": item.name,
                "path": str(item.relative_to(repo_path)),
                "type": "folder" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None
            })
        
        # Sort: folders first, then files, alphabetically
        files.sort(key=lambda x: (x["type"] == "file", x["name"]))
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repositories/{path}/add")
async def add_files(path: str, req: AddRequest, background: BackgroundTasks):
    """Stage files for commit."""
    repo = get_repo(path)
    staged = []
    
    for file_path in req.files:
        try:
            repo.add(file_path)
            staged.append(file_path)
        except Exception as e:
            # Continue with other files
            pass
    
    return {"staged": staged, "count": len(staged)}

@app.delete("/repositories/{path}/unstage/{file}")
async def unstage_file(path: str, file: str):
    """Unstage a file."""
    repo = get_repo(path)
    repo.unstage(file)
    return {"message": f"Unstaged: {file}"}

# --- Version Control ---

@app.post("/repositories/{path}/commit", response_model=VersionResponse)
async def commit(path: str, req: CommitRequest):
    """Create a new commit."""
    repo = get_repo(path)
    
    try:
        version = repo.commit(req.message, req.author)
        return VersionResponse(
            id=version.id[:8],
            message=version.message,
            created_at=version.created_at.isoformat(),
            author=version.author
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/repositories/{path}/log", response_model=list[VersionResponse])
async def get_log(path: str, count: int = 50):
    """Get commit history."""
    repo = get_repo(path)
    versions = repo.log(count)
    return [
        VersionResponse(
            id=v.id[:8],
            message=v.message,
            created_at=v.created_at.isoformat(),
            author=v.author
        )
        for v in versions
    ]

@app.post("/repositories/{path}/checkout")
async def checkout(path: str, req: CheckoutRequest):
    """Checkout a version or branch."""
    repo = get_repo(path)
    
    try:
        if req.branch:
            repo.checkout_branch(req.branch)
            return {"message": f"Switched to branch: {req.branch}"}
        elif req.version:
            repo.checkout_version(req.version)
            return {"message": f"Checked out: {req.version[:8]}"}
        else:
            raise HTTPException(status_code=400, detail="Specify version or branch")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Branches ---

@app.get("/repositories/{path}/branches", response_model=list[BranchResponse])
async def list_branches(path: str):
    """List all branches."""
    repo = get_repo(path)
    branches = repo.branch_list()
    return [BranchResponse(name=b.name, head_version_id=b.head_version_id) for b in branches]

@app.post("/repositories/{path}/branches")
async def create_branch(path: str, req: BranchRequest):
    """Create a new branch."""
    repo = get_repo(path)
    try:
        repo.branch_create(req.name)
        return {"message": f"Created branch: {req.name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/repositories/{path}/branches/{name}")
async def delete_branch(path: str, name: str):
    """Delete a branch."""
    repo = get_repo(path)
    try:
        repo.branch_delete(name)
        return {"message": f"Deleted branch: {name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Diff ---

@app.get("/repositories/{path}/diff")
async def get_diff(path: str):
    """Get staged changes."""
    repo = get_repo(path)
    changes = repo.diff_staged()
    return {"changes": [DiffItem(**c) for c in changes]}

@app.get("/repositories/{path}/diff/{v1}/{v2}")
async def compare_versions(path: str, v1: str, v2: str):
    """Compare two versions."""
    repo = get_repo(path)
    changes = repo.diff(v1, v2)
    return {"changes": [DiffItem(**c) for c in changes]}

# --- AI Features ---

@app.get("/repositories/{path}/ai/status")
async def ai_status(path: str):
    """Check AI provider status."""
    switcher = AISwitcher()
    return switcher.get_status()

@app.post("/repositories/{path}/ai/suggest")
async def suggest_commit(path: str):
    """Suggest a commit message."""
    repo = get_repo(path)
    status = repo.status()
    staged = status.get("staged", [])
    
    if not staged:
        raise HTTPException(status_code=400, detail="No files staged")
    
    suggester = CommitSuggester()
    suggestion = suggester.suggest(staged)
    return {"suggestion": suggestion}

@app.post("/repositories/{path}/ai/explain")
async def explain_changes(path: str):
    """Explain changes in plain language."""
    repo = get_repo(path)
    changes = repo.diff_staged()
    
    if not changes:
        raise HTTPException(status_code=400, detail="No changes to explain")
    
    summarizer = ChangesSummarizer()
    explanation = summarizer.summarize(changes)
    return {"explanation": explanation}

@app.post("/repositories/{path}/ai/story")
async def tell_story(path: str, count: int = 10):
    """Tell version history as a story."""
    repo = get_repo(path)
    versions = repo.log(count)
    
    if not versions:
        raise HTTPException(status_code=400, detail="No version history")
    
    version_dicts = [
        {"id": v.id[:8], "message": v.message, "date": v.created_at.strftime("%Y-%m-%d")}
        for v in versions
    ]
    
    narrator = VersionNarrator()
    story = narrator.narrate_versions(version_dicts, count)
    return {"story": story}

# --- Root ---

@app.get("/")
async def root():
    """API root."""
    return {
        "name": "AugmentedVCS API",
        "version": "0.1.0",
        "docs": "/docs"
    }


def create_app() -> FastAPI:
    """Factory for creating the FastAPI app."""
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
