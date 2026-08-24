from langchain.agents.middleware import HumanInTheLoopMiddleware, ToolCallRequest


def files_changed(request: ToolCallRequest) -> bool:
    """
    Pause when the number of changed files is greater than 5.
    """

    num_files = request.tool_call["args"].get(
        "num_files_changed",
        0,
    )

    try:
        return int(num_files) > 5
    except (TypeError, ValueError):
        return False


def contains_sensitive_files(request: ToolCallRequest) -> bool:
    """
    Pause when sensitive files are part of the proposed changes.
    """

    sensitive_files = request.tool_call["args"].get(
        "sensitive_files",
        [],
    )

    if isinstance(sensitive_files, str):
        sensitive_files = [
            path.strip()
            for path in sensitive_files.split(",")
            if path.strip()
        ]

    if isinstance(sensitive_files, (list, tuple, set)):
        return len(sensitive_files) > 0

    return bool(sensitive_files)


def require_commit_approval(request: ToolCallRequest) -> bool:
    """
    Always require approval before commit/PR operations.
    """

    action = (
        request.tool_call["args"]
        .get("action", "")
        .strip()
        .lower()
    )

    return action in {
        "commit",
        "push",
        "create_pr",
    }

human_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "git_operations": {
            "allowed_decisions": ["approve", "reject", "edit", "respond"],
            "when": lambda request: (
                files_changed(request)
                or contains_sensitive_files(request)
                or require_commit_approval(request)
            ),
        }
    },
)
