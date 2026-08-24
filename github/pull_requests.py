from guardrail.pre_agent import CodingSafetyFilter

MAX_CHANGED_FILES = 5


def is_sensitive_file(path: str) -> bool:
    normalized = path.lower()
    return any(pattern.lower() in normalized for pattern in CodingSafetyFilter.SENSITIVE_FILE_PATTERNS)


def validate_proposed_changes(changes: list[dict[str, str]]) -> None:
    if len(changes) > MAX_CHANGED_FILES:
        raise RuntimeError(
            f"Refusing to apply {len(changes)} changed files. "
            f"Change limit is {MAX_CHANGED_FILES} files."
        )

    sensitive_files = [change["path"] for change in changes if is_sensitive_file(change["path"])]
    if sensitive_files:
        raise RuntimeError(
            "Refusing to apply changes to sensitive files: "
            + ", ".join(sensitive_files)
        )