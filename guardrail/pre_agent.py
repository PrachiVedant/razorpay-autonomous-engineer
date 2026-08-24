from typing import Any
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config,
)
from langgraph.runtime import Runtime


class CodingSafetyFilter(AgentMiddleware):
    """Block dangerous requests before the agent runs."""

    DANGEROUS_TERMS = [
        "rm -rf",
        "delete the entire repository",
        "wipe the system",
        "shutdown",
        "reboot",
        "sudo",
        "curl",
        "wget",
        "python -c",
        "chmod",
        "chown",
        "scp",
        "ssh",
        "netcat",
    ]

    SECRET_PATTERNS = [
        "aws_access_key_id",
        "aws_secret_access_key",
        "private_key",
        "client_secret",
        "ssh_key",
        "authorization: bearer",
        "begin private key",
    ]

    SENSITIVE_FILE_PATTERNS = [
        ".git",
        ".env",
        ".env.production",
        "id_rsa",
        "authorized_keys",
        "credentials",
        "secrets",
    ]

    EXTERNAL_ACCESS_TERMS = [
        "exfiltrate",
        "send to",
        "upload to",
        "post to",
        "download from",
        "external url",
        "http://",
        "https://",
        "ftp://",
        "s3://",
    ]

    UNAUTHORIZED_INTENT_TERMS = [
        "bypass authentication",
        "steal secrets",
        "break into",
        "hack",
        "take over",
        "compromise",
        "escalate privileges",
        "privilege escalation",
    ]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self,
        state: AgentState,
        runtime: Runtime,
    ) -> dict[str, Any] | None:

        messages = state.get("messages")
        if not messages:
            return None

        # Find the most recent human message
        content = None

        for message in reversed(messages):
            role = message.get("role")

            if role == "human":
                content = message.get("content", "").lower()
                break

        if not content:
            return None

        checks = [
            self.dangerous_command_filter,
            self.secret_detection_filter,
            self.sensitive_file_guard,
            self.external_access_filter,
            self.scope_validator,
        ]

        for check in checks:
            matched_term = check(content)

            if matched_term:
                return self._block_response(matched_term)

        return None

    def dangerous_command_filter(self, content: str) -> str | None:
        return self._find_matching_term(
            content,
            self.DANGEROUS_TERMS,
        )

    def secret_detection_filter(self, content: str) -> str | None:
        return self._find_matching_term(
            content,
            self.SECRET_PATTERNS,
        )

    def sensitive_file_guard(self, content: str) -> str | None:
        return self._find_matching_term(
            content,
            self.SENSITIVE_FILE_PATTERNS,
        )

    def external_access_filter(self, content: str) -> str | None:
        return self._find_matching_term(
            content,
            self.EXTERNAL_ACCESS_TERMS,
        )

    def scope_validator(self, content: str) -> str | None:
        return self._find_matching_term(
            content,
            self.UNAUTHORIZED_INTENT_TERMS,
        )

    def _find_matching_term(
        self,
        content: str,
        terms: list[str],
    ) -> str | None:

        for term in terms:
            if term.lower() in content:
                return term

        return None

    def _block_response(self, term: str) -> dict[str, Any]:
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        "Request blocked by guardrails. "
                        f"The request contains a prohibited term: '{term}'."
                    ),
                }
            ],
            "jump_to": "end",
        }