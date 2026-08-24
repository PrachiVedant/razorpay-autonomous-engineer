from github.issues import get_issue
from github.git_operations import git_operations
from github.pull_requests import (
    validate_proposed_changes,
    is_sensitive_file,
)

from agents.repository import (
    get_repo_structure,
    read_file,
)
from agents.repository import write_file
from agents.repository import run_command

from agents.planner import plan_issue
from agents.code_generator import generate_fix


def solve_issue(repo, issue_number):
    """
    Orchestrate the autonomous coding workflow.

    Flow:
        GitHub Issue
            ↓
        Read Repository
            ↓
        Plan
            ↓
        Read Relevant Files
            ↓
        Generate Fix
            ↓
        Validate Changes
            ↓
        Apply Changes
            ↓
        Create Git Branch
            ↓
        Commit
            ↓
        Push
            ↓
        Create Pull Request
    """

    # --------------------------------------------------
    # 1. Fetch GitHub issue
    # --------------------------------------------------

    thread_id = (
        f"{repo.replace('/', '-')}"
        f"-issue-{issue_number}"
    )

    print(
        f"\n1. Fetching issue #{issue_number}..."
    )

    issue = get_issue(
        repo,
        issue_number,
    )

    print(
        f"   Title: {issue['title']}"
    )

    print(
        f"   Thread ID: {thread_id}"
    )

    # --------------------------------------------------
    # 2. Read repository structure
    # --------------------------------------------------

    print(
        "\n2. Reading repo structure..."
    )

    structure = get_repo_structure()

    # --------------------------------------------------
    # 3. Plan the issue
    # --------------------------------------------------

    print(
        "\n3. Analyzing the issue and "
        "planning the fix..."
    )

    plan = plan_issue(
        issue,
        structure,
    )

    print(
        f"   Approach: {plan['approach']}"
    )

    print(
        f"   Files to read: "
        f"{plan['files_to_read']}"
    )

    # --------------------------------------------------
    # 4. Read relevant files
    # --------------------------------------------------

    print(
        "\n4. Reading relevant files..."
    )

    file_content = {}

    for filepath in plan["files_to_read"]:

        content = read_file(
            filepath
        )

        file_content[filepath] = content

        print(
            f"   Read: {filepath}"
        )

    # --------------------------------------------------
    # 5. Generate code changes
    # --------------------------------------------------

    print(
        "\n5. Generating the fix..."
    )

    fix = generate_fix(
        issue,
        plan,
        file_content,
    )

    # --------------------------------------------------
    # 6. Validate generated changes
    # --------------------------------------------------

    try:

        validate_proposed_changes(
            fix["changes"]
        )

    except RuntimeError as error:

        print(
            f"Aborting: {error}"
        )

        return

    # --------------------------------------------------
    # 7. Apply changes
    # --------------------------------------------------

    print(
        "\n6. Applying changes..."
    )

    for change in fix["changes"]:

        write_file(
            change["path"],
            change["content"],
        )

        print(
            f"   Updated: "
            f"{change['path']}"
        )

    # --------------------------------------------------
    # 8. Create Git branch
    # --------------------------------------------------

    branch_name = thread_id

    print(
        f"\n7. Creating branch "
        f"'{branch_name}'..."
    )

    checkout_result = run_command(
        f"git checkout -b {branch_name}"
    )

    print(
        f"   git checkout -b "
        f"{branch_name}: "
        f"{checkout_result}"
    )

    # --------------------------------------------------
    # 9. Check sensitive files
    # --------------------------------------------------

    sensitive_files = [
        change["path"]
        for change in fix["changes"]
        if is_sensitive_file(
            change["path"]
        )
    ]

    # --------------------------------------------------
    # 10. Commit changes
    # --------------------------------------------------

    commit_result = git_operations.invoke(
        {
            "action": "commit",
            "commit_message": (
                f"fix: {issue['title']}"
            ),
            "num_files_changed": (
                len(fix["changes"])
            ),
            "sensitive_files": (
                sensitive_files
            ),
        }
    )

    print(
        f"   commit: {commit_result}"
    )

    # --------------------------------------------------
    # 11. Push branch
    # --------------------------------------------------

    push_result = git_operations.invoke(
        {
            "action": "push",
            "branch_name": branch_name,
        }
    )

    print(
        f"   push: {push_result}"
    )

    # --------------------------------------------------
    # 12. Create Pull Request
    # --------------------------------------------------

    pr_result = git_operations.invoke(
        {
            "action": "create_pr",
            "branch_name": branch_name,
            "repo": repo,
            "pr_title": thread_id,
            "pr_body": fix[
                "pr_description"
            ],
        }
    )

    print(
        f"   create_pr: {pr_result}"
    )

    print("\nDone.")