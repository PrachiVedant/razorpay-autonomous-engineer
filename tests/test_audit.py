import json

from agents.audit import AuditLogger


def test_audit_logger_records_event(tmp_path):
    log_file = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=log_file
    )

    logger.log(
        "TEST_FAILED",
        status="FAIL",
        details={
            "attempt": 1,
            "test_command": "uv run pytest tests/",
        },
    )

    assert log_file.exists()

    lines = log_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 1

    event = json.loads(lines[0])

    assert event["event"] == "TEST_FAILED"
    assert event["status"] == "FAIL"
    assert event["details"]["attempt"] == 1


def test_audit_logger_does_not_require_secrets():
    logger = AuditLogger()

    logger.log(
        "SECURITY_VALIDATION_PASSED",
        details={
            "files": [
                "app/routes/payments.py"
            ]
        },
    )