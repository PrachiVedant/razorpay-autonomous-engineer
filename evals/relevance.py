from typing_extensions import Annotated, TypedDict
import json

from agents.llm import OpenAIProvider


class RelevanceGrade(TypedDict):
    reasoning: Annotated[
        str,
        ...,
        "Explain your reasoning for the response.",
    ]

    relevance: Annotated[
        bool,
        ...,
        "True if the generated changes are relevant to the issue.",
    ]


RELEVANCE_INSTRUCTION = """
You are an expert software engineer evaluating whether an autonomous coding agent
made changes relevant to the user's request.

You will be given:

- A GITHUB ISSUE describing the requested work.
- The ORIGINAL REPOSITORY FILES available to the agent.
- The EXPECTED CHANGES representing files that should reasonably be modified.
- The AGENT GENERATED CHANGES.

Your task is to determine whether the generated changes are relevant to the issue.

Use the following grading criteria:

(1) Verify that the generated changes focus on functionality directly related
    to the GitHub issue.

(2) Determine whether the modified files are appropriate for solving the issue.

(3) Changes to unrelated files should be considered irrelevant unless they are
    necessary dependencies of the requested fix.

(4) Additional refactoring is acceptable only if it directly supports the
    requested work and does not substantially expand the scope of the issue.

(5) Broad modifications affecting unrelated modules, services, or components
    should be marked as irrelevant.

(6) Minor differences in implementation are acceptable as long as the overall
    scope of the work remains aligned with the issue.

Relevance:

A relevance value of True means that the generated changes remain within the
scope of the issue and modify only files reasonably connected to the requested fix.

A relevance value of False means that the generated changes extend beyond the
issue scope or modify unrelated functionality.

Explain your reasoning in a step-by-step manner before arriving at the final decision.

Avoid simply stating the conclusion at the outset.

Do not wrap the JSON in markdown fences.
Do not include any text before or after the JSON.

Respond ONLY in valid JSON using the following format:

{
    "reasoning": "<step-by-step explanation>",
    "relevance": true or false
}
"""


gateway = OpenAIProvider()


def evaluate_relevance(
    example: dict,
    generated_changes: list[dict],
) -> RelevanceGrade:
    """
    Evaluate whether the generated changes were relevant
    to the GitHub issue.
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
            RELEVANCE_INSTRUCTION
            + "\n\n"
            + user_prompt
        )
    )

    try:
        result = json.loads(response)

    except json.JSONDecodeError:
        return {
            "reasoning": "Evaluator returned invalid JSON.",
            "relevance": False,
        }

    if (
        not isinstance(result, dict)
        or "reasoning" not in result
        or "relevance" not in result
    ):
        return {
            "reasoning": "Evaluator returned an invalid schema.",
            "relevance": False,
        }

    if not isinstance(result["relevance"], bool):
        return {
            "reasoning": (
                "Evaluator returned a non-boolean "
                "relevance value."
            ),
            "relevance": False,
        }

    return {
        "reasoning": str(result["reasoning"]),
        "relevance": result["relevance"],
    }
