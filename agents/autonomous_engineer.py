from audit.logger import log_event
from agents.planner import plan_issue
from agents.autonomus_loop import run_autonomous_tests
from guardrail.security_validator import SecurityValidator


def run_autonomous_engineer(
    issue,
    structure,
    file_contents,
    generated_changes,
    apply_changes,
):
    """
    Top-level autonomous software engineering workflow.

    Flow:

        Issue
          ↓
        Planner
          ↓
        Risk decision
          ↓
        Generated changes
          ↓
        Security validation
          ↓
        Test + repair loop
          ↓
        Final result
    """

    # --------------------------------------------------
    # 1. Issue received
    # --------------------------------------------------

    log_event(
        "ISSUE_RECEIVED",
        agent="autonomous_engineer",
        data={
            "issue_title": issue.get("title"),
        },
    )

    # --------------------------------------------------
    # 2. Create plan
    # --------------------------------------------------

    print("\nCreating plan...")

    plan = plan_issue(
        issue,
        structure,
    )

    log_event(
        "PLAN_CREATED",
        agent="planner",
        data={
            "risk_level": plan.get("risk_level"),
            "requires_razorpay": plan.get(
                "requires_razorpay"
            ),
            "payment_operation": plan.get(
                "payment_operation"
            ),
            "requires_human_approval": plan.get(
                "requires_human_approval"
            ),
            "files_to_read": plan.get(
                "files_to_read",
                [],
            ),
        },
    )

    # --------------------------------------------------
    # 3. Human approval check
    # --------------------------------------------------

    if plan.get("requires_human_approval"):

        log_event(
            "HUMAN_APPROVAL_REQUIRED",
            agent="autonomous_engineer",
            data={
                "risk_level": plan.get(
                    "risk_level"
                ),
                "payment_operation": plan.get(
                    "payment_operation"
                ),
            },
        )

        print(
            "\nHuman approval required."
        )

        return {
            "success": False,
            "status": "approval_required",
            "plan": plan,
        }

    # --------------------------------------------------
    # 4. Start autonomous implementation
    # --------------------------------------------------

    log_event(
        "AUTONOMOUS_IMPLEMENTATION_STARTED",
        agent="autonomous_engineer",
        data={
            "risk_level": plan.get(
                "risk_level"
            ),
        },
    )

    print(
        "\nStarting autonomous implementation..."
    )

    # --------------------------------------------------
    # 5. Security validation
    # --------------------------------------------------

    print(
        "\nValidating generated changes..."
    )

    validator = SecurityValidator()

    validation_result = validator.validate_changes(
        generated_changes
    )

    if not validation_result["valid"]:

        print(
            "\nSECURITY VALIDATION FAILED."
        )

        for violation in validation_result[
            "violations"
        ]:
            print(
                f"  - {violation}"
            )

        log_event(
            "SECURITY_VALIDATION_FAILED",
            agent="security_validator",
            data={
                "violations": validation_result[
                    "violations"
                ],
            },
        )

        log_event(
            "CHANGES_REJECTED",
            agent="autonomous_engineer",
            data={
                "reason": "Security validation failed",
            },
        )

        return {
            "success": False,
            "status": "security_validation_failed",
            "plan": plan,
            "changes": generated_changes,
            "security_validation": validation_result,
        }

    print(
        "\nSecurity validation passed."
    )

    log_event(
        "SECURITY_VALIDATION_PASSED",
        agent="security_validator",
        data={
            "files_checked": [
                change.get("path")
                for change in generated_changes
            ],
        },
    )

    # --------------------------------------------------
    # 6. Run test + repair loop
    # --------------------------------------------------

    result = run_autonomous_tests(
        issue=issue,
        plan=plan,
        file_contents=file_contents,
        generated_changes=generated_changes,
        apply_changes=apply_changes,
    )

    # --------------------------------------------------
    # 7. Final result
    # --------------------------------------------------

    if result["success"]:

        log_event(
            "WORKFLOW_COMPLETED",
            agent="autonomous_engineer",
            data={
                "success": True,
                "attempts": result.get(
                    "attempts"
                ),
            },
        )

        print(
            "\nAutonomous workflow completed successfully."
        )

    else:

        log_event(
            "WORKFLOW_FAILED",
            agent="autonomous_engineer",
            data={
                "success": False,
                "attempts": result.get(
                    "attempts"
                ),
            },
        )

        print(
            "\nAutonomous workflow failed."
        )

    return {
        "success": result["success"],
        "status": (
            "completed"
            if result["success"]
            else "failed"
        ),
        "plan": plan,
        "changes": result.get(
            "changes"
        ),
        "test_result": result.get(
            "test_result"
        ),
        "attempts": result.get(
            "attempts"
        ),
        "security_validation": validation_result,
    }