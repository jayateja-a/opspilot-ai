"""Small cooperating e-commerce services and a telemetry/fault controller.

All state and fault controls are deliberately local and synthetic. The workload
generator creates real HTTP requests between containers; telemetry is measured
from those requests rather than copied from incident fixtures.
"""
import json
import os
import queue
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROLE = os.getenv("ROLE", "controller")
PORT = int(os.getenv("PORT", "8081"))
TOKEN = os.getenv("LAB_TOKEN", "local-lab-token")
CHECKOUT = os.getenv("CHECKOUT_URL", "http://commerce-checkout:8081")
STOREFRONT = os.getenv("STOREFRONT_URL", "http://commerce-storefront:8081")
INVENTORY = os.getenv("INVENTORY_URL", "http://commerce-inventory:8081")
SERVICES = {"storefront": STOREFRONT, "checkout": CHECKOUT, "inventory": INVENTORY}

lock = threading.RLock()
fault = None
started = time.time()
requests = 0
errors = 0
latencies = deque(maxlen=500)
logs = deque(maxlen=100)
pool = threading.BoundedSemaphore(int(os.getenv("DB_POOL_SIZE", "3")))
pool_size = int(os.getenv("DB_POOL_SIZE", "3"))
db_active = 0
db_waiters = 0
pending = queue.Queue()
processed = 0
paused_worker = threading.Event()


