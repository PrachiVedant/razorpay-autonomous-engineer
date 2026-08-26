from typing import Any, Dict
from uuid import uuid4

from agents.audit import audit_logger

from merchant.growth_agent import (
    identify_growth_opportunity,
)

from rzp_gate.upsell_policy import (
    validate_upsell,
)

from rzp_tools.payment_link import (
    create_payment_link,
)


def run_growth_workflow(
    merchant_snapshot: Dict[str, Any],
    *,
    merchant_id: str = "demo-merchant",
    mode: str = "test",
) -> Dict[str, Any]:
    """
    Execute the bounded merchant growth workflow.

    Flow:

        Merchant Data
             ↓
        Growth Opportunity
             ↓
        Upsell Proposal
             ↓
        Deterministic Policy
             ↓
        Razorpay Test Mode
             ↓
        Payment Link
             ↓
        Audit

    Safety properties:

        1. The growth agent only proposes.
        2. The upsell is deterministically bounded.
        3. Only Test Mode is allowed.
        4. Razorpay execution is isolated.
        5. Razorpay failures are caught.
        6. Failed money actions never become
           successful results.
        7. Important money-action boundaries
           are written to the audit trail.
    """

    # ==================================================
    # 1. Identify growth opportunity
    # ==================================================

    try:

        opportunity = identify_growth_opportunity(
            merchant_snapshot
        )

    except Exception as error:

        audit_logger.log(
            "GROWTH_WORKFLOW_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "stage": "opportunity_identification",
                "reason": str(error),
            },
        )

        return {
            "success": False,
            "stage": "opportunity_identification",
            "reason": str(error),
        }

    audit_logger.log(
        "GROWTH_OPPORTUNITY_IDENTIFIED",
        status="INFO",
        details={
            "merchant_id": merchant_id,
            "opportunity": opportunity[
                "opportunity"
            ],
        },
    )

    # ==================================================
    # 2. Upsell proposed
    # ==================================================

    audit_logger.log(
        "UPSELL_PROPOSED",
        status="INFO",
        details={
            "merchant_id": merchant_id,
            "base_product": opportunity[
                "base_product"
            ],
            "upsell_product": opportunity[
                "upsell_product"
            ],
            "base_amount": opportunity[
                "base_amount"
            ],
            "upsell_amount": opportunity[
                "upsell_amount"
            ],
            "final_amount": opportunity[
                "final_amount"
            ],
        },
    )

    # ==================================================
    # 3. Deterministic upsell policy
    # ==================================================

    policy_input = {
        **opportunity,
        "operation": "payment_link",
    }

    policy_result = validate_upsell(
        policy_input,
        mode=mode,
    )

    if not policy_result["allowed"]:

        audit_logger.log(
            "UPSELL_POLICY_REJECTED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "reason": policy_result[
                    "reason"
                ],
                "upsell_percentage": (
                    policy_result[
                        "upsell_percentage"
                    ]
                ),
            },
        )

        audit_logger.log(
            "GROWTH_WORKFLOW_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "stage": "upsell_policy",
                "reason": policy_result[
                    "reason"
                ],
            },
        )

        return {
            "success": False,
            "stage": "upsell_policy",
            "reason": policy_result[
                "reason"
            ],
            "policy": policy_result,
        }

    audit_logger.log(
        "UPSELL_POLICY_VALIDATED",
        status="PASS",
        details={
            "merchant_id": merchant_id,
            "upsell_percentage": (
                policy_result[
                    "upsell_percentage"
                ]
            ),
        },
    )

    # ==================================================
    # 4. Prepare Payment Link request
    # ==================================================

    amount = int(
        opportunity["final_amount"]
    )

    description = (
        f"{opportunity['base_product']} "
        f"+ "
        f"{opportunity['upsell_product']}"
    )

    # --------------------------------------------------
    # Generate a unique reference ID.
    #
    # Razorpay does not allow reusing the same
    # reference_id for another Payment Link.
    #
    # Example:
    #
    # demo-merchant-growth-upsell-a81f3c21
    # --------------------------------------------------

    reference_id = (
        f"{merchant_id}-"
        f"growth-upsell-"
        f"{uuid4().hex[:8]}"
    )

    audit_logger.log(
        "PAYMENT_LINK_REQUESTED",
        status="INFO",
        details={
            "merchant_id": merchant_id,
            "amount": amount,
            "currency": "INR",
            "reference_id": reference_id,
            "mode": mode,
        },
    )

    # ==================================================
    # 5. Execute Razorpay Payment Link
    # ==================================================

    try:

        payment_link = create_payment_link(
            amount=amount,
            description=description,
            reference_id=reference_id,
        )

    except Exception as error:

        # --------------------------------------------------
        # Razorpay failure is handled gracefully.
        #
        # No fake Payment Link is returned.
        # No success event is recorded.
        # --------------------------------------------------

        audit_logger.log(
            "PAYMENT_LINK_CREATION_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "reason": str(error),
                "mode": mode,
                "reference_id": reference_id,
            },
        )

        audit_logger.log(
            "GROWTH_WORKFLOW_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "stage": "payment_link_creation",
                "reason": str(error),
                "recovery_action": (
                    "Stopped safely without reporting "
                    "a payment link."
                ),
            },
        )

        return {
            "success": False,
            "stage": "payment_link_creation",
            "reason": str(error),
        }

    # ==================================================
    # 6. Validate Razorpay response
    # ==================================================

    payment_link_id = payment_link.get(
        "id"
    )

    short_url = payment_link.get(
        "short_url"
    )

    # --------------------------------------------------
    # Never claim success without both values.
    # --------------------------------------------------

    if not payment_link_id or not short_url:

        reason = (
            "Razorpay returned an incomplete "
            "Payment Link response."
        )

        audit_logger.log(
            "PAYMENT_LINK_CREATION_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "reason": reason,
                "mode": mode,
                "reference_id": reference_id,
            },
        )

        audit_logger.log(
            "GROWTH_WORKFLOW_FAILED",
            status="FAIL",
            details={
                "merchant_id": merchant_id,
                "stage": (
                    "payment_link_response_validation"
                ),
                "reason": reason,
                "recovery_action": (
                    "Stopped safely without reporting "
                    "an incomplete payment link."
                ),
            },
        )

        return {
            "success": False,
            "stage": (
                "payment_link_response_validation"
            ),
            "reason": reason,
        }

    # ==================================================
    # 7. Payment Link successfully created
    # ==================================================

    audit_logger.log(
        "PAYMENT_LINK_CREATED",
        status="PASS",
        details={
            "merchant_id": merchant_id,
            "payment_link_id": payment_link_id,
            "reference_id": reference_id,
            "amount": amount,
            "mode": mode,
        },
    )

    # ==================================================
    # 8. Workflow completed
    # ==================================================

    audit_logger.log(
        "GROWTH_WORKFLOW_COMPLETED",
        status="PASS",
        details={
            "merchant_id": merchant_id,
            "payment_link_id": payment_link_id,
            "amount": amount,
        },
    )

    return {
        "success": True,
        "stage": "completed",
        "payment_link_id": payment_link_id,
        "short_url": short_url,
        "amount": amount,
        "currency": "INR",
        "opportunity": opportunity,
    }
