from rzp_gate.upsell_policy import (
    validate_upsell,
)


def test_valid_upsell_is_allowed():

    opportunity = {
        "operation": "payment_link",
        "base_amount": 50000,
        "upsell_amount": 5000,
        "final_amount": 55000,
        "evidence": {
            "conversion_rate": 0.25,
        },
    }

    result = validate_upsell(
        opportunity,
        mode="test",
    )

    assert result["allowed"] is True

    assert (
        result["upsell_percentage"]
        == 10.0
    )


def test_upsell_above_limit_is_blocked():

    opportunity = {
        "operation": "payment_link",
        "base_amount": 50000,
        "upsell_amount": 15000,
        "final_amount": 65000,
        "evidence": {
            "conversion_rate": 0.25,
        },
    }

    result = validate_upsell(
        opportunity,
        mode="test",
    )

    assert result["allowed"] is False

    assert (
        "10.0%"
        in result["reason"]
    )


def test_live_mode_is_blocked():

    opportunity = {
        "operation": "payment_link",
        "base_amount": 50000,
        "upsell_amount": 5000,
        "final_amount": 55000,
        "evidence": {
            "conversion_rate": 0.25,
        },
    }

    result = validate_upsell(
        opportunity,
        mode="live",
    )

    assert result["allowed"] is False


def test_missing_evidence_is_blocked():

    opportunity = {
        "operation": "payment_link",
        "base_amount": 50000,
        "upsell_amount": 5000,
        "final_amount": 55000,
        "evidence": None,
    }

    result = validate_upsell(
        opportunity,
        mode="test",
    )

    assert result["allowed"] is False