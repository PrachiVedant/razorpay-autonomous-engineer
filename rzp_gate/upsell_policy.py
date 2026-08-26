from typing import Any, Dict


MAX_UPSELL_PERCENT = 10.0

MAX_PAYMENT_AMOUNT = 100000

ALLOWED_OPERATION = "payment_link"

REQUIRED_MODE = "test"


def validate_upsell(
    opportunity: Dict[str, Any],
    *,
    mode: str = "test",
) -> Dict[str, Any]:
    """
    Deterministically validate a proposed merchant upsell.

    The agent cannot override these rules.

    Rules:

    1. Operation must be payment_link.
    2. Base amount must be positive.
    3. Upsell amount must be positive.
    4. Upsell cannot exceed 10% of base amount.
    5. Final payment cannot exceed ₹100,000.
    6. Only Razorpay Test Mode is allowed.
    7. Evidence must exist.
    """

    errors = []

    operation = opportunity.get(
        "operation",
        ALLOWED_OPERATION,
    )

    if operation != ALLOWED_OPERATION:
        errors.append(
            "Only payment_link operation "
            "is allowed."
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

    evidence = opportunity.get(
        "evidence"
    )

    # --------------------------------------------------
    # Amount validation
    # --------------------------------------------------

    if not isinstance(
        base_amount,
        (int, float),
    ):
        errors.append(
            "Base amount must be numeric."
        )

    elif base_amount <= 0:
        errors.append(
            "Base amount must be positive."
        )

    if not isinstance(
        upsell_amount,
        (int, float),
    ):
        errors.append(
            "Upsell amount must be numeric."
        )

    elif upsell_amount <= 0:
        errors.append(
            "Upsell amount must be positive."
        )

    if not isinstance(
        final_amount,
        (int, float),
    ):
        errors.append(
            "Final amount must be numeric."
        )

    elif final_amount <= 0:
        errors.append(
            "Final amount must be positive."
        )

    # --------------------------------------------------
    # Bounded upsell
    # --------------------------------------------------

    if (
        isinstance(base_amount, (int, float))
        and isinstance(upsell_amount, (int, float))
        and base_amount > 0
    ):

        upsell_percentage = (
            upsell_amount
            / base_amount
            * 100
        )

        if (
            upsell_percentage
            > MAX_UPSELL_PERCENT
        ):
            errors.append(
                "Upsell exceeds the maximum "
                f"allowed limit of "
                f"{MAX_UPSELL_PERCENT}%."
            )

    else:
        upsell_percentage = None

    # --------------------------------------------------
    # Final payment amount
    # --------------------------------------------------

    if (
        isinstance(final_amount, (int, float))
        and final_amount
        > MAX_PAYMENT_AMOUNT
    ):
        errors.append(
            "Final payment amount exceeds "
            f"₹{MAX_PAYMENT_AMOUNT}."
        )

    # --------------------------------------------------
    # Evidence
    # --------------------------------------------------

    if not evidence:
        errors.append(
            "Upsell evidence is required."
        )

    # --------------------------------------------------
    # Test mode
    # --------------------------------------------------

    if mode != REQUIRED_MODE:
        errors.append(
            "Payment Link creation is restricted "
            "to Razorpay Test Mode."
        )

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    if errors:

        return {
            "allowed": False,
            "requires_approval": True,
            "upsell_percentage": (
                upsell_percentage
            ),
            "reason": (
                "; ".join(errors)
            ),
            "errors": errors,
        }

    return {
        "allowed": True,
        "requires_approval": False,
        "upsell_percentage": (
            upsell_percentage
        ),
        "reason": (
            "Upsell is within the configured "
            "10% boundary and Test Mode policy."
        ),
        "errors": [],
    }