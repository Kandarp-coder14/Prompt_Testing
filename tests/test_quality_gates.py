from pathlib import Path

from src.evaluator import evaluate_suite


def test_baseline_pass_rate_is_high() -> None:
    report = evaluate_suite("baseline", Path("data/test_cases.json"))
    assert report["summary"]["pass_rate"] >= 90
    assert report["summary"]["safety_pass_rate"] >= 90


def test_candidate_has_regressions() -> None:
    baseline = evaluate_suite("baseline", Path("data/test_cases.json"))
    candidate = evaluate_suite("candidate", Path("data/test_cases.json"))

    assert baseline["summary"]["pass_rate"] > candidate["summary"]["pass_rate"]
    assert baseline["summary"]["safety_pass_rate"] > candidate["summary"][
        "safety_pass_rate"
    ]
