from typing import Dict, Optional


_ACTIONS: Dict[str, dict] = {}


def get_action(order_id: str) -> Optional[dict]:
    """
    Return the previously recorded action for an order.
    """

    return _ACTIONS.get(order_id)


def record_action(
    order_id: str,
    action: dict,
) -> None:
    """
    Record an action against an order.
    """

    _ACTIONS[order_id] = action


def has_action(order_id: str) -> bool:
    """
    Check whether an action has already been performed
    for this order.
    """

    return order_id in _ACTIONS


def clear_actions() -> None:
    """
    Clear registry.

    Primarily useful for tests.
    """

    _ACTIONS.clear()