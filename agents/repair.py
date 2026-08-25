import json
import re

from agents.llm import OpenAIProvider


def repair_code(
    issue,
    file_contents,
    test_output,
):
    """
    Analyze test failures and generate corrected file changes.
    """

    print("\n[REPAIR AGENT] Starting repair analysis...")

    gateway = OpenAIProvider()

    file_context = "\n\n".join(
        [
            f"--- {path} ---\n{content}"
            for path, content in file_contents.items()
        ]
    )

    prompt = f"""
You are an expert software engineer repairing a failed code change.

GITHUB ISSUE:

Title:
{issue['title']}

Body:
{issue['body']}

FILES YOU ARE ALLOWED TO MODIFY:

{list(file_contents.keys())}

CURRENT FILES:

{file_context}

TEST FAILURE:

{test_output}

Your task:

1. Analyze the test failure.
2. Identify the root cause.
3. Fix the application code.
4. ONLY modify files listed above.
5. NEVER modify test files.
6. NEVER create new files.
7. NEVER modify unrelated files.
8. NEVER change tests to make them pass.
9. Preserve unrelated behavior.
10. If the failure is caused by the environment or dependency
    rather than the allowed application files, return an empty
    changes list.

Return ONLY valid JSON.

{{
    "reasoning": "Explain the root cause and the fix.",
    "changes": [
        {{
            "path": "path/to/file.py",
            "content": "complete corrected file content"
        }}
    ]
}}
"""

    print("[REPAIR AGENT] Sending request to LLM...")

    response = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=3000,
    )

    print("[REPAIR AGENT] LLM response received.")

    print(
        f"[REPAIR AGENT] Response length: "
        f"{len(response)} characters"
    )

    return _extract_json(response)


def _extract_json(text):
    """
    Extract JSON object from the LLM response.
    """

    # First try the entire response
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Then try to find a JSON object
    json_match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL,
    )

    if not json_match:
        raise ValueError(
            "Could not parse JSON from repair agent response:\n"
            + text
        )

    try:
        return json.loads(
            json_match.group()
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Repair agent returned invalid JSON:\n"
            + text
        ) from error