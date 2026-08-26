import os
from typing import Any, Dict


class RazorpayTools:
    """
    Controlled interface for Razorpay-related operations.

    Secrets are loaded from environment variables and are
    never exposed to the LLM.
    """

    def __init__(self):
        self.key_id = os.getenv(
            "RAZORPAY_KEY_ID"
        )

        self.key_secret = os.getenv(
            "RAZORPAY_KEY_SECRET"
        )

    def credentials_available(self) -> bool:
        """
        Check whether Razorpay credentials are configured.
        """

        return bool(
            self.key_id
            and self.key_secret
        )

    def get_configuration_status(
        self,
    ) -> Dict[str, Any]:
        """
        Return safe configuration information.

        Never return the actual secret.
        """

        return {
            "configured": self.credentials_available(),
            "key_id_configured": bool(
                self.key_id
            ),
            "key_secret_configured": bool(
                self.key_secret
            ),
        }