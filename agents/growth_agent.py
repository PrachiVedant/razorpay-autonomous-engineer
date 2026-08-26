import json
import re

from agents.llm import OpenAIProvider
from merchant.tools import get_merchant_snapshot


def identify_growth_opportunity():
    """
    Analyze merchant performance and identify a growth opportunity.
    """

    snapshot = get_merchant_snapshot()

    prompt = f"""
You are a Growth Intelligence Agent for a payment platform.

Your job is to analyze a merchant's payment and revenue data
and identify the most important growth opportunity.

MERCHANT SNAPSHOT:

{json.dumps(snapshot, indent=2)}

Analyze the data carefully.

You must:

1. Identify the most important growth opportunity.
2. Support the opportunity using ONLY evidence from the snapshot.
3. Identify the relevant payment or revenue metric.
4. Estimate the potential impact using the available data.
5. Recommend a next step.
6. Assign a confidence score between 0 and 1.

IMPORTANT:

- Do not invent data.
- Do not invent transaction values.
- Do not claim an action was performed.
- This stage is ANALYSIS ONLY.
- Do not recommend refunds or other financial actions as if they
  have already been executed.

Return ONLY valid JSON in this exact structure:

{{
    "opportunity_type": "string",
    "severity": "low|medium|high",
    "evidence": [
        {{
            "metric": "string",
            "value": "string",
            "interpretation": "string"
        }}
    ],
    "estimated_impact": "string",
    "recommendation": "string",
    "confidence": 0.0
}}
"""

    gateway = OpenAIProvider()

    response = gateway.generate(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=1500,
    )

    return _extract_json(response)


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