from typing import Dict, Any


def create_growth_plan(
    opportunity: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert a validated growth opportunity into
    a bounded action plan.

    This function does NOT execute anything.
    It only proposes an action.
    """

    if not opportunity:
        raise ValueError(
            "Opportunity is required."
        )

    opportunity_type = opportunity.get(
        "opportunity_type"
    )

    if opportunity_type == "payment_conversion":

        return {
            "action": "recover_failed_payment",
            "payment_operation": "payment_link",
            "target_statuses": [
                "abandoned",
                "failed",
            ],
            "amount_source": "original_order",
            "risk_level": "medium",
            "requires_approval": False,
            "reason": (
                "Recover abandoned or failed "
                "payments identified by the "
                "growth opportunity."
            ),
        }

    raise ValueError(
        f"Unsupported opportunity type: "
        f"{opportunity_type}"
    )