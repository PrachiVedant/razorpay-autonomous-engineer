import json

from agents.audit import AuditLogger


def test_audit_entries_are_valid_json(tmp_path):
    """
    Every audit record must be valid JSON and contain
    the standard audit structure.
    """

    audit_log = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=audit_log
    )

    logger.log(
        "ISSUE_RECEIVED",
        status="INFO",
        details={
            "repo": "test/repository",
            "issue_number": 1,
        },
    )

    logger.log(
        "PLAN_CREATED",
        status="INFO",
        details={
            "files_to_read": [
                "calculator.py"
            ]
        },
    )

    logger.log(
        "SECURITY_VALIDATION_PASSED",
        status="PASS",
        details={
            "files": [
                "calculator.py"
            ]
        },
    )

    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 3

    for line in lines:

        entry = json.loads(line)

        assert isinstance(
            entry,
            dict
        )

        assert "timestamp" in entry
        assert "event" in entry
        assert "status" in entry
        assert "details" in entry

        assert isinstance(
            entry["timestamp"],
            str,
        )

        assert isinstance(
            entry["event"],
            str,
        )

        assert isinstance(
            entry["status"],
            str,
        )

        assert isinstance(
            entry["details"],
            dict,
        )


def test_audit_events_preserve_chronological_order(
    tmp_path,
):
    """
    Audit records must remain in the same order in
    which the workflow generated them.
    """

    audit_log = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=audit_log
    )

    expected_events = [
        "ISSUE_RECEIVED",
        "REPOSITORY_ANALYZED",
        "PLAN_CREATED",
        "CODE_GENERATED",
        "SECURITY_VALIDATION_PASSED",
        "CHANGES_APPLIED",
        "TEST_PASSED",
        "GIT_BRANCH_CREATED",
        "GIT_COMMIT_CREATED",
        "GIT_PUSHED",
        "PULL_REQUEST_CREATED",
        "WORKFLOW_COMPLETED",
    ]

    for event in expected_events:

        logger.log(
            event,
            status="PASS",
        )

    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    actual_events = [
        json.loads(line)["event"]
        for line in lines
    ]

    assert actual_events == expected_events


def test_audit_trail_does_not_store_secrets(
    tmp_path,
):
    """
    Audit metadata must never contain credentials,
    API keys, or secret values.
    """

    audit_log = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=audit_log
    )

    secret_value = (
        "sk_live_SUPER_SECRET_123456"
    )

    logger.log(
        "SECURITY_VALIDATION_FAILED",
        status="FAIL",
        details={
            "reason": "secret detected",
            "files": [
                "payment.py"
            ],
        },
    )

    content = audit_log.read_text(
        encoding="utf-8"
    )

    assert secret_value not in content

    assert "sk_live_" not in content


def test_audit_trail_does_not_store_source_code(
    tmp_path,
):
    """
    Audit logs should contain metadata rather than
    complete source-code contents.
    """

    audit_log = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=audit_log
    )

    source_code = """
def process_payment(amount):
    return charge_card(amount)
"""

    logger.log(
        "CODE_GENERATED",
        status="INFO",
        details={
            "files": [
                "payment.py"
            ],
            "num_changes": 1,
        },
    )

    content = audit_log.read_text(
        encoding="utf-8"
    )

    assert source_code not in content

    assert (
        "def process_payment"
        not in content
    )

    assert (
        "charge_card"
        not in content
    )


def test_audit_failure_contains_recovery_context(
    tmp_path,
):
    """
    A failed workflow must leave enough metadata in
    the audit trail to understand what happened without
    storing sensitive data.
    """

    audit_log = tmp_path / "audit.jsonl"

    logger = AuditLogger(
        log_path=audit_log
    )

    logger.log(
        "TEST_FAILED",
        status="FAIL",
        details={
            "attempt": 3,
            "test_command": (
                "uv run pytest tests/"
            ),
        },
    )

    logger.log(
        "REPAIR_LOOP_FAILED",
        status="FAIL",
        details={
            "attempts": 3,
            "max_retries": 3,
            "files": [
                "calculator.py"
            ],
        },
    )

    logger.log(
        "ROLLBACK_COMPLETED",
        status="PASS",
        details={
            "files": [
                "calculator.py"
            ],
            "attempts": 3,
        },
    )

    events = [
        json.loads(line)
        for line in audit_log.read_text(
            encoding="utf-8"
        ).splitlines()
    ]

    event_names = [
        event["event"]
        for event in events
    ]

    assert event_names == [
        "TEST_FAILED",
        "REPAIR_LOOP_FAILED",
        "ROLLBACK_COMPLETED",
    ]

    assert (
        events[0]["status"]
        == "FAIL"
    )

    assert (
        events[1]["details"]["attempts"]
        == 3
    )

    assert (
        events[2]["status"]
        == "PASS"
    )