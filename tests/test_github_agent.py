from agents.github_agent import solve_issue


def test_solve_issue_end_to_end(monkeypatch):
    events = []

    monkeypatch.setattr(
        "github_agent.get_issue",
        lambda repo, issue_number: {
            "title": "Fix calculator addition",
            "body": "Fix the addition function.",
        },
    )

    monkeypatch.setattr(
        "github_agent.get_repo_structure",
        lambda: {
            "files": [
                "calculator.py",
                "tests/test_sample.py",
            ]
        },
    )

    monkeypatch.setattr(
        "github_agent.plan_issue",
        lambda issue, structure: {
            "approach": "Fix addition function",
            "files_to_read": ["calculator.py"],
            "requires_razorpay": False,
        },
    )

    monkeypatch.setattr(
        "github_agent.validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
        },
    )

    monkeypatch.setattr(
        "github_agent.read_file",
        lambda path: "def add(a, b):\n    return a - b",
    )

    monkeypatch.setattr(
        "github_agent.generate_fix",
        lambda issue, plan, file_content: {
            "changes": [
                {
                    "path": "calculator.py",
                    "content": "def add(a, b):\n    return a + b",
                }
            ],
            "pr_description": "Fix calculator addition.",
        },
    )

    monkeypatch.setattr(
        "github_agent.validate_proposed_changes",
        lambda changes: None,
    )

    monkeypatch.setattr(
        "github_agent.validate_changes",
        lambda changes: {
            "valid": True,
            "errors": [],
        },
    )

    monkeypatch.setattr(
        "github_agent.write_file",
        lambda path, content: None,
    )

    monkeypatch.setattr(
        "github_agent.repair_loop",
        lambda issue, changed_files, test_command: {
            "success": True,
            "attempts": 1,
            "final_changes": changed_files,
            "test_output": "1 passed",
        },
    )

    class FakeGitOperations:

        def invoke(self, params):
            events.append(params["action"])

            if params["action"] == "commit":
                return "commit created"

            if params["action"] == "push":
                return "branch pushed"

            if params["action"] == "create_pr":
                return "PR created"

            return "success"

    monkeypatch.setattr(
        "github_agent.git_operations",
        FakeGitOperations(),
    )

    solve_issue(
        "test/repository",
        1,
    )

    assert events == [
        "branch",
        "commit",
        "push",
        "create_pr",
    ]