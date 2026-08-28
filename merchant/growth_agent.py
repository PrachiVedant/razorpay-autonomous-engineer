from typing import Any, Dict, List



# =========================================================
# Helpers
# =========================================================

def _validate_product(product: Dict[str, Any]) -> bool:
    """Return True when a product contains usable data."""

    name = product.get("name")
    price = product.get("price")
    sales = product.get("sales", 0)

    if not name:
        return False

    if not isinstance(price, (int, float)) or price <= 0:
        return False

    if not isinstance(sales, (int, float)) or sales < 0:
        return False

    return True


def _calculate_evidence_strength(
    conversion_rate: float,
    sales: float,
) -> str:
    """
    Classify the quality of historical evidence.

    This is deterministic and intentionally separate from
    the LLM. Financial facts should not be hallucinated.
    """

    if conversion_rate >= 0.20 and sales >= 50:
        return "strong"

    if conversion_rate >= 0.10 and sales >= 20:
        return "moderate"

    return "weak"


def _calculate_confidence(
    conversion_rate: float,
    sales: float,
) -> float:
    """
    Produce a deterministic confidence score between 0 and 1.

    Confidence is based on historical evidence, not on the
    payment execution itself.
    """

    # Conversion contribution.
    conversion_score = min(
        conversion_rate / 0.25,
        1.0,
    )

    # More historical purchases provide stronger evidence.
    volume_score = min(
        sales / 100,
        1.0,
    )

    confidence = (
        0.7 * conversion_score
        + 0.3 * volume_score
    )

    return round(
        min(max(confidence, 0.0), 1.0),
        2,
    )


# =========================================================
# Growth Opportunity Identification
# =========================================================

