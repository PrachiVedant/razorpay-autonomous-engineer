from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.planner import plan_issue
from agents.code_generator import generate_fix
from evals.correctness import evaluate_correctness
from evals.datasets import get_all_examples
from evals.relevance import evaluate_relevance

Example = Dict[str, Any]
EvaluationResult = Dict[str, Any]


def run_agent(example: Example) -> List[Dict[str, Any]]:
    """
    Run the autonomous coding agent for a single evaluation example.

    Unlike the production GitHub workflow, this evaluation runner
    uses the synthetic dataset directly and skips Git operations.
    """

    issue = example["issue"]
    repo_files = example["repo_files"]

    structure = "\n".join(repo_files.keys())

    plan = plan_issue(
        issue,
        structure,
    )

    file_contents = {}

    for filepath in plan["files_to_read"]:
        file_contents[filepath] = repo_files.get(
            filepath,
            f"File not found: {filepath}",
        )

    fix = generate_fix(
        issue,
        plan,
        file_contents,
    )

    return fix["changes"]


def target(example: Example) -> List[Dict[str, Any]]:
    """
    Generate agent output for a single evaluation example.
    """

    return run_agent(example)


def evaluate_example(
    example: Example,
) -> EvaluationResult:
    """
    Evaluate a single example using correctness
    and relevance metrics.
    """

    start_time = time.time()

    try:
        generated_changes = target(example)

    except Exception as e:
        return {
            "example_id": example["id"],
            "latency_seconds": 0.0,
            "correctness": {
                "reasoning": f"Agent execution failed: {e}",
                "correctness": False,
            },
            "relevance": {
                "reasoning": f"Agent execution failed: {e}",
                "relevance": False,
            },
        }

    latency = time.time() - start_time

    correctness_result = evaluate_correctness(
        example,
        generated_changes,
    )

    relevance_result = evaluate_relevance(
        example,
        generated_changes,
    )

    return {
        "example_id": example["id"],
        "latency_seconds": latency,
        "correctness": correctness_result,
        "relevance": relevance_result,
    }


def run_evaluations(
    dataset: Optional[List[Example]] = None,
) -> List[EvaluationResult]:
    """
    Execute evaluations over the dataset.
    """

    dataset = dataset if dataset is not None else get_all_examples()

    return [
        evaluate_example(example)
        for example in dataset
    ]


def calculate_overall_scores(
    results: List[EvaluationResult],
) -> Dict[str, float]:
    """
    Calculate aggregate evaluation metrics.
    """

    total = len(results)

    if total == 0:
        return {
            "correctness_score": 0.0,
            "relevance_score": 0.0,
            "average_latency": 0.0,
        }

    correctness_score = (
        sum(
            1
            for result in results
            if result["correctness"]["correctness"]
        )
        / total
    )

    relevance_score = (
        sum(
            1
            for result in results
            if result["relevance"]["relevance"]
        )
        / total
    )

    average_latency = (
        sum(
            result["latency_seconds"]
            for result in results
        )
        / total
    )

    return {
        "correctness_score": correctness_score,
        "relevance_score": relevance_score,
        "average_latency": average_latency,
    }


def save_results(
    results: List[EvaluationResult],
) -> None:
    """
    Save evaluation outputs for future analysis.
    """

    results_dir = Path("evals/results")

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        results_dir / "latest.json",
        "w",
    ) as f:
        json.dump(
            results,
            f,
            indent=2,
        )


def print_evaluation_results(
    results: List[EvaluationResult],
) -> None:
    """
    Print detailed evaluation results.
    """

    print("\nExperiment Results")
    print("-" * 50)

    for result in results:
        print(f"\nExample: {result['example_id']}")

        print(
            f"Latency: "
            f"{result['latency_seconds']:.2f}s"
        )

        print(
            f"Correctness: "
            f"{result['correctness']['correctness']}"
        )

        print(
            f"Correctness Reason: "
            f"{result['correctness']['reasoning']}"
        )

        print(
            f"Relevance: "
            f"{result['relevance']['relevance']}"
        )

        print(
            f"Relevance Reason: "
            f"{result['relevance']['reasoning']}"
        )

    scores = calculate_overall_scores(results)

    print("\nOverall Metrics")
    print("-" * 50)

    print(
        f"Correctness Score: "
        f"{scores['correctness_score']:.2%}"
    )

    print(
        f"Relevance Score: "
        f"{scores['relevance_score']:.2%}"
    )

    print(
        f"Average Latency: "
        f"{scores['average_latency']:.2f}s"
    )


if __name__ == "__main__":
    results = run_evaluations()

    save_results(results)

    print_evaluation_results(results)