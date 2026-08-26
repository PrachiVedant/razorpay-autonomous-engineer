from agents import repair_loop as repair_loop_module


def test_failure_repair_pass(monkeypatch, tmp_path):
    """
    Verify the autonomous recovery flow:

        test fails
            ↓
        repair agent is called
            ↓
        repair is applied
            ↓
        test passes
    """

    file_path = tmp_path / "calculator.py"

    # Initial broken implementation
    file_path.write_text(
        "def add(a, b):\n"
        "    return a - b\n",
        encoding="utf-8",
    )

    # Track test attempts
    test_attempts = []

    def fake_run_tests(command):

        attempt = len(test_attempts) + 1

        test_attempts.append(attempt)

        # First attempt intentionally fails
        if attempt == 1:

            return {
                "passed": False,
                "stdout": "",
                "stderr": (
                    "AssertionError: "
                    "add(2, 3) returned -1"
                ),
            }

        # Second attempt succeeds
        return {
            "passed": True,
            "stdout": "1 passed",
            "stderr": "",
        }

    monkeypatch.setattr(
        repair_loop_module,
        "run_tests",
        fake_run_tests,
    )

    repair_calls = []

    def fake_repair_code(
        issue,
        file_contents,
        test_output,
    ):

        repair_calls.append(
            {
                "issue": issue,
                "test_output": test_output,
            }
        )

        return {
            "reasoning": (
                "The addition function incorrectly "
                "uses subtraction. Replace subtraction "
                "with addition."
            ),
            "changes": [
                {
                    "path": "calculator.py",
                    "content": (
                        "def add(a, b):\n"
                        "    return a + b\n"
                    ),
                }
            ],
        }

    monkeypatch.setattr(
        repair_loop_module,
        "repair_code",
        fake_repair_code,
    )

    # IMPORTANT:
    # repair_loop uses repository.read_file/write_file,
    # so run it from the temporary directory.
    monkeypatch.chdir(tmp_path)

    issue = {
        "title": "Fix calculator addition",
        "body": "The calculator addition is broken.",
    }

    changed_files = [
        {
            "path": "calculator.py",
            "content": (
                "def add(a, b):\n"
                "    return a - b\n"
            ),
        }
    ]

    result = repair_loop_module.repair_loop(
        issue=issue,
        changed_files=changed_files,
        test_command="pytest tests/",
    )

    # ----------------------------------------
    # Verify recovery
    # ----------------------------------------

    assert result["success"] is True

    # First test failed, second test passed
    assert result["attempts"] == 2

    # Repair agent was actually called
    assert len(repair_calls) == 1

    # Final change contains repaired code
    assert result["final_changes"][0]["content"] == (
        "def add(a, b):\n"
        "    return a + b\n"
    )

    # Verify actual file was repaired
    final_content = file_path.read_text(
        encoding="utf-8"
    )

    assert "return a + b" in final_content

    # Verify test was executed twice
    assert test_attempts == [1, 2]