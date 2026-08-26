from agents.audit import AuditLogger


def test_repair_failure_audit_trail(tmp_path):

    log_file = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=log_file
    )

    # Simulate failed test
    logger.log(
        "TEST_FAILED",
        status="FAIL",
        details={
            "attempt": 1,
            "test_command": "uv run pytest tests/",
        },
    )

    # Simulate repair attempt
    logger.log(
        "REPAIR_STARTED",
        details={
            "attempt": 1,
            "files": [
                "calculator.py"
            ],
        },
    )

    # Simulate repair failure
    logger.log(
        "REPAIR_FAILED",
        status="FAIL",
        details={
            "attempt": 1,
            "reason": (
                "Repair agent proposed no changes."
            ),
        },
    )

    lines = log_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 3

    assert (
        '"event": "TEST_FAILED"'
        in lines[0]
    )

    assert (
        '"event": "REPAIR_STARTED"'
        in lines[1]
    )

    assert (
        '"event": "REPAIR_FAILED"'
        in lines[2]
    )