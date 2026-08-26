import json

import agents.github_agent as github_agent


def test_workflow_rolls_back_when_repair_fails(
    monkeypatch,
    tmp_path,
):
    """
    Verify the complete failure path:

        Issue
          ↓
        Plan
          ↓
        Generate code
          ↓
        Security validation
          ↓
        Apply changes
          ↓
        Repair fails
          ↓
        Rollback
          ↓
        Workflow stops

    No commit, push, or PR should happen.
    """

    # --------------------------------------------------
    # Audit log
    # --------------------------------------------------

    audit_log = tmp_path / "audit_log.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    # --------------------------------------------------
    # Fake GitHub issue
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        lambda repo, issue_number: {
            "title": "Fix calculator addition",
            "body": "Fix the addition function.",
        },
    )

    # --------------------------------------------------
    # Fake repository
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "get_repo_structure",
        lambda: {
            "files": [
                "calculator.py",
                "tests/test_sample.py",
            ]
        },
    )

    # --------------------------------------------------
    # Fake planner
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "plan_issue",
        lambda issue, structure: {
            "approach": "Fix addition function",
            "files_to_read": [
                "calculator.py",
            ],
            "requires_razorpay": False,
        },
    )

    # --------------------------------------------------
    # Fake Razorpay policy
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
        },
    )

    # --------------------------------------------------
    # Fake repository reader
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "read_file",
        lambda path: (
            "def add(a, b):\n"
            "    return a - b"
        ),
    )

    # --------------------------------------------------
    # Fake code generator
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "generate_fix",
        lambda issue, plan, file_content: {
            "changes": [
                {
                    "path": "calculator.py",
                    "content": (
                        "def add(a, b):\n"
                        "    return a + b"
                    ),
                }
            ],
            "pr_description": (
                "Fix calculator addition."
            ),
        },
    )

    # --------------------------------------------------
    # Validation passes
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "validate_proposed_changes",
        lambda changes: None,
    )

    monkeypatch.setattr(
        github_agent,
        "validate_changes",
        lambda changes: {
            "valid": True,
            "errors": [],
        },
    )

    # --------------------------------------------------
    # Security validator
    # --------------------------------------------------

    class FakeSecurityValidator:

        def validate_changes(self, changes):
            return {
                "valid": True,
                "violations": [],
            }

    monkeypatch.setattr(
        github_agent,
        "SecurityValidator",
        FakeSecurityValidator,
    )

    # --------------------------------------------------
    # Track file modifications
    # --------------------------------------------------

    written_files = []

    def fake_write_file(path, content):

        written_files.append(
            {
                "path": path,
                "content": content,
            }
        )

    monkeypatch.setattr(
        github_agent,
        "write_file",
        fake_write_file,
    )

    # --------------------------------------------------
    # Repair fails
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "repair_loop",
        lambda issue, changed_files, test_command: {
            "success": False,
            "attempts": 3,
            "final_changes": changed_files,
            "test_output": "3 failed",
        },
    )

    # --------------------------------------------------
    # Fake Git operations
    # --------------------------------------------------

    git_events = []

    class FakeGitOperations:

        def invoke(self, params):

            action = params["action"]

            git_events.append(action)

            if action == "rollback":
                return "rollback completed"

            if action in {
                "commit",
                "push",
                "create_pr",
            }:

                raise AssertionError(
                    f"{action} should not "
                    "execute after repair failure"
                )

            return "success"

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FakeGitOperations(),
    )

    # --------------------------------------------------
    # Run workflow
    # --------------------------------------------------

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    # --------------------------------------------------
    # Verify changes were initially applied
    # --------------------------------------------------

    assert written_files == [
        {
            "path": "calculator.py",
            "content": (
                "def add(a, b):\n"
                "    return a + b"
            ),
        }
    ]

    # --------------------------------------------------
    # Verify rollback happened
    # --------------------------------------------------

    assert git_events == [
        "rollback",
    ]

    # --------------------------------------------------
    # Read audit trail
    # --------------------------------------------------

    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    events = [
        json.loads(line)
        for line in lines
    ]

    event_names = [
        entry["event"]
        for entry in events
    ]

    # --------------------------------------------------
    # Verify critical failure events
    # --------------------------------------------------

    assert (
        "REPAIR_LOOP_FAILED"
        in event_names
    )

    assert (
        "ROLLBACK_COMPLETED"
        in event_names
    )

    # --------------------------------------------------
    # Verify no Git delivery events
    # --------------------------------------------------

    assert (
        "GIT_COMMIT_CREATED"
        not in event_names
    )

    assert (
        "GIT_PUSHED"
        not in event_names
    )

    assert (
        "PULL_REQUEST_CREATED"
        not in event_names
    )


# ======================================================
# 5.4 — Git commit failure
# ======================================================


