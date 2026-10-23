"""Black-box tests for the local multi-container commerce workload."""
import json
import os
import pathlib
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

APP = Path(__file__).with_name("commerce_lab.py")
TOKEN = "test-lab-token"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(url, path, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    if token: headers["X-Lab-Token"] = token
    req = urllib.request.Request(url + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_generated_commerce_traffic_observes_pool_exhaustion_and_queue_backlog():
    ports = {role: free_port() for role in ("inventory", "checkout", "storefront", "controller")}
    urls = {role: f"http://127.0.0.1:{port}" for role, port in ports.items()}
    envs = {
        "inventory": {},
        "checkout": {"INVENTORY_URL": urls["inventory"], "LAB_TOKEN": TOKEN, "DB_POOL_SIZE": "3"},
        "storefront": {"CHECKOUT_URL": urls["checkout"]},
        "controller": {"CHECKOUT_URL": urls["checkout"], "STOREFRONT_URL": urls["storefront"],
                       "INVENTORY_URL": urls["inventory"], "LAB_TOKEN": TOKEN},
    }
    processes = []
    try:
        for role in ("inventory", "checkout", "storefront", "controller"):
            env = os.environ.copy()
            env.update(envs[role]); env.update({"ROLE": role, "PORT": str(ports[role])})
            processes.append(subprocess.Popen([sys.executable, str(APP)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for role in urls:
            deadline = time.time() + 8
            while time.time() < deadline:
                if processes[list(urls).index(role)].poll() is not None:
                    raise AssertionError(f"{role} service exited during startup")
                try:
                    if request(urls[role], "/health")[0] == 200: break
                except Exception: time.sleep(.05)
            else: raise AssertionError(f"{role} service did not become healthy")

        assert request(urls["controller"], "/ops/faults", "POST", {"scenario_id": "commerce-db-pool"}, TOKEN)[0] == 200
        def shop(_): return request(urls["storefront"], "/shop")[0]
        with ThreadPoolExecutor(max_workers=12) as pool:
            statuses = list(pool.map(shop, range(24)))
        assert 503 in statuses and 202 in statuses
        observed = request(urls["controller"], "/ops/telemetry")[1]
        assert observed["domain"] == "ecommerce"
        assert observed["metrics"]["database_pool_size"] == 3
        assert observed["metrics"]["errors_total"] > 0
        assert any("connection pool wait timed out" in line for line in observed["logs"])

        request(urls["controller"], "/ops/faults", "POST", {"scenario_id": "commerce-queue-backlog"}, TOKEN)
        for _ in range(8): request(urls["storefront"], "/shop")
        observed = request(urls["controller"], "/ops/telemetry")[1]
        assert observed["metrics"]["queue_backlog"] >= 8
        assert observed["services"]["checkout"]["queue_processed_total"] >= 0
        request(urls["controller"], "/ops/faults", "POST", {"scenario_id": None}, TOKEN)
        deadline = time.time() + 3
        while time.time() < deadline:
            observed = request(urls["controller"], "/ops/telemetry")[1]
            if observed["metrics"]["queue_backlog"] == 0: break
            time.sleep(.05)
        assert observed["metrics"]["queue_backlog"] == 0

        # Exercise every additional fault injector and prove its family-specific
        # measurement is collected from a running service.
        catalog = json.loads((APP.parents[1] / "fixtures" / "incidents.json").read_text())
        exercised = {"db-pool", "queue-backlog"}
        for scenario in catalog:
            family = scenario.get("fault_family")
            if not family or family in exercised: continue
            exercised.add(family)
            activated=request(urls["controller"], "/ops/faults", "POST", {"scenario_id": scenario["id"]}, TOKEN)
            assert activated[0] == 200, f"{scenario['id']} activation failed: {activated}"
            for _ in range(6): request(urls["storefront"], "/shop")
            observed = request(urls["controller"], "/ops/telemetry")[1]["metrics"]
            key = scenario["runtime_signal"]
            value = observed.get("queue_backlog", 0) if key == "queue_backlog" else observed.get("fault_signals", {}).get(key, 0)
            assert value >= scenario.get("runtime_min", 1), f"{scenario['id']} {key}={value}: {observed}"
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try: process.wait(timeout=3)
            except subprocess.TimeoutExpired: process.kill()
