from rzp_gate.validator import validate_changes


safe_changes = [
    {
        "path": "payments.py",
        "content": """
import os

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
"""
    }
]


unsafe_changes = [
    {
        "path": "payments.py",
        "content": """
RAZORPAY_KEY_ID = "rzp_test_123456"
RAZORPAY_KEY_SECRET = "my-super-secret-key"
"""
    }
]


print("\nSAFE CHANGE")
print("--------------------")

print(
    validate_changes(
        safe_changes
    )
)


print("\nUNSAFE CHANGE")
print("--------------------")

print(
    validate_changes(
        unsafe_changes
    )
)