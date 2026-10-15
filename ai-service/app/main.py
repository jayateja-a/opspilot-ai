import logging
import secrets
import time
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException
from .config import settings
from .models import Analyze, Execute, RunbookInput, AnalysisResult
from . import retrieval, tools
from .reasoning import reason

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opspilot-agent")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.agent_token:
        raise RuntimeError("AGENT_TOKEN required")
    if settings.ai_mode == "openai" and not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required in openai mode")
    for attempt in range(15):
        try:
            retrieval.seed()
            break
        except Exception:
            if attempt == 14:
                raise
            logger.warning("Waiting for migrated database; attempt %s", attempt+1)
            # Startup only. Request handlers have bounded connection/HTTP timeouts.
            import asyncio
            await asyncio.sleep(2)
    yield

app = FastAPI(title="OpsPilot AI Agent", version="0.1.0", lifespan=lifespan)

def authorize(x_agent_token: str = Header(default="")):
    if not secrets.compare_digest(x_agent_token, settings.agent_token):
        raise HTTPException(401,"Unauthorized")

@app.get("/health")
def health():
    try:
        with retrieval.connect() as db:
            db.execute("SELECT 1")
        return {"status":"UP", "mode":settings.ai_mode}
    except Exception:
        raise HTTPException(503,"Database unavailable")

@app.get("/v1/scenarios", dependencies=[Depends(authorize)])
def scenarios():
    return [{k:s[k] for k in ("id","service","title","severity","description")} for s in tools.SCENARIOS.values()]

@app.get("/v1/runbooks", dependencies=[Depends(authorize)])
def runbooks():
    return retrieval.list_runbooks()

@app.post("/v1/runbooks", dependencies=[Depends(authorize)], status_code=201)
def ingest(request: RunbookInput):
    if request.id.startswith("rb-"):
        raise HTTPException(409,"Built-in runbook IDs are reserved; use a custom ID")
    try:
        return retrieval.ingest(request.model_dump())
    except Exception:
        logger.exception("Runbook ingestion failed")
        raise HTTPException(502,"Runbook ingestion failed")

@app.post("/v1/analyze", dependencies=[Depends(authorize)], response_model=AnalysisResult)
def analyze(request: Analyze):
    started = time.monotonic()
    scenario = tools.scenario_for(request.scenario_id, request.service)
    evidence, calls = tools.collect(scenario)
    try:
        citations = retrieval.retrieve(request.service, request.description + " " + str(evidence))
    except Exception:
        logger.exception("Retrieval failed")
        raise HTTPException(503,"Retrieval unavailable")
    calls.append({"tool":"retrieve_runbooks", "status":"ok", "count":len(citations)})
    supported = scenario is not None and any(c["runbook_id"] == scenario["expected_runbook"] for c in citations)
    warnings = ["All telemetry and remediation are simulated."]
    root_cause = "Insufficient evidence to identify a root cause."
    reasoning = "Collect actual telemetry and a matching runbook before proposing an executable action."
    confidence = 0.0
    if supported:
        if settings.ai_mode == "openai":
            try:
                hypothesis = reason(request.description, evidence, citations)
                root_cause, reasoning, confidence = hypothesis.root_cause, hypothesis.reasoning, hypothesis.confidence
            except Exception:
                logger.exception("LLM reasoning failed")
                raise HTTPException(502,"LLM unavailable or ungrounded response; no recommendation issued")
        else:
            root_cause = scenario["root_cause"]
            reasoning = "The selected reproducible scenario's logs and metrics match the retrieved runbook. This is rule-based demo reasoning, not an LLM diagnosis."
            confidence = 0.9
            warnings.append("Demo confidence is a fixed fixture score, not a calibrated probability.")
    rec = {"action":scenario["action"] if supported else "manual_review",
           "risk":scenario["risk"] if supported else "HIGH", "executable":supported,
           "human_approval_required":True,
           "explanation":"Approve only after reviewing evidence, capacity, and rollback conditions." if supported else "No execution allowed without sufficient evidence."}
    logger.info("Analysis incident=%s mode=%s elapsed_ms=%s", request.incident_id, settings.ai_mode, round((time.monotonic()-started)*1000))
    return {"mode":settings.ai_mode,"root_cause":root_cause,"reasoning":reasoning,"confidence":confidence,
            "evidence":evidence,"citations":citations,"recommendation":rec,"tool_calls":calls,"warnings":warnings}

@app.post("/v1/execute", dependencies=[Depends(authorize)])
def execute(request: Execute):
    scenario = tools.scenario_for(request.scenario_id, request.service)
    if scenario is None:
        raise HTTPException(403,"No executable scenario")
    # Verify approval and exact persisted action, not merely the caller's boolean.
    with retrieval.connect() as db:
        row = db.execute("""SELECT i.analysis,i.status,i.service,i.scenario_id,a.decision FROM incidents i
            JOIN approvals a ON a.incident_id=i.id WHERE i.id=%s AND a.id=%s""",(request.incident_id,request.approval_id)).fetchone()
    if not row or row["decision"] != "APPROVE" or row["status"] not in ("APPROVED","RESOLVED"):
        raise HTTPException(403,"Persisted human approval required")
    if row["service"] != request.service or row["scenario_id"] != request.scenario_id or row["analysis"]["recommendation"]["action"] != request.action:
        raise HTTPException(403,"Approved action context mismatch")
    return tools.simulate(str(request.incident_id),str(request.approval_id),scenario,request.action)
