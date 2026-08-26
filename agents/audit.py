import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = Path("audit_log.jsonl")


class AuditLogger:
    """
    Lightweight audit logger for the autonomous coding agent.

    Each event is written as one JSON object per line.
    Secrets and file contents must never be logged.
    """

    def __init__(self, log_path=AUDIT_LOG_PATH):
        self.log_path = Path(log_path)

    def log(
        self,
        event: str,
        *,
        status: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a workflow event.

        Only metadata should be placed in details.
        Never include credentials, secrets, or file contents.
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