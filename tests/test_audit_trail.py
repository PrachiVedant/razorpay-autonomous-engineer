import json

from agents.audit import AuditLogger, AuditEvents


def test_failure_recovery_audit_trail(tmp_path):
    """
    Verify that an autonomous failure-recovery workflow
    produces a complete audit trail.

    Expected sequence:

        TEST_FAILED
            ↓
        REPAIR_STARTED
            ↓
        REPAIR_FAILED
            ↓
        ROLLBACK_COMPLETED
            ↓
        WORKFLOW_FAILED
    """

    log_path = tmp_path / "audit_log.jsonl"

    logger = AuditLogger(
        log_path=log_path
    )

    logger.log(
        AuditEvents.TEST_FAILED,
        status="FAIL",
        details={
            "attempt": 1,
        },
    )

    logger.log(
        AuditEvents.REPAIR_STARTED,
        status="INFO",
        details={
            "attempt": 1,
        },
    )

    logger.log(
        AuditEvents.REPAIR_FAILED,
        status="FAIL",
        details={
            "attempt": 1,
            "reason": "Repair agent produced no effective changes.",
        },
    )

    logger.log(
        AuditEvents.ROLLBACK_COMPLETED,
        status="PASS",
        details={
            "files": [
                "calculator.py",
            ],
        },
    )

    logger.log(
        AuditEvents.WORKFLOW_FAILED,
        status="FAIL",
        details={
            "reason": "Autonomous repair failed.",
        },
    )

    lines = log_path.read_text(
        encoding="utf-8"
    ).splitlines()

    events = []

    for line in lines:

        entry = json.loads(line)

        events.append(
            entry
        )

    assert [
        entry["event"]
        for entry in events
    ] == [
        AuditEvents.TEST_FAILED,
        AuditEvents.REPAIR_STARTED,
        AuditEvents.REPAIR_FAILED,
        AuditEvents.ROLLBACK_COMPLETED,
        AuditEvents.WORKFLOW_FAILED,
    ]

    assert events[0]["status"] == "FAIL"
    assert events[1]["status"] == "INFO"
    assert events[2]["status"] == "FAIL"
    assert events[3]["status"] == "PASS"
    assert events[4]["status"] == "FAIL"


def test_audit_log_contains_timestamp(tmp_path):
    """
    Every audit event must contain a timestamp.
    """

    log_path = tmp_path / "audit_log.jsonl"

    logger = AuditLogger(
        log_path=log_path
    )

    logger.log(
        AuditEvents.TEST_PASSED,
        status="PASS",
        details={
            "attempt": 1,
        },
    )

    line = log_path.read_text(
        encoding="utf-8"
    ).splitlines()[0]

    entry = json.loads(line)

    assert "timestamp" in entry
    assert entry["timestamp"]


def test_audit_log_does_not_store_source_code(tmp_path):
    """
    Verify that the audit test itself only records metadata
    and does not contain source-code content.
    """

    log_path = tmp_path / "audit_log.jsonl"

    logger = AuditLogger(
        log_path=log_path
    )

    logger.log(
        AuditEvents.CODE_GENERATED,
        status="INFO",
        details={
            "files": [
                "calculator.py",
            ],
            "num_changes": 1,
        },
    )

    content = log_path.read_text(
        encoding="utf-8"
    )

    assert "def add(a, b)" not in content
    assert "return a + b" not in content

    entry = json.loads(
        content.splitlines()[0]
    )

    assert entry["event"] == (
        AuditEvents.CODE_GENERATED
    )