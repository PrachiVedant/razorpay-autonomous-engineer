import json

import agents.github_agent as github_agent


# ============================================================
# Helpers
# ============================================================

def read_events(audit_log):
    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines
    ]


def setup_basic_workflow(monkeypatch):
    """
    Configure everything up to the boundary
    under test so the test remains focused.
    """

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        lambda repo, issue_number: {
            "title": "Fix calculator addition",
            "body": "Fix addition.",
        },
    )

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

    monkeypatch.setattr(
        github_agent,
        "plan_issue",
        lambda issue, structure: {
            "approach": "Fix addition",
            "files_to_read": [
                "calculator.py",
            ],
            "requires_razorpay": False,
        },
    )

    monkeypatch.setattr(
        github_agent,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
        },
    )

    monkeypatch.setattr(
        github_agent,
        "read_file",
        lambda path: (
            "def add(a, b):\n"
            "    return a - b"
        ),
    )

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

    monkeypatch.setattr(
        github_agent,
        "write_file",
        lambda path, content: None,
    )

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


# ============================================================
# 1. GitHub issue failure
# ============================================================

def test_issue_fetch_failure_stops_workflow(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    def fail_get_issue(repo, issue_number):
        raise RuntimeError(
            "GitHub API unavailable"
        )

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        fail_get_issue,
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert "ISSUE_FETCH_FAILED" in names

    assert (
        "REPOSITORY_ANALYZED"
        not in names
    )

    assert (
        "GIT_BRANCH_CREATED"
        not in names
    )

    assert (
        "PULL_REQUEST_CREATED"
        not in names
    )


# ============================================================
# 2. Repository analysis failure
# ============================================================

def test_repository_analysis_failure_stops_workflow(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        lambda repo, issue_number: {
            "title": "Test issue",
            "body": "Test body",
        },
    )

    def fail_repository():
        raise RuntimeError(
            "Repository unavailable"
        )

    monkeypatch.setattr(
        github_agent,
        "get_repo_structure",
        fail_repository,
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "REPOSITORY_ANALYSIS_FAILED"
        in names
    )

    assert (
        "PLAN_CREATED"
        not in names
    )


# ============================================================
# 3. Planner failure
# ============================================================

def test_planner_failure_stops_workflow(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        lambda repo, issue_number: {
            "title": "Test issue",
            "body": "Test body",
        },
    )

    monkeypatch.setattr(
        github_agent,
        "get_repo_structure",
        lambda: {
            "files": [
                "calculator.py",
            ]
        },
    )

    def fail_planner(issue, structure):
        raise RuntimeError(
            "Planner unavailable"
        )

    monkeypatch.setattr(
        github_agent,
        "plan_issue",
        fail_planner,
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "PLAN_CREATION_FAILED"
        in names
    )

    assert (
        "CODE_GENERATED"
        not in names
    )


# ============================================================
# 4. File reading failure
# ============================================================

def test_file_read_failure_stops_workflow(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    def fail_read_file(path):
        raise RuntimeError(
            f"Cannot read {path}"
        )

    monkeypatch.setattr(
        github_agent,
        "read_file",
        fail_read_file,
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "FILES_READ_FAILED"
        in names
    )

    assert (
        "CODE_GENERATED"
        not in names
    )


# ============================================================
# 5. Code generation failure
# ============================================================

def test_code_generation_failure_stops_workflow(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    def fail_generator(
        issue,
        plan,
        file_content,
    ):
        raise RuntimeError(
            "LLM generation failed"
        )

    monkeypatch.setattr(
        github_agent,
        "generate_fix",
        fail_generator,
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "CODE_GENERATION_FAILED"
        in names
    )

    assert (
        "CHANGES_APPLIED"
        not in names
    )


# ============================================================
# 6. Security validation failure
# ============================================================

def test_security_validation_failure_blocks_changes(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    class RejectingSecurityValidator:

        def validate_changes(self, changes):
            return {
                "valid": False,
                "violations": [
                    "Hardcoded secret detected"
                ],
            }

    monkeypatch.setattr(
        github_agent,
        "SecurityValidator",
        RejectingSecurityValidator,
    )

    written_files = []

    monkeypatch.setattr(
        github_agent,
        "write_file",
        lambda path, content: written_files.append(
            path
        ),
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    assert written_files == []

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "SECURITY_VALIDATION_FAILED"
        in names
    )

    assert (
        "CHANGES_APPLIED"
        not in names
    )


# ============================================================
# 7. Razorpay validation failure
# ============================================================

def test_razorpay_validation_failure_blocks_changes(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    monkeypatch.setattr(
        github_agent,
        "validate_changes",
        lambda changes: {
            "valid": False,
            "errors": [
                "Unsafe payment modification"
            ],
        },
    )

    written_files = []

    monkeypatch.setattr(
        github_agent,
        "write_file",
        lambda path, content: written_files.append(
            path
        ),
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    assert written_files == []

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "RAZORPAY_SECURITY_VALIDATION_FAILED"
        in names
    )

    assert (
        "CHANGES_APPLIED"
        not in names
    )


# ============================================================
# 8. Git branch creation failure
# ============================================================

def test_git_branch_failure_stops_delivery(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    class FailingGit:

        def invoke(self, params):

            if params["action"] == "branch":
                raise RuntimeError(
                    "Branch creation failed"
                )

            raise AssertionError(
                "Unexpected Git operation"
            )

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FailingGit(),
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "GIT_BRANCH_CREATION_FAILED"
        in names
    )

    assert (
        "GIT_COMMIT_CREATED"
        not in names
    )

    assert (
        "GIT_PUSHED"
        not in names
    )

    assert (
        "PULL_REQUEST_CREATED"
        not in names
    )


# ============================================================
# 9. Git push failure
# ============================================================

def test_git_push_failure_stops_before_pr(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    git_events = []

    class FailingPushGit:

        def invoke(self, params):

            action = params["action"]

            git_events.append(
                action
            )

            if action == "branch":
                return "branch created"

            if action == "commit":
                return "commit created"

            if action == "push":
                raise RuntimeError(
                    "Push failed"
                )

            if action == "create_pr":
                raise AssertionError(
                    "PR must not be created"
                )

            return "success"

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FailingPushGit(),
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    assert git_events == [
        "branch",
        "commit",
        "push",
    ]

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "GIT_PUSH_FAILED"
        in names
    )

    assert (
        "PULL_REQUEST_CREATED"
        not in names
    )


# ============================================================
# 10. Pull Request creation failure
# ============================================================

def test_pr_creation_failure_records_failure(
    monkeypatch,
    tmp_path,
):
    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    setup_basic_workflow(
        monkeypatch
    )

    git_events = []

    class FailingPRGit:

        def invoke(self, params):

            action = params["action"]

            git_events.append(
                action
            )

            if action == "branch":
                return "branch created"

            if action == "commit":
                return "commit created"

            if action == "push":
                return "push successful"

            if action == "create_pr":
                raise RuntimeError(
                    "Pull Request creation failed"
                )

            return "success"

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FailingPRGit(),
    )

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    assert result is None

    assert git_events == [
        "branch",
        "commit",
        "push",
        "create_pr",
    ]

    events = read_events(audit_log)

    names = [
        event["event"]
        for event in events
    ]

    assert (
        "PULL_REQUEST_CREATION_FAILED"
        in names
    )

    assert (
        "WORKFLOW_COMPLETED"
        not in names
    )