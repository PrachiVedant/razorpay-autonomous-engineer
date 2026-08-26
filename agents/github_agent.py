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
from agents.audit import audit_logger

from razorpay.policy import validate_payment_plan
from razorpay.validator import validate_changes


def solve_issue(repo, issue_number):
    """
    Orchestrate the autonomous coding workflow.

    The workflow is:

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
        Repair Agent if needed
            ↓
        Git Branch
            ↓
        Commit
            ↓
        Push
            ↓
        Pull Request

    All important workflow transitions are recorded
    in the audit trail.
    """

    thread_id = (
        f"{repo.replace('/', '-')}"
        f"-issue-{issue_number}"
    )

    # --------------------------------------------------
    # 1. Fetch GitHub issue
    # --------------------------------------------------

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

    audit_logger.log(
        "ISSUE_RECEIVED",
        details={
            "repo": repo,
            "issue_number": issue_number,
            "thread_id": thread_id,
            "title": issue["title"],
        },
    )

    # --------------------------------------------------
    # 2. Read repository structure
    # --------------------------------------------------

    print(
        "\n2. Reading repository structure..."
    )

    structure = get_repo_structure()

    audit_logger.log(
        "REPOSITORY_ANALYZED",
        details={
            "thread_id": thread_id,
        },
    )

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

    audit_logger.log(
        "PLAN_CREATED",
        details={
            "thread_id": thread_id,
            "files_to_read": plan["files_to_read"],
            "requires_razorpay": plan.get(
                "requires_razorpay",
                False,
            ),
        },
    )

    # --------------------------------------------------
    # 4. Razorpay risk classification
    # --------------------------------------------------

    payment_policy = validate_payment_plan(
        plan
    )

    if not payment_policy["allowed"]:

        print(
            "\nPayment policy rejected the plan."
        )

        print(
            f"Reason: "
            f"{payment_policy['reason']}"
        )

        audit_logger.log(
            "PAYMENT_POLICY_REJECTED",
            status="FAIL",
            details={
                "reason": payment_policy["reason"],
            },
        )

        audit_logger.log(
            "WORKFLOW_ABORTED",
            status="FAIL",
            details={
                "reason": "Payment policy rejected plan.",
            },
        )

        return

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

        audit_logger.log(
            "PAYMENT_RISK_CLASSIFIED",
            details={
                "operation": plan.get(
                    "payment_operation"
                ),
                "risk_level": plan.get(
                    "risk_level"
                ),
                "requires_approval": payment_policy[
                    "requires_approval"
                ],
            },
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

    audit_logger.log(
        "FILES_READ",
        details={
            "files": list(file_content.keys()),
        },
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

    audit_logger.log(
        "CODE_GENERATED",
        details={
            "files": [
                change["path"]
                for change in fix["changes"]
            ],
            "num_changes": len(
                fix["changes"]
            ),
        },
    )

    # --------------------------------------------------
    # 7. Validate generated changes
    # --------------------------------------------------

    print(
        "\n6. Validating generated changes..."
    )

    try:

        validate_proposed_changes(
            fix["changes"]
        )

    except RuntimeError as error:

        print(
            f"Aborting: {error}"
        )

        audit_logger.log(
            "SECURITY_VALIDATION_FAILED",
            status="FAIL",
            details={
                "validator": "github",
                "reason": str(error),
            },
        )

        audit_logger.log(
            "WORKFLOW_ABORTED",
            status="FAIL",
            details={
                "reason": "GitHub change validation failed.",
            },
        )

        return

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

        audit_logger.log(
            "SECURITY_VALIDATION_FAILED",
            status="FAIL",
            details={
                "validator": "razorpay",
                "error_count": len(
                    razorpay_validation["errors"]
                ),
            },
        )

        audit_logger.log(
            "WORKFLOW_ABORTED",
            status="FAIL",
            details={
                "reason": "Razorpay security validation failed.",
            },
        )

        print(
            "\nAborting before applying changes."
        )

        return

    print(
        "   Validation passed."
    )

    audit_logger.log(
        "SECURITY_VALIDATION_PASSED",
        status="PASS",
        details={
            "files": [
                change["path"]
                for change in fix["changes"]
            ],
        },
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

        audit_logger.log(
            "HUMAN_APPROVAL_REQUIRED",
            details={
                "operation": plan.get(
                    "payment_operation"
                ),
                "risk_level": plan.get(
                    "risk_level"
                ),
                "files": [
                    change["path"]
                    for change in fix["changes"]
                ],
            },
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

            audit_logger.log(
                "HUMAN_APPROVAL_DENIED",
                status="FAIL",
                details={
                    "operation": plan.get(
                        "payment_operation"
                    ),
                },
            )

            audit_logger.log(
                "WORKFLOW_ABORTED",
                status="FAIL",
                details={
                    "reason": "Human approval denied.",
                },
            )

            return

        print(
            "\nHuman approval granted."
        )

        audit_logger.log(
            "HUMAN_APPROVAL_GRANTED",
            status="PASS",
            details={
                "operation": plan.get(
                    "payment_operation"
                ),
            },
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

    audit_logger.log(
        "CHANGES_APPLIED",
        status="PASS",
        details={
            "files": [
                change["path"]
                for change in fix["changes"]
            ],
        },
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

        audit_logger.log(
            "WORKFLOW_ABORTED",
            status="FAIL",
            details={
                "reason": "Autonomous repair failed.",
                "attempts": repair_result["attempts"],
            },
        )

        return

    print(
        "\n   Tests passed!"
    )

    fix["changes"] = repair_result[
        "final_changes"
    ]

    print(
        f"   Final files: "
        f"{[change['path'] for change in fix['changes']]}"
    )

    audit_logger.log(
        "REPAIR_LOOP_COMPLETED",
        status="PASS",
        details={
            "attempts": repair_result["attempts"],
            "files": [
                change["path"]
                for change in fix["changes"]
            ],
        },
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

    audit_logger.log(
        "GIT_BRANCH_CREATED",
        status="PASS",
        details={
            "branch": branch_name,
        },
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

    audit_logger.log(
        "GIT_COMMIT_CREATED",
        status="PASS",
        details={
            "num_files_changed": len(
                fix["changes"]
            ),
        },
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

    audit_logger.log(
        "GIT_PUSHED",
        status="PASS",
        details={
            "branch": branch_name,
        },
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

    audit_logger.log(
        "PULL_REQUEST_CREATED",
        status="PASS",
        details={
            "repo": repo,
            "branch": branch_name,
        },
    )

    # --------------------------------------------------
    # DONE
    # --------------------------------------------------

    audit_logger.log(
        "WORKFLOW_COMPLETED",
        status="PASS",
        details={
            "repo": repo,
            "issue_number": issue_number,
            "branch": branch_name,
        },
    )

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