from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Any

from .types import AssessmentResult, Decision


@dataclass
class Rule:
    name: str
    description: str
    apply: Callable[[Dict[str, Any], Dict[str, Any]], Tuple[Dict[str, Any], List[str]]]
    # apply(app, metrics) -> (updated_metrics, reasons)


class Engine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def assess(self, applicant: Dict[str, Any]) -> AssessmentResult:
        metrics: Dict[str, Any] = {}
        reasons: List[str] = []
        traces: List[str] = []

        for rule in self.rules:
            metrics, rule_reasons = rule.apply(applicant, metrics)
            if rule_reasons:
                reasons.extend(rule_reasons)
                traces.append(f"{rule.name}: " + "; ".join(rule_reasons))

        approved = metrics.get("approved", False)
        decision = Decision(
            approved=approved,
            limit=metrics.get("credit_limit") if approved else None,
            interest_rate_apr=metrics.get("interest_rate_apr") if approved else None,
            reasons=reasons if not approved else metrics.get("approval_notes", []),
        )

        applicant_id = str(applicant.get("applicant_id", "unknown"))
        return AssessmentResult(
            applicant_id=applicant_id,
            decision=decision,
            metrics=metrics,
            rule_traces=traces,
        )
