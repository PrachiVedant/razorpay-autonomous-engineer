from agents.audit import AuditLogger


def test_repair_failure_is_recorded(tmp_path):
    log_file = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=log_file
    )

    logger.log(
        "TEST_FAILED",
        status="FAIL",
        details={
            "attempt": 1,
        },
    )

    logger.log(
        "REPAIR_STARTED",
        details={
            "attempt": 1,
            "files": ["calculator.py"],
        },
    )

    logger.log(
        "REPAIR_APPLIED",
        status="PASS",
        details={
            "attempt": 1,
            "files": ["calculator.py"],
        },
    )

    logger.log(
        "TEST_PASSED",
        status="PASS",
        details={
            "attempt": 2,
        },
    )

    lines = log_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 4

    assert '"event": "TEST_FAILED"' in lines[0]
    assert '"event": "REPAIR_STARTED"' in lines[1]
    assert '"event": "REPAIR_APPLIED"' in lines[2]
    assert '"event": "TEST_PASSED"' in lines[3]