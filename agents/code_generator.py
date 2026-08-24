import json
from agents.llm import OpenAIProvider


def generate_fix(issue, plan, file_contents):
    """Generate the complete file changes for the issue fix."""
    gateway = OpenAIProvider()
    file_context = "\n\n".join(
        [f"---{path}---\n{content}" for path, content in file_contents.items()]
    )
    messages = [
        {
            "role": "user",
            "content": f"""You are fixing this GitHub issue:

Title: {issue['title']}
Body: {issue['body']}

Your approach: {plan['approach']}

Here are the current file contents:

{file_context}

Write the complete fixed version of each file that needs to change.
Respond with JSON:
{{
    "changes": [
        {{"path": "path/to/file.py", "content": "full file content here"}},
    ],
    "pr_description": "description of what was fixed and why"
}}"""
        }
    ]

    prompt = messages[0]["content"]
    fix_text = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=4000,
    )
    return _extract_json(fix_text)


def _extract_json(text):
    import re

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError(f"Could not parse JSON from response: {text}")
    return json.loads(json_match.group())