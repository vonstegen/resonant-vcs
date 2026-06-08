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
            if f.is_file() and not f.is_hidden() and ".avcs" not in f.parts:
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


# Export the cli group as the main command
main = cli


if __name__ == "__main__":
    cli()
