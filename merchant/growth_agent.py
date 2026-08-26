from typing import Any, Dict


def identify_growth_opportunity(
    merchant_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Identify a bounded upsell opportunity from merchant data.

    The agent proposes an opportunity.
    It does NOT create a payment or call Razorpay.

    Expected merchant_snapshot structure:

    {
        "products": [
            {
                "name": "Premium Annual Plan",
                "price": 50000,
                "sales": 100
            }
        ],
        "upsell_evidence": [
            {
                "base_product": "Premium Annual Plan",
                "upsell_product": "Premium Support",
                "upsell_price": 5000,
                "conversion_rate": 0.25
            }
        ]
    }
    """

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

    # --------------------------------------------------
    # Find the highest-value product
    # --------------------------------------------------

    high_value_product = max(
        products,
        key=lambda product: product.get(
            "price",
            0,
        ),
    )

    product_name = high_value_product.get(
        "name"
    )

    base_price = high_value_product.get(
        "price"
    )

    if not product_name:
        raise ValueError(
            "High-value product has no name."
        )

    if not isinstance(
        base_price,
        (int, float),
    ):
        raise ValueError(
            "Product price must be numeric."
        )

    if base_price <= 0:
        raise ValueError(
            "Product price must be positive."
        )

    # --------------------------------------------------
    # Find evidence for this product
    # --------------------------------------------------

    matching_evidence = [
        item
        for item in evidence
        if item.get("base_product")
        == product_name
    ]

    if not matching_evidence:
        raise ValueError(
            "No upsell evidence found for "
            f"{product_name}."
        )

    # Select the strongest evidence
    selected = max(
        matching_evidence,
        key=lambda item: item.get(
            "conversion_rate",
            0,
        ),
    )

    upsell_product = selected.get(
        "upsell_product"
    )

    upsell_price = selected.get(
        "upsell_price"
    )

    conversion_rate = selected.get(
        "conversion_rate",
        0,
    )

    if not upsell_product:
        raise ValueError(
            "Upsell evidence has no product name."
        )

    if not isinstance(
        upsell_price,
        (int, float),
    ):
        raise ValueError(
            "Upsell price must be numeric."
        )

    if upsell_price <= 0:
        raise ValueError(
            "Upsell price must be positive."
        )

    if not 0 <= conversion_rate <= 1:
        raise ValueError(
            "Invalid conversion rate."
        )

    final_amount = (
        base_price
        + upsell_price
    )

    return {
        "opportunity": (
            "bounded_upsell"
        ),
        "base_product": product_name,
        "base_amount": base_price,
        "upsell_product": upsell_product,
        "upsell_amount": upsell_price,
        "final_amount": final_amount,
        "conversion_rate": conversion_rate,
        "reason": (
            f"{upsell_product} has demonstrated "
            f"upsell evidence for customers buying "
            f"{product_name}."
        ),
        "evidence": {
            "base_product": product_name,
            "upsell_product": upsell_product,
            "conversion_rate": conversion_rate,
        },
    }