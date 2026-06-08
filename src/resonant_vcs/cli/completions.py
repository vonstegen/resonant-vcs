"""Shell completion setup for avcs."""

import os
import sys
import subprocess
from pathlib import Path


def install_bash_completion():
    """Install bash completion."""
    completions = """_avcs_completions()
{
    local cur prev words cword
    _init_completion -n = || return

    case "${prev}" in
        init|add|commit|checkout|branch|diff|restore|unstage)
            _filedir
            ;;
        -m|--message)
            return
            ;;
        -d|--description|--delete)
            return
            ;;
        -b|--branch)
            # Would need to query repo for branch names
            return
            ;;
        *)
            local commands="init add commit status log checkout branch diff restore unstage ai ai-status suggest explain story chat"
            COMPREPLY=( $(compgen -W "${commands}" -- "${cur}") )
            ;;
    esac
}

complete -F _avcs_completions avcs"""

    # Check if we're in a bashrc or profile
    bash_files = [
        Path.home() / ".bashrc",
        Path.home() / ".bash_completion",
        Path.home() / ".profile",
    ]

    for bash_file in bash_files:
        if bash_file.exists():
            content = bash_file.read_text()
            if "avcs_completions" not in content:
                bash_file.write_text(content + "\n\n# AugmentedVCS completion\n" + completions + "\n")
                print(f"Added completions to {bash_file}")
                return True

    # If none exist, create a new completion file
    completion_dir = Path.home() / ".bash_completion.d"
    completion_dir.mkdir(exist_ok=True)
    (completion_dir / "avcs").write_text(completions + "\n")

    print(f"Created {completion_dir / 'avcs'}")
    print("Add this to your .bashrc:")
    print("  source ~/.bash_completion.d/avcs")
    return True


def install_zsh_completion():
    """Install zsh completion."""
    completions = """#compdef avcs

_avcs() {
    local -a commands
    commands=(
        'init:Initialize a new repository'
        'add:Stage files for commit'
        'commit:Create a new version'
        'status:Show working tree status'
        'log:Show version history'
        'checkout:Switch versions or branches'
        'branch:Create or list branches'
        'diff:Show changes between versions'
        'restore:Restore files from the last commit'
        'unstage:Unstage files'
        'ai:Process natural language VCS command'
        'ai-status:Check AI provider status'
        'suggest:Suggest a commit message'
        'explain:Explain changes in plain language'
        'story:Tell version history as a story'
        'chat:Start conversational AI assistant'
    )

    _describe 'command' commands
}

_avcs"""

    comp_dir = Path.home() / ".zsh" / "completions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "_avcs").write_text(completions + "\n")
    print(f"Created zsh completion at {comp_dir / '_avcs'}")
    return True


def install_fish_completion():
    """Install fish completion."""
    completions = """complete -c avcs -f -a 'init' -d 'Initialize a new repository'
complete -c avcs -f -a 'add' -d 'Stage files for commit'
complete -c avcs -f -a 'commit' -d 'Create a new version'
complete -c avcs -f -a 'status' -d 'Show working tree status'
complete -c avcs -f -a 'log' -d 'Show version history'
complete -c avcs -f -a 'checkout' -d 'Switch versions or branches'
complete -c avcs -f -a 'branch' -d 'Create or list branches'
complete -c avcs -f -a 'diff' -d 'Show changes between versions'
complete -c avcs -f -a 'restore' -d 'Restore files from the last commit'
complete -c avcs -f -a 'unstage' -d 'Unstage files'
complete -c avcs -f -a 'ai' -d 'Process natural language VCS command'
complete -c avcs -f -a 'ai-status' -d 'Check AI provider status'
complete -c avcs -f -a 'suggest' -d 'Suggest a commit message'
complete -c avcs -f -a 'explain' -d 'Explain changes in plain language'
complete -c avcs -f -a 'story' -d 'Tell version history as a story'
complete -c avcs -f -a 'chat' -d 'Start conversational AI assistant'"""

    comp_dir = Path.home() / ".config" / "fish" / "completions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "avcs.fish").write_text(completions + "\n")
    print(f"Created fish completion at {comp_dir / 'avcs.fish'}")
    return True


def install_completions(shell: str = None):
    """Install shell completions."""
    if shell is None:
        shell = os.path.basename(os.environ.get("SHELL", "bash"))

    if "zsh" in shell:
        return install_zsh_completion()
    elif "fish" in shell:
        return install_fish_completion()
    elif "bash" in shell:
        return install_bash_completion()
    else:
        print(f"Unknown shell: {shell}")
        print("Supported: bash, zsh, fish")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Install shell completions for avcs")
    parser.add_argument("-s", "--shell", choices=["bash", "zsh", "fish"], help="Shell type")
    args = parser.parse_args()

    success = install_completions(args.shell)
    sys.exit(0 if success else 1)