import json
import pytest
from razorpay.errors import BadRequestError, ServerError, GatewayError
from rzp_gate.action_registry import clear_actions
import agents.growth_loop as growth_loop

@pytest.fixture(autouse=True)
def reset_action_registry():
    clear_actions()
    yield
    clear_actions()


def fake_opportunity():
    return {
        "opportunity_type": "payment_conversion",
        "severity": "high",
        "evidence": [
            {
                "metric": "card_failure_rate",
                "value": "100%",
                "interpretation": "All card payments are failing.",
            },
            {
                "metric": "failed_payment_value",
                "value": "6796",
                "interpretation": "Failed payments represent significant transaction value.",
            },
        ],
        "estimated_impact": "Potential recovery of failed payment value.",
        "recommendation": "Recover failed payments.",
        "confidence": 0.95,
    }


def fake_validation():
    return {
        "valid": True,
        "reason": "Evidence matches merchant data.",
    }


def fake_order():
    return {
        "order_id": "order_test_001",
        "amount": 499,
        "status": "abandoned",
    }


def test_payment_link_failure_is_logged_and_escalated(monkeypatch, tmp_path):


    monkeypatch.setattr(
        growth_loop,
        "identify_growth_opportunity",
        lambda: fake_opportunity(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_opportunity",
        lambda opportunity: fake_validation(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
            "reason": "Allowed for test.",
        },
    )

    monkeypatch.setattr(
        growth_loop,
        "get_orders",
        lambda: [fake_order()],
    )

    class FakeActions:

        def create_recovery_payment_link(self, order):

            raise BadRequestError(
                "Invalid payment link request"
            )

    monkeypatch.setattr(
        growth_loop,
        "RazorpayActions",
        FakeActions,
    )

    result = growth_loop.run_growth_cycle()

    assert result["status"] == "failed"

    assert result["escalated"] is True

    assert "Invalid payment link request" in result["reason"]

def test_transient_failure_retries_once_and_succeeds(monkeypatch):

    monkeypatch.setattr(
        growth_loop,
        "identify_growth_opportunity",
        lambda: fake_opportunity(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_opportunity",
        lambda opportunity: fake_validation(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
            "reason": "Allowed for test.",
        },
    )

    monkeypatch.setattr(
        growth_loop,
        "get_orders",
        lambda: [fake_order()],
    )

    class FakeActions:

        def __init__(self):
            self.attempts = 0

        def create_recovery_payment_link(self, order):

            self.attempts += 1

            if self.attempts == 1:
                raise ServerError(
                    "Temporary Razorpay server failure"
                )

            return {
                "id": "plink_test_001",
                "short_url": "https://rzp.io/test",
            }

    monkeypatch.setattr(
        growth_loop,
        "RazorpayActions",
        FakeActions,
    )

    result = growth_loop.run_growth_cycle()

    assert result["status"] == "completed"

    assert result["attempts"] == 2

    assert result["payment_link"]["id"] == "plink_test_001"

def test_transient_failure_retry_also_fails(monkeypatch):

    monkeypatch.setattr(
        growth_loop,
        "identify_growth_opportunity",
        lambda: fake_opportunity(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_opportunity",
        lambda opportunity: fake_validation(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
            "reason": "Allowed for test.",
        },
    )

    monkeypatch.setattr(
        growth_loop,
        "get_orders",
        lambda: [fake_order()],
    )

    class FakeActions:

        def __init__(self):
            self.attempts = 0

        def create_recovery_payment_link(self, order):

            self.attempts += 1

            raise ServerError(
                "Razorpay server unavailable"
            )

    monkeypatch.setattr(
        growth_loop,
        "RazorpayActions",
        FakeActions,
    )

    result = growth_loop.run_growth_cycle()

    assert result["status"] == "failed"

    assert result["attempts"] == 2

    assert "Razorpay server unavailable" in result["reason"]


def test_duplicate_payment_link_is_prevented(monkeypatch):

    clear_actions()

    monkeypatch.setattr(
        growth_loop,
        "identify_growth_opportunity",
        lambda: fake_opportunity(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_opportunity",
        lambda opportunity: fake_validation(),
    )

    monkeypatch.setattr(
        growth_loop,
        "validate_payment_plan",
        lambda plan: {
            "allowed": True,
            "requires_approval": False,
            "reason": "Allowed for test.",
        },
    )

    monkeypatch.setattr(
        growth_loop,
        "get_orders",
        lambda: [fake_order()],
    )

    calls = []

    class FakeActions:

        def create_recovery_payment_link(self, order):

            calls.append(order["order_id"])

            return {
                "id": "plink_duplicate_test",
                "short_url": "https://rzp.io/test",
            }

    monkeypatch.setattr(
        growth_loop,
        "RazorpayActions",
        FakeActions,
    )

    # First cycle
    first_result = growth_loop.run_growth_cycle()

    assert first_result["status"] == "completed"

    assert len(calls) == 1

    # Second cycle
    second_result = growth_loop.run_growth_cycle()

    assert second_result["status"] == "already_processed"

    # Razorpay action must NOT run again
    assert len(calls) == 1