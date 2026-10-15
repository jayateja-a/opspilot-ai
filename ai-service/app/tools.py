import hashlib
import json
from fastapi import HTTPException
from .config import settings

SCENARIOS = {s["id"]: s for s in json.loads((settings.fixtures_dir / "incidents.json").read_text())}
ALLOWED_ACTIONS = frozenset(s["action"] for s in SCENARIOS.values())

def scenario_for(scenario_id: str, service: str) -> dict | None:
    scenario = SCENARIOS.get(scenario_id)
    if scenario_id and (scenario is None or scenario["service"] != service):
        raise HTTPException(422, "Scenario and service must match")
    return scenario

def collect(scenario: dict | None) -> tuple[list[dict], list[dict]]:
    if scenario is None:
        return [], [{"tool":"get_logs", "status":"no_simulated_source"}]
    evidence = [{"id":"logs:1", "type":"logs", "source":"mock-telemetry", "data":scenario["logs"]},
                {"id":"metrics:1", "type":"metrics", "source":"mock-telemetry", "data":scenario["metrics"]}]
    calls = [{"tool":"get_logs", "status":"ok"}, {"tool":"get_metrics", "status":"ok"}]
    return evidence, calls

def simulate(incident_id: str, approval_id: str, scenario: dict, action: str) -> dict:
    # No shell, subprocess, network, or Kubernetes writes. Action derived from trusted fixtures.
    if action not in ALLOWED_ACTIONS or action != scenario["action"]:
        raise HTTPException(403, "Action outside the scenario allowlist")
    before = dict(scenario["metrics"])
    after = dict(before)
    outcomes = {
        "tune_pool":{"db_active":15,"pool_size":30},
        "rollback_deployment":{"error_rate":0.001,"deployment_version":1},
        "increase_memory":{"memory_percent":60,"restart_count":7},
        "scale_deployment":{"cpu_percent":55,"replicas":3},
        "clean_archives":{"disk_percent":55,"archive_gb":0},
        "reconnect_cache":{"cache_error_rate":0,"redis_available":1},
        "scale_consumers":{"consumer_lag":100,"consumers":3},
        "renew_certificate":{"tls_failures":0,"certificate_days_remaining":90},
        "refresh_dns":{"dns_failures":0,"dns_ttl_seconds":60},
        "enable_backoff":{"upstream_429":0,"retry_delay_seconds":30},
    }
    after.update(outcomes[action])
    receipt = hashlib.sha256(f"{incident_id}:{approval_id}:{action}".encode()).hexdigest()
    return {"success":True, "simulated":True, "receipt":receipt, "action":action,
            "before":before, "after":after, "verification":"Expected simulated metric changes applied; no real infrastructure was changed."}
