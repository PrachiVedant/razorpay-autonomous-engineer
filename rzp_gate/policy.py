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


# --------------------------------------------------
# Autonomous payment safety boundary
# --------------------------------------------------

MAX_AUTONOMOUS_AMOUNT = 2000


def validate_payment_plan(
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the Razorpay-related portion of an
    autonomous agent plan.

    Safety guarantees:

    1. Unknown Razorpay operations are rejected.
    2. Unknown risk levels are rejected.
    3. Monetary actions cannot exceed the autonomous
       amount limit.
    4. Medium/high-risk operations require approval.
    5. Explicit human approval requirements are respected.

    This function only validates the PLAN.

    It does not execute a Razorpay transaction.
    """

    requires_razorpay = plan.get(
        "requires_razorpay",
        False,
    )

    # --------------------------------------------------
    # No Razorpay operation
    # --------------------------------------------------

    if not requires_razorpay:

        return {
            "allowed": True,
            "requires_approval": False,
            "reason": (
                "No Razorpay functionality detected."
            ),
        }

    # --------------------------------------------------
    # Validate operation
    # --------------------------------------------------

    operation = plan.get(
        "payment_operation"
    )

    if operation not in ALLOWED_OPERATIONS:

        return {
            "allowed": False,
            "requires_approval": True,
            "reason": (
                f"Unknown Razorpay operation: "
                f"{operation}"
            ),
        }

    # --------------------------------------------------
    # Validate risk level
    # --------------------------------------------------

    risk_level = plan.get(
        "risk_level",
        "high",
    )

    if risk_level not in PAYMENT_RISK_LEVELS:

        return {
            "allowed": False,
            "requires_approval": True,
            "reason": (
                f"Unknown risk level: "
                f"{risk_level}"
            ),
        }

    # --------------------------------------------------
    # Validate monetary amount
    # --------------------------------------------------

    amount = plan.get(
        "amount"
    )

    # Only monetary operations need an amount.
    monetary_operations = {
        "order",
        "create_payment",
        "refund",
        "subscription",
        "payment_link",
    }

    if operation in monetary_operations:

        if amount is None:

            return {
                "allowed": False,
                "requires_approval": True,
                "reason": (
                    "Monetary Razorpay operation "
                    "requires an amount."
                ),
            }

        # Reject booleans because bool is a subclass of int.
        if isinstance(amount, bool):

            return {
                "allowed": False,
                "requires_approval": True,
                "reason": (
                    "Payment amount must be numeric."
                ),
            }

        if not isinstance(
            amount,
            (int, float),
        ):

            return {
                "allowed": False,
                "requires_approval": True,
                "reason": (
                    "Payment amount must be numeric."
                ),
            }

        if amount <= 0:

            return {
                "allowed": False,
                "requires_approval": True,
                "reason": (
                    "Payment amount must be "
                    "greater than zero."
                ),
            }

        # --------------------------------------------------
        # Autonomous safety boundary
        # --------------------------------------------------

        if amount > MAX_AUTONOMOUS_AMOUNT:

            return {
                "allowed": False,
                "requires_approval": True,
                "reason": (
                    f"Amount {amount} exceeds "
                    f"autonomous limit of "
                    f"{MAX_AUTONOMOUS_AMOUNT}."
                ),
            }

    # --------------------------------------------------
    # Determine human approval requirement
    # --------------------------------------------------

    requires_approval = (
        plan.get(
            "requires_human_approval",
            True,
        )
        or risk_level in {
            "medium",
            "high",
        }
    )

    # --------------------------------------------------
    # Successful validation
    # --------------------------------------------------

    return {
        "allowed": True,
        "requires_approval": requires_approval,
        "reason": (
            f"Razorpay operation '{operation}' "
            f"classified as {risk_level} risk "
            f"and within the autonomous safety boundary."
        ),
        "amount": amount,
        "max_autonomous_amount": (
            MAX_AUTONOMOUS_AMOUNT
        ),
    }