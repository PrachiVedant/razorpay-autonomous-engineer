from rzp_gate.policy import (
    validate_payment_plan,
    MAX_AUTONOMOUS_AMOUNT,
)


def test_low_risk_payment_within_limit_is_allowed():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": 500,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is True

    assert result["requires_approval"] is False

    assert (
        result["max_autonomous_amount"]
        == MAX_AUTONOMOUS_AMOUNT
    )


def test_payment_at_autonomous_limit_is_allowed():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": 2000,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is True


def test_payment_above_autonomous_limit_is_blocked():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": 2001,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False

    assert (
        "exceeds autonomous limit"
        in result["reason"]
    )


def test_zero_payment_is_blocked():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": 0,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False


def test_negative_payment_is_blocked():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": -500,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False


def test_high_risk_payment_requires_approval():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "refund",
        "amount": 1000,
        "risk_level": "high",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is True

    assert result["requires_approval"] is True


def test_unknown_operation_is_blocked():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "transfer_money",
        "amount": 500,
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False


def test_unknown_risk_level_is_blocked():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "amount": 500,
        "risk_level": "critical",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False


def test_monetary_operation_requires_amount():

    plan = {
        "requires_razorpay": True,
        "payment_operation": "create_payment",
        "risk_level": "low",
        "requires_human_approval": False,
    }

    result = validate_payment_plan(plan)

    assert result["allowed"] is False