from guardrail.security_validator import SecurityValidator


def test_safe_code_passes():

    changes = [
        {
            "path": "payment.py",
            "content": """
import os

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is True
    assert result["violations"] == []


def test_hardcoded_secret_is_rejected():

    changes = [
        {
            "path": "payment.py",
            "content": """
RAZORPAY_KEY_SECRET = "fake_secret_123"
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is False


def test_secret_logging_is_rejected():

    changes = [
        {
            "path": "payment.py",
            "content": """
print("secret:", RAZORPAY_KEY_SECRET)
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is False


def test_dangerous_execution_is_rejected():

    changes = [
        {
            "path": "payment.py",
            "content": """
import os
os.system("something")
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is False