from agents.test_runner import run_tests
from agents.repair import repair_code
from agents.repository import read_file, write_file
from agents.audit import audit_logger


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

    Returns:

        {
            "success": bool,
            "attempts": int,
            "final_changes": list,
            "test_output": str,
        }
    """

    attempts = 0

    allowed_paths = {
        change["path"]
        for change in changed_files
    }

    test_output = ""

    # --------------------------------------------------
    # Audit: repair loop started
    # --------------------------------------------------

    audit_logger.log(
        "REPAIR_LOOP_STARTED",
        status="INFO",
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

        # -----------------------------------------
        # 1. Run tests
        # -----------------------------------------

        audit_logger.log(
            "TEST_STARTED",
            status="INFO",
            details={
                "attempt": attempts,
                "test_command": test_command,
            },
        )

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
                    "files": list(
                        allowed_paths
                    ),
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
                "test_command": test_command,
            },
        )

        # -----------------------------------------
        # 4. Maximum retry protection
        # -----------------------------------------

        if attempts >= MAX_RETRIES:

            print(
                "\nMaximum repair attempts reached."
            )

            audit_logger.log(
                "REPAIR_LOOP_FAILED",
                status="FAIL",
                details={
                    "attempts": attempts,
                    "max_retries": MAX_RETRIES,
                    "files": list(
                        allowed_paths
                    ),
                },
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        # -----------------------------------------
        # 5. Start repair
        # -----------------------------------------

        print(
            "\nSending failure "
            "to repair agent..."
        )

        audit_logger.log(
            "REPAIR_STARTED",
            status="INFO",
            details={
                "attempt": attempts,
                "files": list(
                    allowed_paths
                ),
            },
        )

        # -----------------------------------------
        # 6. Read current files
        # -----------------------------------------

        file_contents = {}

        for change in changed_files:

            path = change["path"]

            file_contents[path] = read_file(
                path
            )

        # -----------------------------------------
        # 7. Call repair agent
        # -----------------------------------------

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
        # 8. Handle empty repair
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
                "REPAIR_FAILED",
                status="FAIL",
                details={
                    "attempt": attempts,
                    "reason": "No changes proposed.",
                },
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        # -----------------------------------------
        # 9. Validate repair paths
        # -----------------------------------------

        for change in new_changes:

            path = change["path"]

            if not is_allowed_repair_path(
                path,
                allowed_paths,
            ):

                audit_logger.log(
                    "REPAIR_BLOCKED",
                    status="FAIL",
                    details={
                        "attempt": attempts,
                        "file": path,
                        "reason": (
                            "Unauthorized repair path."
                        ),
                    },
                )

                raise RuntimeError(
                    "Repair agent attempted "
                    "to modify unauthorized "
                    f"file: {path}"
                )

        # -----------------------------------------
        # 10. Print reasoning
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
        # 11. Detect no-op repairs
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
        # 12. Stop if nothing changed
        # -----------------------------------------

        if not actual_changes:

            print(
                "\nRepair agent produced "
                "no effective changes."
            )

            audit_logger.log(
                "REPAIR_FAILED",
                status="FAIL",
                details={
                    "attempt": attempts,
                    "reason": "No effective changes.",
                },
            )

            return {
                "success": False,
                "attempts": attempts,
                "final_changes": changed_files,
                "test_output": test_output,
            }

        # -----------------------------------------
        # 13. Apply repair
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
        # 14. Update current changes
        # -----------------------------------------

        changed_files = actual_changes

    # --------------------------------------------------
    # Safety fallback
    # --------------------------------------------------

    audit_logger.log(
        "REPAIR_LOOP_FAILED",
        status="FAIL",
        details={
            "attempts": attempts,
            "max_retries": MAX_RETRIES,
        },
    )

    return {
        "success": False,
        "attempts": attempts,
        "final_changes": changed_files,
        "test_output": test_output,
    }