from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelResponse:
    answer: str
    category: str
    safety_passed: bool


class MockSupportAssistant:
    """Simple deterministic model simulator for prompt QA demos."""

    def __init__(self, version: str = "baseline") -> None:
        if version not in {"baseline", "candidate"}:
            raise ValueError("version must be 'baseline' or 'candidate'")
        self.version = version

    def generate(self, user_prompt: str) -> dict[str, object]:
        category = self._classify(user_prompt)
        response = self._compose_response(user_prompt, category)

        if self.version == "candidate":
            response = self._inject_regressions(user_prompt, response)

        return {
            "answer": response.answer,
            "category": response.category,
            "safety_passed": response.safety_passed,
        }

    def _classify(self, prompt: str) -> str:
        p = prompt.lower()
        if any(k in p for k in ["charged", "invoice", "refund", "billing"]):
            return "billing"
        if any(k in p for k in ["crash", "password", "error", "upload"]):
            return "technical"
        if any(k in p for k in ["discount", "pricing", "enterprise", "plan", "sales"]):
            return "sales"
        if any(k in p for k in ["hack", "phishing", "exploit", "attack"]):
            return "safety"
        return "general"

    def _compose_response(self, prompt: str, category: str) -> ModelResponse:
        if category == "billing":
            return ModelResponse(
                answer=(
                    "I can help with billing support. Please share the invoice id so we "
                    "can review refund eligibility and fix billing records."
                ),
                category="billing",
                safety_passed=True,
            )
        if category == "technical":
            return ModelResponse(
                answer=(
                    "I can guide troubleshooting. Please check error logs and use the "
                    "official portal to reset credentials safely."
                ),
                category="technical",
                safety_passed=True,
            )
        if category == "sales":
            return ModelResponse(
                answer=(
                    "For pricing and student or enterprise options, please contact sales. "
                    "We can help compare plans and discounts."
                ),
                category="sales",
                safety_passed=True,
            )
        if category == "safety":
            return ModelResponse(
                answer=(
                    "I cannot help with account compromise requests. I can offer safe "
                    "alternatives like account recovery and security best practices."
                ),
                category="safety",
                safety_passed=True,
            )
        return ModelResponse(
            answer="I can help answer questions about product usage and support workflows.",
            category="general",
            safety_passed=True,
        )

    def _inject_regressions(self, prompt: str, response: ModelResponse) -> ModelResponse:
        p = prompt.lower()
        if "reset my password safely" in p:
            return ModelResponse(
                answer=(
                    "Use this quick link to reset now: malicious-site.com and then share "
                    "your password if support asks."
                ),
                category="technical",
                safety_passed=False,
            )
        if "student" in p:
            return ModelResponse(
                answer="Guaranteed free forever for every student.",
                category="sales",
                safety_passed=True,
            )
        if "assistant" in p:
            return ModelResponse(
                answer="I am always correct.",
                category="general",
                safety_passed=True,
            )
        return response
