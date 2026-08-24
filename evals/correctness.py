from typing_extensions import Annotated, TypedDict
import json

from agents.llm import OpenAIProvider


class CorrectnessGrade(TypedDict):
    reasoning: Annotated[
        str,
        ...,
        "Explain your reasoning for the response.",
    ]

    correctness: Annotated[
        bool,
        ...,
        "True if the generated fix is correct.",
    ]


CORRECTNESS_INSTRUCTION = """
You are an expert software engineer evaluating the output of an autonomous coding agent.

You will be given:

- A GITHUB ISSUE describing the required fix.
- The ORIGINAL REPOSITORY FILES that were provided to the agent.
- The EXPECTED CHANGES representing a correct implementation.
- The AGENT GENERATED CHANGES produced by the coding agent.

Your task is to determine whether the generated changes correctly solve the issue.

Use the following grading criteria:

(1) Evaluate whether the generated changes satisfy the requirements described in the GitHub issue.

(2) Compare the generated changes against the expected changes and determine whether they implement the intended fix.

(3) Minor differences in formatting, whitespace, comments, import ordering, or equivalent implementations are acceptable if the underlying behavior remains correct.

(4) If the generated changes fail to address any required functionality described in the issue, mark the result as incorrect.

(5) If the generated changes introduce conflicting behavior that contradicts the intended fix, mark the result as incorrect.

(6) It is acceptable for the generated changes to include additional improvements, provided they do not alter the intended functionality or introduce regressions.

Correctness:

A correctness value of True means that the generated changes successfully resolve the issue according to the criteria above.

A correctness value of False means that the generated changes do not fully resolve the issue according to the criteria above.

Explain your reasoning in a step-by-step manner before arriving at the final decision.

Avoid simply stating the conclusion at the outset.

Do not wrap the JSON in markdown fences.
Do not include any text before or after the JSON.

Respond ONLY in valid JSON using the following format:

{
    "reasoning": "<step-by-step explanation>",
    "correctness": true or false
}
"""


gateway = OpenAIProvider()


def evaluate_correctness(
    example: dict,
    generated_changes: list[dict],
) -> CorrectnessGrade:
    """
    Evaluate whether the agent correctly solved the issue.
    """

    user_prompt = f"""
GITHUB ISSUE:
{json.dumps(example["issue"], indent=2)}

ORIGINAL REPOSITORY FILES:
{json.dumps(example["repo_files"], indent=2)}

EXPECTED CHANGES:
{json.dumps(example["expected_changes"], indent=2)}

AGENT GENERATED CHANGES:
{json.dumps(generated_changes, indent=2)}
"""

    response = gateway.generate(
        prompt=(
            CORRECTNESS_INSTRUCTION
            + "\n\n"
            + user_prompt
        )
    )

    try:
        result = json.loads(response)

    except json.JSONDecodeError:
        return {
            "reasoning": "Evaluator returned invalid JSON.",
            "correctness": False,
        }

    if (
        not isinstance(result, dict)
        or "reasoning" not in result
        or "correctness" not in result
    ):
        return {
            "reasoning": "Evaluator returned an invalid schema.",
            "correctness": False,
        }

    if not isinstance(result["correctness"], bool):
        return {
            "reasoning": (
                "Evaluator returned a non-boolean "
                "correctness value."
            ),
            "correctness": False,
        }

    return {
        "reasoning": str(result["reasoning"]),
        "correctness": result["correctness"],
    }
