import json
from datetime import datetime, timezone
from pathlib import Path


AUDIT_DIR = Path("audit")
AUDIT_FILE = AUDIT_DIR / "audit.jsonl"


def log_event(
    event: str,
    agent: str | None = None,
    data: dict | None = None,
):
    """
    Record an event in the autonomous engineer audit trail.

    Each event is stored as one JSON object per line.
    """

    AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "event": event,
        "agent": agent,
        "data": data or {},
    }

    with open(
        AUDIT_FILE,
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                record,
                default=str,
            )
            + "\n"
        )


def read_audit_log():
    """
    Read all audit events.
    """

    if not AUDIT_FILE.exists():
        return []

    events = []

    with open(
        AUDIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            events.append(
                json.loads(line)
            )

    return events


def clear_audit_log():
    """
    Clear the audit trail.

    Useful for starting a fresh autonomous run.
    """

    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()