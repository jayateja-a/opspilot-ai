"""Unit tests for the safe, deterministic synthetic service lab."""
import os, sys, threading, time, urllib.request, urllib.error, json
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import app

def client(domain):
    handler=app.Handler
    old_domain=app.DOMAIN
    old_allowed=app.ALLOWED
    app.DOMAIN=domain
    app.ALLOWED={s["id"] for s in app.FIXTURES if ((s["id"] in app.HEALTHCARE)==(domain=="healthcare"))}
    server=ThreadingHTTPServer(("127.0.0.1",0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,thread,(old_domain,old_allowed)

def request(server,path,method="GET",payload=None,token=None):
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(f"http://127.0.0.1:{server.server_port}{path}",data=data,method=method,headers={"Content-Type":"application/json",**({"X-Lab-Token":token} if token else {})})
    try:
        with urllib.request.urlopen(req,timeout=2) as r:return r.status,json.loads(r.read())
    except urllib.error.HTTPError as e:return e.code,json.loads(e.read())

def test_domain_fault_allowlist_auth_and_recovery():
    server,_,old=client("fintech")
    try:
        assert request(server,"/ops/faults","POST",{"scenario_id":"oom"},app.TOKEN)[0]==422
        assert request(server,"/ops/faults","POST",{"scenario_id":"db-pool"},"bad")[0]==401
        assert request(server,"/ops/faults","POST",{"scenario_id":"bad-release"},app.TOKEN)[0]==200
        assert request(server,"/payments")[0]==503
        assert request(server,"/ops/faults","POST",{},app.TOKEN)[0]==200
        assert request(server,"/payments")[0]==200
    finally:server.shutdown();app.DOMAIN=old[0];app.ALLOWED=old[1]

def test_healthcare_endpoint_is_synthetic_and_fault_scoped():
    server,_,old=client("healthcare")
    try:
        assert request(server,"/fhir/Patient")[1]["synthetic"] is True
        assert request(server,"/ops/faults","POST",{"scenario_id":"certificate"},app.TOKEN)[0]==200
        assert request(server,"/ops/telemetry")[1]["domain"]=="healthcare"
    finally:server.shutdown();app.DOMAIN=old[0];app.ALLOWED=old[1]
