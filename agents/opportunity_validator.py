from merchant.analytics import (
    get_revenue_metrics,
    get_payment_metrics,
    get_payment_method_metrics,
)


def _normalize_value(value):
    """
    Normalize values coming from the LLM so that simple
    formatting differences do not cause false rejections.
    """
    if isinstance(value, str):
        return value.strip().replace(",", "").replace("₹", "").replace("%", "")

    return value


def _values_match(actual, claimed):
    """
    Compare deterministic ground-truth values with LLM claims.

    The LLM may return values such as:
        "100%"
        "1,000"
        "₹6796"

    while the merchant data contains:
        100
        1000
        6796
    """

    try:
        actual_normalized = float(_normalize_value(actual))
        claimed_normalized = float(_normalize_value(claimed))

        return actual_normalized == claimed_normalized

    except (TypeError, ValueError):
        return str(actual).strip().lower() == str(claimed).strip().lower()


def _get_ground_truth():
    """
    Build a deterministic snapshot from merchant data.

    The validator uses this snapshot instead of trusting
    the LLM-generated evidence.
    """

    revenue = get_revenue_metrics()
    payments = get_payment_metrics()
    payment_methods = get_payment_method_metrics()

    return {
        "card_failure_rate": payment_methods["card"]["failure_rate"],
        "upi_failure_rate": payment_methods["upi"]["failure_rate"],
        "failed_payment_value": revenue["abandoned_revenue"],
        "abandoned_orders": revenue["abandoned_orders"],
        "total_payments": payments["total_payments"],
        "failed_payments": payments["failed_payments"],
    }


def validate_opportunity(opportunity):
    """
    Deterministically validate an LLM-generated growth opportunity.

    The LLM is allowed to identify a hypothesis, but it cannot
    establish the truth of the evidence.

    Every evidence item must match merchant ground-truth data.

    Returns:
        {
            "valid": bool,
            "reason": str,
            "validated_evidence": [...]
        }
    """

    if not isinstance(opportunity, dict):
        return {
            "valid": False,
            "reason": "Opportunity must be a dictionary.",
            "validated_evidence": [],
        }

    evidence = opportunity.get("evidence")

    if not isinstance(evidence, list) or not evidence:
        return {
            "valid": False,
            "reason": "Opportunity contains no evidence.",
            "validated_evidence": [],
        }

    ground_truth = _get_ground_truth()

    validated_evidence = []

    for item in evidence:

        if not isinstance(item, dict):
            return {
                "valid": False,
                "reason": "Invalid evidence item.",
                "validated_evidence": validated_evidence,
            }

        metric = item.get("metric")
        claimed_value = item.get("value")

        if metric not in ground_truth:
            return {
                "valid": False,
                "reason": f"Unknown evidence metric: {metric}",
                "validated_evidence": validated_evidence,
            }

        actual_value = ground_truth[metric]

        if not _values_match(actual_value, claimed_value):
            return {
                "valid": False,
                "reason": (
                    f"Evidence mismatch for '{metric}': "
                    f"claimed={claimed_value}, "
                    f"actual={actual_value}"
                ),
                "validated_evidence": validated_evidence,
            }

        validated_evidence.append(
            {
                "metric": metric,
                "claimed_value": claimed_value,
                "actual_value": actual_value,
                "verified": True,
            }
        )

    return {
        "valid": True,
        "reason": "All opportunity evidence matches merchant ground truth.",
        "validated_evidence": validated_evidence,
    }