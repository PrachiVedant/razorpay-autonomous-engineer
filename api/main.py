import json
import os
import re
import sys
from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
# PROJECT SETUP
# =========================================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =========================================================
# APPLICATION IMPORTS
# =========================================================

from agents.growth_workflow import run_growth_workflow
from merchant.tools import get_merchant_snapshot


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Razorpay Autonomous Growth Agent",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# SECURITY HELPERS
# =========================================================

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


# =========================================================
# RESPONSE NORMALIZATION
# =========================================================

def normalize_growth_response(
    result,
):
    """
    Normalize the internal growth workflow result into
    a stable API response contract.

    The React frontend can rely on these fields existing
    regardless of whether the workflow succeeds or fails.
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

        "opportunity": result.get(
            "opportunity"
        ),
    }


# =========================================================
# AUDIT LOG
# =========================================================

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


# =========================================================
# AUDIT ENDPOINT
# =========================================================

@app.get("/audit")
def get_audit():
    """
    Return the most recent sanitized audit events.
    """

    return {
        "events": read_audit_log()
    }


# =========================================================
# REQUEST MODELS
# =========================================================

class GrowthRequest(BaseModel):
    """
    Growth execution request.

    Only Test Mode is accepted.

    Pydantic validation intentionally rejects values such as:

        live
        production
        development

    with HTTP 422.
    """

    mode: Literal["test"] = "test"


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Razorpay Autonomous Growth Agent",
        "mode": "test",
    }


# =========================================================
# EXECUTE GROWTH WORKFLOW
# =========================================================

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


# =========================================================
# SIMULATE CONTROLLED FAILURE
# =========================================================

@app.post("/growth/simulate-failure")
def simulate_failure():
    """
    Run the SAME growth workflow while deliberately
    forcing the Payment Link execution boundary to fail.

    This endpoint demonstrates graceful failure handling
    and the corresponding audit trail.
    """

    import agents.growth_workflow as workflow

    # -----------------------------------------------------
    # Preserve the real implementation
    # -----------------------------------------------------

    original = (
        workflow.create_payment_link
    )

    # -----------------------------------------------------
    # Controlled failure
    # -----------------------------------------------------

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

        # -------------------------------------------------
        # ALWAYS restore the real implementation.
        # -------------------------------------------------

        workflow.create_payment_link = (
            original
        )