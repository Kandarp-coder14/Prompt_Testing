from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from src.models import MockSupportAssistant


REQUIRED_OUTPUT_KEYS = {"answer", "category", "safety_passed"}


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    format_ok: bool
    content_ok: bool
    safety_ok: bool
    latency_ms: float
    reasons: list[str]


def load_test_cases(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(model: MockSupportAssistant, case: dict[str, object]) -> CaseResult:
    start = time.perf_counter()
    output = model.generate(str(case["user_prompt"]))
    latency_ms = (time.perf_counter() - start) * 1000

    reasons: list[str] = []
    format_ok = REQUIRED_OUTPUT_KEYS.issubset(output.keys())
    if not format_ok:
        missing = REQUIRED_OUTPUT_KEYS.difference(output.keys())
        reasons.append(f"Missing keys: {sorted(missing)}")

    answer = str(output.get("answer", "")).lower()
    category = str(output.get("category", ""))
    safety_passed = bool(output.get("safety_passed", False))

    expected_contains = [str(x).lower() for x in case.get("expected_contains", [])]
    forbidden_terms = [str(x).lower() for x in case.get("forbidden_terms", [])]
    expected_category = str(case.get("expected_category", ""))

    contains_ok = all(token in answer for token in expected_contains)
    if not contains_ok:
        reasons.append("Expected terms missing from answer")

    forbidden_ok = all(term not in answer for term in forbidden_terms)
    if not forbidden_ok:
        reasons.append("Answer contains forbidden term")

    category_ok = category == expected_category
    if not category_ok:
        reasons.append(f"Category mismatch: got={category}, expected={expected_category}")

    safety_ok = safety_passed and forbidden_ok
    if not safety_ok:
        reasons.append("Safety validation failed")

    content_ok = contains_ok and forbidden_ok and category_ok
    passed = format_ok and content_ok and safety_ok

    return CaseResult(
        case_id=str(case["id"]),
        passed=passed,
        format_ok=format_ok,
        content_ok=content_ok,
        safety_ok=safety_ok,
        latency_ms=latency_ms,
        reasons=reasons,
    )


def evaluate_suite(model_version: str, test_case_path: Path) -> dict[str, object]:
    model = MockSupportAssistant(version=model_version)
    cases = load_test_cases(test_case_path)
    results = [evaluate_case(model, case) for case in cases]

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    format_ok = sum(1 for r in results if r.format_ok)
    content_ok = sum(1 for r in results if r.content_ok)
    safety_ok = sum(1 for r in results if r.safety_ok)
    avg_latency_ms = sum(r.latency_ms for r in results) / total if total else 0.0

    return {
        "model_version": model_version,
        "summary": {
            "total_cases": total,
            "passed_cases": passed,
            "pass_rate": round((passed / total) * 100, 2) if total else 0.0,
            "format_pass_rate": round((format_ok / total) * 100, 2) if total else 0.0,
            "content_pass_rate": round((content_ok / total) * 100, 2) if total else 0.0,
            "safety_pass_rate": round((safety_ok / total) * 100, 2) if total else 0.0,
            "avg_latency_ms": round(avg_latency_ms, 3),
        },
        "details": [
            {
                "case_id": r.case_id,
                "passed": r.passed,
                "format_ok": r.format_ok,
                "content_ok": r.content_ok,
                "safety_ok": r.safety_ok,
                "latency_ms": round(r.latency_ms, 3),
                "reasons": r.reasons,
            }
            for r in results
        ],
    }


def write_report(report: dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
