"""Black-box regression suite against Compose API, PostgreSQL/pgvector, Spring AI demo, and lab."""
import os, uuid
from concurrent.futures import ThreadPoolExecutor
import httpx, pytest

pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Compose integration profile sets RUN_INTEGRATION=1")
BASE=os.getenv("API_BASE","http://127.0.0.1:8080/api")
TOKEN=os.getenv("API_TOKEN","local-demo-token")
SCENARIOS=["db-pool","bad-release","oom","cpu","disk","redis","kafka","certificate","dns","rate-limit"]
def call(method,path,body=None,expected=200):
    r=httpx.request(method,BASE+path,headers={"Authorization":"Bearer "+TOKEN},json=body,timeout=90,trust_env=False)
    assert r.status_code==expected,f"{method} {path}: {r.status_code} {r.text}"
    return r.json()
def create(sid="db-pool"):
    s=next(s for s in call("GET","/scenarios") if s["id"]==sid)
    return call("POST","/incidents",{"service":s["service"],"title":s["title"],"severity":s["severity"],"description":s["description"],"scenarioId":s["id"]},201)

@pytest.mark.parametrize("sid",SCENARIOS)
def test_itil_incident_investigation_approval_simulation_and_rca(sid):
    i=create(sid); iid=i["id"]
    assert i["status"]=="OPEN" and i["ticket_number"].startswith("INC-")
    assert i["priority"] in ("P1","P2","P3","P4") and i["affected_ci"]==i["service"]
    call("POST",f"/incidents/{iid}/execute",{},409)
    i=call("POST",f"/incidents/{iid}/analyze",{})
    assert i["status"]=="AWAITING_APPROVAL"
    a=i["analysis"]
    assert a["recommendation"]["executable"] and a["recommendation"]["human_approval_required"]
    assert any(c["runbook_id"]=="rb-"+sid for c in a["citations"])
    assert len(a["evidence"])==2 and a["causal_graph"]["nodes"] and a["fix_graph"]["nodes"]
    assert i["rcaDocuments"] and i["rcaDocuments"][0]["status"]=="DRAFT"
    call("POST",f"/incidents/{iid}/analyze",{},409)
    i=call("POST",f"/incidents/{iid}/approval",{"decision":"APPROVE","reviewer":"e2e-operator","note":"Reviewed synthetic telemetry, impact, and rollback."})
    assert i["status"]=="APPROVED"
    i=call("POST",f"/incidents/{iid}/execute",{})
    assert i["status"]=="RESOLVED" and i["execution"]["result"]["simulated"]
    assert i["execution"]["result"]["before"]!=i["execution"]["result"]["after"]
    assert call("POST",f"/incidents/{iid}/execute",{})["execution"]==i["execution"]
    assert [e["event"] for e in i["events"]]==["INCIDENT_CREATED","ANALYSIS_COMPLETED","RCA_DRAFT_CREATED","HUMAN_APPROVE","SIMULATION_EXECUTED"]

def test_rejection_and_insufficient_evidence_are_non_executable():
    i=create(); iid=i["id"]
    call("POST",f"/incidents/{iid}/approval",{"decision":"APPROVE","reviewer":"x","note":"early"},409)
    call("POST",f"/incidents/{iid}/analyze",{})
    i=call("POST",f"/incidents/{iid}/approval",{"decision":"REJECT","reviewer":"operator","note":"Need more evidence"})
    assert i["status"]=="REJECTED"
    call("POST",f"/incidents/{iid}/execute",{},409)
    n=call("POST","/incidents",{"service":"unknown-service","title":"No telemetry","description":"Investigate the timeout","severity":"P3"},201)
    n=call("POST",f"/incidents/{n['id']}/analyze",{})
    assert not n["analysis"]["recommendation"]["executable"]
    call("POST",f"/incidents/{n['id']}/approval",{"decision":"APPROVE","reviewer":"x","note":"override"},409)

