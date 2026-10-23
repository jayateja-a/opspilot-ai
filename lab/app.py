"""Synthetic fintech/healthcare workload used only by the isolated local lab."""
import json, os, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DOMAIN=os.getenv("DOMAIN","fintech")
TOKEN=os.getenv("LAB_TOKEN","local-lab-token")
FIXTURES=json.loads((Path(__file__).parents[1]/"fixtures"/"incidents.json").read_text())
HEALTHCARE={"oom","certificate","dns"}
ALLOWED={s["id"] for s in FIXTURES if ((s["id"] in HEALTHCARE)==(DOMAIN=="healthcare"))}
state={"scenario":None,"requests":0,"started_at":time.time()}
lock=threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): return
    def send_json(self,status,data):
        body=json.dumps(data).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=="/health": return self.send_json(200,{"status":"UP","domain":DOMAIN})
        if self.path=="/ops/telemetry":
            with lock: active=state["scenario"]; count=state["requests"]
            scenario=next((s for s in FIXTURES if s["id"]==active),None)
            return self.send_json(200,{"domain":DOMAIN,"service":"payment-service" if DOMAIN=="fintech" else "patient-record-service","scenario_id":active,"logs":scenario["logs"] if scenario else ["Synthetic service healthy"],"metrics":{**(scenario["metrics"] if scenario else {}),"request_count":count},"observed_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())})
        if self.path in ("/payments","/api/payments") and DOMAIN=="fintech": return self.workload("payment")
        if self.path in ("/fhir/Patient","/api/patients") and DOMAIN=="healthcare": return self.workload("patient")
        return self.send_json(404,{"error":"Not found"})
    def workload(self,kind):
        with lock: state["requests"]+=1; active=state["scenario"]
        if active=="bad-release": return self.send_json(503,{"error":"synthetic release regression","kind":kind})
        if active=="db-pool": time.sleep(.03)
        return self.send_json(200,{"status":"ok","domain":DOMAIN,"resource":kind,"synthetic":True})
    def do_POST(self):
        if self.path=="/ops/faults":
            if self.headers.get("X-Lab-Token","")!=TOKEN: return self.send_json(401,{"error":"Unauthorized"})
            try: data=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0")))); sid=data.get("scenario_id")
            except Exception: return self.send_json(400,{"error":"Invalid JSON"})
            if sid is not None and sid not in ALLOWED: return self.send_json(422,{"error":"Scenario is not allowlisted for this lab domain"})
            with lock: state["scenario"]=sid
            return self.send_json(200,{"domain":DOMAIN,"scenario_id":sid,"active":sid is not None})
        return self.send_json(404,{"error":"Not found"})

if __name__=="__main__": ThreadingHTTPServer(("0.0.0.0",8081),Handler).serve_forever()
