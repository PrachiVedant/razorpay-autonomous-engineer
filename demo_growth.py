from agents.growth_workflow import (
    run_growth_workflow,
)


MERCHANT_SNAPSHOT = {
    "products": [
        {
            "name": "Premium Annual Plan",
            "price": 50000,
            "sales": 100,
        },
        {
            "name": "Basic Plan",
            "price": 10000,
            "sales": 200,
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


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("RAZORPAY AI GROWTH DEMO")
    print("=" * 60)

    print()
    print("Merchant:")
    print("  Premium Annual Plan: ₹50,000")

    print()
    print("Agent opportunity:")
    print("  Premium Support: ₹5,000")

    print()
    print("Bound:")
    print("  Maximum upsell: 10%")

    print()
    print("Environment:")
    print("  Razorpay Test Mode")

    result = run_growth_workflow(
        MERCHANT_SNAPSHOT,
        merchant_id="demo-merchant",
        mode="test",
    )

    print()
    print("=" * 60)

    if result["success"]:

        print("PAYMENT LINK CREATED")
        print()
        print(
            f"Amount: ₹{result['amount']}"
        )

        print(
            f"Payment Link ID: "
            f"{result['payment_link_id']}"
        )

        print(
            f"Short URL: "
            f"{result['short_url']}"
        )

    else:

        print("GROWTH WORKFLOW FAILED")

        print(
            f"Stage: "
            f"{result['stage']}"
        )

        print(
            f"Reason: "
            f"{result['reason']}"
        )

    print("=" * 60)