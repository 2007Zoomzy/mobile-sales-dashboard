from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .metrics import compute_basic_metrics, clamp
from .validators import validate_applicant


RuleApplyResult = Tuple[Dict[str, Any], List[str]]


class Rule:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        raise NotImplementedError


class ValidationRule(Rule):
    def __init__(self):
        super().__init__(name="validation", description="Validate required fields and ranges")

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        errors = validate_applicant(app)
        new_metrics = dict(metrics)
        if errors:
            new_metrics["approved"] = False
            return new_metrics, errors
        return new_metrics, []


class MetricsRule(Rule):
    def __init__(self):
        super().__init__(name="metrics", description="Compute base metrics for assessment")

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        computed = compute_basic_metrics(app)
        updated = {**metrics, **computed}
        return updated, []


class EligibilityRule(Rule):
    def __init__(self):
        super().__init__(name="eligibility", description="Hard eligibility checks (age, DTI caps, etc)")

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        updated = dict(metrics)
        reasons: List[str] = []

        age = int(app.get("age", 0) or 0)
        if age and (age < 18 or age > 75):
            updated["approved"] = False
            reasons.append("Age outside lending policy (18-75)")

        if metrics.get("dti", 0) > 0.5:
            updated["approved"] = False
            reasons.append("Debt-to-income ratio too high (>50%)")

        if metrics.get("affordability_score", 0) < 0.3:
            updated["approved"] = False
            reasons.append("Insufficient affordability score")

        return updated, reasons


class PricingAndLimitRule(Rule):
    def __init__(self):
        super().__init__(name="pricing_limit", description="Set indicative APR and credit limit")

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        updated = dict(metrics)
        reasons: List[str] = []

        risk = metrics.get("risk_score", 0.0)
        # Map risk 0..1 to APR 36%..8%
        apr = clamp(0.36 - (risk * 0.28), 0.08, 0.36)

        disposable_income = float(metrics.get("disposable_income", 0.0))
        # Allow up to 35% of disposable income towards payment
        max_payment = disposable_income * 0.35

        term = int(metrics.get("term_months", 0))
        monthly_rate = apr / 12.0
        if term > 0 and monthly_rate > 0:
            # Reverse loan payment formula to compute principal given payment cap
            limit = max_payment * (1 - (1 + monthly_rate) ** (-term)) / monthly_rate
        else:
            limit = 0.0

        requested_amount = float(metrics.get("requested_amount", 0.0))
        credit_limit = max(0.0, min(limit, requested_amount))

        updated["interest_rate_apr"] = round(apr, 4)
        updated["credit_limit"] = round(credit_limit, 2)

        if credit_limit <= 0.0:
            updated["approved"] = False
            reasons.append("Insufficient capacity for any credit limit")

        return updated, reasons


class FinalDecisionRule(Rule):
    def __init__(self):
        super().__init__(name="final_decision", description="Set final approval flag and notes")

    def apply(self, app: Dict[str, Any], metrics: Dict[str, Any]) -> RuleApplyResult:
        updated = dict(metrics)
        reasons: List[str] = []

        # If any prior rule set approved False, maintain decline unless override
        if updated.get("approved") is False:
            return updated, reasons

        # Approve if affordability and risk are good
        if updated.get("affordability_score", 0) >= 0.5 and updated.get("risk_score", 0) >= 0.5:
            updated["approved"] = True
            updated.setdefault("approval_notes", []).append("Meets affordability and risk thresholds")
        else:
            updated["approved"] = False
            if updated.get("affordability_score", 0) < 0.5:
                reasons.append("Affordability below threshold")
            if updated.get("risk_score", 0) < 0.5:
                reasons.append("Risk score below threshold")

        # Ensure positive credit limit and APR exist on approval
        if updated.get("approved"):
            if not updated.get("credit_limit") or not updated.get("interest_rate_apr"):
                updated["approved"] = False
                reasons.append("Incomplete pricing/limit for approval")

        return updated, reasons


DEFAULT_RULES: List[Rule] = [
    ValidationRule(),
    MetricsRule(),
    EligibilityRule(),
    PricingAndLimitRule(),
    FinalDecisionRule(),
]