def identify_growth_opportunity(
    merchant_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Identify the strongest evidence-backed growth opportunity.

    The growth agent:

        1. Examines merchant products.
        2. Examines historical upsell evidence.
        3. Generates multiple candidate opportunities.
        4. Calculates expected incremental revenue.
        5. Scores the evidence.
        6. Selects the strongest opportunity.

    IMPORTANT:

        This function only PROPOSES a growth action.

        It does NOT:
            - approve the transaction
            - validate the financial policy
            - call Razorpay
            - create a Payment Link

    Those responsibilities belong to later stages of the
    growth workflow.
    """

    if not isinstance(
        merchant_snapshot,
        dict,
    ):
        raise ValueError(
            "Merchant snapshot must be a dictionary."
        )

    products = merchant_snapshot.get(
        "products",
        [],
    )

    evidence = merchant_snapshot.get(
        "upsell_evidence",
        [],
    )

    if not products:
        raise ValueError(
            "Merchant snapshot contains no products."
        )

    if not evidence:
        raise ValueError(
            "No upsell evidence available."
        )

    # =====================================================
    # 1. Validate merchant products
    # =====================================================

    valid_products = [
        product
        for product in products
        if _validate_product(product)
    ]

    if not valid_products:
        raise ValueError(
            "Merchant snapshot contains no valid products."
        )

    # Map product name -> product information.
    product_map = {
        product["name"]: product
        for product in valid_products
    }

    # =====================================================
    # 2. Generate candidate opportunities
    # =====================================================

    candidates: List[Dict[str, Any]] = []

    for item in evidence:

        base_product = item.get(
            "base_product"
        )

        upsell_product = item.get(
            "upsell_product"
        )

        upsell_price = item.get(
            "upsell_price"
        )

        conversion_rate = item.get(
            "conversion_rate",
            0,
        )

        # -----------------------------------------------
        # Validate evidence
        # -----------------------------------------------

        if base_product not in product_map:
            continue

        if not upsell_product:
            continue

        if not isinstance(
            upsell_price,
            (int, float),
        ):
            continue

        if upsell_price <= 0:
            continue

        if not isinstance(
            conversion_rate,
            (int, float),
        ):
            continue

        if not 0 <= conversion_rate <= 1:
            continue

        # -----------------------------------------------
        # Base product information
        # -----------------------------------------------

        product = product_map[
            base_product
        ]

        base_price = product[
            "price"
        ]

        sales = product.get(
            "sales",
            0,
        )

        # -----------------------------------------------
        # Financial calculations
        # -----------------------------------------------

        final_amount = (
            base_price
            + upsell_price
        )

        upsell_percentage = (
            upsell_price
            / base_price
        )

        expected_incremental_revenue = (
            upsell_price
            * conversion_rate
        )

        evidence_strength = (
            _calculate_evidence_strength(
                conversion_rate,
                sales,
            )
        )

        confidence = _calculate_confidence(
            conversion_rate,
            sales,
        )

        # -----------------------------------------------
        # Candidate
        # -----------------------------------------------

        candidates.append(
            {
                "base_product": base_product,
                "base_amount": base_price,

                "upsell_product": upsell_product,
                "upsell_amount": upsell_price,

                "final_amount": final_amount,

                "upsell_percentage": round(
                    upsell_percentage,
                    4,
                ),

                "conversion_rate": (
                    conversion_rate
                ),

                "historical_purchases": sales,

                "expected_incremental_revenue": round(
                    expected_incremental_revenue,
                    2,
                ),

                "evidence_strength": (
                    evidence_strength
                ),

                "confidence": confidence,
            }
        )

    # =====================================================
    # 3. Validate generated opportunities
    # =====================================================

    if not candidates:
        raise ValueError(
            "No valid growth opportunities found."
        )

    # =====================================================
    # 4. Rank opportunities
    # =====================================================

    # We prioritize expected incremental revenue,
    # while using evidence quality and confidence as
    # secondary signals.
    #
    # NOTE:
    # The 10% financial boundary is NOT checked here.
    # That belongs to the deterministic policy engine.

    candidates.sort(
        key=lambda candidate: (
            candidate[
                "expected_incremental_revenue"
            ],
            candidate[
                "confidence"
            ],
            candidate[
                "conversion_rate"
            ],
        ),
        reverse=True,
    )

    selected = candidates[0]

    # =====================================================
    # 5. Build reasoning
    # =====================================================

    base_product = selected[
        "base_product"
    ]

    upsell_product = selected[
        "upsell_product"
    ]

    conversion_rate = selected[
        "conversion_rate"
    ]

    historical_purchases = selected[
        "historical_purchases"
    ]

    expected_revenue = selected[
        "expected_incremental_revenue"
    ]

    evidence_strength = selected[
        "evidence_strength"
    ]

    confidence = selected[
        "confidence"
    ]

    reasoning = [
        (
            f"{base_product} generated "
            f"{historical_purchases:g} historical purchases."
        ),
        (
            f"{upsell_product} has a "
            f"{conversion_rate:.0%} historical "
            f"conversion rate."
        ),
        (
            f"The estimated incremental revenue "
            f"is ₹{expected_revenue:,.0f} per "
            f"eligible customer."
        ),
        (
            f"Historical evidence strength is "
            f"{evidence_strength}."
        ),
        (
            "The opportunity was selected because "
            "it has the highest expected incremental "
            "revenue among the available opportunities."
        ),
    ]

    # =====================================================
    # 6. Return selected opportunity
    # =====================================================

    return {
        "opportunity": "bounded_upsell",

        "base_product": base_product,
        "base_amount": selected[
            "base_amount"
        ],

        "upsell_product": upsell_product,
        "upsell_amount": selected[
            "upsell_amount"
        ],

        "final_amount": selected[
            "final_amount"
        ],

        "conversion_rate": conversion_rate,

        "upsell_percentage": selected[
            "upsell_percentage"
        ],

        "expected_incremental_revenue": (
            expected_revenue
        ),

        "confidence": confidence,

        "reason": (
            f"{upsell_product} was selected because "
            f"it has demonstrated {conversion_rate:.0%} "
            f"historical conversion with "
            f"{evidence_strength} evidence."
        ),

        "evidence": {
            "base_product": base_product,
            "upsell_product": upsell_product,
            "historical_purchases": (
                historical_purchases
            ),
            "conversion_rate": conversion_rate,
            "evidence_strength": (
                evidence_strength
            ),
            "expected_incremental_revenue": (
                expected_revenue
            ),
        },

        "reasoning": reasoning,

        # Useful for the React dashboard.
        "evaluated_opportunities": candidates,
    }