from agents.repair_loop import repair_loop
from agents.audit import audit_logger

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
)

from agents.planner import plan_issue
from agents.code_generator import generate_fix

from razorpay.policy import validate_payment_plan
from razorpay.validator import validate_changes

from guardrail.security_validator import SecurityValidator


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
        ┌─────────────────────┐
        │                     │
       PASS                  FAIL
        │                     │
        ↓                     ↓
       Git                Repair Agent
        │                     ↓
        │                 Run Tests
        │                     ↓
        │                   PASS
        │                     ↓
        └─────────────────── Git
                              ↓
                              PR

    The agent stops safely whenever validation,
    testing, repair, Git, or PR creation fails.
    """

    # ==================================================
    # 1. Fetch GitHub issue
    # ==================================================

    thread_id = (
        f"{repo.replace('/', '-')}"
        f"-issue-{issue_number}"
    )

    print(
        f"\n1. Fetching GitHub issue #{issue_number}..."
    )

    try:
        issue = get_issue(
            repo,
            issue_number,
        )

    except Exception as error:

        print(
            f"\nFailed to fetch GitHub issue: {error}"
        )

        audit_logger.log(
            "ISSUE_FETCH_FAILED",
            status="FAIL",
            details={
                "repo": repo,
                "issue_number": issue_number,
                "reason": str(error),
            },
        )

        return

    print(
        f"   Title: {issue['title']}"
    )

    print(
        f"   Thread ID: {thread_id}"
    )

    audit_logger.log(
        "ISSUE_RECEIVED",
        status="INFO",
        details={
            "repo": repo,
            "issue_number": issue_number,
            "thread_id": thread_id,
            "title": issue["title"],
        },
    )

    # ==================================================
    # 2. Read repository structure
    # ==================================================

    print(
        "\n2. Reading repository structure..."
    )

    try:
        structure = get_repo_structure()

    except Exception as error:

        print(
            f"\nRepository analysis failed: {error}"
        )

        audit_logger.log(
            "REPOSITORY_ANALYSIS_FAILED",
            status="FAIL",
            details={
                "thread_id": thread_id,
                "reason": str(error),
            },
        )

        return

    audit_logger.log(
        "REPOSITORY_ANALYZED",
        status="INFO",
        details={
            "thread_id": thread_id,
        },
    )

    # ==================================================
    # 3. Plan issue
    # ==================================================

    print(
        "\n3. Analyzing issue and planning fix..."
    )

    try:
        plan = plan_issue(
            issue,
            structure,
        )

    except Exception as error:

        print(
            f"\nPlanning failed: {error}"
        )

        audit_logger.log(
            "PLAN_CREATION_FAILED",
            status="FAIL",
            details={
                "thread_id": thread_id,
                "reason": str(error),
            },
        )

        return

    print(
        f"   Approach: {plan['approach']}"
    )

    print(
        f"   Files to read: "
        f"{plan['files_to_read']}"
    )

    audit_logger.log(
        "PLAN_CREATED",
        status="INFO",
        details={
            "thread_id": thread_id,
            "files_to_read": plan["files_to_read"],
            "requires_razorpay": plan.get(
                "requires_razorpay",
                False,
            ),
        },
    )

    # ==================================================
    # 4. Razorpay risk classification
    # ==================================================

    payment_policy = validate_payment_plan(
        plan
    )

    if not payment_policy["allowed"]:

        print(
            "\nRazorpay payment policy rejected "
            "this operation."
        )

        print(
            f"Reason: "
            f"{payment_policy['reason']}"
        )

        audit_logger.log(
            "PAYMENT_POLICY_REJECTED",
            status="FAIL",
            details={
                "thread_id": thread_id,
                "reason": payment_policy["reason"],
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
            status="INFO",
            details={
                "thread_id": thread_id,
                "operation": plan.get(
                    "payment_operation"
                ),
                "risk_level": plan.get(
                    "risk_level"
                ),
                "requires_approval": (
                    payment_policy[
                        "requires_approval"
                    ]
                ),
            },
        )

    # ==================================================
    # 5. Read relevant files
    # ==================================================

    print(
        "\n4. Reading relevant files..."
    )

    file_content = {}

    try:

        for filepath in plan["files_to_read"]:

            content = read_file(
                filepath
            )

            file_content[filepath] = content

            print(
                f"   Read: {filepath}"
            )

    except Exception as error:

        print(
            f"\nFailed to read repository files: {error}"
        )

        audit_logger.log(
            "FILES_READ_FAILED",
            status="FAIL",
            details={
                "thread_id": thread_id,
                "reason": str(error),
            },
        )

        return

    audit_logger.log(
        "FILES_READ",
        status="INFO",
        details={
            "files": list(
                file_content.keys()
            ),
        },
    )

    # ==================================================
    # 6. Generate code changes
    # ==================================================

    print(
        "\n5. Generating the fix..."
    )

    try:

        fix = generate_fix(
            issue,
            plan,
            file_content,
        )

    except Exception as error:

        print(
            f"\nCode generation failed: {error}"
        )

        audit_logger.log(
            "CODE_GENERATION_FAILED",
            status="FAIL",
            details={
                "thread_id": thread_id,
                "reason": str(error),
            },
        )

        return

    changes = fix.get(
        "changes",
        [],
    )

    if not changes:

        print(
            "\nCode generator produced no changes."
        )

        audit_logger.log(
            "CODE_GENERATION_EMPTY",
            status="FAIL",
            details={
                "thread_id": thread_id,
            },
        )

        return

    print(
        f"   Generated "
        f"{len(changes)} file change(s)"
    )

    audit_logger.log(
        "CODE_GENERATED",
        status="INFO",
        details={
            "files": [
                change["path"]
                for change in changes
            ],
            "num_changes": len(changes),
        },
    )

    # ==================================================
    # 7. Validate generated changes
    # ==================================================

    print(
        "\n6. Validating generated changes..."
    )

    # --------------------------------------------------
    # 7A. GitHub change safety validation
    # --------------------------------------------------

    try:

        validate_proposed_changes(
            changes
        )

    except RuntimeError as error:

        print(
            f"\nAborting: {error}"
        )

        audit_logger.log(
            "CHANGE_VALIDATION_FAILED",
            status="FAIL",
            details={
                "files": [
                    change["path"]
                    for change in changes
                ],
                "reason": str(error),
            },
        )

        return

    # --------------------------------------------------
    # 7B. Deterministic security validation
    # --------------------------------------------------

    security_validator = SecurityValidator()

    security_result = (
        security_validator.validate_changes(
            changes
        )
    )

    if not security_result["valid"]:

        print(
            "\nSECURITY VALIDATION FAILED"
        )

        for violation in (
            security_result["violations"]
        ):

            print(
                f"   - {violation}"
            )

        audit_logger.log(
            "SECURITY_VALIDATION_FAILED",
            status="FAIL",
            details={
                "files": [
                    change["path"]
                    for change in changes
                ],
                "violations": (
                    security_result[
                        "violations"
                    ]
                ),
            },
        )

        print(
            "\nAborting before applying changes."
        )

        return

    # --------------------------------------------------
    # 7C. Razorpay-specific validation
    # --------------------------------------------------

    razorpay_validation = validate_changes(
        changes
    )

    if not razorpay_validation["valid"]:

        print(
            "\nRazorpay security validation failed."
        )

        for error in (
            razorpay_validation["errors"]
        ):

            print(
                f"   - {error}"
            )

        audit_logger.log(
            "RAZORPAY_SECURITY_VALIDATION_FAILED",
            status="FAIL",
            details={
                "files": [
                    change["path"]
                    for change in changes
                ],
                "errors": (
                    razorpay_validation[
                        "errors"
                    ]
                ),
            },
        )

        print(
            "\nAborting before applying changes."
        )

        return

    # --------------------------------------------------
    # All security checks passed
    # --------------------------------------------------

    audit_logger.log(
        "SECURITY_VALIDATION_PASSED",
        status="PASS",
        details={
            "files": [
                change["path"]
                for change in changes
            ],
        },
    )

    print(
        "   Validation passed."
    )

    # ==================================================
    # 8. Human approval
    # ==================================================

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
            f"{len(changes)} file change(s)."
        )

        print(
            "\nFiles that will be modified:"
        )

        for change in changes:

            print(
                f"   - {change['path']}"
            )

        audit_logger.log(
            "HUMAN_APPROVAL_REQUIRED",
            status="INFO",
            details={
                "operation": plan.get(
                    "payment_operation"
                ),
                "risk_level": plan.get(
                    "risk_level"
                ),
                "files": [
                    change["path"]
                    for change in changes
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
                    "files": [
                        change["path"]
                        for change in changes
                    ],
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
                "files": [
                    change["path"]
                    for change in changes
                ],
            },
        )

    # ==================================================
    # 9. Apply generated changes
    # ==================================================

    print(
        "\n7. Applying changes..."
    )

    try:

        for change in changes:

            write_file(
                change["path"],
                change["content"],
            )

            print(
                f"   Updated: "
                f"{change['path']}"
            )

    except Exception as error:

        print(
            f"\nFailed to apply changes: {error}"
        )

        audit_logger.log(
            "CHANGES_APPLICATION_FAILED",
            status="FAIL",
            details={
                "files": [
                    change["path"]
                    for change in changes
                ],
                "reason": str(error),
            },
        )

        return

    audit_logger.log(
        "CHANGES_APPLIED",
        status="PASS",
        details={
            "files": [
                change["path"]
                for change in changes
            ],
        },
    )

    # ==================================================
    # 10. Run tests + autonomous repair
    # ==================================================

    print(
        "\n8. Running test suite..."
    )

    audit_logger.log(
        "TEST_STARTED",
        status="INFO",
        details={
            "thread_id": thread_id,
            "test_command": "uv run pytest tests/",
        },
    )

    repair_result = repair_loop(
        issue=issue,
        changed_files=changes,
        test_command="uv run pytest tests/",
    )

    # ==================================================
    # 11. Handle test/repair result
    # ==================================================

    if not repair_result["success"]:

        print(
            "\n   Autonomous repair failed."
        )

        print(
            "   Rolling back generated changes..."
        )

        changed_paths = [
            change["path"]
            for change in changes
        ]

        audit_logger.log(
            "TEST_FAILED",
            status="FAIL",
            details={
                "files": changed_paths,
                "attempts": repair_result[
                    "attempts"
                ],
            },
        )

        try:

            git_operations.invoke(
                {
                    "action": "rollback",
                    "files": changed_paths,
                }
            )

            print(
                "   Rollback completed."
            )

            audit_logger.log(
                "ROLLBACK_COMPLETED",
                status="PASS",
                details={
                    "files": changed_paths,
                    "attempts": repair_result[
                        "attempts"
                    ],
                },
            )

        except Exception as error:

            print(
                f"   Rollback failed: {error}"
            )

            audit_logger.log(
                "ROLLBACK_FAILED",
                status="FAIL",
                details={
                    "files": changed_paths,
                    "reason": str(error),
                },
            )

        audit_logger.log(
            "REPAIR_LOOP_FAILED",
            status="FAIL",
            details={
                "files": changed_paths,
                "attempts": repair_result[
                    "attempts"
                ],
            },
        )

        print(
            "\n   Aborting before Git operations."
        )

        # IMPORTANT:
        # Return ONLY when repair actually failed.
        return

    # ==================================================
    # Repair/test succeeded
    # ==================================================

    audit_logger.log(
        "TEST_PASSED",
        status="PASS",
        details={
            "files": [
                change["path"]
                for change in changes
            ],
            "attempts": repair_result[
                "attempts"
            ],
        },
    )

    audit_logger.log(
        "REPAIR_LOOP_COMPLETED",
        status="PASS",
        details={
            "attempts": repair_result[
                "attempts"
            ],
        },
    )

    # IMPORTANT:
    #
    # The repair loop may have modified the files.
    # Therefore, use the final repaired changes.

    changes = repair_result[
        "final_changes"
    ]

    fix["changes"] = changes

    final_files = [
        change["path"]
        for change in changes
    ]

    print(
        f"   Final files: "
        f"{final_files}"
    )

    # ==================================================
    # 12. Check sensitive files
    # ==================================================

    sensitive_files = [
        change["path"]
        for change in changes
        if is_sensitive_file(
            change["path"]
        )
    ]

    if sensitive_files:

        print(
            "\nSensitive files detected."
        )

        print(
            "Aborting before Git operations."
        )

        audit_logger.log(
            "SENSITIVE_FILES_DETECTED",
            status="FAIL",
            details={
                "files": sensitive_files,
            },
        )

        return

    # ==================================================
    # 13. Create Git branch
    # ==================================================

    branch_name = thread_id

    print(
        f"\n9. Creating branch "
        f"'{branch_name}'..."
    )

    try:

        checkout_result = (
            git_operations.invoke(
                {
                    "action": "branch",
                    "branch_name": branch_name,
                }
            )
        )

        print(
            f"   branch: "
            f"{checkout_result}"
        )

        audit_logger.log(
            "GIT_BRANCH_CREATED",
            status="PASS",
            details={
                "branch": branch_name,
            },
        )

    except Exception as error:

        print(
            f"\nGit branch creation failed: "
            f"{error}"
        )

        audit_logger.log(
            "GIT_BRANCH_CREATION_FAILED",
            status="FAIL",
            details={
                "branch": branch_name,
                "reason": str(error),
            },
        )

        return

    # ==================================================
    # 14. Commit changes
    # ==================================================

    print(
        "\n10. Committing changes..."
    )

    changed_paths = [
        change["path"]
        for change in changes
    ]

    try:

        commit_result = (
            git_operations.invoke(
                {
                    "action": "commit",
                    "commit_message": (
                        f"fix: {issue['title']}"
                    ),
                    "files": changed_paths,
                }
            )
        )

        print(
            f"   commit: "
            f"{commit_result}"
        )

        audit_logger.log(
            "GIT_COMMIT_CREATED",
            status="PASS",
            details={
                "num_files_changed": len(
                    changed_paths
                ),
                "files": changed_paths,
            },
        )

    except Exception as error:

        print(
            f"\nGit commit failed: {error}"
        )

        audit_logger.log(
            "GIT_COMMIT_FAILED",
            status="FAIL",
            details={
                "files": changed_paths,
                "reason": str(error),
            },
        )

        print(
            "\nAborting before push."
        )

        return

    # ==================================================
    # 15. Push branch
    # ==================================================

    print(
        "\n11. Pushing branch..."
    )

    try:

        push_result = (
            git_operations.invoke(
                {
                    "action": "push",
                    "branch_name": branch_name,
                }
            )
        )

        print(
            f"   push: "
            f"{push_result}"
        )

        audit_logger.log(
            "GIT_PUSHED",
            status="PASS",
            details={
                "branch": branch_name,
            },
        )

    except Exception as error:

        print(
            f"\nGit push failed: {error}"
        )

        audit_logger.log(
            "GIT_PUSH_FAILED",
            status="FAIL",
            details={
                "branch": branch_name,
                "reason": str(error),
            },
        )

        print(
            "\nAborting before Pull Request creation."
        )

        return

    # ==================================================
    # 16. Create Pull Request
    # ==================================================

    print(
        "\n12. Creating Pull Request..."
    )

    try:

        pr_result = (
            git_operations.invoke(
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
        )

        print(
            f"   create_pr: "
            f"{pr_result}"
        )

        audit_logger.log(
            "PULL_REQUEST_CREATED",
            status="PASS",
            details={
                "repo": repo,
                "branch": branch_name,
            },
        )

    except Exception as error:

        print(
            f"\nPull Request creation failed: "
            f"{error}"
        )

        audit_logger.log(
            "PULL_REQUEST_CREATION_FAILED",
            status="FAIL",
            details={
                "repo": repo,
                "branch": branch_name,
                "reason": str(error),
            },
        )

        return

    # ==================================================
    # DONE
    # ==================================================

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