def log(message):
    with lock:
        logs.append({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message": message})


def call(url, path, method="GET", payload=None, timeout=2):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url + path, data=data, method=method,
        headers={"Content-Type": "application/json"} if data is not None else {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try: body = json.loads(exc.read())
        except Exception: body = {"error": str(exc)}
        return exc.code, body


def worker():
    global processed
    while True:
        if paused_worker.is_set():
            time.sleep(.05)
            continue
        try: pending.get(timeout=.1)
        except queue.Empty: continue
        time.sleep(.04)
        with lock: processed += 1
        pending.task_done()


if ROLE == "checkout":
    threading.Thread(target=worker, daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def send_json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health": return self.send_json(200, {"status": "UP", "role": ROLE})
        if self.path == "/ops/telemetry": return self.send_json(200, self.telemetry())
        if ROLE == "inventory" and self.path == "/inventory/reserve":
            self.record("inventory", 200, 1)
            return self.send_json(200, {"reserved": True, "sku": "demo-item-1"})
        if ROLE == "storefront" and self.path in ("/shop", "/shop/checkout"):
            start = time.monotonic()
            status, body = call(CHECKOUT, "/checkout", "POST", {"sku": "demo-item-1"})
            self.record("checkout", status, time.monotonic() - start)
            return self.send_json(status, {"storefront": "synthetic", **body})
        return self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if ROLE == "controller" and self.path == "/ops/faults":
            if self.headers.get("X-Lab-Token", "") != TOKEN:
                return self.send_json(401, {"error": "Unauthorized"})
            try: body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            except Exception: return self.send_json(400, {"error": "Invalid JSON"})
            sid = body.get("scenario_id")
            if sid not in (None, "commerce-db-pool", "commerce-queue-backlog"):
                return self.send_json(422, {"error": "Scenario is not allowlisted for commerce lab"})
            status, result = call(CHECKOUT, "/ops/faults", "POST", {"scenario_id": sid})
            if status == 200 and sid is not None:
                # Let generated users exercise the fault before we snapshot evidence.
                time.sleep(float(os.getenv("TELEMETRY_SETTLE_SECONDS", ".9")))
            return self.send_json(status, result)
        if ROLE == "checkout" and self.path == "/ops/faults":
            try: sid = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0")))).get("scenario_id")
            except Exception: return self.send_json(400, {"error": "Invalid JSON"})
            if sid not in (None, "commerce-db-pool", "commerce-queue-backlog"):
                return self.send_json(422, {"error": "Scenario is not allowlisted for commerce lab"})
            global fault
            with lock: fault = sid
            if sid == "commerce-queue-backlog": paused_worker.set()
            else: paused_worker.clear()
            log("Fault activated: " + str(sid or "none"))
            return self.send_json(200, {"role": ROLE, "scenario_id": sid, "active": sid is not None})
        if ROLE == "checkout" and self.path == "/checkout":
            return self.checkout()
        return self.send_json(404, {"error": "Not found"})

    def checkout(self):
        global db_active, db_waiters
        start = time.monotonic()
        with lock: active_fault = fault
        if active_fault == "commerce-db-pool":
            with lock: db_waiters += 1
            acquired = pool.acquire(timeout=.08)
            with lock: db_waiters -= 1
            if not acquired:
                elapsed = time.monotonic() - start
                self.record("db_pool_exhausted", 503, elapsed)
                log("checkout rejected: database connection pool wait timed out")
                return self.send_json(503, {"error": "synthetic database pool exhausted"})
            with lock: db_active += 1
            time.sleep(.45)
            with lock: db_active -= 1
            pool.release()
        status, inventory = call(INVENTORY, "/inventory/reserve")
        if status >= 400:
            self.record("inventory_failure", status, time.monotonic() - start)
            return self.send_json(503, {"error": "inventory dependency unavailable"})
        pending.put({"order": "synthetic", "sku": inventory["sku"]})
        self.record("checkout", 202, time.monotonic() - start)
        return self.send_json(202, {"accepted": True, "order": "synthetic-order", "inventory_reserved": True})

    def record(self, message, status, seconds):
        global requests, errors
        with lock:
            requests += 1
            if status >= 500: errors += 1
            latencies.append(seconds * 1000)
        log(f"{message} status={status} latency_ms={seconds * 1000:.1f}")

    def telemetry(self):
        with lock:
            times = list(latencies)
            result = {"service": ROLE, "requests_total": requests, "errors_total": errors,
                "error_rate": round(errors / requests, 3) if requests else 0,
                "latency_ms_avg": round(sum(times) / len(times), 2) if times else 0,
                "uptime_seconds": round(time.time() - started, 1), "logs": list(logs)}
            if ROLE == "checkout":
                result.update({"database_pool_size": pool_size, "database_connections_active": db_active,
                    "database_waiters": db_waiters, "queue_backlog": pending.qsize(),
                    "queue_processed_total": processed, "active_fault": fault})
            return result


def run_controller():
    services = {}
    for name, url in SERVICES.items():
        try: services[name] = call(url, "/ops/telemetry")[1]
        except Exception as exc: services[name] = {"service": name, "unavailable": str(exc), "logs": []}
    checkout = services.get("checkout", {})
    logs_out = [f"[{name}] {item['message']}" for name, info in services.items() for item in info.get("logs", [])]
    metrics = {"services": services, "requests_total": sum(x.get("requests_total", 0) for x in services.values()),
        "errors_total": sum(x.get("errors_total", 0) for x in services.values()),
        "checkout_error_rate": checkout.get("error_rate", 0), "checkout_latency_ms_avg": checkout.get("latency_ms_avg", 0),
        "database_pool_size": checkout.get("database_pool_size", 0),
        "database_connections_active": checkout.get("database_connections_active", 0),
        "database_waiters": checkout.get("database_waiters", 0), "queue_backlog": checkout.get("queue_backlog", 0),
        "queue_processed_total": checkout.get("queue_processed_total", 0)}
    observed = next((sid for sid in ("commerce-db-pool", "commerce-queue-backlog") if sid == checkout.get("active_fault")), None)
    return {"domain": "ecommerce", "service": "checkout-service", "scenario_id": observed,
        "logs": logs_out[-200:], "metrics": metrics, "services": services,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


if __name__ == "__main__":
    if ROLE == "loadgen":
        interval = float(os.getenv("TRAFFIC_INTERVAL_SECONDS", ".12"))
        users = int(os.getenv("TRAFFIC_USERS", "12"))
        def user_loop(user_id):
            while True:
                try: call(STOREFRONT, "/shop", timeout=2)
                except Exception as exc: log(f"synthetic-user-{user_id} request failed: {exc}")
                time.sleep(interval)
        for user_id in range(users):
            threading.Thread(target=user_loop, args=(user_id,), daemon=True).start()
        while True: time.sleep(60)
    elif ROLE == "controller":
        # Controller endpoint behavior is handled by the custom wrapper below.
        class Controller(Handler):
            def do_GET(self):
                if self.path == "/ops/telemetry": return self.send_json(200, run_controller())
                return super().do_GET()
        ThreadingHTTPServer(("0.0.0.0", PORT), Controller).serve_forever()
    else:
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
