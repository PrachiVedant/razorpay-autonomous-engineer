import os


def get_env(
    name,
    default=None,
    required=False,
):
    """
    Read a configuration value from the environment.

    Args:
        name: Environment variable name.
        default: Value returned when variable is absent.
        required: Whether the variable must exist.

    Returns:
        Environment variable value.

    Raises:
        RuntimeError: If a required variable is missing.
    """

    value = os.getenv(name)

    if value is None or value == "":

        if required:
            raise RuntimeError(
                f"Required environment variable "
                f"'{name}' is not configured."
            )

        return default

    return value


OPENAI_API_KEY = get_env(
    "OPENAI_API_KEY",
)

OPENAI_MODEL = get_env(
    "OPENAI_MODEL",
    default="gpt-4o-mini",
)

GITHUB_TOKEN = get_env(
    "GITHUB_TOKEN",
)

TEST_COMMAND = get_env(
    "TEST_COMMAND",
    default="uv run pytest tests/",
)

LOG_LEVEL = get_env(
    "LOG_LEVEL",
    default="INFO",
)

MAX_REPAIR_RETRIES = int(
    get_env(
        "MAX_REPAIR_RETRIES",
        default="3",
    )
)