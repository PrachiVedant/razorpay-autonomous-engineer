import json
from agents.llm import OpenAIProvider


def plan_issue(issue, structure):
    """Create a plan for fixing the issue."""
    gateway = OpenAIProvider()
    messages = [
        {
            "role": "user",
            "content": f"""You are an expert software engineer. Here's a GitHub issue to fix.

ISSUE:
Title: {issue['title']}
Body: {issue['body']}

REPO STRUCTURE:
{structure}

Your job:
1. Identify which files need to change
2. Explain your approach in 2-3 sentences
3. List the exact files to read before making changes

Respond with JSON:
{{
    "approach": "your approach in 2-3 sentences",
    "files_to_read": ["path/to/file1.py", "path/to/file2.py"]
}}"""
        }
    ]

    prompt = messages[0]["content"]
    plan_text = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=2000,
    )
    return _extract_json(plan_text)


def _extract_json(text):
    import re

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError(f"Could not parse JSON from response: {text}")
    return json.loads(json_match.group())