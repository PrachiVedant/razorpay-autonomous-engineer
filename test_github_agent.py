import agents.github_agent as github_agent

from agents.llm import OpenAIProvider


# --------------------------------------------------
# Fake GitHub issue
# --------------------------------------------------

def fake_get_issue(repo, issue_number):
    print("\n[MOCK] Fetching GitHub issue")

    return {
        "title": "Fix calculator addition",
        "body": (
            "The add function in calculator.py is "
            "incorrect. It should add two numbers."
        ),
    }


# --------------------------------------------------
# Fake GitHub repository
# --------------------------------------------------

def fake_repo_structure():
    print("\n[MOCK] Reading repository structure")

    return """
calculator.py
tests/test_sample.py
"""


# --------------------------------------------------
# Fake repository reader
# --------------------------------------------------

def fake_read_file(filepath):
    print(
        f"[MOCK] Reading file: {filepath}"
    )

    if filepath == "calculator.py":
        return """
def add(a, b):
    return a - b
"""

    if filepath == "tests/test_sample.py":
        return """
from calculator import add


def test_addition():
    assert add(1, 2) == 3
"""

    return ""


# --------------------------------------------------
# Fake file writer
# --------------------------------------------------

def fake_write_file(filepath, content):
    print(
        f"[MOCK] Writing file: {filepath}"
    )

    print(
        f"[MOCK] Content preview:\n{content}"
    )


# --------------------------------------------------
# Fake shell command
# --------------------------------------------------

def fake_run_command(command):
    print(
        f"[MOCK] Running command: {command}"
    )

    return "SUCCESS"


# --------------------------------------------------
# Fake Git operations
# --------------------------------------------------

class FakeGitOperations:

    def invoke(self, payload):

        print(
            "\n[MOCK] Git operation:"
        )

        print(
            payload
        )

        return "SUCCESS"


# --------------------------------------------------
# Replace real external operations with mocks
# --------------------------------------------------

github_agent.get_issue = fake_get_issue

github_agent.get_repo_structure = (
    fake_repo_structure
)

github_agent.read_file = fake_read_file

github_agent.write_file = fake_write_file

github_agent.run_command = fake_run_command

github_agent.git_operations = (
    FakeGitOperations()
)


# --------------------------------------------------
# Mock LLM
# --------------------------------------------------

planner_response = """
{
    "approach": "Fix the calculator addition function.",
    "files_to_read": [
        "calculator.py",
        "tests/test_sample.py"
    ],
    "requires_razorpay": false,
    "payment_operation": null,
    "risk_level": "low",
    "requires_human_approval": false
}
"""


generator_response = """
{
    "changes": [
        {
            "path": "calculator.py",
            "content": "def add(a, b):\\n    return a + b\\n"
        }
    ],
    "pr_description": "Fixed the calculator addition function to return the sum of two numbers."
}
"""


repair_response = """
{
    "reasoning": "The generated code should add the two numbers.",
    "changes": [
        {
            "path": "calculator.py",
            "content": "def add(a, b):\\n    return a + b\\n"
        }
    ]
}
"""


original_generate = OpenAIProvider.generate


def mock_generate(
    self,
    prompt,
    model=None,
    max_tokens=None,
):
    """
    Return deterministic responses for the
    different LLM stages.
    """

    if '"pr_description"' in prompt:
        print(
            "[MOCK LLM] Returning generator response"
        )

        return generator_response

    if '"reasoning"' in prompt:
        print(
            "[MOCK LLM] Returning repair response"
        )

        return repair_response

    print(
        "[MOCK LLM] Returning planner response"
    )

    return planner_response


OpenAIProvider.generate = mock_generate


# --------------------------------------------------
# Run workflow
# --------------------------------------------------

try:

    print(
        "\n"
        + "=" * 60
    )

    print(
        "GITHUB AGENT INTEGRATION TEST"
    )

    print(
        "=" * 60
    )

    github_agent.solve_issue(
        repo="test/repository",
        issue_number=1,
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "GITHUB AGENT TEST COMPLETE"
    )

    print(
        "=" * 60
    )

finally:

    OpenAIProvider.generate = original_generate