from audit.logger import log_event
from agents.test_runner import run_tests
from agents.repair import repair_fix
from guardrail.security_validator import SecurityValidator


MAX_RETRIES = 3


def run_autonomous_tests(
    issue,
    plan,
    file_contents,
    generated_changes,
    apply_changes,
):
    """
    Run tests and allow the agent to repair
    failed generated code.

    Every repaired change is passed through the
    deterministic security validator before it
    can be applied.

    Returns the final changes and test result.
    """

    changes = generated_changes

    validator = SecurityValidator()

    for attempt in range(MAX_RETRIES + 1):

        print(
            f"\nTest attempt "
            f"{attempt + 1}/{MAX_RETRIES + 1}"
        )

        # --------------------------------------------------
        # Apply current changes
        # --------------------------------------------------

        apply_changes(changes)

        log_event(
            "CHANGES_APPLIED",
            agent="autonomous_engineer",
            data={
                "attempt": attempt + 1,
                "files": [
                    change.get("path")
                    for change in changes
                ],
            },
        )

        # --------------------------------------------------
        # Run tests
        # --------------------------------------------------

        log_event(
            "TEST_STARTED",
            agent="test_runner",
            data={
                "attempt": attempt + 1,
            },
        )

        test_result = run_tests()

        if test_result["passed"]:

            print(
                "\nTests passed."
            )

            log_event(
                "TEST_PASSED",
                agent="test_runner",
                data={
                    "attempt": attempt + 1,
                },
            )

            return {
                "success": True,
                "changes": changes,
                "test_result": test_result,
                "attempts": attempt + 1,
            }

        # --------------------------------------------------
        # Tests failed
        # --------------------------------------------------

        print(
            "\nTests failed."
        )

        print(
            test_result["stderr"]
        )

        log_event(
            "TEST_FAILED",
            agent="test_runner",
            data={
                "attempt": attempt + 1,
            },
        )

        # --------------------------------------------------
        # No more retries
        # --------------------------------------------------

        if attempt >= MAX_RETRIES:

            log_event(
                "MAX_RETRIES_REACHED",
                agent="autonomous_engineer",
                data={
                    "attempts": attempt + 1,
                },
            )

            return {
                "success": False,
                "changes": changes,
                "test_result": test_result,
                "attempts": attempt + 1,
            }

        # --------------------------------------------------
        # Ask repair agent
        # --------------------------------------------------

        print(
            "\nAsking agent to repair the failure..."
        )

        log_event(
            "REPAIR_STARTED",
            agent="repair",
            data={
                "attempt": attempt + 1,
            },
        )

        repaired = repair_fix(
            issue,
            plan,
            file_contents,
            changes,
            test_result,
        )

        repaired_changes = repaired.get(
            "changes",
            [],
        )

        # --------------------------------------------------
        # Validate repaired changes
        # --------------------------------------------------

        print(
            "\nValidating repaired changes..."
        )

        validation_result = validator.validate_changes(
            repaired_changes
        )

        if not validation_result["valid"]:

            print(
                "\nSECURITY VALIDATION FAILED "
                "FOR REPAIRED CODE."
            )

            for violation in validation_result[
                "violations"
            ]:
                print(
                    f"  - {violation}"
                )

            log_event(
                "REPAIR_SECURITY_VALIDATION_FAILED",
                agent="security_validator",
                data={
                    "attempt": attempt + 1,
                    "violations": validation_result[
                        "violations"
                    ],
                },
            )

            log_event(
                "REPAIRED_CHANGES_REJECTED",
                agent="autonomous_engineer",
                data={
                    "reason": (
                        "Repair generated code "
                        "failed security validation"
                    ),
                },
            )

            return {
                "success": False,
                "changes": changes,
                "test_result": test_result,
                "attempts": attempt + 1,
                "security_validation": validation_result,
            }

        print(
            "\nRepaired code passed security validation."
        )

        log_event(
            "REPAIR_SECURITY_VALIDATION_PASSED",
            agent="security_validator",
            data={
                "attempt": attempt + 1,
                "files": [
                    change.get("path")
                    for change in repaired_changes
                ],
            },
        )

        # --------------------------------------------------
        # Accept repaired changes
        # --------------------------------------------------

        changes = repaired_changes

        log_event(
            "REPAIR_COMPLETED",
            agent="repair",
            data={
                "attempt": attempt + 1,
            },
        )

    return {
        "success": False,
        "changes": changes,
        "test_result": test_result,
        "attempts": MAX_RETRIES + 1,
    }