def test_auth_validation_config_items_and_record_not_found():
    assert httpx.get(BASE+"/incidents",trust_env=False).status_code==401
    assert {x["domain"] for x in call("GET","/configuration-items")}=={"FINTECH","HEALTHCARE"}
    call("POST","/incidents",{"service":"payment-service","title":"","description":"x","severity":"P0"},400)
    call("POST","/incidents",{"service":"wrong","title":"x","description":"x","severity":"P1","scenarioId":"db-pool"},400)
    call("GET","/incidents/"+str(uuid.uuid4()),expected=404)

def test_priority_is_derived_from_impact_and_urgency():
    i=call("POST","/incidents",{"service":"payment-service","title":"Broad outage","description":"Many users cannot complete payments","severity":"P3","impact":"HIGH","urgency":"HIGH","category":"AVAILABILITY","reportedBy":"synthetic-monitor","sourceChannel":"MONITORING"},201)
    assert i["priority"]=="P1" and i["major_incident"] is True
    assert i["category"]=="AVAILABILITY" and i["reported_by"]=="synthetic-monitor" and i["source_channel"]=="MONITORING"

def test_concurrent_execute_has_exactly_one_audit_receipt():
    i=create("cpu");iid=i["id"]
    call("POST",f"/incidents/{iid}/analyze",{})
    call("POST",f"/incidents/{iid}/approval",{"decision":"APPROVE","reviewer":"operator","note":"Reviewed"})
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(lambda _:call("POST",f"/incidents/{iid}/execute",{}),range(2)))
    assert results[0]["execution"]==results[1]["execution"]
    assert sum(e["event"]=="SIMULATION_EXECUTED" for e in results[1]["events"])==1

def test_runbook_vector_retrieval_and_idempotent_replace():
    book_id="custom-test-"+str(uuid.uuid4())
    payload={"id":book_id,"service":"isolated-test-service","title":"Database timeout procedure","content":"Inspect database pool metrics and PostgreSQL connection budget. "*60}
    result=call("POST","/runbooks",payload,201); assert result["chunks"]>1
    second=call("POST","/runbooks",payload,201); assert second["chunks"]==result["chunks"]
    i=call("POST","/incidents",{"service":"isolated-test-service","title":"Database timeout","description":"Database pool timeout and connection budget","severity":"P2"},201)
    i=call("POST",f"/incidents/{i['id']}/analyze",{})
    citations=i["analysis"]["citations"]
    assert citations and citations[0]["runbook_id"]==book_id
    assert not i["analysis"]["recommendation"]["executable"]

def test_problem_and_change_management_lifecycle():
    i=create();iid=i["id"]
    problem=call("POST","/problems",{"title":"Recurring connection exhaustion","description":"Investigate recurring payment database saturation","rootCause":"Pool under-sized","workaround":"Drain idle sessions","incidentId":iid},201)
    assert problem["ticket_number"].startswith("PRB-")
    change=call("POST","/changes",{"title":"Increase payment pool capacity","description":"Increase DB pool with staged verification","changeType":"NORMAL","risk":"MEDIUM","impact":"MEDIUM","implementationPlan":"Change pool cap and observe","rollbackPlan":"Restore the previous cap","incidentId":iid},201)
    assert change["ticket_number"].startswith("CHG-")
    call("POST",f"/changes/{change['id']}/transition",{"status":"AUTHORIZED","reviewer":"CAB"},409)
    change=call("POST",f"/changes/{change['id']}/transition",{"status":"ASSESSMENT","reviewer":"owner"})
    change=call("POST",f"/changes/{change['id']}/transition",{"status":"AUTHORIZED","reviewer":"CAB"})
    assert change["status"]=="AUTHORIZED"

def test_human_approved_rca_is_audited_and_promoted_to_rag():
    i=create("rate-limit");i=call("POST",f"/incidents/{i['id']}/analyze",{})
    draft=i["rcaDocuments"][0]
    approved=call("POST",f"/rca/{draft['id']}/review",{"approve":True,"reviewer":"problem-manager"})
    assert approved["status"]=="APPROVED"
    details=call("GET",f"/incidents/{i['id']}")
    assert any(e["event"]=="RCA_APPROVED" for e in details["events"])
    assert any(book["id"]=="rca-"+draft["id"] for book in call("GET","/runbooks"))
