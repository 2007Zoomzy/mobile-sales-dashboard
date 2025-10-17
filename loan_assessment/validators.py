from __future__ import annotations

from typing import Any, Dict, List


class ValidationError(Exception):
    pass


REQUIRED_FIELDS: List[str] = [
    "applicant_id",
    "income_monthly",
    "expenses_monthly",
    "existing_debt_monthly",
    "credit_score",
    "requested_amount",
    "requested_term_months",
]


def validate_applicant(app: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if app.get(field) in (None, ""):
            errors.append(f"Missing required field: {field}")
    try:
        credit_score = float(app.get("credit_score", 0))
        if not 300 <= credit_score <= 850:
            errors.append("credit_score must be between 300 and 850")
    except Exception:
        errors.append("credit_score must be numeric")

    try:
        requested_amount = float(app.get("requested_amount", 0))
        if requested_amount <= 0:
            errors.append("requested_amount must be > 0")
    except Exception:
        errors.append("requested_amount must be numeric")

    try:
        term = int(app.get("requested_term_months", 0))
        if term <= 0:
            errors.append("requested_term_months must be > 0")
    except Exception:
        errors.append("requested_term_months must be integer")

    income = float(app.get("income_monthly", 0) or 0)
    expenses = float(app.get("expenses_monthly", 0) or 0)
    if income <= 0:
        errors.append("income_monthly must be > 0")
    if expenses < 0:
        errors.append("expenses_monthly must be >= 0")

    return errors
