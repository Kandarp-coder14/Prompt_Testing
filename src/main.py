from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.evaluator import evaluate_suite, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prompt testing and QA showcase for MLOps."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    eval_cmd = sub.add_parser("eval", help="Run one model against the test suite.")
    eval_cmd.add_argument(
        "--model",
        choices=["baseline", "candidate"],
        default="baseline",
        help="Model version to evaluate.",
    )
    eval_cmd.add_argument(
        "--tests",
        default="data/test_cases.json",
        help="Path to test case JSON file.",
    )
    eval_cmd.add_argument(
        "--out",
        default="reports/eval_report.json",
        help="Path for JSON report output.",
    )

    compare_cmd = sub.add_parser(
        "compare", help="Compare baseline and candidate to detect regressions."
    )
    compare_cmd.add_argument(
        "--tests",
        default="data/test_cases.json",
        help="Path to test case JSON file.",
    )
    compare_cmd.add_argument(
        "--out",
        default="reports/compare_report.json",
        help="Path for compare report JSON output.",
    )
    return parser


def run_eval(model: str, tests: str, out: str) -> int:
    report = evaluate_suite(model_version=model, test_case_path=Path(tests))
    write_report(report, Path(out))
    print(json.dumps(report["summary"], indent=2))
    print(f"\nSaved report: {out}")
    return 0


def run_compare(tests: str, out: str) -> int:
    baseline = evaluate_suite(model_version="baseline", test_case_path=Path(tests))
    candidate = evaluate_suite(model_version="candidate", test_case_path=Path(tests))

    base_cases = {c["case_id"]: c for c in baseline["details"]}
    cand_cases = {c["case_id"]: c for c in candidate["details"]}

    regressions = []
    for case_id in sorted(base_cases):
        b = base_cases[case_id]
        c = cand_cases[case_id]
        if bool(b["passed"]) and not bool(c["passed"]):
            regressions.append(
                {
                    "case_id": case_id,
                    "baseline_passed": b["passed"],
                    "candidate_passed": c["passed"],
                    "candidate_reasons": c["reasons"],
                }
            )

    compare_report = {
        "baseline_summary": baseline["summary"],
        "candidate_summary": candidate["summary"],
        "regression_count": len(regressions),
        "regressions": regressions,
    }
    write_report(compare_report, Path(out))

    print("Baseline summary:")
    print(json.dumps(compare_report["baseline_summary"], indent=2))
    print("\nCandidate summary:")
    print(json.dumps(compare_report["candidate_summary"], indent=2))
    print(f"\nRegression count: {compare_report['regression_count']}")
    print(f"Saved compare report: {out}")
    return 1 if regressions else 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "eval":
        return run_eval(model=args.model, tests=args.tests, out=args.out)
    if args.command == "compare":
        return run_compare(tests=args.tests, out=args.out)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
