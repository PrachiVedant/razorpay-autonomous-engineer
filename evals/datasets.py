"""Evaluation dataset examples for later metric calculations."""

from typing import Any, Dict, List

EVALUATION_EXAMPLES: List[Dict[str, Any]] = [
    {
        "id": "issue_fix_001",
        "task": "issue_fix",
        "description": "Fix a typo in a greeting helper function.",
        "issue": {
            "title": "Fix greeting typo in helper function",
            "body": "The greet_user function prints 'Helo' instead of 'Hello'. Update the function so it prints the correct greeting.",
        },
        "repo_files": {
            "utils/greeting.py": "def greet_user(name):\n    print(f\"Helo, {name}!\")\n",
        },
        "expected_changes": [
            {
                "path": "utils/greeting.py",
                "change_type": "modify",
                "expected_content": "def greet_user(name):\n    print(f\"Hello, {name}!\")\n",
            }
        ],
    },
    {
        "id": "issue_fix_002",
        "task": "issue_fix",
        "description": "Add missing import for datetime in output formatting.",
        "issue": {
            "title": "Import datetime for date formatting",
            "body": "The script fails because datetime is used without being imported. Add the missing import and keep the output formatting unchanged.",
        },
        "repo_files": {
            "scripts/report.py": "def generate_report():\n    today = datetime.date.today()\n    return f\"Report for {today}\"\n",
        },
        "expected_changes": [
            {
                "path": "scripts/report.py",
                "change_type": "modify",
                "expected_content": "import datetime\n\n"
                                      "def generate_report():\n"
                                      "    today = datetime.date.today()\n"
                                      "    return f\"Report for {today}\"\n",
            }
        ],
    },
    {
        "id": "issue_fix_003",
        "task": "issue_fix",
        "description": "Update README to document a new environment variable.",
        "issue": {
            "title": "Document NEW_API_KEY environment variable",
            "body": "The README does not mention NEW_API_KEY. Add a short usage example to the configuration section.",
        },
        "repo_files": {
            "README.md": "# Project\n\n## Configuration\n\nSet the following variables before running the agent.\n",
        },
        "expected_changes": [
            {
                "path": "README.md",
                "change_type": "modify",
                "expected_content": "# Project\n\n## Configuration\n\nSet the following variables before running the agent.\n\n- `NEW_API_KEY`: API key for connecting to the external service.\n",
            }
        ],
    },
]


def get_all_examples() -> List[Dict[str, Any]]:
    """Return all evaluation examples."""
    return EVALUATION_EXAMPLES


def get_examples_by_task(task: str) -> List[Dict[str, Any]]:
    """Return only the evaluation examples that match the provided task."""
    return [example for example in EVALUATION_EXAMPLES if example["task"] == task]


def get_issue_fix_examples() -> List[Dict[str, Any]]:
    """Return issue-fix evaluation examples."""
    return get_examples_by_task("issue_fix")