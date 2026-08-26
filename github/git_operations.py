import subprocess


class GitOperationsError(RuntimeError):
    """Raised when a Git operation fails."""


def _run_git_command(command):
    """Run a git command and return its output."""

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise GitOperationsError(
            f"Git command failed:\n"
            f"{result.stderr.strip()}"
        )

    return result.stdout.strip()


class GitOperations:
    """
    Safe Git operations for the autonomous coding agent.

    Git operations are intentionally restricted so that
    the agent only commits files that it explicitly changed.
    """

    # --------------------------------------------------
    # Branch
    # --------------------------------------------------

    def create_branch(self, branch_name):
        """
        Create and checkout a new branch.
        """

        if not branch_name:
            raise GitOperationsError(
                "Branch name cannot be empty."
            )

        return _run_git_command(
            f'git checkout -b "{branch_name}"'
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def get_status(self):
        """
        Return current git status.
        """

        return _run_git_command(
            "git status --short"
        )

        # --------------------------------------------------
    # Rollback
    # --------------------------------------------------

    def rollback_files(self, files):
        """
        Restore only the files explicitly supplied.

        Used when autonomous repair fails and the
        repository must be returned to its previous state.
        """

        if not files:
            raise GitOperationsError(
                "No files supplied for rollback."
            )

        for filepath in files:

            if not filepath:
                raise GitOperationsError(
                    "Invalid empty file path."
                )

            normalized = filepath.replace(
                "\\",
                "/",
            )

            if normalized.startswith("../"):
                raise GitOperationsError(
                    f"Unsafe file path: {filepath}"
                )

            _run_git_command(
                f'git restore -- "{filepath}"'
            )

        return True

    # --------------------------------------------------
    # Stage specific files
    # --------------------------------------------------

    def stage_files(self, files):
        """
        Stage only the files supplied by the agent.
        """

        if not files:
            raise GitOperationsError(
                "No files supplied for staging."
            )

        for filepath in files:

            if not filepath:
                raise GitOperationsError(
                    "Invalid empty file path."
                )

            # Prevent obvious path traversal.
            normalized = filepath.replace(
                "\\",
                "/",
            )

            if normalized.startswith("../"):
                raise GitOperationsError(
                    f"Unsafe file path: {filepath}"
                )

            _run_git_command(
                f'git add -- "{filepath}"'
            )

        return _run_git_command(
            "git diff --cached --name-only"
        )

    # --------------------------------------------------
    # Verify staged files
    # --------------------------------------------------

    def verify_staged_files(self, expected_files):
        """
        Ensure that ONLY expected files are staged.
        """

        staged_output = _run_git_command(
            "git diff --cached --name-only"
        )

        staged_files = [
            line.strip()
            for line in staged_output.splitlines()
            if line.strip()
        ]

        expected = {
            path.replace("\\", "/")
            for path in expected_files
        }

        actual = {
            path.replace("\\", "/")
            for path in staged_files
        }

        if actual != expected:

            raise GitOperationsError(
                "Staged files do not match generated changes.\n"
                f"Expected: {sorted(expected)}\n"
                f"Actual: {sorted(actual)}"
            )

        return True

    # --------------------------------------------------
    # Commit
    # --------------------------------------------------

    def commit(
        self,
        commit_message,
        files=None,
    ):
        """
        Stage and commit only explicitly generated files.
        """

        if files is None:
            raise GitOperationsError(
                "Explicit file list is required for commit."
            )

        self.stage_files(files)

        self.verify_staged_files(
            files
        )

        return _run_git_command(
            f'git commit -m "{commit_message}"'
        )

    # --------------------------------------------------
    # Push
    # --------------------------------------------------

    def push(self, branch_name):
        """
        Push the agent branch to origin.
        """

        if not branch_name:
            raise GitOperationsError(
                "Branch name cannot be empty."
            )

        return _run_git_command(
            f'git push -u origin "{branch_name}"'
        )

    # --------------------------------------------------
    # Pull Request
    # --------------------------------------------------

    def create_pr(
        self,
        branch_name,
        repo,
        pr_title,
        pr_body,
    ):
        """
        Create a GitHub Pull Request using GitHub CLI.
        """

        if not branch_name:
            raise GitOperationsError(
                "Branch name cannot be empty."
            )

        if not repo:
            raise GitOperationsError(
                "Repository cannot be empty."
            )

        title = (
            pr_title
            .replace('"', '\\"')
        )

        body = (
            pr_body
            .replace('"', '\\"')
        )

        command = (
            f'gh pr create '
            f'--repo "{repo}" '
            f'--head "{branch_name}" '
            f'--title "{title}" '
            f'--body "{body}"'
        )

        return _run_git_command(
            command
        )

    # --------------------------------------------------
    # Generic invoke interface
    # --------------------------------------------------

    def invoke(self, params):

        action = params.get(
            "action"
        )

        if action == "branch":

            return self.create_branch(
                params["branch_name"]
            )

        if action == "commit":

            return self.commit(
                commit_message=params[
                    "commit_message"
                ],
                files=params.get(
                    "files"
                ),
            )

        if action == "push":

            return self.push(
                branch_name=params[
                    "branch_name"
                ]
            )

        if action == "create_pr":

            return self.create_pr(
                branch_name=params[
                    "branch_name"
                ],
                repo=params[
                    "repo"
                ],
                pr_title=params[
                    "pr_title"
                ],
                pr_body=params[
                    "pr_body"
                ],
            )
        if action == "rollback":

            return self.rollback_files(
                params["files"]
            )

        raise GitOperationsError(
            f"Unknown git operation: {action}"
        )


git_operations = GitOperations()