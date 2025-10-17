from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Decision:
    approved: bool
    limit: Optional[float]
    interest_rate_apr: Optional[float]
    reasons: List[str]


@dataclass(frozen=True)
class AssessmentResult:
    applicant_id: str
    decision: Decision
    metrics: Dict[str, Any]
    rule_traces: List[str]
