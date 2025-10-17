from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .engine import Engine
from .rules import DEFAULT_RULES


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Loan assessment expert system")
    parser.add_argument("input", help="Path to applicant JSON file")
    parser.add_argument("--traces", action="store_true", help="Print rule traces")
    args = parser.parse_args(argv)

    app = load_json(args.input)
    engine = Engine(DEFAULT_RULES)
    result = engine.assess(app)

    out = {
        "applicant_id": result.applicant_id,
        "approved": result.decision.approved,
        "credit_limit": result.decision.limit,
        "interest_rate_apr": result.decision.interest_rate_apr,
        "reasons": result.decision.reasons,
        "metrics": result.metrics,
    }
    if args.traces:
        out["rule_traces"] = result.rule_traces

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
