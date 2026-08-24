import json
import re

from agents.llm import OpenAIProvider
from razorpay.tools import RazorpayTools


def plan_issue(issue, structure):
    """Create a plan for fixing the issue."""

    gateway = OpenAIProvider()

    razorpay_tools = RazorpayTools()

    razorpay_configured = (
        razorpay_tools.credentials_available()
    )

    prompt = f"""
You are an expert autonomous software engineer.

You are analyzing a GitHub issue and planning a safe code change.

GITHUB ISSUE:

Title:
{issue['title']}

Body:
{issue['body']}

REPOSITORY STRUCTURE:

{structure}

Your job:

1. Identify which files need to change.
2. Explain the approach in 2-3 sentences.
3. List the exact files that must be read before making changes.
4. Determine whether the issue involves Razorpay/payment functionality.
5. If Razorpay is involved, classify the payment operation.
6. Assign a risk level.
7. Determine whether human approval is required.

Razorpay operations can include:

- order
- create_payment
- verify_payment
- refund
- subscription
- webhook
- payment_link

Risk classification:

LOW:
Documentation, configuration, tests, or non-payment code.

MEDIUM:
Creating orders, payment integration, checkout integration,
or payment-related application code.

HIGH:
Refunds, payment verification logic, modifying payment amounts,
subscriptions, credentials, webhooks, or anything that can
directly affect financial transactions.

IMPORTANT:

Never request or expose Razorpay secrets.

Return ONLY valid JSON in this exact structure:

{{
    "approach": "your approach in 2-3 sentences",
    "files_to_read": [
        "path/to/file1.py"
    ],
    "requires_razorpay": true,
    "payment_operation": "order",
    "risk_level": "medium",
    "requires_human_approval": true
}}

If Razorpay is NOT involved, return:

{{
    "approach": "your approach",
    "files_to_read": [
        "path/to/file1.py"
    ],
    "requires_razorpay": false,
    "payment_operation": null,
    "risk_level": "low",
    "requires_human_approval": false
}}

Razorpay credentials configured:
{razorpay_configured}
"""

    plan_text = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=2000,
    )

    plan = _extract_json(
        plan_text
    )

    # --------------------------------------------------
    # Enforce deterministic security rules
    # --------------------------------------------------

    if plan.get("requires_razorpay"):

        risk_level = plan.get(
            "risk_level",
            "high",
        )

        if risk_level in {
            "medium",
            "high",
        }:
            plan[
                "requires_human_approval"
            ] = True

    else:

        plan[
            "payment_operation"
        ] = None

        plan[
            "risk_level"
        ] = "low"

        plan[
            "requires_human_approval"
        ] = False

    return plan


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