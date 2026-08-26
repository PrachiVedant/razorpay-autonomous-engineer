from merchant.tools import get_merchant_snapshot


def validate_opportunity(opportunity):
    """
    Validate an LLM-generated growth opportunity against
    deterministic merchant data.
    """

    snapshot = get_merchant_snapshot()

    opportunity_type = opportunity.get(
        "opportunity_type"
    )

    evidence = opportunity.get(
        "evidence",
        []
    )

    if not opportunity_type:
        return {
            "valid": False,
            "reason": "Missing opportunity type",
        }

    if not evidence:
        return {
            "valid": False,
            "reason": "No evidence provided",
        }

    if opportunity_type == "payment_conversion":

        card_metrics = snapshot[
            "payment_methods"
        ].get("card")

        if not card_metrics:
            return {
                "valid": False,
                "reason": "Card payment metrics unavailable",
            }

        card_failure_rate = card_metrics[
            "failure_rate"
        ]

        if card_failure_rate <= 0:
            return {
                "valid": False,
                "reason": (
                    "Card failure rate does not indicate an issue"
                ),
            }

        failed_payment_value = snapshot[
            "payments"
        ]["failed_payment_value"]

        if failed_payment_value <= 0:
            return {
                "valid": False,
                "reason": "No failed payment value detected",
            }

        # --------------------------------------------------
        # Validate evidence claims
        # --------------------------------------------------

        for item in evidence:

            metric = item.get("metric")
            value = str(item.get("value", ""))

            # ----------------------------------------------
            # Card failure rate
            # ----------------------------------------------

            if metric == "card_failure_rate":

                normalized_value = (
                    value.replace("%", "")
                    .strip()
                )

                try:
                    reported_rate = float(
                        normalized_value
                    )
                except ValueError:
                    return {
                        "valid": False,
                        "reason": (
                            "Card failure rate evidence "
                            "is not numeric"
                        ),
                    }

                if reported_rate != card_failure_rate:

                    return {
                        "valid": False,
                        "reason": (
                            "Card failure rate evidence "
                            "does not match merchant data"
                        ),
                    }

            # ----------------------------------------------
            # Failed payment value
            # ----------------------------------------------

            elif metric == "failed_payment_value":

                normalized_value = (
                    value.replace("₹", "")
                    .replace(",", "")
                    .strip()
                )

                try:
                    reported_value = float(
                        normalized_value
                    )
                except ValueError:
                    return {
                        "valid": False,
                        "reason": (
                            "Failed payment value evidence "
                            "is not numeric"
                        ),
                    }

                if reported_value != failed_payment_value:

                    return {
                        "valid": False,
                        "reason": (
                            "Failed payment value evidence "
                            "does not match merchant data"
                        ),
                    }

            # ----------------------------------------------
            # Unsupported evidence
            # ----------------------------------------------

            else:

                return {
                    "valid": False,
                    "reason": (
                        f"Unsupported evidence metric: "
                        f"{metric}"
                    ),
                }

        return {
            "valid": True,
            "reason": (
                "Opportunity supported by "
                "deterministic merchant data"
            ),
        }

    return {
        "valid": False,
        "reason": (
            f"Unsupported opportunity type: "
            f"{opportunity_type}"
        ),
    }