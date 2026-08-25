import subprocess
from pathlib import Path


def _run_git_command(command):
    """Run a git command and return its output."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed:\n"
            f"{result.stderr.strip()}"
        )

    return result.stdout.strip()


class GitOperations:
    def invoke(self, params):
        action = params.get("action")

        if action == "commit":
            return self.commit(
                commit_message=params["commit_message"]
            )

        if action == "push":
            return self.push(
                branch_name=params["branch_name"]
            )

        if action == "create_pr":
            return self.create_pr(
                branch_name=params["branch_name"],
                repo=params["repo"],
                pr_title=params["pr_title"],
                pr_body=params["pr_body"],
            )

        raise ValueError(
            f"Unknown git operation: {action}"
        )

    def commit(self, commit_message):
        """Stage and commit changes."""

        _run_git_command("git add .")

        return _run_git_command(
            f'git commit -m "{commit_message}"'
        )

    def push(self, branch_name):
        """Push the current branch to origin."""

        return _run_git_command(
            f"git push -u origin {branch_name}"
        )

    def create_pr(
        self,
        branch_name,
        repo,
        pr_title,
        pr_body,
    ):
        """
        Create a GitHub pull request using GitHub CLI.

        Requires:
            gh auth login
        """

        # Escape quotes for shell command
        title = pr_title.replace('"', '\\"')
        body = pr_body.replace('"', '\\"')

        command = (
            f'gh pr create '
            f'--repo "{repo}" '
            f'--head "{branch_name}" '
            f'--title "{title}" '
            f'--body "{body}"'
        )

        return _run_git_command(command)


git_operations = GitOperations()