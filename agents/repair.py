import json
import re

from agents.llm import OpenAIProvider


def repair_fix(
    issue,
    plan,
    file_contents,
    changes,
    test_result,
):
    """
    Analyze a failed generated code change and produce
    corrected file changes.

    This function is called by the autonomous test/repair loop.
    """

    print("\n[REPAIR AGENT] Starting repair analysis...")

    gateway = OpenAIProvider()

    # --------------------------------------------------
    # Build file context
    # --------------------------------------------------

    file_context = "\n\n".join(
        [
            f"--- {path} ---\n{content}"
            for path, content in file_contents.items()
        ]
    )

    # --------------------------------------------------
    # Build generated changes context
    # --------------------------------------------------

    changes_context = "\n\n".join(
        [
            f"--- {change.get('path')} ---\n"
            f"{change.get('content', '')}"
            for change in changes
        ]
    )

    # --------------------------------------------------
    # Build test failure context
    # --------------------------------------------------

    test_output = (
        test_result.get("stdout", "")
        + "\n"
        + test_result.get("stderr", "")
    )

    prompt = f"""
You are an expert autonomous software engineer.

You are repairing a failed code change generated for a GitHub issue.

GITHUB ISSUE:

Title:
{issue['title']}

Body:
{issue['body']}

ORIGINAL PLAN:

{json.dumps(plan, indent=2)}

FILES YOU ARE ALLOWED TO MODIFY:

{list(file_contents.keys())}

CURRENT FILES:

{file_context}

GENERATED CHANGES:

{changes_context}

TEST OUTPUT:

{test_output}

YOUR TASK:

1. Analyze the test failure.
2. Identify the root cause.
3. Fix the application code.
4. ONLY modify files listed in the allowed files.
5. NEVER modify test files.
6. NEVER create new files.
7. NEVER modify unrelated files.
8. NEVER change tests to make them pass.
9. Preserve all unrelated behavior.
10. Return complete file contents for every modified file.
11. If the failure is caused by the environment or dependency rather than
    the allowed application files, return an empty changes list.

IMPORTANT:

The returned changes must contain complete file contents,
not patches or partial snippets.

Return ONLY valid JSON in exactly this format:

{{
    "reasoning": "Explain the root cause and the fix.",
    "changes": [
        {{
            "path": "path/to/file.py",
            "content": "complete corrected file content"
        }}
    ]
}}

If no safe application-code fix can be made:

{{
    "reasoning": "Explain why the failure cannot be safely fixed.",
    "changes": []
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


def repair_code(
    issue,
    file_contents,
    test_output,
):
    """
    Backward-compatible repair function.

    This allows older code that calls repair_code()
    to continue working.
    """

    test_result = {
        "stdout": "",
        "stderr": test_output,
        "passed": False,
    }

    plan = {}

    changes = []

    result = repair_fix(
        issue=issue,
        plan=plan,
        file_contents=file_contents,
        changes=changes,
        test_result=test_result,
    )

    return result


def _extract_json(text):
    """
    Extract a JSON object from an LLM response.
    """

    # --------------------------------------------------
    # First: try the entire response
    # --------------------------------------------------

    try:
        return json.loads(text.strip())

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------
    # Second: extract JSON object from surrounding text
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Parse extracted JSON
    # --------------------------------------------------

    try:
        return json.loads(
            json_match.group()
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "Repair agent returned invalid JSON:\n"
            + text
        ) from error