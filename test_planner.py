from agents.planner import plan_issue
from agents.llm import OpenAIProvider


def test_planner():
    issue = {
        "title": "Add Razorpay premium payment endpoint",
        "body": """
Add a POST /payments/premium endpoint.

The endpoint should create a Razorpay order
for ₹499 and return the order details.
""",
    }

    structure = """
app/
├── main.py
├── routes/
│   └── payments.py
├── services/
│   └── payment_service.py
└── models/
    └── order.py
requirements.txt
"""

    fake_response = """
{
    "approach": "Create the premium payment endpoint using the existing payment service to create a Razorpay order.",
    "files_to_read": [
        "app/routes/payments.py",
        "app/services/payment_service.py"
    ],
    "requires_razorpay": true,
    "payment_operation": "order",
    "risk_level": "medium",
    "requires_human_approval": true
}
"""

    original_generate = OpenAIProvider.generate

    def mock_generate(self, prompt, model=None, max_tokens=None):
        return fake_response

    OpenAIProvider.generate = mock_generate

    try:
        plan = plan_issue(issue, structure)

        assert plan["requires_razorpay"] is True
        assert plan["payment_operation"] == "order"
        assert plan["risk_level"] == "medium"
        assert plan["requires_human_approval"] is True

    finally:
        OpenAIProvider.generate = original_generate