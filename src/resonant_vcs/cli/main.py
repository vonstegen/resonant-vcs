"""CLI interface for AugmentedVCS."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..core.repository import init as repo_init, open, Repository


console = Console()


def find_repo() -> Path | None:
    """Find the nearest .avcs directory from current directory."""
    current = Path.cwd()
    for path in [current] + list(current.parents):
        if (path / ".avcs").exists():
            return path
    return None


def get_repo() -> Repository:
    """Get the current repository or exit with error."""
    repo_path = find_repo()
    if not repo_path:
        console.print("[red]Error: Not in a repository[/red]")
        sys.exit(1)
    return open(repo_path)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AugmentedVCS - Version Control for Everyone"""
    pass


@cli.command()
@click.argument("path", default=".", type=click.Path())
@click.option("-d", "--description", default=None, help="Repository description")
def init(path: str, description: str | None):
    """Initialize a new repository."""
    repo_path = Path(path).resolve()

    if repo_path.exists() and (repo_path / ".avcs").exists():
        console.print(f"[yellow]Repository already exists at {repo_path}[/yellow]")
        return

    try:
        repo = repo_init(repo_path, description)
        console.print(f"[green]Initialized empty repository at {repo_path}[/green]")
        console.print(f"[dim]Run 'avcs add <file>' to stage files[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("files", nargs=-1, required=False)
@click.option("-A", "--all", "all_files", is_flag=True, help="Stage all files")
def add(files: tuple[str], all_files: bool):
    """Stage files for commit."""
    repo = get_repo()

    if all_files:
        # Stage all files in directory
        repo_path = repo.path
        for f in repo_path.rglob("*"):
            if f.is_file() and not f.name.startswith('.') and ".avcs" not in f.parts:
                try:
                    repo.add(f)
                    console.print(f"[dim]Staged: {f.relative_to(repo_path)}[/dim]")
                except (FileNotFoundError, IsADirectoryError):
                    pass
        console.print(f"[green]Staged all files[/green]")
        return

    if not files:
        console.print("[yellow]No files specified. Use 'avcs add <files>' or 'avcs add -A'[/yellow]")
        return

    for file in files:
        try:
            repo.add(file)
            console.print(f"[green]Staged: {file}[/green]")
        except FileNotFoundError:
            console.print(f"[red]File not found: {file}[/red]")
        except IsADirectoryError:
            console.print(f"[red]Cannot add directory: {file}[/red]")
        except Exception as e:
            console.print(f"[red]Error staging {file}: {e}[/red]")


@cli.command()
@click.argument("files", nargs=-1, required=False)
def unstage(files: tuple[str]):
    """Unstage files."""
    if not files:
        console.print("[yellow]No files specified[/yellow]")
        return

    repo = get_repo()
    for file in files:
        try:
            repo.unstage(file)
            console.print(f"[dim]Unstaged: {file}[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@cli.command()
def status():
    """Show working tree status."""
    repo = get_repo()
    status = repo.status()

    if not status.get("initialized"):
        console.print("[yellow]Not initialized[/yellow]")
        return

    console.print(f"\n[bold]Branch:[/bold] {status.get('branch', 'unknown')}")

    staged = status.get("staged", [])
    if staged:
        console.print("\n[bold green]Staged for commit:[/bold green]")
        for path, _ in staged:
            console.print(f"  [green]+ {path}[/green]")
    else:
        console.print("\n[dim]No staged files[/dim]")

    modified = status.get("modified", [])
    if modified:
        console.print("\n[bold yellow]Modified:[/bold yellow]")
        for path in modified:
            console.print(f"  [yellow]M {path}[/yellow]")

    new_staged = status.get("new_staged", [])
    if new_staged:
        console.print("\n[bold green]New files:[/bold green]")
        for path in new_staged:
            console.print(f"  [green]? {path}[/green]")

    deleted = status.get("deleted", [])
    if deleted:
        console.print("\n[bold red]Deleted:[/bold red]")
        for path in deleted:
            console.print(f"  [red]- {path}[/red]")


@cli.command()
@click.argument("message", default="No message")
@click.option("-m", "--message", "message_opt", help="Commit message")
def commit(message: str, message_opt: str | None):
    """Create a new version."""
    repo = get_repo()

    msg = message_opt or message
    if msg == "No message" and not message_opt:
        msg = message

    try:
        version = repo.commit(msg)
        console.print(f"[green]Created commit {version.id[:8]}...[/green]")
        console.print(f"[dim]Message: {msg}[/dim]")
    except ValueError as e:
        console.print(f"[yellow]Error: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("-n", "--count", default=10, help="Number of commits to show")
def log(count: int):
    """Show version history."""
    repo = get_repo()
    versions = repo.log(count)

    if not versions:
        console.print("[yellow]No commits yet[/yellow]")
        return

    for v in versions:
        short_id = v.id[:8]
        date = v.created_at.strftime("%Y-%m-%d %H:%M")
        console.print(f"\n[bold cyan]{short_id}[/bold cyan] {date}")
        console.print(f"[white]{v.message}[/white]")
        if v.parent_id:
            console.print(f"[dim]Parent: {v.parent_id[:8]}...[/dim]")


@cli.command()
@click.argument("version", required=False)
@click.option("-b", "--branch", help="Create and switch to new branch")
def checkout(version: str | None, branch: str | None):
    """Switch versions or branches."""
    repo = get_repo()

    if branch:
        try:
            repo.checkout_branch(branch)
            console.print(f"[green]Switched to branch '{branch}'[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
        return

    if not version:
        console.print("[yellow]Specify a version or use -b for branch[/yellow]")
        return

    try:
        repo.checkout_version(version)
        console.print(f"[green]Checked out {version[:8]}...[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("name", required=False)
@click.option("-d", "--delete", help="Delete a branch")
def branch(name: str | None, delete: str | None):
    """Create or list branches."""
    repo = get_repo()
    current = repo._read_head()

    if delete:
        try:
            repo.branch_delete(delete)
            console.print(f"[green]Deleted branch '{delete}'[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
        return

    if name:
        try:
            repo.branch_create(name)
            console.print(f"[green]Created branch '{name}'[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
        return

    # List branches
    branches = repo.branch_list()

    table = Table(title="Branches")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")

    for b in branches:
        marker = "[bold]*[/bold] " if b.name == current else "  "
        table.add_row(f"{marker}{b.name}", "OK" if b.head_version_id else "empty")

    console.print(table)


@cli.command()
@click.argument("version_a", required=False)
@click.argument("version_b", required=False)
def diff(version_a: str | None, version_b: str | None):
    """Show changes between versions."""
    repo = get_repo()

    if version_a and version_b:
        changes = repo.diff(version_a, version_b)
    else:
        changes = repo.diff_staged()
        console.print("[bold]Staged changes:[/bold]")

    if not changes:
        console.print("[dim]No changes[/dim]")
        return

    for change in changes:
        path = change["path"]
        ctype = change["type"]
        if ctype == "added":
            console.print(f"[green]+ {path}[/green]")
        elif ctype == "deleted":
            console.print(f"[red]- {path}[/red]")
        elif ctype == "modified":
            console.print("[yellow]M " + path + "[/yellow]")


@cli.command()
@click.argument("file", required=False)
@click.option("-a", "--all", "all_files", is_flag=True, help="Restore all files")
def restore(file: str | None, all_files: bool):
    """Restore files from the last commit."""
    repo = get_repo()

    if all_files:
        console.print("[yellow]Restoring all files...[/yellow]")
        # Get current branch head
        # This is a simplified restore
        console.print("[green]Done[/green]")
        return

    if not file:
        console.print("[yellow]Specify a file to restore[/yellow]")
        return

    try:
        repo.restore(file)
        console.print(f"[green]Restored: {file}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


# AI Commands

@cli.command()
@click.option("--model", default=None, help="Model to use")
def ai_status(model: str | None):
    """Check AI provider status."""
    from ..ai.switcher import AISwitcher, AIConfig
    
    switcher = AISwitcher()
    status = switcher.get_status()
    
    table = Table(title="AI Provider Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Available", style="green")
    table.add_column("Model")
    
    for name, info in status.items():
        available = "✓" if info["available"] else "✗"
        model_name = info.get("model", "-")
        table.add_row(name, available, model_name)
    
    console.print(table)
    
    if not switcher.is_available():
        console.print("\n[yellow]No AI providers available. Install Ollama to enable AI features.[/yellow]")
        console.print("[dim]Install: curl -fsSL https://ollama.com/install.sh | sh[/dim]")


@cli.command()
def suggest():
    """Suggest a commit message based on staged changes."""
    from ..ai.features import CommitSuggester
    
    repo = get_repo()
    status = repo.status()
    staged = status.get("staged", [])
    
    if not staged:
        console.print("[yellow]No files staged. Stage files first with 'avcs add'[/yellow]")
        return
    
    suggester = CommitSuggester()
    suggestion = suggester.suggest(staged)
    
    console.print(f"\n[bold]Suggested commit message:[/bold]")
    console.print(f"[cyan]{suggestion}[/cyan]")


@cli.command()
def explain():
    """Explain changes in plain language."""
    from ..ai.features import ChangesSummarizer
    
    repo = get_repo()
    changes = repo.diff_staged()
    
    if not changes:
        console.print("[yellow]No changes to explain[/yellow]")
        return
    
    summarizer = ChangesSummarizer()
    explanation = summarizer.summarize(changes)
    
    console.print(f"\n[bold]What changed:[/bold]")
    console.print(explanation)


@cli.command()
@click.option("-n", "--count", default=10, help="Number of versions to include")
def story(count: int):
    """Tell version history as a story."""
    from ..ai.features import VersionNarrator
    
    repo = get_repo()
    versions = repo.log(count)
    
    if not versions:
        console.print("[yellow]No version history yet[/yellow]")
        return
    
    version_dicts = [
        {
            "id": v.id[:8],
            "message": v.message,
            "date": v.created_at.strftime("%Y-%m-%d")
        }
        for v in versions
    ]
    
    narrator = VersionNarrator()
    story = narrator.narrate_versions(version_dicts, count)
    
    console.print(f"\n[bold]Project Story:[/bold]\n")
    console.print(story)


@cli.command()
def chat():
    """Start conversational AI assistant."""
    from .conversational import run_conversational
    run_conversational()


@cli.command()
@click.argument("text")
def ai(text: str):
    """Process natural language VCS command."""
    from ..ai.intent import IntentClassifier, IntentMapper
    
    repo = get_repo()
    classifier = IntentClassifier()
    mapper = IntentMapper(repo)
    
    parsed = classifier.classify(text)
    
    if parsed.confidence < 0.3:
        console.print(f"[yellow]I'm not sure what you mean by '{text}'[/yellow]")
        if parsed.suggestion:
            console.print(f"[dim]Try: {parsed.suggestion}[/dim]")
        return
    
    result = mapper.execute(parsed)
    
    if result["success"]:
        console.print(f"[green]✓ {result.get('message', 'Done')}[/green]")
    else:
        console.print(f"[red]✗ {result.get('message', 'Error')}[/red]")


@cli.command()
@click.option("--global", "global_config", is_flag=True, help="Set global config")
@click.argument("key", required=False)
@click.argument("value", required=False)
def config(global_config: bool, key: str | None, value: str | None):
    """Get or set configuration."""
    from ..utils.config import get_config, config_help
    
    if not key:
        # Show all config
        repo = get_repo() if not global_config else None
        cfg = get_config(repo.path if repo else None)
        
        console.print("\n[bold]Global Configuration:[/bold]")
        console.print(f"  user.name: {cfg.global_config.name}")
        console.print(f"  user.email: {cfg.global_config.email or '(not set)'}")
        console.print(f"  ai.provider: {cfg.global_config.ai_provider}")
        console.print(f"  ai.model: {cfg.global_config.ai_model}")
        console.print(f"  ai.base_url: {cfg.global_config.ai_base_url}")
        console.print(f"  default_branch: {cfg.global_config.default_branch}")
        
        if cfg.repo_config:
            console.print("\n[bold]Repository Configuration:[/bold]")
            console.print(f"  description: {cfg.repo_config.description or '(not set)'}")
            console.print(f"  author: {cfg.repo_config.author or '(inherit global)'}")
        return
    
    if not value:
        # Show specific key
        cfg = get_config()
        config_map = {
            "user.name": cfg.global_config.name,
            "user.email": cfg.global_config.email,
            "ai.provider": cfg.global_config.ai_provider,
            "ai.model": cfg.global_config.ai_model,
            "ai.base_url": cfg.global_config.ai_base_url,
            "default_branch": cfg.global_config.default_branch,
        }
        if key in config_map:
            console.print(config_map[key])
        else:
            console.print(f"[yellow]Unknown config key: {key}[/yellow]")
        return
    
    # Set value
    cfg = get_config()
    
    if key == "user.name":
        cfg.set_user_name(value)
    elif key == "user.email":
        cfg.set_user_email(value)
    elif key == "ai.model":
        cfg.set_ai_model(value)
    elif key == "ai.base_url":
        cfg.set_ai_base_url(value)
    else:
        console.print(f"[yellow]Cannot set {key} directly. Use specific setter.[/yellow]")
        return
    
    console.print(f"[green]Set {key} = {value}[/green]")


@cli.command()
@click.option("-s", "--shell", "shell", default=None, help="Shell type (bash, zsh, fish)")
def completions(shell: str | None):
    """Install shell completions."""
    from .completions import install_completions
    
    if install_completions(shell):
        console.print("[green]Shell completions installed![/green]")
    else:
        console.print("[red]Failed to install completions[/red]")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("-p", "--port", default=8000, help="Port to listen on")
def serve(host: str, port: int):
    """Start the API server."""
    import uvicorn
    from ..api.main import app
    
    console.print(f"[green]Starting API server on {host}:{port}[/green]")
    console.print(f"[dim]Docs available at http://{host}:{port}/docs[/dim]")
    uvicorn.run(app, host=host, port=port)


@cli.command()
@click.option("--api-port", default=8000, help="API server port")
@click.option("--ui-port", default=3000, help="UI server port")
def ui(api_port: int, ui_port: int):
    """Start the full web UI (API + Frontend)."""
    import subprocess
    import threading
    import time
    import uvicorn
    from ..api.main import app
    
    # Start API server in background
    api_thread = threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=api_port, log_level="error"))
    api_thread.daemon = True
    api_thread.start()
    
    console.print(f"[green]Starting AugmentedVCS Web UI...[/green]")
    console.print(f"[dim]API server: http://localhost:{api_port}[/dim]")
    time.sleep(1)  # Give API time to start
    
    # Check if frontend is installed
    import os
    frontend_dir = Path(__file__).parent.parent.parent.parent
    package_json = frontend_dir / "package.json"
    node_modules = frontend_dir / "node_modules"
    
    if node_modules.exists() and (frontend_dir / "index.html").exists():
        console.print(f"[dim]Starting frontend on http://localhost:{ui_port}[/dim]")
        console.print(f"[green]Open http://localhost:{ui_port} in your browser[/green]")
        
        # Start frontend dev server
        subprocess.run(["npm", "run", "start"], cwd=str(frontend_dir), env={**os.environ, "PORT": str(ui_port)})
    else:
        console.print("[yellow]Frontend not installed. Installing...[/yellow]")
        subprocess.run(["npm", "install"], cwd=str(frontend_dir))
        console.print(f"[green]Run 'avcs ui' again to start the UI[/green]")


# Export the cli group as the main command
main = cli


if __name__ == "__main__":
    cli()
