from agents.repair_loop import repair_loop
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
        Repository Analysis
            ↓
        Planner
            ↓
        Razorpay Risk Classification
            ↓
        Read Relevant Files
            ↓
        Code Generator
            ↓
        Security Validation
            ↓
        Human Approval
            ↓
        Apply Changes
            ↓
        Run Tests
            ↓
        ┌─────────────────┐
        │                 │
       PASS              FAIL
        │                 │
        ↓                 ↓
       Git            Repair Agent
                         ↓
                     Run Tests
                         ↓
                       PASS
                         ↓
                        Git
                         ↓
                        PR
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
    # 3. Plan issue
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
    # 4. Razorpay risk classification
    # --------------------------------------------------

    payment_policy = validate_payment_plan(
        plan
    )

    if plan.get(
        "requires_razorpay",
        False,
    ):

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

    print(
        f"   Generated "
        f"{len(fix['changes'])} file change(s)"
    )

    # --------------------------------------------------
    # 7. Validate generated changes
    # --------------------------------------------------

    print(
        "\n6. Validating generated changes..."
    )

    # GitHub/security validation

    try:

        validate_proposed_changes(
            fix["changes"]
        )

    except RuntimeError as error:

        print(
            f"Aborting: {error}"
        )

        return

    # Razorpay security validation

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
    # 8. Human approval
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
    # 9. Apply generated changes
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
    # 10. Run tests + autonomous repair
    # --------------------------------------------------

    print(
        "\n8. Running test suite..."
    )

    repair_result = repair_loop(
        issue=issue,
        changed_files=fix["changes"],
        test_command="uv run pytest tests/",
    )

    # --------------------------------------------------
    # 11. Handle test/repair result
    # --------------------------------------------------

    if not repair_result["success"]:

        print(
            "\n   Autonomous repair failed."
        )

        print(
            "   Aborting before Git operations."
        )

        return

    print(
        "\n   Tests passed!"
    )

    # IMPORTANT:
    # The repair loop may have modified the files.
    # Therefore, use the final repaired changes.
    fix["changes"] = repair_result[
        "final_changes"
    ]

    print(
        f"   Final files: "
        f"{[change['path'] for change in fix['changes']]}"
    )

    # --------------------------------------------------
    # 12. Create Git branch
    # --------------------------------------------------

    branch_name = thread_id

    print(
        f"\n9. Creating branch "
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
    # 13. Check sensitive files
    # --------------------------------------------------

    sensitive_files = [
        change["path"]
        for change in fix["changes"]
        if is_sensitive_file(
            change["path"]
        )
    ]

    # --------------------------------------------------
    # 14. Commit changes
    # --------------------------------------------------

    print(
        "\n10. Committing changes..."
    )

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
    # 15. Push branch
    # --------------------------------------------------

    print(
        "\n11. Pushing branch..."
    )

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
    # 16. Create Pull Request
    # --------------------------------------------------

    print(
        "\n12. Creating Pull Request..."
    )

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

    # --------------------------------------------------
    # DONE
    # --------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "AUTONOMOUS CODING WORKFLOW COMPLETE"
    )

    print(
        "=" * 60
    )