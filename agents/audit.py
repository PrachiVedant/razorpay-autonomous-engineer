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

    # --------------------------------------------------
    # Issue / Repository / Planning
    # --------------------------------------------------

    ISSUE_RECEIVED = "ISSUE_RECEIVED"
    ISSUE_FETCH_FAILED = "ISSUE_FETCH_FAILED"

    REPOSITORY_ANALYZED = "REPOSITORY_ANALYZED"
    REPOSITORY_ANALYSIS_FAILED = (
        "REPOSITORY_ANALYSIS_FAILED"
    )

    PLAN_CREATED = "PLAN_CREATED"
    PLAN_CREATION_FAILED = (
        "PLAN_CREATION_FAILED"
    )

    # --------------------------------------------------
    # Code Generation
    # --------------------------------------------------

    CODE_GENERATED = "CODE_GENERATED"

    CODE_GENERATION_FAILED = (
        "CODE_GENERATION_FAILED"
    )

    CODE_GENERATION_EMPTY = (
        "CODE_GENERATION_EMPTY"
    )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    CHANGE_VALIDATION_FAILED = (
        "CHANGE_VALIDATION_FAILED"
    )

    SECURITY_VALIDATION_PASSED = (
        "SECURITY_VALIDATION_PASSED"
    )

    SECURITY_VALIDATION_FAILED = (
        "SECURITY_VALIDATION_FAILED"
    )

    RAZORPAY_SECURITY_VALIDATION_FAILED = (
        "RAZORPAY_SECURITY_VALIDATION_FAILED"
    )

    SENSITIVE_FILES_DETECTED = (
        "SENSITIVE_FILES_DETECTED"
    )

    # --------------------------------------------------
    # Razorpay Payment Risk
    # --------------------------------------------------

    PAYMENT_POLICY_REJECTED = (
        "PAYMENT_POLICY_REJECTED"
    )

    PAYMENT_RISK_CLASSIFIED = (
        "PAYMENT_RISK_CLASSIFIED"
    )

    # --------------------------------------------------
    # Human Approval
    # --------------------------------------------------

    HUMAN_APPROVAL_REQUIRED = (
        "HUMAN_APPROVAL_REQUIRED"
    )

    HUMAN_APPROVAL_GRANTED = (
        "HUMAN_APPROVAL_GRANTED"
    )

    HUMAN_APPROVAL_DENIED = (
        "HUMAN_APPROVAL_DENIED"
    )

    # --------------------------------------------------
    # File Operations
    # --------------------------------------------------

    FILES_READ = "FILES_READ"

    FILES_READ_FAILED = (
        "FILES_READ_FAILED"
    )

    CHANGES_APPLIED = "CHANGES_APPLIED"

    CHANGES_APPLICATION_FAILED = (
        "CHANGES_APPLICATION_FAILED"
    )

    # --------------------------------------------------
    # Testing
    # --------------------------------------------------

    TEST_STARTED = "TEST_STARTED"
    TEST_FAILED = "TEST_FAILED"
    TEST_PASSED = "TEST_PASSED"

    # --------------------------------------------------
    # Autonomous Repair
    # --------------------------------------------------

    REPAIR_LOOP_STARTED = (
        "REPAIR_LOOP_STARTED"
    )

    REPAIR_STARTED = "REPAIR_STARTED"

    REPAIR_APPLIED = "REPAIR_APPLIED"

    REPAIR_FAILED = "REPAIR_FAILED"

    REPAIR_LOOP_COMPLETED = (
        "REPAIR_LOOP_COMPLETED"
    )

    # --------------------------------------------------
    # Rollback
    # --------------------------------------------------

    ROLLBACK_COMPLETED = (
        "ROLLBACK_COMPLETED"
    )

    ROLLBACK_FAILED = (
        "ROLLBACK_FAILED"
    )

    # --------------------------------------------------
    # Git
    # --------------------------------------------------

    GIT_BRANCH_CREATED = (
        "GIT_BRANCH_CREATED"
    )

    GIT_BRANCH_CREATION_FAILED = (
        "GIT_BRANCH_CREATION_FAILED"
    )

    GIT_COMMIT_CREATED = (
        "GIT_COMMIT_CREATED"
    )

    GIT_COMMIT_FAILED = (
        "GIT_COMMIT_FAILED"
    )

    GIT_PUSHED = "GIT_PUSHED"

    GIT_PUSH_FAILED = (
        "GIT_PUSH_FAILED"
    )

    # --------------------------------------------------
    # Pull Request
    # --------------------------------------------------

    PULL_REQUEST_CREATED = (
        "PULL_REQUEST_CREATED"
    )

    PULL_REQUEST_CREATION_FAILED = (
        "PULL_REQUEST_CREATION_FAILED"
    )

    # --------------------------------------------------
    # Workflow
    # --------------------------------------------------

    WORKFLOW_COMPLETED = (
        "WORKFLOW_COMPLETED"
    )

    WORKFLOW_FAILED = (
        "WORKFLOW_FAILED"
    )


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