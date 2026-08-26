import razorpay
from razorpay.errors import BadRequestError, ServerError, GatewayError

from config import get_env


class RazorpayActions:
    """
    Executes real (test-mode) Razorpay actions.

    Every call here represents a money action and must be
    logged by the caller (see agents/growth_loop.py).
    """

    def __init__(self):
        self.key_id = get_env(
            "RAZORPAY_KEY_ID",
            required=True,
        )

        self.key_secret = get_env(
            "RAZORPAY_KEY_SECRET",
            required=True,
        )

        self.client = razorpay.Client(
            auth=(self.key_id, self.key_secret)
        )

    def create_recovery_payment_link(self, order: dict) -> dict:
        """
        Create a test-mode payment link for an abandoned
        or failed order, to recover lost revenue.

        Raises:
            razorpay.errors.BadRequestError: invalid/malformed request.
                Not retried — caller should escalate to a human.
            razorpay.errors.ServerError: transient Razorpay-side error.
                Safe to retry once.
            razorpay.errors.GatewayError: transient gateway error.
                Safe to retry once.
        """

        payload = {
            "amount": int(order["amount"] * 100),  # rupees -> paise
            "currency": "INR",
            "description": f"Complete your order {order['order_id']}",
            "reference_id": order["order_id"],
            "notify": {
                "sms": False,
                "email": False,
            },
        }

        return self.client.payment_link.create(payload)