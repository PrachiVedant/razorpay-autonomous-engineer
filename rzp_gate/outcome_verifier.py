from typing import Any, Dict


def verify_payment_link(
    payment_link: Dict[str, Any],
    expected_amount: int,
    expected_currency: str = "INR",
) -> Dict[str, Any]:
    """
    Deterministically verify a Razorpay Payment Link response.

    This verifier does NOT call Razorpay.

    It only checks whether the response returned by the
    execution layer contains the information required for
    the workflow to safely claim success.

    Validation rules:

        1. Response must be a dictionary.
        2. Payment Link ID must exist.
        3. Short URL must exist.
        4. Amount must match when returned by Razorpay.
        5. Currency must match when returned by Razorpay.

    Returns:

        {
            "verified": True,
            "reason": "...",
        }

    or:

        {
            "verified": False,
            "reason": "...",
        }
    """

    # =====================================================
    # 1. Validate response type
    # =====================================================

    if not isinstance(payment_link, dict):
        return {
            "verified": False,
            "reason": (
                "Payment Link response is not a dictionary."
            ),
        }

    # =====================================================
    # 2. Validate Payment Link ID
    # =====================================================

    payment_link_id = payment_link.get("id")

    if not payment_link_id:
        return {
            "verified": False,
            "reason": (
                "Payment Link response is missing its ID."
            ),
        }

    # =====================================================
    # 3. Validate short URL
    # =====================================================

    short_url = payment_link.get("short_url")

    if not short_url:
        return {
            "verified": False,
            "reason": (
                "Payment Link response is missing its "
                "short URL."
            ),
        }

    # =====================================================
    # 4. Validate amount if Razorpay returned it
    # =====================================================

    returned_amount = payment_link.get("amount")

    if returned_amount is not None:

        expected_amount_paise = int(
            expected_amount * 100
        )

        if returned_amount != expected_amount_paise:
            return {
                "verified": False,
                "reason": (
                    "Payment Link amount does not match "
                    "the requested amount."
                ),
            }

    # =====================================================
    # 5. Validate currency if Razorpay returned it
    # =====================================================

    returned_currency = payment_link.get("currency")

    if returned_currency is not None:

        if returned_currency != expected_currency:
            return {
                "verified": False,
                "reason": (
                    "Payment Link currency does not match "
                    "the expected currency."
                ),
            }

    # =====================================================
    # 6. Verification successful
    # =====================================================

    return {
        "verified": True,
        "reason": (
            "Payment Link response passed deterministic "
            "outcome verification."
        ),
    }