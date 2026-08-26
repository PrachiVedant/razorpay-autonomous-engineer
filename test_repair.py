from agents.repair import repair_code
from agents.llm import OpenAIProvider


def test_repair():
    issue = {
        "title": "Fix addition function",
        "body": "The add function should return the sum of two numbers.",
    }

    file_contents = {
        "calculator.py": """
def add(a, b):
    return a - b
"""
    }

    test_output = """
FAILED tests/test_sample.py::test_addition

AssertionError:
assert add(1, 2) == 3
E       assert -1 == 3
"""

    fake_response = """
{
    "reasoning": "The function subtracts b from a instead of adding the two values.",
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
        result = repair_code(
            issue,
            file_contents,
            test_output,
        )

        assert "reasoning" in result
        assert "changes" in result
        assert len(result["changes"]) == 1
        assert result["changes"][0]["path"] == "calculator.py"

    finally:
        OpenAIProvider.generate = original_generate