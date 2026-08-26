from guardrail.security_validator import SecurityValidator


def test_security_gate_blocks_hardcoded_razorpay_secret():

    changes = [
        {
            "path": "payment.py",
            "content": """
RAZORPAY_KEY_SECRET = "rzp_test_fake_secret"
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is False

    assert any(
        "hardcoded secret" in violation.lower()
        for violation in result["violations"]
    )


def test_security_gate_blocks_dangerous_execution():

    changes = [
        {
            "path": "payment.py",
            "content": """
import os

os.system("rm -rf something")
"""
        }
    ]

    validator = SecurityValidator()

    result = validator.validate_changes(
        changes
    )

    assert result["valid"] is False

    assert any(
        "dangerous code" in violation.lower()
        for violation in result["violations"]
    )