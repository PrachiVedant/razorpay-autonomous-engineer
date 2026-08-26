from agents.audit import audit_logger
from agents.test_runner import run_tests
from agents.repair import repair_code
from agents.repository import read_file, write_file
from agents.audit import audit_logger

from razorpay.validator import validate_changes


MAX_RETRIES = 3


def is_allowed_repair_path(path, allowed_paths):
    """
    Ensure the repair agent can only modify files
    that were originally selected by the coding agent.

    Test files can never be modified by the repair agent.
    """

    normalized = path.replace("\\", "/")

    if path not in allowed_paths:
        return False

    if normalized.startswith("tests/"):
        return False

    if normalized.startswith("test_"):
        return False

    return True


def repair_loop(
    issue,
    changed_files,
    test_command="uv run python -m pytest tests/",
):
    """
    Run tests and automatically repair failures.

    The repair agent is restricted to the files
    originally changed by the coding agent.

    Every repair is passed through the deterministic
    Razorpay security validator before being applied.

    Important:
    The audit trail records workflow metadata only.
    It must never contain secrets or file contents.
    """

    attempts = 0

    allowed_paths = {
        change["path"]
        for change in changed_files
    }

    test_output = ""

    audit_logger.log(
        "REPAIR_LOOP_STARTED",
        details={
            "files": list(allowed_paths),
            "max_retries": MAX_RETRIES,
        },
    )

    while attempts < MAX_RETRIES:

        attempts += 1

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"TEST ATTEMPT "
            f"{attempts}/{MAX_RETRIES}"
        )

        print(
            f"{'=' * 60}"
        )

        audit_logger.log(
            "TEST_STARTED",
            details={
                "attempt": attempts,
                "test_command": test_command,
            },
        )

        # -----------------------------------------
        # 1. Run tests
        # -----------------------------------------

        result = run_tests(
            test_command
        )

        print(
            f"Tests passed: "
            f"{result['passed']}"
        )

        # -----------------------------------------
        # 2. Tests passed
        # -----------------------------------------

        if result["passed"]:

            print(
                "\nAll tests passed!"
            )

            audit_logger.log(
                "TEST_PASSED",
                status="PASS",
                details={
                    "attempt": attempts,
                },
            )

            audit_logger.log(
                "REPAIR_LOOP_COMPLETED",
                status="PASS",
                details={
                    "attempts": attempts,
                },
            )

            return {
                "success": True,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": result["stdout"],
            }

        # -----------------------------------------
        # 3. Tests failed
        # -----------------------------------------

        print(
            "\nTests failed."
        )

        test_output = (
            result["stdout"]
            + "\n"
            + result["stderr"]
        )

        audit_logger.log(
            "TEST_FAILED",
            status="FAIL",
            details={
                "attempt": attempts,
            },
        )

        print(
            "\nSending failure "
            "to repair agent..."
        )

        # -----------------------------------------
        # 4. Read current versions of files
        # -----------------------------------------

        file_contents = {}

        for change in changed_files:

            path = change["path"]

            file_contents[path] = read_file(
                path
            )

        # -----------------------------------------
        # 5. Ask repair agent for a fix
        # -----------------------------------------

        audit_logger.log(
            "REPAIR_STARTED",
            details={
                "attempt": attempts,
                "files": list(file_contents.keys()),
            },
        )

        print(
            "\n[REPAIR LOOP] Calling repair agent...",
            flush=True,
        )

        print(
            f"[REPAIR LOOP] Files: "
            f"{list(file_contents.keys())}",
            flush=True,
        )

        print(
            f"[REPAIR LOOP] Test output length: "
            f"{len(test_output)} characters",
            flush=True,
        )

        repair_result = repair_code(
            issue=issue,
            file_contents=file_contents,
            test_output=test_output,
        )

        print(
            "[REPAIR LOOP] Repair agent returned.",
            flush=True,
        )

        # -----------------------------------------
        # 6. Handle empty repair
        # -----------------------------------------

        new_changes = repair_result.get(
            "changes",
            []
        )

        if not new_changes:

            print(
                "\nRepair agent proposed "
                "no changes."
            )

            audit_logger.log(
                "REPAIR_NO_CHANGES",
                status="FAIL",
                details={
                    "attempt": attempts,
                },
            )

            audit_logger.log(
                "REPAIR_LOOP_ABORTED",
                status="FAIL",
                details={
                    "reason": "No repair changes returned.",
                    "attempt": attempts,
                },
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        # -----------------------------------------
        # 7. SECURITY:
        # Validate repair paths
        # -----------------------------------------

        for change in new_changes:

            path = change.get(
                "path",
                ""
            )

            if not path:

                audit_logger.log(
                    "REPAIR_SECURITY_REJECTED",
                    status="FAIL",
                    details={
                        "reason": "Missing file path.",
                        "attempt": attempts,
                    },
                )

                raise RuntimeError(
                    "Repair agent returned "
                    "a change without a file path."
                )

            if not is_allowed_repair_path(
                path,
                allowed_paths,
            ):

                audit_logger.log(
                    "REPAIR_SECURITY_REJECTED",
                    status="FAIL",
                    details={
                        "reason": "Unauthorized repair path.",
                        "path": path,
                        "attempt": attempts,
                    },
                )

                raise RuntimeError(
                    "Repair agent attempted "
                    "to modify unauthorized "
                    f"file: {path}"
                )

        # -----------------------------------------
        # 8. SECURITY:
        # Validate repaired code
        # -----------------------------------------

        print(
            "\nValidating repair "
            "with security validator..."
        )

        security_validation = validate_changes(
            new_changes
        )

        if not security_validation["valid"]:

            print(
                "\nRepair rejected by "
                "Razorpay security validator."
            )

            for error in security_validation["errors"]:

                print(
                    f"   - {error}"
                )

            audit_logger.log(
                "REPAIR_SECURITY_REJECTED",
                status="FAIL",
                details={
                    "attempt": attempts,
                    "error_count": len(
                        security_validation["errors"]
                    ),
                },
            )

            audit_logger.log(
                "REPAIR_LOOP_ABORTED",
                status="FAIL",
                details={
                    "reason": "Security validation failed.",
                    "attempt": attempts,
                },
            )

            print(
                "\nRepair will NOT be applied."
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        print(
            "   Security validation passed."
        )

        audit_logger.log(
            "REPAIR_SECURITY_VALIDATED",
            status="PASS",
            details={
                "attempt": attempts,
                "files": [
                    change["path"]
                    for change in new_changes
                ],
            },
        )

        # -----------------------------------------
        # 9. Print repair reasoning
        # -----------------------------------------

        print(
            "\nRepair reasoning:"
        )

        print(
            repair_result.get(
                "reasoning",
                "No reasoning provided."
            )
        )

        # -----------------------------------------
        # 10. Detect no-op repairs
        # -----------------------------------------

        actual_changes = []

        for change in new_changes:

            path = change["path"]

            current_content = read_file(
                path
            )

            if current_content == change["content"]:

                print(
                    f"\nNo actual change for: "
                    f"{path}"
                )

                continue

            actual_changes.append(
                change
            )

        # -----------------------------------------
        # 11. Stop if repair changed nothing
        # -----------------------------------------

        if not actual_changes:

            print(
                "\nRepair agent produced "
                "no effective changes."
            )

            audit_logger.log(
                "REPAIR_NO_EFFECTIVE_CHANGE",
                status="FAIL",
                details={
                    "attempt": attempts,
                },
            )

            audit_logger.log(
                "REPAIR_LOOP_ABORTED",
                status="FAIL",
                details={
                    "reason": "Repair produced no effective changes.",
                    "attempt": attempts,
                },
            )

            print(
                "Stopping repair loop because "
                "retrying would produce the same result."
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        # -----------------------------------------
        # 12. Apply repair
        # -----------------------------------------

        print(
            "\nApplying repair..."
        )

        for change in actual_changes:

            write_file(
                change["path"],
                change["content"],
            )

            print(
                f"Updated: "
                f"{change['path']}"
            )

        audit_logger.log(
            "REPAIR_APPLIED",
            status="PASS",
            details={
                "attempt": attempts,
                "files": [
                    change["path"]
                    for change in actual_changes
                ],
            },
        )

        # -----------------------------------------
        # 13. Update current changes
        # -----------------------------------------

        changed_files = actual_changes

    # ---------------------------------------------
    # Maximum retries reached
    # ---------------------------------------------

    print(
        "\nMaximum repair attempts reached."
    )

    audit_logger.log(
        "REPAIR_LOOP_ABORTED",
        status="FAIL",
        details={
            "reason": "Maximum retry limit reached.",
            "attempts": attempts,
        },
    )

    return {
        "success": False,
        "attempts": attempts,
        "final_changes": changed_files,
        "test_output": test_output,
    }