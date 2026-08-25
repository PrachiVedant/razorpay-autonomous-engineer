import subprocess
from typing import Dict


def run_tests(
    command: str = "uv run python -m pytest",
) -> Dict[str, object]:
    """
    Run the repository test suite.

    Returns:
        {
            "passed": bool,
            "return_code": int,
            "stdout": str,
            "stderr": str,
        }
    """

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

        return {
            "passed": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Test execution timed out after 120 seconds.",
        }

    except Exception as error:
        return {
            "passed": False,
            "return_code": -1,
            "stdout": "",
            "stderr": str(error),
        }