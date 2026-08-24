from agents.code_generator import generate_fix


issue = {
    "title": "Add Razorpay premium order endpoint",
    "body": """
Create a POST /payments/premium endpoint.

The endpoint should create a Razorpay order
for ₹499 and return the order details.

Do not hardcode credentials.
"""
}


plan = {
    "approach": (
        "Create a premium payment endpoint that uses "
        "the existing payment service to create a "
        "Razorpay order."
    ),
    "files_to_read": [
        "app/routes/payments.py",
        "app/services/payment_service.py",
    ],
    "requires_razorpay": True,
    "payment_operation": "order",
    "risk_level": "medium",
    "requires_human_approval": True,
}


file_contents = {
    "app/routes/payments.py": """
from fastapi import APIRouter

router = APIRouter()
""",

    "app/services/payment_service.py": """
def create_order():
    pass
""",
}


fix = generate_fix(
    issue,
    plan,
    file_contents,
)


print("\nGenerated Changes")
print("--------------------")

for change in fix["changes"]:

    print(
        f"\nFILE: {change['path']}"
    )

    print(
        change["content"]
    )


print("\nPR Description")
print("--------------------")

print(
    fix["pr_description"]
)