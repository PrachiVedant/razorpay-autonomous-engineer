# tests/test_growth_loop_failure.py
from unittest.mock import patch
import agents.growth_loop as growth_loop

def test_payment_link_failure_is_logged_and_escalated(monkeypatch, tmp_path):
    # force policy through, force a bad-request-style failure
    monkeypatch.setattr(growth_loop, "validate_payment_plan",
        lambda plan: {"allowed": True, "requires_approval": False})
    # ... mock create_recovery_payment_link to raise, assert PAYMENT_LINK_FAILED in audit log