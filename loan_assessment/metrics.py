from __future__ import annotations

from typing import Dict, Any


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator


def compute_basic_metrics(app: Dict[str, Any]) -> Dict[str, Any]:
    """Compute basic affordability and risk metrics.

    Expected applicant fields:
    - income_monthly
    - expenses_monthly
    - existing_debt_monthly
    - credit_score (300-850)
    - requested_amount
    - requested_term_months
    - employment_years
    - age
    - loan_purpose
    """
    income = float(app.get("income_monthly", 0) or 0)
    expenses = float(app.get("expenses_monthly", 0) or 0)
    debt = float(app.get("existing_debt_monthly", 0) or 0)
    credit_score = float(app.get("credit_score", 0) or 0)
    requested_amount = float(app.get("requested_amount", 0) or 0)
    term_months = int(app.get("requested_term_months", 0) or 0)

    disposable_income = max(0.0, income - expenses - debt)
    dti = safe_div(debt, max(1.0, income), 0.0)  # Debt to Income ratio
    expense_ratio = safe_div(expenses, max(1.0, income), 0.0)

    # Normalize credit score to 0..1
    credit_score_norm = clamp((credit_score - 300.0) / 550.0, 0.0, 1.0)

    # Simple affordability score based on disposable income vs requested monthly
    # Assume a nominal base interest for estimate of payment proportion
    nominal_apr = 0.18  # 18% APR baseline
    monthly_rate = nominal_apr / 12.0
    est_payment = requested_amount * monthly_rate / max(1e-6, (1 - (1 + monthly_rate) ** (-term_months))) if term_months > 0 else 0.0
    affordability_ratio = safe_div(est_payment, max(1.0, disposable_income), 1.0)

    affordability_score = clamp(1.0 - affordability_ratio, 0.0, 1.0)

    # Employment stability proxy (cap at 10 years)
    employment_years = float(app.get("employment_years", 0) or 0)
    employment_stability = clamp(employment_years / 10.0, 0.0, 1.0)

    # Risk score: combination of credit score, DTI, expense ratio, stability
    risk_score = clamp(
        0.5 * credit_score_norm + 0.2 * (1.0 - dti) + 0.1 * (1.0 - expense_ratio) + 0.2 * employment_stability,
        0.0,
        1.0,
    )

    return {
        "disposable_income": disposable_income,
        "dti": dti,
        "expense_ratio": expense_ratio,
        "credit_score_norm": credit_score_norm,
        "affordability_score": affordability_score,
        "employment_stability": employment_stability,
        "risk_score": risk_score,
        "requested_amount": requested_amount,
        "term_months": term_months,
    }
