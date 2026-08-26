from merchant.growth_agent import (
    identify_growth_opportunity,
)


def test_identifies_high_value_product_upsell():

    merchant_snapshot = {
        "products": [
            {
                "name": "Basic Plan",
                "price": 10000,
                "sales": 200,
            },
            {
                "name": "Premium Annual Plan",
                "price": 50000,
                "sales": 100,
            },
        ],
        "upsell_evidence": [
            {
                "base_product": (
                    "Premium Annual Plan"
                ),
                "upsell_product": (
                    "Premium Support"
                ),
                "upsell_price": 5000,
                "conversion_rate": 0.25,
            }
        ],
    }

    result = (
        identify_growth_opportunity(
            merchant_snapshot
        )
    )

    assert (
        result["base_product"]
        == "Premium Annual Plan"
    )

    assert (
        result["upsell_product"]
        == "Premium Support"
    )

    assert result["base_amount"] == 50000

    assert result["upsell_amount"] == 5000

    assert result["final_amount"] == 55000