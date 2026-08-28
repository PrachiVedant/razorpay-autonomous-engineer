import os
from typing import Any, Dict

import razorpay
from dotenv import load_dotenv


load_dotenv()


class PaymentLinkClient:
    """
    Razorpay Test Mode Payment Link client.

    Responsibilities:
        - Load Razorpay Test Mode credentials.
        - Refuse live mode.
        - Create Razorpay Payment Links.
        - Support controlled failure demonstration.

    The growth agent proposes.
    The policy validates.
    This class executes.
    """

    def __init__(self):

        self.mode = os.getenv(
            "RAZORPAY_MODE",
            "test",
        ).lower().strip()

        # =================================================
        # SECURITY BOUNDARY
        # =================================================

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

        # IMPORTANT:
        # Credentials are used only to construct the
        # Razorpay client and are never returned or logged.

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

        Razorpay receives amount in paise.

        A controlled failure can be enabled with:

            RAZORPAY_DEMO_FORCE_FAILURE=1

        This deliberately raises an exception and never
        returns a fake successful payment link.
        """

        # =================================================
        # Validate amount
        # =================================================

        if not isinstance(
            amount,
            (int, float),
        ):
            raise ValueError(
                "Payment amount must be numeric."
            )

        if amount <= 0:
            raise ValueError(
                "Payment amount must be positive."
            )

        # =================================================
        # Validate reference ID
        # =================================================

        if not reference_id:
            raise ValueError(
                "Payment reference ID is required."
            )

        if len(reference_id) > 40:
            raise ValueError(
                "Payment reference ID must not exceed "
                "40 characters."
            )

        # =================================================
        # Validate description
        # =================================================

        if not description:
            raise ValueError(
                "Payment description is required."
            )

        # =================================================
        # Controlled demo failure
        # =================================================

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

        # =================================================
        # Convert rupees → paise
        # =================================================

        amount_in_paise = int(
            amount * 100
        )

        payload = {
            "amount": amount_in_paise,
            "currency": "INR",
            "description": description,
            "reference_id": reference_id,
        }

        # =================================================
        # REAL RAZORPAY TEST MODE API CALL
        # =================================================

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