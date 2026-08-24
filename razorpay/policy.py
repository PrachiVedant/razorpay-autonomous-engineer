from typing import Any, Dict


PAYMENT_RISK_LEVELS = {
    "low": 0,
    "medium": 1,
    "high": 2,
}


ALLOWED_OPERATIONS = {
    "order",
    "create_payment",
    "verify_payment",
    "refund",
    "subscription",
    "webhook",
    "payment_link",
}


def validate_payment_plan(
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the Razorpay-related portion of an agent plan.
    """

    requires_razorpay = plan.get(
        "requires_razorpay",
        False,
    )

    if not requires_razorpay:
        return {
            "allowed": True,
            "requires_approval": False,
            "reason": "No Razorpay functionality detected.",
        }

    operation = plan.get(
        "payment_operation"
    )

    if operation not in ALLOWED_OPERATIONS:
        return {
            "allowed": False,
            "requires_approval": True,
            "reason": (
                f"Unknown Razorpay operation: {operation}"
            ),
        }

    risk_level = plan.get(
        "risk_level",
        "high",
    )

    if risk_level not in PAYMENT_RISK_LEVELS:
        return {
            "allowed": False,
            "requires_approval": True,
            "reason": (
                f"Unknown risk level: {risk_level}"
            ),
        }

    requires_approval = (
        plan.get(
            "requires_human_approval",
            True,
        )
        or risk_level in {"medium", "high"}
    )

    return {
        "allowed": True,
        "requires_approval": requires_approval,
        "reason": (
            f"Razorpay operation '{operation}' "
            f"classified as {risk_level} risk."
        ),
    }