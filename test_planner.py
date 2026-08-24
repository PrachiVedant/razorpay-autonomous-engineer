from agents.planner import plan_issue


issue = {
    "title": "Add Razorpay premium payment endpoint",
    "body": """
Add a POST /payments/premium endpoint.

The endpoint should create a Razorpay order
for ₹499 and return the order details.
"""
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


plan = plan_issue(
    issue,
    structure,
)


print("\nPlanner Output")
print("--------------------")

for key, value in plan.items():

    print(
        f"{key}: {value}"
    )