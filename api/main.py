import json
import os
import re
import sys
from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agents.growth_workflow import run_growth_workflow
from merchant.tools import get_merchant_snapshot

app = FastAPI(
    title="Razorpay Autonomous Growth Agent",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SENSITIVE_PATTERNS = [
    r"RAZORPAY_KEY_ID",
    r"RAZORPAY_KEY_SECRET",
    r"key_id",
    r"key_secret",
    r"api_key",
    r"access_token",
    r"authorization",
    r"password",
    r"secret",
    r"token",
]


def sanitize_error(error: Exception) -> str:
    """
    Prevent sensitive credential information from leaking
    through API responses.
    """

    message = str(error)

    for pattern in SENSITIVE_PATTERNS:
        if re.search(
            pattern,
            message,
            re.IGNORECASE,
        ):
            return (
                "An internal execution error occurred. "
                "Sensitive information was withheld."
            )

    return message


def sanitize_audit_event(event):
    """
    Recursively redact sensitive fields before audit data
    is exposed to the frontend.
    """

    sensitive_keys = {
        "key",
        "key_id",
        "key_secret",
        "secret",
        "password",
        "token",
        "access_token",
        "authorization",
        "api_key",
    }

    if isinstance(event, dict):

        sanitized = {}

        for key, value in event.items():

            if key.lower() in sensitive_keys:
                sanitized[key] = "[REDACTED]"
                continue

            sanitized[key] = sanitize_audit_event(
                value
            )

        return sanitized

    if isinstance(event, list):
        return [
            sanitize_audit_event(item)
            for item in event
        ]

    return event

#opportunity
def normalize_opportunity(opportunity):
    """
    Convert the internal growth-agent opportunity into
    a stable frontend contract.

    Internal growth agent fields:

        base_product
        upsell_product
        base_amount
        upsell_amount
        final_amount
        conversion_rate
        historical_purchases
        evidence
        reason
        reasoning

    Frontend-friendly aliases are added without removing
    the original fields.
    """

    if not isinstance(opportunity, dict):
        return None

    base_product = opportunity.get(
        "base_product"
    )

    upsell_product = opportunity.get(
        "upsell_product"
    )

    base_amount = opportunity.get(
        "base_amount"
    )

    upsell_amount = opportunity.get(
        "upsell_amount"
    )

    final_amount = opportunity.get(
        "final_amount"
    )

    conversion_rate = opportunity.get(
        "conversion_rate"
    )

    historical_purchases = opportunity.get(
        "historical_purchases"
    )

    evidence = opportunity.get(
        "evidence",
        {},
    )

    reason = opportunity.get(
        "reason"
    )

    reasoning = opportunity.get(
        "reasoning",
        [],
    )

    evidence_strength = opportunity.get(
        "evidence_strength"
    )

    confidence = opportunity.get(
        "confidence"
    )

    upsell_percentage = opportunity.get(
        "upsell_percentage"
    )

    expected_incremental_revenue = opportunity.get(
        "expected_incremental_revenue"
    )

    normalized = dict(opportunity)

    normalized["base_product_name"] = (
        base_product
    )

    normalized["upsell_product_name"] = (
        upsell_product
    )

    #evidence
    normalized["base_product_evidence"] = (
        f"{historical_purchases:g} historical purchases"
        if isinstance(
            historical_purchases,
            (int, float),
        )
        else None
    )

    normalized["upsell_evidence"] = (
        f"{conversion_rate:.0%} historical conversion"
        if isinstance(
            conversion_rate,
            (int, float),
        )
        else None
    )

    normalized["base_product_reason"] = (
        f"{base_product} is the selected high-value "
        "base product based on merchant data."
        if base_product
        else None
    )

    normalized["upsell_reason"] = (
        reason
        or (
            f"{upsell_product} is supported by "
            f"{conversion_rate:.0%} historical conversion "
            "evidence."
            if (
                upsell_product
                and isinstance(
                    conversion_rate,
                    (int, float),
                )
            )
            else None
        )
    )

    if (
        isinstance(upsell_percentage, (int, float))
        and upsell_percentage <= 0.10
    ):
        normalized["policy_reason"] = (
            f"The upsell is "
            f"{upsell_percentage:.0%} of the base amount, "
            "which is within the 10% autonomous financial "
            "boundary."
        )
    else:
        normalized["policy_reason"] = (
            "The deterministic policy engine controls "
            "whether the financial action is permitted."
        )

    normalized["evidence_summary"] = (
        evidence
    )

    normalized["reasoning"] = reasoning

    normalized["evidence_strength"] = (
        evidence_strength
    )

    normalized["confidence"] = confidence

    normalized["expected_incremental_revenue"] = (
        expected_incremental_revenue
    )

    return normalized


def normalize_growth_response(result):
    """
    Normalize the internal growth workflow result into
    a stable API response contract.
    """

    if not isinstance(
        result,
        dict,
    ):
        return {
            "success": False,
            "stage": "api",
            "reason": "Invalid workflow response.",
            "amount": None,
            "currency": "INR",
            "payment_link_id": None,
            "short_url": None,
            "opportunity": None,
        }

    opportunity = normalize_opportunity(
        result.get("opportunity")
    )

    return {
        "success": result.get(
            "success",
            False,
        ),

        "stage": result.get(
            "stage"
        ),

        "reason": result.get(
            "reason"
        ),

        "amount": result.get(
            "amount"
        ),

        "currency": "INR",

        "payment_link_id": result.get(
            "payment_link_id"
        ),

        "short_url": result.get(
            "short_url"
        ),

        "opportunity": opportunity,
    }

#logging
AUDIT_FILE = os.path.join(
    ROOT_DIR,
    "audit_log.jsonl",
)


def read_audit_log(
    limit=30,
):
    """
    Read the most recent audit events.

    Malformed JSON lines are ignored so that a corrupted
    audit entry cannot crash the API.
    """

    if not os.path.exists(
        AUDIT_FILE
    ):
        return []

    events = []

    with open(
        AUDIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            try:

                event = json.loads(
                    line
                )

                event = sanitize_audit_event(
                    event
                )

                events.append(
                    event
                )

            except json.JSONDecodeError:
                continue

    return events[-limit:][::-1]


@app.get("/audit")
def get_audit():
    """
    Return the most recent sanitized audit events.
    """

    return {
        "events": read_audit_log()
    }


class GrowthRequest(BaseModel):
    """
    Growth execution request.

    Only Test Mode is accepted.
    """

    mode: Literal["test"] = "test"


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Razorpay Autonomous Growth Agent",
        "mode": "test",
    }


@app.post("/growth/execute")
def execute_growth(
    request: GrowthRequest,
):
    """
    Execute the autonomous growth workflow.

    Flow:

        Merchant Data
             ↓
        Growth Agent
             ↓
        Deterministic Policy
             ↓
        Razorpay Test Mode
             ↓
        Payment Link
             ↓
        Audit Trail
    """

    merchant_id = (
        "merchant-demo-"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
    )

    try:

        merchant_snapshot = (
            get_merchant_snapshot()
        )

        result = run_growth_workflow(
            merchant_snapshot,
            merchant_id=merchant_id,
            mode="test",
        )

        return normalize_growth_response(
            result
        )

    except Exception as exc:

        return {
            "success": False,
            "stage": "api",
            "reason": sanitize_error(
                exc
            ),
            "amount": None,
            "currency": "INR",
            "payment_link_id": None,
            "short_url": None,
            "opportunity": None,
        }


@app.post("/growth/simulate-failure")
def simulate_failure():
    """
    Run the SAME growth workflow while deliberately
    forcing the Payment Link execution boundary to fail.

    This demonstrates graceful failure handling and
    auditability.
    """

    import agents.growth_workflow as workflow

    original = (
        workflow.create_payment_link
    )

    def fake_failure(**kwargs):
        raise RuntimeError(
            "Controlled Razorpay Test Mode API failure "
            "for graceful demonstration."
        )

    workflow.create_payment_link = (
        fake_failure
    )

    try:

        merchant_snapshot = (
            get_merchant_snapshot()
        )

        result = run_growth_workflow(
            merchant_snapshot,
            merchant_id="failure-demo",
            mode="test",
        )

        return normalize_growth_response(
            result
        )

    except Exception as exc:

        return {
            "success": False,
            "stage": "create_payment_link",
            "reason": sanitize_error(
                exc
            ),
            "amount": None,
            "currency": "INR",
            "payment_link_id": None,
            "short_url": None,
            "opportunity": None,
        }

    finally:

        workflow.create_payment_link = (
            original
        )