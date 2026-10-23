"""Opt-in benchmark of configured OpsPilot diagnosis against labeled scenario cases.

Usage: AI_MODE=openai API_BASE=http://localhost:8080/api API_TOKEN=... \
       python scripts/evaluate_ai.py --limit 12 --output ai-evaluation.json
This sends one provider-backed analysis request per selected case and may incur
provider charges. It never approves or executes a remediation.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "fixtures" / "incidents.json").read_text())
STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "under", "during", "service", "synthetic", "failure", "issue", "system", "causing", "cause", "because", "when", "where"}


def terms(text):
    return {x for x in re.findall(r"[a-z0-9]+", text.lower()) if len(x) > 2 and x not in STOP}


def keyword_score(expected, actual):
    expected = set(expected)
    return len(expected & terms(actual)) / len(expected) if expected else 0.0


def request(client, method, path, body=None):
    return client.request(method, path, body)


class ApiClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def __enter__(self): return self
    def __exit__(self, *_): return False

    def request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": "Bearer " + self.token}
        if data is not None: headers["Content-Type"] = "application/json"
        req = Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=120) as response: return json.loads(response.read())
        except (HTTPError, URLError) as exc:
            detail = exc.read().decode(errors="replace") if isinstance(exc, HTTPError) else str(exc)
            raise RuntimeError(f"{method} {path} failed: {detail}") from exc


def evaluate(args):
    api = os.getenv("API_BASE", "http://127.0.0.1:8080/api").rstrip("/")
    token = os.getenv("API_TOKEN", "local-demo-token")
    expected_mode = os.getenv("EVALUATION_AI_MODE", "openai")
    cases = CATALOG
    if args.scenario:
        selected = set(args.scenario)
        cases = [s for s in cases if s["id"] in selected]
        missing = selected - {s["id"] for s in cases}
        if missing: raise ValueError("Unknown scenario IDs: " + ", ".join(sorted(missing)))
    if args.limit: cases = cases[:args.limit]
    if not cases: raise ValueError("No evaluation scenarios selected")

    output = []
    with ApiClient(api, token) as client:
        runbooks = request(client, "GET", "/runbooks")
        runbook_ids = {b["id"] for b in runbooks}
        for index, scenario in enumerate(cases, 1):
            started = time.perf_counter()
            record = {"scenario_id": scenario["id"], "priority": scenario["severity"], "expected_runbook": scenario["expected_runbook"]}
            try:
                incident = request(client, "POST", "/incidents", {
                    "service": scenario["service"], "title": scenario["title"],
                    "description": scenario["description"], "severity": scenario["severity"],
                    "scenarioId": scenario["id"]})
                incident = request(client, "POST", f"/incidents/{incident['id']}/analyze", {})
                analysis = incident.get("analysis") or {}
                citation_ids = {x.get("runbook_id") for x in analysis.get("citations", [])}
                root = str(analysis.get("root_cause", ""))
                expected_words = scenario.get("evaluation_keywords", terms(scenario["root_cause"]))
                score = keyword_score(expected_words, root + " " + str(analysis.get("reasoning", "")))
                signal_ok = True
                if scenario.get("runtime_signal"):
                    metric = analysis.get("evidence", [{}, {"data": {}}])[-1].get("data", {})
                    signal = scenario["runtime_signal"]
                    observed = metric.get("queue_backlog", 0) if signal == "queue_backlog" else metric.get("fault_signals", {}).get(signal, 0)
                    signal_ok = observed >= scenario.get("runtime_min", 1)
                record.update({
                    "status": incident.get("status"), "mode": analysis.get("mode"),
                    "diagnosis": root, "diagnosis_keyword_score": round(score, 3),
                    "diagnosis_match": score >= args.keyword_threshold,
                    "expected_runbook_retrieved": scenario["expected_runbook"] in citation_ids,
                    "citations_grounded": citation_ids.issubset(runbook_ids),
                    "expected_action": scenario["action"],
                    "proposed_action": (analysis.get("recommendation") or {}).get("action"),
                    "action_match": (analysis.get("recommendation") or {}).get("action") == scenario["action"],
                    "proposal_executable": (analysis.get("recommendation") or {}).get("executable") is True,
                    "runtime_signal_verified": signal_ok,
                    "evidence_count": len(analysis.get("evidence", [])),
                    "confidence": analysis.get("confidence"),
                    "error": incident.get("last_error")})
                if record["mode"] != expected_mode and not args.allow_demo:
                    record["error"] = f"Expected AI mode {expected_mode}, got {record['mode']}"
            except Exception as exc:
                record.update({"error": str(exc), "diagnosis_match": False,
                    "expected_runbook_retrieved": False, "citations_grounded": False,
                    "action_match": False, "proposal_executable": False,
                    "runtime_signal_verified": False, "evidence_count": 0})
            record["latency_seconds"] = round(time.perf_counter() - started, 3)
            output.append(record)
            print(f"[{index}/{len(cases)}] {scenario['id']}: {record.get('error') or 'scored'}")

    count = len(output)
    summary = {"cases": count}
    for key in ("diagnosis_match", "expected_runbook_retrieved", "citations_grounded", "action_match", "proposal_executable", "runtime_signal_verified"):
        summary[key + "_rate"] = round(sum(bool(x.get(key)) for x in output) / count, 4)
    summary["mean_diagnosis_keyword_score"] = round(sum(x.get("diagnosis_keyword_score", 0) for x in output) / count, 4)
    summary["mean_latency_seconds"] = round(sum(x.get("latency_seconds", 0) for x in output) / count, 3)
    confidences = [x.get("confidence") for x in output if isinstance(x.get("confidence"), (int, float))]
    summary["mean_confidence"] = round(sum(confidences) / len(confidences), 4) if confidences else None
    calibrated = [((x.get("confidence") - (1.0 if x.get("diagnosis_match") else 0.0)) ** 2)
        for x in output if isinstance(x.get("confidence"), (int, float))]
    summary["diagnosis_confidence_brier_score"] = round(sum(calibrated) / len(calibrated), 4) if calibrated else None
    summary["errors"] = sum(bool(x.get("error")) for x in output)
    report = {"configured_mode": expected_mode, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "summary": summary, "results": output}
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("Report:", args.output)
    if summary["errors"] or summary["expected_runbook_retrieved_rate"] < args.minimum_runbook_rate or summary["diagnosis_match_rate"] < args.minimum_diagnosis_rate:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", help="Scenario ID; repeat to select multiple")
    parser.add_argument("--limit", type=int, default=0, help="Run only the first N cases")
    parser.add_argument("--output", default="ai-evaluation.json")
    parser.add_argument("--keyword-threshold", type=float, default=.35)
    parser.add_argument("--minimum-runbook-rate", type=float, default=.95)
    parser.add_argument("--minimum-diagnosis-rate", type=float, default=.70)
    parser.add_argument("--allow-demo", action="store_true", help="Allow deterministic demo mode (not a provider evaluation)")
    options = parser.parse_args()
    try: sys.exit(evaluate(options))
    except Exception as error:
        print("Evaluation could not run:", error, file=sys.stderr)
        sys.exit(2)
