import json

import agents.github_agent as github_agent


def test_complete_autonomous_workflow(
    monkeypatch,
    tmp_path,
):
    """
    Verify the complete successful autonomous
    coding workflow from GitHub issue to PR.

        Issue
          ↓
        Plan
          ↓
        Generate
          ↓
        Security
          ↓
        Apply
          ↓
        Tests
          ↓
        Branch
          ↓
        Commit
          ↓
        Push
          ↓
        PR
          ↓
        Complete
    """

    # ==================================================
    # Audit log
    # ==================================================

    audit_log = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        github_agent.audit_logger,
        "log_path",
        audit_log,
    )

    # ==================================================
    # Track execution
    # ==================================================

    execution = []

    # ==================================================
    # GitHub issue
    # ==================================================

    def fake_get_issue(repo, issue_number):

        execution.append(
            "issue"
        )

        return {
            "title": "Fix calculator addition",
            "body": (
                "The add function is incorrect."
            ),
        }

    monkeypatch.setattr(
        github_agent,
        "get_issue",
        fake_get_issue,
    )

    # ==================================================
    # Repository
    # ==================================================

    def fake_repo_structure():

        execution.append(
            "repository"
        )

        return {
            "files": [
                "calculator.py",
                "tests/test_sample.py",
            ]
        }

    monkeypatch.setattr(
        github_agent,
        "get_repo_structure",
        fake_repo_structure,
    )

    # ==================================================
    # Planner
    # ==================================================

    def fake_plan(issue, structure):

        execution.append(
            "plan"
        )

        return {
            "approach": (
                "Fix calculator addition"
            ),
            "files_to_read": [
                "calculator.py",
            ],
            "requires_razorpay": False,
        }

    monkeypatch.setattr(
        github_agent,
        "plan_issue",
        fake_plan,
    )

    # ==================================================
    # Payment policy
    # ==================================================

    def fake_payment_policy(plan):

        execution.append(
            "payment_policy"
        )

        return {
            "allowed": True,
            "requires_approval": False,
        }

    monkeypatch.setattr(
        github_agent,
        "validate_payment_plan",
        fake_payment_policy,
    )

    # ==================================================
    # File reader
    # ==================================================

    def fake_read_file(path):

        execution.append(
            f"read:{path}"
        )

        return (
            "def add(a, b):\n"
            "    return a - b"
        )

    monkeypatch.setattr(
        github_agent,
        "read_file",
        fake_read_file,
    )

    # ==================================================
    # Code generator
    # ==================================================

    def fake_generate_fix(
        issue,
        plan,
        file_content,
    ):

        execution.append(
            "generate"
        )

        return {
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
        }

    monkeypatch.setattr(
        github_agent,
        "generate_fix",
        fake_generate_fix,
    )

    # ==================================================
    # GitHub change validation
    # ==================================================

    def fake_validate_proposed_changes(
        changes
    ):

        execution.append(
            "change_validation"
        )

    monkeypatch.setattr(
        github_agent,
        "validate_proposed_changes",
        fake_validate_proposed_changes,
    )

    # ==================================================
    # Security validator
    # ==================================================

    class FakeSecurityValidator:

        def validate_changes(
            self,
            changes,
        ):

            execution.append(
                "security"
            )

            return {
                "valid": True,
                "violations": [],
            }

    monkeypatch.setattr(
        github_agent,
        "SecurityValidator",
        FakeSecurityValidator,
    )

    # ==================================================
    # Razorpay validator
    # ==================================================

    def fake_validate_changes(changes):

        execution.append(
            "razorpay_validation"
        )

        return {
            "valid": True,
            "errors": [],
        }

    monkeypatch.setattr(
        github_agent,
        "validate_changes",
        fake_validate_changes,
    )

    # ==================================================
    # Apply changes
    # ==================================================

    written_files = []

    def fake_write_file(
        path,
        content,
    ):

        execution.append(
            "write"
        )

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

    # ==================================================
    # Tests / repair
    # ==================================================

    def fake_repair_loop(
        issue,
        changed_files,
        test_command,
    ):

        execution.append(
            "tests"
        )

        return {
            "success": True,
            "attempts": 1,
            "final_changes": changed_files,
            "test_output": "1 passed",
        }

    monkeypatch.setattr(
        github_agent,
        "repair_loop",
        fake_repair_loop,
    )

    # ==================================================
    # Git operations
    # ==================================================

    git_events = []

    class FakeGitOperations:

        def invoke(self, params):

            action = params["action"]

            execution.append(
                f"git:{action}"
            )

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
                return "PR created"

            raise AssertionError(
                f"Unexpected Git action: {action}"
            )

    monkeypatch.setattr(
        github_agent,
        "git_operations",
        FakeGitOperations(),
    )

    # ==================================================
    # Run complete workflow
    # ==================================================

    result = github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    # ==================================================
    # Workflow returns safely
    # ==================================================

    assert result is None

    # ==================================================
    # Verify generated code was applied
    # ==================================================

    assert written_files == [
        {
            "path": "calculator.py",
            "content": (
                "def add(a, b):\n"
                "    return a + b"
            ),
        }
    ]

    # ==================================================
    # Verify Git sequence
    # ==================================================

    assert git_events == [
        "branch",
        "commit",
        "push",
        "create_pr",
    ]

    # ==================================================
    # Verify major execution order
    # ==================================================

    assert execution.index(
        "issue"
    ) < execution.index(
        "repository"
    )

    assert execution.index(
        "repository"
    ) < execution.index(
        "plan"
    )

    assert execution.index(
        "plan"
    ) < execution.index(
        "generate"
    )

    assert execution.index(
        "generate"
    ) < execution.index(
        "security"
    )

    assert execution.index(
        "security"
    ) < execution.index(
        "razorpay_validation"
    )

    assert execution.index(
        "razorpay_validation"
    ) < execution.index(
        "write"
    )

    assert execution.index(
        "write"
    ) < execution.index(
        "tests"
    )

    assert execution.index(
        "tests"
    ) < execution.index(
        "git:branch"
    )

    assert execution.index(
        "git:branch"
    ) < execution.index(
        "git:commit"
    )

    assert execution.index(
        "git:commit"
    ) < execution.index(
        "git:push"
    )

    assert execution.index(
        "git:push"
    ) < execution.index(
        "git:create_pr"
    )

    # ==================================================
    # Read audit trail
    # ==================================================

    lines = audit_log.read_text(
        encoding="utf-8"
    ).splitlines()

    events = [
        json.loads(line)
        for line in lines
    ]

    event_names = [
        event["event"]
        for event in events
    ]

    # ==================================================
    # Verify successful workflow audit trail
    # ==================================================

    assert (
        "ISSUE_RECEIVED"
        in event_names
    )

    assert (
        "REPOSITORY_ANALYZED"
        in event_names
    )

    assert (
        "PLAN_CREATED"
        in event_names
    )

    assert (
        "CODE_GENERATED"
        in event_names
    )

    assert (
        "SECURITY_VALIDATION_PASSED"
        in event_names
    )

    assert (
        "CHANGES_APPLIED"
        in event_names
    )

    assert (
        "TEST_PASSED"
        not in event_names
    ) or (
        "REPAIR_LOOP_COMPLETED"
        in event_names
    )

    assert (
        "GIT_BRANCH_CREATED"
        in event_names
    )

    assert (
        "GIT_COMMIT_CREATED"
        in event_names
    )

    assert (
        "GIT_PUSHED"
        in event_names
    )

    assert (
        "PULL_REQUEST_CREATED"
        in event_names
    )

    assert (
        "WORKFLOW_COMPLETED"
        in event_names
    )

    # ==================================================
    # Verify no failure event ended the workflow
    # ==================================================

    assert (
        "WORKFLOW_FAILED"
        not in event_names
    )