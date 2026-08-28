from rzp_gate.action_registry import (
    get_action,
    record_action,
    has_action,
    clear_actions,
)


def test_action_can_be_recorded():

    clear_actions()

    assert has_action("order_001") is False

    record_action(
        "order_001",
        {
            "action": "payment_link",
            "link_id": "plink_001",
        },
    )

    assert has_action("order_001") is True


def test_recorded_action_can_be_retrieved():

    clear_actions()

    action = {
        "action": "payment_link",
        "link_id": "plink_001",
    }

    record_action(
        "order_001",
        action,
    )

    result = get_action("order_001")

    assert result == action


def test_different_orders_have_independent_actions():

    clear_actions()

    record_action(
        "order_001",
        {
            "action": "payment_link",
            "link_id": "plink_001",
        },
    )

    assert has_action("order_001") is True

    assert has_action("order_002") is False