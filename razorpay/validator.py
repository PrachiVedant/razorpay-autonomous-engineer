import re
from typing import Any, Dict, List


SECRET_PATTERNS = [
    r"rzp_live_[A-Za-z0-9]+",
    r"rzp_test_[A-Za-z0-9]+",
    r"sk_live_[A-Za-z0-9]+",
    r"sk_test_[A-Za-z0-9]+",
]


SENSITIVE_VARIABLES = [
    "RAZORPAY_KEY_SECRET",
    "RAZORPAY_SECRET",
    "RAZORPAY_KEY_ID",
]


def validate_changes(
    changes: List[Dict[str, Any]],
) -> Dict[str, Any]:

    errors = []

    for change in changes:

        path = change.get(
            "path",
            "",
        )

        content = change.get(
            "content",
            "",
        )

        # ------------------------------------------
        # Check known Razorpay secret formats
        # ------------------------------------------

        for pattern in SECRET_PATTERNS:

            if re.search(
                pattern,
                content,
            ):
                errors.append(
                    f"Possible Razorpay secret "
                    f"found in {path}"
                )

        # ------------------------------------------
        # Check suspicious hardcoded secret variables
        # ------------------------------------------

        for variable in SENSITIVE_VARIABLES:

            pattern = (
                rf"{variable}\s*=\s*['\"][^'\"]+['\"]"
            )

            if re.search(
                pattern,
                content,
                re.IGNORECASE,
            ):
                errors.append(
                    f"Possible hardcoded secret "
                    f"{variable} found in {path}"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }