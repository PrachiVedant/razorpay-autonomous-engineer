from github.issues import get_issue
from github.git_operations import git_operations
from github.pull_requests import (
    validate_proposed_changes,
    is_sensitive_file,
)

from agents.repository import (
    get_repo_structure,
    read_file,
    write_file,
    run_command,
)

from agents.planner import plan_issue
from agents.code_generator import generate_fix

from razorpay.policy import validate_payment_plan
from razorpay.validator import validate_changes


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
        Razorpay Policy Check
            ↓
        Security Validation
            ↓
        Human Approval (if required)
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
        f"\n1. Fetching GitHub issue #{issue_number}..."
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
        "\n2. Reading repository structure..."
    )

    structure = get_repo_structure()

    # --------------------------------------------------
    # 3. Plan the issue
    # --------------------------------------------------

    print(
        "\n3. Analyzing issue and planning fix..."
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
    # 4. Display Razorpay risk classification
    # --------------------------------------------------

    payment_policy = validate_payment_plan(
        plan
    )

    if plan.get("requires_razorpay", False):

        print(
            "\n   Razorpay payment operation detected."
        )

        print(
            f"   Operation: "
            f"{plan.get('payment_operation')}"
        )

        print(
            f"   Risk level: "
            f"{plan.get('risk_level')}"
        )

        print(
            f"   Human approval required: "
            f"{payment_policy['requires_approval']}"
        )

    # --------------------------------------------------
    # 5. Read relevant files
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
    # 6. Generate code changes
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
    # 7. Validate generated changes
    # --------------------------------------------------

    print(
        "\n6. Validating generated changes..."
    )

    # Existing GitHub/security validation
    try:

        validate_proposed_changes(
            fix["changes"]
        )

    except RuntimeError as error:

        print(
            f"Aborting: {error}"
        )

        return

    # Razorpay-specific security validation
    razorpay_validation = validate_changes(
        fix["changes"]
    )

    if not razorpay_validation["valid"]:

        print(
            "\nRazorpay security validation failed."
        )

        for error in razorpay_validation["errors"]:

            print(
                f"   - {error}"
            )

        print(
            "\nAborting before applying changes."
        )

        return

    print(
        "   Validation passed."
    )

    # --------------------------------------------------
    # 8. Human approval for risky payment changes
    # --------------------------------------------------

    if payment_policy["requires_approval"]:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "HUMAN APPROVAL REQUIRED"
        )

        print(
            "=" * 60
        )

        print(
            f"Payment operation: "
            f"{plan.get('payment_operation')}"
        )

        print(
            f"Risk level: "
            f"{plan.get('risk_level')}"
        )

        print(
            "\nThe autonomous agent generated "
            f"{len(fix['changes'])} file change(s)."
        )

        print(
            "\nFiles that will be modified:"
        )

        for change in fix["changes"]:

            print(
                f"   - {change['path']}"
            )

        print(
            "\nThe changes will NOT be applied "
            "without approval."
        )

        approval = input(
            "\nApprove these payment changes? "
            "[y/N]: "
        ).strip().lower()

        if approval not in {
            "y",
            "yes",
        }:

            print(
                "\nApproval denied."
            )

            print(
                "Aborting before modifying "
                "the repository."
            )

            return

        print(
            "\nHuman approval granted."
        )

    # --------------------------------------------------
    # 9. Apply changes
    # --------------------------------------------------

    print(
        "\n7. Applying changes..."
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
    # 10. Create Git branch
    # --------------------------------------------------

    branch_name = thread_id

    print(
        f"\n8. Creating branch "
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
    # 11. Check sensitive files
    # --------------------------------------------------

    sensitive_files = [
        change["path"]
        for change in fix["changes"]
        if is_sensitive_file(
            change["path"]
        )
    ]

    # --------------------------------------------------
    # 12. Commit changes
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
    # 13. Push branch
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
    # 14. Create Pull Request
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

    print(
        "\nDone."
    )