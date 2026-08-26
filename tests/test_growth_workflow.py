import agents.growth_workflow as growth_workflow


def test_growth_workflow_creates_payment_link(
    monkeypatch,
):

    merchant_snapshot = {
        "products": [
            {
                "name": "Premium Annual Plan",
                "price": 50000,
                "sales": 100,
            }
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

    monkeypatch.setattr(
        growth_workflow,
        "create_payment_link",
        lambda **kwargs: {
            "id": "plink_test_123",
            "short_url": (
                "https://rzp.io/i/test123"
            ),
        },
    )

    result = (
        growth_workflow.run_growth_workflow(
            merchant_snapshot
        )
    )

    assert result["success"] is True

    assert (
        result["payment_link_id"]
        == "plink_test_123"
    )

    assert (
        result["short_url"]
        == "https://rzp.io/i/test123"
    )

    assert result["amount"] == 55000


def test_growth_workflow_blocks_excessive_upsell(
    monkeypatch,
):

    merchant_snapshot = {
        "products": [
            {
                "name": "Premium Annual Plan",
                "price": 50000,
                "sales": 100,
            }
        ],
        "upsell_evidence": [
            {
                "base_product": (
                    "Premium Annual Plan"
                ),
                "upsell_product": (
                    "Premium Support"
                ),
                "upsell_price": 15000,
                "conversion_rate": 0.25,
            }
        ],
    }

    called = False

    def fake_payment_link(**kwargs):
        nonlocal called
        called = True

        return {}

    monkeypatch.setattr(
        growth_workflow,
        "create_payment_link",
        fake_payment_link,
    )

    result = (
        growth_workflow.run_growth_workflow(
            merchant_snapshot
        )
    )

    assert result["success"] is False

    assert (
        result["stage"]
        == "upsell_policy"
    )

    assert called is False