from merchant.analytics import (
    get_revenue_metrics,
    get_payment_metrics,
    get_payment_method_metrics,
)


def test_revenue_metrics():

    metrics = get_revenue_metrics()

    assert metrics["revenue"] == 3596

    assert metrics["abandoned_revenue"] == 6796

    assert metrics["abandoned_orders"] == 4


def test_payment_metrics():

    metrics = get_payment_metrics()

    assert metrics["total_payments"] == 8

    assert metrics["failed_payments"] == 4


def test_payment_method_metrics():

    metrics = get_payment_method_metrics()

    assert metrics["upi"]["failure_rate"] == 0

    assert metrics["card"]["failure_rate"] == 100

from merchant.tools import get_merchant_snapshot


def test_merchant_snapshot():

    snapshot = get_merchant_snapshot()

    assert snapshot["revenue"]["revenue"] == 3596

    assert snapshot["revenue"]["abandoned_revenue"] == 6796

    assert snapshot["payments"]["failed_payments"] == 4

    assert snapshot["payment_methods"]["card"]["failure_rate"] == 100

    assert snapshot["payment_methods"]["upi"]["failure_rate"] == 0

from agents.growth_agent import identify_growth_opportunity
import agents.growth_agent as growth_agent


def test_growth_agent_identifies_opportunity(monkeypatch):

    def fake_generate(
        self,
        prompt,
        model=None,
        max_tokens=None,
    ):
        return """
        {
            "opportunity_type": "payment_conversion",
            "severity": "high",
            "evidence": [
                {
                    "metric": "card_failure_rate",
                    "value": "100%",
                    "interpretation": "All card payments are failing."
                },
                {
                    "metric": "failed_payment_value",
                    "value": "6796",
                    "interpretation": "Failed payments represent significant transaction value."
                }
            ],
            "estimated_impact": "Potential recovery of ₹6796 in failed payment value.",
            "recommendation": "Investigate the card payment failure issue before taking action.",
            "confidence": 0.95
        }
        """

    monkeypatch.setattr(
        growth_agent.OpenAIProvider,
        "generate",
        fake_generate,
    )

    opportunity = identify_growth_opportunity()

    assert opportunity["opportunity_type"] == "payment_conversion"

    assert opportunity["severity"] == "high"

    assert opportunity["evidence"][0]["metric"] == "card_failure_rate"

    assert opportunity["confidence"] == 0.95



from agents.opportunity_validator import validate_opportunity


def test_valid_payment_opportunity():

    opportunity = {
        "opportunity_type": "payment_conversion",
        "severity": "high",
        "evidence": [
            {
                "metric": "card_failure_rate",
                "value": "100%",
                "interpretation": "Card payments are failing.",
            },
            {
                "metric": "failed_payment_value",
                "value": "6796",
                "interpretation": "Failed payments represent significant value.",
            },
        ],
        "estimated_impact": "Potential recovery of failed payments.",
        "recommendation": "Investigate card payment failures.",
        "confidence": 0.95,
    }

    result = validate_opportunity(
        opportunity
    )

    assert result["valid"] is True


def test_hallucinated_payment_evidence_is_rejected():

    opportunity = {
        "opportunity_type": "payment_conversion",
        "severity": "high",
        "evidence": [
            {
                "metric": "card_failure_rate",
                "value": "10%",
                "interpretation": "Card payments are failing.",
            }
        ],
        "estimated_impact": "Potential recovery.",
        "recommendation": "Investigate card payment failures.",
        "confidence": 0.99,
    }

    result = validate_opportunity(
        opportunity
    )

    assert result["valid"] is False