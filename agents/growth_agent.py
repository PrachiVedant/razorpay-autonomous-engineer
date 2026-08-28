import json
from agents.llm import OpenAIProvider
from merchant.tools import get_merchant_snapshot
from typing import Any, Dict


def identify_growth_opportunity(
    merchant_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Identify a growth opportunity from merchant evidence.

    The LLM proposes the opportunity, but it does not execute
    any payment action. The resulting evidence is later checked
    deterministically by opportunity_validator.py.
    """

    if merchant_snapshot is None:
        merchant_snapshot = get_merchant_snapshot()

    prompt = f"""
You are a merchant growth analyst.

Analyze the following merchant snapshot and identify ONE concrete,
bounded growth opportunity.

MERCHANT SNAPSHOT:
{json.dumps(merchant_snapshot, indent=2)}

Focus on payment conversion and failed payments when the evidence
supports it.

Return ONLY valid JSON in exactly this structure:

{{
    "opportunity_type": "payment_conversion",
    "severity": "high",
    "evidence": [
        {{
            "metric": "card_failure_rate",
            "value": "100%",
            "interpretation": "All card payments are failing."
        }},
        {{
            "metric": "failed_payment_value",
            "value": "6796",
            "interpretation": "Failed payments represent significant transaction value."
        }}
    ],
    "estimated_impact": "Potential recovery of failed payment value.",
    "recommendation": "Investigate the card payment failure issue before taking action.",
    "confidence": 0.95
}}

Important:
- Use ONLY metrics present in the merchant snapshot.
- Do not invent numbers.
- Do not execute any payment action.
- Do not create payment links.
- Return JSON only.
"""

    provider = OpenAIProvider()

    response = provider.generate(prompt)

    try:
        opportunity = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Growth agent returned invalid JSON: {error}"
        ) from error

    return opportunity