"""Unit tests for the provider benchmark scoring helpers."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("evaluate_ai", Path(__file__).with_name("evaluate_ai.py"))
evaluate_ai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluate_ai)


def test_keyword_score_rewards_expected_diagnostic_terms():
    assert evaluate_ai.keyword_score(["database", "pool", "timeout"], "Database connection pool timeout") == 1
    assert evaluate_ai.keyword_score(["database", "pool", "timeout"], "Database latency is high") == 1 / 3
    assert evaluate_ai.keyword_score(["certificate", "expired"], "No TLS signal observed") == 0
