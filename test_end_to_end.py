from agents.planner import plan_issue
from agents.code_generator import generate_fix

from razorpay.policy import validate_payment_plan
from razorpay.validator import validate_changes


# --------------------------------------------------
# Simulated GitHub Issue
# --------------------------------------------------

ISSUE = {
    "title": "Add premium Razorpay payment endpoint",
    "body": """
Create a POST /payments/premium endpoint.

The endpoint should create a Razorpay order
for ₹499 and return the order details.

Use the existing payment service if possible.

Razorpay credentials must be loaded from
environment variables and must never be hardcoded.
"""
}


# --------------------------------------------------
# Simulated Repository
# --------------------------------------------------

REPO_STRUCTURE = """
app/
├── main.py
├── routes/
│   └── payments.py
├── services/
│   └── payment_service.py
├── models/
│   └── order.py

requirements.txt
"""


REPO_FILES = {

    "app/main.py": """
from fastapi import FastAPI

app = FastAPI()

from app.routes.payments import router

app.include_router(router)
""",

    "app/routes/payments.py": """
from fastapi import APIRouter

router = APIRouter()
""",

    "app/services/payment_service.py": """
def create_order():
    pass
""",

    "app/models/order.py": """
class Order:
    pass
""",

    "requirements.txt": """
fastapi
uvicorn
"""
}


def print_section(title):
    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():

    # ==================================================
    # 1. PLANNER
    # ==================================================

    print_section("1. PLANNER")

    plan = plan_issue(
        ISSUE,
        REPO_STRUCTURE,
    )

    print(
        f"Approach:\n{plan['approach']}"
    )

    print(
        f"\nFiles to read:\n"
        f"{plan['files_to_read']}"
    )

    print(
        f"\nRazorpay required: "
        f"{plan.get('requires_razorpay')}"
    )

    print(
        f"Payment operation: "
        f"{plan.get('payment_operation')}"
    )

    print(
        f"Risk level: "
        f"{plan.get('risk_level')}"
    )

    print(
        f"Human approval: "
        f"{plan.get('requires_human_approval')}"
    )

    # ==================================================
    # 2. ASSERT PLANNER DECISION
    # ==================================================

    print_section("2. PLANNER ASSERTIONS")

    assert plan["requires_razorpay"] is True

    assert plan["payment_operation"] in {
        "order",
        "create_payment",
    }

    assert plan["risk_level"] in {
        "medium",
        "high",
    }

    assert (
        plan["requires_human_approval"]
        is True
    )

    print("Planner assertions: PASS")

    # ==================================================
    # 3. RAZORPAY POLICY
    # ==================================================

    print_section("3. RAZORPAY POLICY")

    policy = validate_payment_plan(
        plan
    )

    print(
        f"Allowed: "
        f"{policy['allowed']}"
    )

    print(
        f"Approval required: "
        f"{policy['requires_approval']}"
    )

    print(
        f"Reason: "
        f"{policy['reason']}"
    )

    assert policy["allowed"] is True

    assert (
        policy["requires_approval"]
        is True
    )

    print(
        "\nPolicy assertions: PASS"
    )

    # ==================================================
    # 4. READ FILES
    # ==================================================

    print_section("4. REPOSITORY READING")

    file_contents = {}

    for filepath in plan["files_to_read"]:

        if filepath not in REPO_FILES:

            print(
                f"WARNING: {filepath} "
                f"not found in simulated repository"
            )

            continue

        file_contents[filepath] = (
            REPO_FILES[filepath]
        )

        print(
            f"Read: {filepath}"
        )

    # ==================================================
    # 5. CODE GENERATION
    # ==================================================

    print_section("5. CODE GENERATION")

    fix = generate_fix(
        ISSUE,
        plan,
        file_contents,
    )

    print(
        f"Generated {len(fix['changes'])} "
        f"file change(s)"
    )

    for change in fix["changes"]:

        print(
            f"\n--- {change['path']} ---"
        )

        print(
            change["content"]
        )

    # ==================================================
    # 6. GENERATOR ASSERTIONS
    # ==================================================

    print_section("6. GENERATOR ASSERTIONS")

    assert len(
        fix["changes"]
    ) > 0

    print(
        "Generated changes: PASS"
    )

    # ==================================================
    # 7. RAZORPAY SECURITY VALIDATION
    # ==================================================

    print_section(
        "7. RAZORPAY SECURITY VALIDATION"
    )

    validation = validate_changes(
        fix["changes"]
    )

    print(
        f"Valid: "
        f"{validation['valid']}"
    )

    if validation["errors"]:

        print("\nErrors:")

        for error in validation["errors"]:

            print(
                f"  - {error}"
            )

    assert validation["valid"] is True

    print(
        "\nSecurity validation: PASS"
    )

    # ==================================================
    # 8. SECURITY ASSERTION
    # ==================================================

    print_section(
        "8. CREDENTIAL SAFETY CHECK"
    )

    combined_content = "\n".join(
        change["content"]
        for change in fix["changes"]
    )

    assert "rzp_live_" not in combined_content
    assert "rzp_test_" not in combined_content
    assert "sk_live_" not in combined_content
    assert "sk_test_" not in combined_content

    assert (
        "RAZORPAY_KEY_SECRET"
        in combined_content
    )

    print(
        "No hardcoded Razorpay credentials: PASS"
    )

    # ==================================================
    # 9. HUMAN APPROVAL DECISION
    # ==================================================

    print_section(
        "9. HUMAN APPROVAL GATE"
    )

    if policy["requires_approval"]:

        print(
            "Payment change detected."
        )

        print(
            f"Risk level: "
            f"{plan['risk_level']}"
        )

        print(
            "Human approval would be required "
            "before applying these changes."
        )

        print(
            "Approval gate: PASS"
        )

    # ==================================================
    # 10. FINAL RESULT
    # ==================================================

    print_section(
        "END-TO-END RESULT"
    )

    print(
        "PASS"
    )

    print(
        """
Issue
  ↓
Planner
  ↓
Razorpay Detection
  ↓
Risk Classification
  ↓
Policy
  ↓
Repository Reading
  ↓
Code Generation
  ↓
Security Validation
  ↓
Human Approval Gate
"""
    )

    print(
        "Autonomous Razorpay coding pipeline "
        "completed successfully."
    )


if __name__ == "__main__":
    main()