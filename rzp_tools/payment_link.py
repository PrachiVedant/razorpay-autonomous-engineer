import os
from typing import Any, Dict

import razorpay
from dotenv import load_dotenv


# Load .env automatically.
#
# This is safe because the actual secret values are never
# written to the audit log or returned by this module.
load_dotenv()


class PaymentLinkClient:
    """
    Razorpay Test Mode Payment Link client.

    Responsibilities:
        - Load Razorpay Test Mode credentials.
        - Ensure only Test Mode is used.
        - Create a real Razorpay Payment Link.
        - Provide a deterministic failure switch for the demo.

    The growth agent proposes.
    The policy validates.
    This class executes.
    """

    def __init__(self):

        self.mode = os.getenv(
            "RAZORPAY_MODE",
            "test",
        ).lower()

        # --------------------------------------------------
        # Live mode is NEVER allowed by this demo.
        # --------------------------------------------------

        if self.mode != "test":
            raise RuntimeError(
                "Payment Link client only supports "
                "Razorpay Test Mode."
            )

        key_id = os.getenv(
            "RAZORPAY_KEY_ID"
        )

        key_secret = os.getenv(
            "RAZORPAY_KEY_SECRET"
        )

        if not key_id:
            raise RuntimeError(
                "RAZORPAY_KEY_ID is not configured."
            )

        if not key_secret:
            raise RuntimeError(
                "RAZORPAY_KEY_SECRET is not configured."
            )

        self.client = razorpay.Client(
            auth=(
                key_id,
                key_secret,
            )
        )

    def create_payment_link(
        self,
        *,
        amount: int,
        description: str,
        reference_id: str,
    ) -> Dict[str, Any]:
        """
        Create a Razorpay Test Mode Payment Link.

        amount:
            Amount in rupees.

        The Razorpay API receives the amount in paise.

        A controlled failure can be enabled for the final
        failure demo with:

            RAZORPAY_DEMO_FORCE_FAILURE=1

        This failure happens at the execution boundary,
        allowing the workflow's real error handling and
        audit trail to be demonstrated safely.
        """

        # --------------------------------------------------
        # Validate amount
        # --------------------------------------------------

        if amount <= 0:
            raise ValueError(
                "Payment amount must be positive."
            )

        # --------------------------------------------------
        # Controlled demo failure
        # --------------------------------------------------
        #
        # IMPORTANT:
        # This does NOT create a fake successful payment link.
        #
        # It deliberately raises an execution failure so that
        # the workflow handles the same type of exception that
        # a Razorpay API/network failure would produce.
        #
        # This is only enabled explicitly for the failure demo.
        # --------------------------------------------------

        force_failure = os.getenv(
            "RAZORPAY_DEMO_FORCE_FAILURE",
            "0",
        ).lower()

        if force_failure in {
            "1",
            "true",
            "yes",
        }:
            raise RuntimeError(
                "Controlled Razorpay Test Mode API failure "
                "for graceful-failure demonstration."
            )

        # --------------------------------------------------
        # Convert rupees → paise
        # --------------------------------------------------

        amount_in_paise = int(
            amount * 100
        )

        payload = {
            "amount": amount_in_paise,
            "currency": "INR",
            "description": description,
            "reference_id": reference_id,
        }

        # --------------------------------------------------
        # REAL Razorpay Test Mode API call
        # --------------------------------------------------

        return self.client.payment_link.create(
            payload
        )


def create_payment_link(
    *,
    amount: int,
    description: str,
    reference_id: str,
) -> Dict[str, Any]:
    """
    Convenience function used by the growth workflow.
    """

    client = PaymentLinkClient()

    return client.create_payment_link(
        amount=amount,
        description=description,
        reference_id=reference_id,
    )