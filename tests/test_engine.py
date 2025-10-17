import json
from loan_assessment.engine import Engine
from loan_assessment.rules import DEFAULT_RULES


def test_assessment_runs_on_sample_good():
    engine = Engine(DEFAULT_RULES)
    with open("loan_assessment/data/samples/applicant_good.json", "r") as f:
        app = json.load(f)
    result = engine.assess(app)
    assert result.applicant_id == "A1001"
    assert isinstance(result.metrics, dict)


def test_cli_output_structure():
    from loan_assessment.cli import main
    import tempfile, os, sys
    import io

    engine = Engine(DEFAULT_RULES)
    with open("loan_assessment/data/samples/applicant_borderline.json", "r") as f:
        app = json.load(f)

    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w") as f:
        json.dump(app, f)

    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        code = main([path, "--traces"])
        assert code == 0
    finally:
        sys.stdout = old_stdout

    data = json.loads(buf.getvalue())
    assert set(["applicant_id", "approved", "credit_limit", "interest_rate_apr", "reasons", "metrics", "rule_traces"]) <= set(data.keys())
