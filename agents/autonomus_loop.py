from agents.test_runner import run_tests
from agents.repair import repair_fix


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

    Returns the final changes and test result.
    """

    changes = generated_changes

    for attempt in range(MAX_RETRIES + 1):

        print(
            f"\nTest attempt "
            f"{attempt + 1}/{MAX_RETRIES + 1}"
        )

        # Apply current changes
        apply_changes(changes)

        # Run tests
        test_result = run_tests()

        if test_result["passed"]:

            print(
                "\nTests passed."
            )

            return {
                "success": True,
                "changes": changes,
                "test_result": test_result,
                "attempts": attempt + 1,
            }

        print(
            "\nTests failed."
        )

        print(
            test_result["stderr"]
        )

        # No more retries
        if attempt >= MAX_RETRIES:

            return {
                "success": False,
                "changes": changes,
                "test_result": test_result,
                "attempts": attempt + 1,
            }

        print(
            "\nAsking agent to repair the failure..."
        )

        repaired = repair_fix(
            issue,
            plan,
            file_contents,
            changes,
            test_result,
        )

        changes = repaired["changes"]

    return {
        "success": False,
        "changes": changes,
        "test_result": test_result,
        "attempts": MAX_RETRIES + 1,
    }