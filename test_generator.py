from agents.code_generator import generate_fix
from agents.llm import OpenAIProvider


def test_generator():
    issue = {
        "title": "Add Razorpay premium order endpoint",
        "body": """
Create a POST /payments/premium endpoint.

The endpoint should create a Razorpay order
for ₹499 and return the order details.

Do not hardcode credentials.
""",
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

    fake_response = """
{
    "changes": [
        {
            "path": "app/routes/payments.py",
            "content": "from fastapi import APIRouter\\n\\nrouter = APIRouter()"
        }
    ],
    "pr_description": "Added the premium payment endpoint using the existing payment architecture."
}
"""

    original_generate = OpenAIProvider.generate

    def mock_generate(self, prompt, model=None, max_tokens=None):
        return fake_response

    OpenAIProvider.generate = mock_generate

    try:
        result = generate_fix(
            issue,
            plan,
            file_contents,
        )

        assert "changes" in result
        assert "pr_description" in result
        assert isinstance(result["changes"], list)

    finally:
        OpenAIProvider.generate = original_generate