def test_workflow_stops_when_git_commit_fails(
    monkeypatch,
    tmp_path,
):
    """
    Verify that the workflow stops safely when
    Git commit fails.

    Expected flow:

        Issue
          ↓
        Plan
          ↓
        Generate code
          ↓
        Security validation
          ↓
        Apply changes
          ↓
        Tests pass
          ↓
        Branch created
          ↓
        Commit fails
          ↓
        STOP

    Push and PR creation must never happen.
    """

    # --------------------------------------------------
    # Audit log
    # --------------------------------------------------

    audit_log = tmp_path / "audit_log.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    # --------------------------------------------------
    # Fake GitHub issue
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        lambda repo, issue_number: {
            "title": "Fix calculator addition",
            "body": "Fix the addition function.",
        },
    )

    # --------------------------------------------------
    # Fake repository
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "get_repo_structure",
        lambda: {
            "files": [
                "calculator.py",
                "tests/test_sample.py",
            ]
        },
    )

    # --------------------------------------------------
    # Fake planner
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "plan_issue",
        lambda issue, structure: {
            "approach": "Fix addition function",
            "files_to_read": [
                "calculator.py",
            ],
            "requires_razorpay": False,
        },
    )

    # --------------------------------------------------
    # Fake Razorpay policy
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
        },
    )

    # --------------------------------------------------
    # Fake file reader
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "read_file",
        lambda path: (
            "def add(a, b):\n"
            "    return a - b"
        ),
    )

    # --------------------------------------------------
    # Fake code generator
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "generate_fix",
        lambda issue, plan, file_content: {
            "changes": [
                {
                    "path": "calculator.py",
                    "content": (
                        "def add(a, b):\n"
                        "    return a + b"
                    ),
                }
            ],
            "pr_description": (
                "Fix calculator addition."
            ),
        },
    )

    # --------------------------------------------------
    # Validation passes
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "validate_proposed_changes",
        lambda changes: None,
    )

    monkeypatch.setattr(
        github_agent,
        "validate_changes",
        lambda changes: {
            "valid": True,
            "errors": [],
        },
    )

    # --------------------------------------------------
    # Security validation passes
    # --------------------------------------------------

    class FakeSecurityValidator:

        def validate_changes(self, changes):
            return {
                "valid": True,
                "violations": [],
            }

    monkeypatch.setattr(
        github_agent,
        "SecurityValidator",
        FakeSecurityValidator,
    )

    # --------------------------------------------------
    # Track file modifications
    # --------------------------------------------------

    written_files = []

    def fake_write_file(path, content):

        written_files.append(
            {
                "path": path,
                "content": content,
            }
        )

    monkeypatch.setattr(
        github_agent,
        "write_file",
        fake_write_file,
    )

    # --------------------------------------------------
    # Tests pass
    # --------------------------------------------------

    monkeypatch.setattr(
        github_agent,
        "repair_loop",
        lambda issue, changed_files, test_command: {
            "success": True,
            "attempts": 1,
            "final_changes": changed_files,
            "test_output": "1 passed",
        },
    )

    # --------------------------------------------------
    # Fake Git operations
    # --------------------------------------------------

    git_events = []

    class FakeGitOperations:

        def invoke(self, params):

            action = params["action"]

            git_events.append(action)

            # Branch succeeds
            if action == "branch":
                return "branch created"

            # Commit fails
            if action == "commit":
                raise RuntimeError(
                    "Simulated Git commit failure"
                )

            # Push and PR must never happen
            if action in {
                "push",
                "create_pr",
            }:

                raise AssertionError(
                    f"{action} should not execute "
                    "after commit failure"
                )

            return "success"

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FakeGitOperations(),
    )

    # --------------------------------------------------
    # Run workflow
    # --------------------------------------------------

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    # --------------------------------------------------
    # Workflow should terminate safely
    # --------------------------------------------------

    assert result is None

    # --------------------------------------------------
    # Verify generated change was applied
    # --------------------------------------------------

    assert written_files == [
        {
            "path": "calculator.py",
            "content": (
                "def add(a, b):\n"
                "    return a + b"
            ),
        }
    ]

    # --------------------------------------------------
    # Verify Git sequence
    # --------------------------------------------------

    assert git_events == [
        "branch",
        "commit",
    ]

    # --------------------------------------------------
    # Read audit trail
    # --------------------------------------------------

    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    events = [
        json.loads(line)
        for line in lines
    ]

    event_names = [
        entry["event"]
        for entry in events
    ]

    # --------------------------------------------------
    # Verify branch was created
    # --------------------------------------------------

    assert (
        "GIT_BRANCH_CREATED"
        in event_names
    )

    # --------------------------------------------------
    # Verify commit failure was recorded
    # --------------------------------------------------

    assert (
        "GIT_COMMIT_FAILED"
        in event_names
    )

    # --------------------------------------------------
    # Verify delivery stopped
    # --------------------------------------------------

    assert (
        "GIT_PUSHED"
        not in event_names
    )

    assert (
        "PULL_REQUEST_CREATED"
        not in event_names
    )