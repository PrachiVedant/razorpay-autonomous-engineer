from agents.repair_loop import repair_loop
from agents.llm import OpenAIProvider


def test_repair_loop():
    issue = {
        "title": "Fix addition function",
        "body": "The add function should return the sum of two numbers.",
    }

    changed_files = [
        {
            "path": "calculator.py",
            "content": """def add(a, b):
    return a - b
""",
        }
    ]

    fake_response = """
{
    "reasoning": "The function uses subtraction instead of addition.",
    "changes": [
        {
            "path": "calculator.py",
            "content": "def add(a, b):\\n    return a + b\\n"
        }
    ]
}
"""

    original_generate = OpenAIProvider.generate

    def mock_generate(self, prompt, model=None, max_tokens=None):
        return fake_response

    OpenAIProvider.generate = mock_generate

    try:
        result = repair_loop(
            issue=issue,
            changed_files=changed_files,
            test_command="pytest tests/",
        )

        assert "success" in result
        assert "attempts" in result

    finally:
        OpenAIProvider.generate = original_generate