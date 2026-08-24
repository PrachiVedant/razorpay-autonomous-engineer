import json
import re

from agents.llm import OpenAIProvider


def generate_fix(issue, plan, file_contents):
    """
    Generate the complete file changes for the issue fix.

    Adds additional security constraints when the issue
    involves Razorpay/payment functionality.
    """

    gateway = OpenAIProvider()

    file_context = "\n\n".join(
        [
            f"---{path}---\n{content}"
            for path, content in file_contents.items()
        ]
    )

    # --------------------------------------------------
    # Razorpay-specific instructions
    # --------------------------------------------------

    razorpay_instructions = ""

    if plan.get("requires_razorpay", False):

        operation = plan.get(
            "payment_operation",
            "unknown",
        )

        risk_level = plan.get(
            "risk_level",
            "high",
        )

        razorpay_instructions = f"""

IMPORTANT: THIS IS A RAZORPAY/PAYMENT TASK.

Payment operation:
{operation}

Risk level:
{risk_level}

You MUST follow these security rules:

1. NEVER hardcode Razorpay credentials.

2. NEVER generate fake Razorpay credentials.

3. NEVER expose or print API secrets.

4. Load credentials from environment variables.

Use patterns such as:

    os.getenv("RAZORPAY_KEY_ID")
    os.getenv("RAZORPAY_KEY_SECRET")

5. Do not place secrets in:
   - Python source files
   - configuration files
   - README examples
   - tests
   - JSON responses
   - logs

6. Do not change payment amounts unless explicitly
   requested by the GitHub issue.

7. Preserve the existing application architecture.

8. Only modify files that are necessary for the issue.

9. Do not introduce unrelated refactoring.

10. If the existing repository already has a payment
    service, extend it instead of creating a duplicate
    payment implementation.

11. For payment operations, prefer explicit validation
    and error handling.

12. Do not claim that a payment was successful unless
    the application actually verifies the payment.

13. Never bypass existing authentication,
    authorization, or payment validation logic.

14. If credentials are required but are not present in
    the repository, assume they will be supplied through
    environment variables at runtime.

The generated code will be passed through a deterministic
security validator before it can be applied.
"""

    # --------------------------------------------------
    # Main generation prompt
    # --------------------------------------------------

    prompt = f"""
You are an expert software engineer working on a
production repository.

You are fixing this GitHub issue.

TITLE:
{issue['title']}

BODY:
{issue['body']}

PLANNED APPROACH:
{plan['approach']}

FILES TO READ:
{plan['files_to_read']}

CURRENT FILE CONTENTS:

{file_context}

{razorpay_instructions}

TASK:

Generate the complete updated contents of ONLY the files
that need to change.

Important:

- Do not modify unrelated files.
- Preserve existing functionality.
- Do not remove existing functionality unless explicitly
  required by the issue.
- Follow the repository's existing coding style.
- Do not invent APIs or files unnecessarily.
- Make the smallest reasonable change that solves
  the issue.
- Return complete file contents rather than patches.

Respond with ONLY valid JSON:

{{
    "changes": [
        {{
            "path": "path/to/file.py",
            "content": "complete file content here"
        }}
    ],
    "pr_description": "description of what was fixed and why"
}}
"""

    fix_text = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=4000,
    )

    return _extract_json(fix_text)


def _extract_json(text):
    """
    Extract JSON from an LLM response.
    """

    json_match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL,
    )

    if not json_match:
        raise ValueError(
            f"Could not parse JSON from response: {text}"
        )

    return json.loads(
        json_match.group()
    )