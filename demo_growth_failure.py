import os

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

    os.environ[
        "RAZORPAY_DEMO_FORCE_FAILURE"
    ] = "1"

    print()
    print("=" * 60)
    print("RAZORPAY AI GROWTH FAILURE DEMO")
    print("=" * 60)

    print()
    print("Merchant:")
    print(
        "  Premium Annual Plan: ₹50,000"
    )

    print()
    print("Agent opportunity:")
    print(
        "  Premium Support: ₹5,000"
    )

    print()
    print("Bound:")
    print(
        "  Maximum upsell: 10%"
    )

    print()
    print("Environment:")
    print(
        "  Razorpay Test Mode"
    )

    print()
    print("Execution:")
    print(
        "  Controlled Razorpay API failure"
    )

    print()
    print("-" * 60)

    result = run_growth_workflow(
        MERCHANT_SNAPSHOT,
        merchant_id="demo-merchant-failure",
        mode="test",
    )

    print("-" * 60)

    print()

    if result["success"]:
        print(
            "UNEXPECTED SUCCESS"
        )

        print(
            f"Payment Link ID: "
            f"{result.get('payment_link_id')}"
        )

        print(
            f"Short URL: "
            f"{result.get('short_url')}"
        )

    else:

        print(
            "RAZORPAY FAILURE HANDLED GRACEFULLY"
        )

        print()
        print(
            f"Stage: "
            f"{result['stage']}"
        )

        print(
            f"Reason: "
            f"{result['reason']}"
        )

        print()
        print(
            "Agent action:"
        )

        print(
            "  Payment Link was NOT reported as successful."
        )

        print(
            "  Workflow stopped safely."
        )

        print(
            "  No fake short_url was returned."
        )

        print()
        print(
            "Audit trail:"
        )

        print(
            "  PAYMENT_LINK_CREATION_FAILED"
        )

        print(
            "  GROWTH_WORKFLOW_FAILED"
        )

    print()
    print("=" * 60)