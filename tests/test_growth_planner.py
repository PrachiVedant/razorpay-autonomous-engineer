from agents.growth_planner import create_growth_plan


def test_payment_conversion_creates_recovery_plan():

    opportunity = {
        "opportunity_type": "payment_conversion",
        "severity": "high",
        "confidence": 0.95,
        "evidence": [
            {
                "metric": "card_failure_rate",
                "value": "100%",
            }
        ],
    }

    plan = create_growth_plan(opportunity)

    assert plan["action"] == "recover_failed_payment"

    assert plan["payment_operation"] == "payment_link"

    assert "abandoned" in plan["target_statuses"]

    assert "failed" in plan["target_statuses"]

    assert plan["amount_source"] == "original_order"

    assert plan["risk_level"] == "medium"


def test_unsupported_opportunity_is_rejected():

    opportunity = {
        "opportunity_type": "unknown_action"
    }

    try:
        create_growth_plan(opportunity)
        assert False
    except ValueError:
        assert True