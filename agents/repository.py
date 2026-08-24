import subprocess
import os
from pathlib import Path

REPO_PATH = os.getcwd()


def run_command(command):
    """Run a shell command and return output."""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, cwd=REPO_PATH
    )
    return f"stdout: {result.stdout}\nstderr: {result.stderr}\nreturncode: {result.returncode}"

def get_repo_structure():
    """Get the current repo file structure."""
    root = Path.cwd()
    paths = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.match(".git/*"):
            continue
        if path.match("node_modules/*"):
            continue
        if path.match("venv/*") or path.match(".venv/*"):
            continue
        paths.append(str(path.relative_to(root)))

    return "\n".join(sorted(paths))


def read_file(filepath):
    """Read a file's contents."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {filepath}"


def write_file(filepath, content):
    """Write content to a file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return f"Written to {filepath}"