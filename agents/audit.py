import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = Path("audit_log.jsonl")


class AuditEvents:
    """
    Standard event names used throughout the autonomous
    coding workflow.
    """

    ISSUE_RECEIVED = "ISSUE_RECEIVED"
    REPOSITORY_ANALYZED = "REPOSITORY_ANALYZED"
    PLAN_CREATED = "PLAN_CREATED"

    CODE_GENERATED = "CODE_GENERATED"

    SECURITY_VALIDATION_PASSED = (
        "SECURITY_VALIDATION_PASSED"
    )

    SECURITY_VALIDATION_FAILED = (
        "SECURITY_VALIDATION_FAILED"
    )

    HUMAN_APPROVAL_REQUIRED = (
        "HUMAN_APPROVAL_REQUIRED"
    )

    HUMAN_APPROVAL_GRANTED = (
        "HUMAN_APPROVAL_GRANTED"
    )

    HUMAN_APPROVAL_DENIED = (
        "HUMAN_APPROVAL_DENIED"
    )

    CHANGES_APPLIED = "CHANGES_APPLIED"

    TEST_STARTED = "TEST_STARTED"
    TEST_FAILED = "TEST_FAILED"
    TEST_PASSED = "TEST_PASSED"

    REPAIR_LOOP_STARTED = "REPAIR_LOOP_STARTED"
    REPAIR_STARTED = "REPAIR_STARTED"
    REPAIR_APPLIED = "REPAIR_APPLIED"
    REPAIR_FAILED = "REPAIR_FAILED"
    REPAIR_LOOP_COMPLETED = "REPAIR_LOOP_COMPLETED"

    GIT_BRANCH_CREATED = "GIT_BRANCH_CREATED"
    GIT_COMMIT_CREATED = "GIT_COMMIT_CREATED"
    GIT_PUSHED = "GIT_PUSHED"

    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"

    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"


class AuditLogger:
    """
    Lightweight structured audit logger.

    Every event is stored as one JSON object per line.

    IMPORTANT:
    Only metadata should be stored in the audit log.

    Never store:
        - API keys
        - secrets
        - credentials
        - source-code contents
        - test output containing secrets
    """

    def __init__(
        self,
        log_path=AUDIT_LOG_PATH,
    ):
        self.log_path = Path(log_path)

    def log(
        self,
        event: str,
        *,
        status: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a structured workflow event.
        """

        entry = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "event": event,

            "status": status,

            "details": details or {},
        }

        self.log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.log_path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    entry,
                    ensure_ascii=False,
                )
                + "\n"
            )


audit_logger = AuditLogger()