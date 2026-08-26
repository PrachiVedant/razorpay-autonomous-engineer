import re


class SecurityValidationError(Exception):
    """Raised when generated code violates security rules."""


class SecurityValidator:
    """
    Deterministic validator for LLM-generated code.

    This validator runs before generated changes are applied
    to the repository.
    """

    SECRET_PATTERNS = [
        r"RAZORPAY_KEY_SECRET\s*=\s*['\"][^'\"]+['\"]",
        r"RAZORPAY_KEY_ID\s*=\s*['\"][^'\"]+['\"]",
        r"api_key\s*=\s*['\"][^'\"]+['\"]",
        r"api_secret\s*=\s*['\"][^'\"]+['\"]",
        r"secret\s*=\s*['\"][^'\"]+['\"]",
    ]

    DANGEROUS_PATTERNS = [
        r"\bos\.system\s*\(",
        r"\bsubprocess\.",
        r"\beval\s*\(",
        r"\bexec\s*\(",
    ]

    SECRET_LOG_PATTERNS = [
        r"print\s*\([^)]*(secret|api_key|key_secret)",
        r"logger\.[a-z]+\s*\([^)]*(secret|api_key|key_secret)",
        r"log_event\s*\([^)]*(secret|api_key|key_secret)",
    ]

    def validate_changes(self, changes):
        """
        Validate all generated file changes.

        Returns:
            {
                "valid": True,
                "violations": []
            }

        or:

            {
                "valid": False,
                "violations": [...]
            }
        """

        violations = []

        for change in changes:

            path = change.get("path")
            content = change.get("content", "")

            if not path:
                violations.append(
                    "Generated change is missing a file path."
                )
                continue

            if not isinstance(content, str):
                violations.append(
                    f"Invalid content for file: {path}"
                )
                continue

            violations.extend(
                self._validate_file(
                    path,
                    content,
                )
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _validate_file(self, path, content):

        violations = []

        # --------------------------------------------
        # Sensitive files
        # --------------------------------------------

        normalized_path = path.replace("\\", "/").lower()

        sensitive_files = [
            ".env",
            ".env.production",
            ".env.local",
            "id_rsa",
            "authorized_keys",
        ]

        for sensitive_file in sensitive_files:

            if normalized_path.endswith(
                sensitive_file
            ):

                violations.append(
                    f"Modification of sensitive file is prohibited: {path}"
                )

        # --------------------------------------------
        # Hardcoded secrets
        # --------------------------------------------

        for pattern in self.SECRET_PATTERNS:

            if re.search(
                pattern,
                content,
                re.IGNORECASE,
            ):

                violations.append(
                    f"Possible hardcoded secret detected in: {path}"
                )

        # --------------------------------------------
        # Secret logging
        # --------------------------------------------

        for pattern in self.SECRET_LOG_PATTERNS:

            if re.search(
                pattern,
                content,
                re.IGNORECASE,
            ):

                violations.append(
                    f"Possible secret exposure through logging in: {path}"
                )

        # --------------------------------------------
        # Dangerous execution
        # --------------------------------------------

        for pattern in self.DANGEROUS_PATTERNS:

            if re.search(
                pattern,
                content,
            ):

                violations.append(
                    f"Dangerous code pattern detected in: {path}"
                )

        return violations