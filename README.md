# Loan Assessment Expert System

A simple, explainable, rule-based expert system for loan application assessments.

## Features
- Input validation and metrics computation
- Eligibility checks and pricing/limit derivation
- Final decision with explanations and rule traces
- CLI for assessing JSON applications

## Quick start

Run the CLI on a sample applicant:

```bash
python -m loan_assessment.cli loan_assessment/data/samples/applicant_good.json --traces
```

## JSON input schema

Required fields:
- `applicant_id`: string
- `income_monthly`: number (> 0)
- `expenses_monthly`: number (>= 0)
- `existing_debt_monthly`: number (>= 0)
- `credit_score`: number (300..850)
- `requested_amount`: number (> 0)
- `requested_term_months`: integer (> 0)

Optional fields:
- `employment_years`: number
- `age`: integer
- `loan_purpose`: string

## Testing

```bash
python -m pytest -q
```
