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

def test_workflow_rejects_incomplete_payment_link(monkeypatch):

    # --------------------------------------------------
    # Force a valid growth opportunity
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "identify_growth_opportunity",
        lambda snapshot: {
            "opportunity": "bounded_upsell",
            "base_product": "Premium Annual Plan",
            "base_amount": 50000,
            "upsell_product": "Premium Support",
            "upsell_amount": 5000,
            "final_amount": 55000,
            "conversion_rate": 0.25,
            "upsell_percentage": 0.10,
            "expected_incremental_revenue": 1250,
            "confidence": 0.95,
            "reason": "Strong historical evidence.",
            "evidence": {},
            "reasoning": [],
            "evaluated_opportunities": [],
        },
    )

    # --------------------------------------------------
    # Allow the deterministic policy
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "validate_upsell",
        lambda opportunity, mode="test": {
            "allowed": True,
            "upsell_percentage": 0.10,
            "reason": "Allowed for test.",
        },
    )

    # --------------------------------------------------
    # Return an INVALID Razorpay response
    # Missing short_url
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "create_payment_link",
        lambda **kwargs: {
            "id": "plink_test_001",
            "amount": 5500000,
            "currency": "INR",
        },
    )

    result = growth_workflow.run_growth_workflow(
        {
            "products": [],
            "upsell_evidence": [],
        },
        merchant_id="verification-test",
        mode="test",
    )

    assert result["success"] is False

    assert result["stage"] == "outcome_verification"

    assert "short URL" in result["reason"]

def test_workflow_rejects_payment_link_with_wrong_amount(
    monkeypatch,
):

    # --------------------------------------------------
    # Force a valid growth opportunity
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "identify_growth_opportunity",
        lambda snapshot: {
            "opportunity": "bounded_upsell",
            "base_product": "Premium Annual Plan",
            "base_amount": 50000,
            "upsell_product": "Premium Support",
            "upsell_amount": 5000,
            "final_amount": 55000,
            "conversion_rate": 0.25,
            "upsell_percentage": 0.10,
            "expected_incremental_revenue": 1250,
            "confidence": 0.95,
            "reason": "Strong historical evidence.",
            "evidence": {},
            "reasoning": [],
            "evaluated_opportunities": [],
        },
    )

    # --------------------------------------------------
    # Allow policy
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "validate_upsell",
        lambda opportunity, mode="test": {
            "allowed": True,
            "upsell_percentage": 0.10,
            "reason": "Allowed for test.",
        },
    )

    # --------------------------------------------------
    # Razorpay returns WRONG amount
    # --------------------------------------------------

    monkeypatch.setattr(
        growth_workflow,
        "create_payment_link",
        lambda **kwargs: {
            "id": "plink_test_002",
            "short_url": "https://rzp.io/test",
            "amount": 99900,
            "currency": "INR",
        },
    )

    result = growth_workflow.run_growth_workflow(
        {
            "products": [],
            "upsell_evidence": [],
        },
        merchant_id="verification-test",
        mode="test",
    )

    assert result["success"] is False

    assert result["stage"] == "outcome_verification"

    assert "amount does not match" in result["reason"]