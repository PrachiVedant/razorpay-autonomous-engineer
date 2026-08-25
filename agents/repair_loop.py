from agents.test_runner import run_tests
from agents.repair import repair_code
from agents.repository import read_file, write_file


MAX_RETRIES = 3


def is_allowed_repair_path(path, allowed_paths):
    """
    Ensure the repair agent can only modify files
    that were originally selected by the coding agent.

    Test files can never be modified by the repair agent.
    """

    normalized = path.replace("\\", "/")

    # Must be one of the originally changed files
    if path not in allowed_paths:
        return False

    # Never allow modification of tests
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

    # --------------------------------------------------
    # Files that the repair agent is allowed to modify
    # during the ENTIRE repair loop.
    # --------------------------------------------------

    allowed_paths = {
        change["path"]
        for change in changed_files
    }

    test_output = ""

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


        print(
            "\n[REPAIR LOOP] Calling repair agent...",
            flush=True,
        )

        print(
            f"[REPAIR LOOP] Files: {list(file_contents.keys())}",
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

            print(
                "The failure may be caused by "
                "the environment or may be "
                "outside the allowed repair scope."
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

            path = change["path"]

            if not is_allowed_repair_path(
                path,
                allowed_paths,
            ):

                raise RuntimeError(
                    "Repair agent attempted "
                    "to modify unauthorized "
                    f"file: {path}"
                )

        # -----------------------------------------
        # 8. Print repair reasoning
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
        # 9. Detect no-op repairs
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
        # 10. Stop if repair changed nothing
        # -----------------------------------------

        if not actual_changes:

            print(
                "\nRepair agent produced "
                "no effective changes."
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
        # 11. Apply repair
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

        # -----------------------------------------
        # 12. Update current changes
        # -----------------------------------------

        changed_files = actual_changes

    # ---------------------------------------------
    # Maximum retries reached
    # ---------------------------------------------

    print(
        "\nMaximum repair attempts reached."
    )

    return {
        "success": False,
        "attempts": attempts,
        "final_changes": changed_files,
        "test_output": test_output,
    }