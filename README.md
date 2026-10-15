# OpsPilot AI

A local incident investigation workspace built with **Java 17 / Spring Boot**, **FastAPI**, **React / TypeScript**, **PostgreSQL / pgvector**, and Docker Compose.

Create an incident → collect simulated logs and metrics → retrieve runbook chunks → analyze → review and approve → execute a bounded simulation → inspect verification and audit history.

## AI development handoff

Start a coding session with [docs/memory.md](docs/memory.md), then [docs/rules.md](docs/rules.md). Read only the relevant specification sections and source files for the assigned task; the other documents are references, not a mandatory full-context bundle.

| Document | Purpose |
| --- | --- |
| [docs/PRD.md](docs/PRD.md) | What is being built, why, users, scope, and acceptance conditions |
| [docs/architecture.md](docs/architecture.md) | End-to-end flow, ownership, contracts, source locations, and failure boundaries |
| [docs/rules.md](docs/rules.md) | Application AI limits and coding-assistant working rules |
| [docs/Design.md](docs/Design.md) | Visual direction, screens, interactions, responsive behavior, and UI constraints |
| [docs/Tasks.md](docs/Tasks.md) | Completed build sequence, open validation, and explicitly proposed future work |
| [docs/memory.md](docs/memory.md) | Short project checkpoint, decisions, resolved issues, and dated verification |

Suggested session instruction: "Read docs/memory.md and docs/rules.md first. For this task, load only the relevant spec sections and code. Preserve the Local MVP scope, implement the requested change, run relevant checks, and update affected docs with actual results."

These are ordinary Markdown files. Tell a new coding tool to read them; automatic loading depends on that tool. They reduce duplicated context through selective reading, not a guaranteed token reduction.

## Start in Docker

Install Docker Desktop (Windows/macOS) or Docker Engine with the Compose v2 plugin (Linux). Allow roughly 4 GB memory and several GB of disk for the first build. No OpenAI key is needed in demo mode.

```bash
cp .env.example .env
docker compose up --build -d --wait --wait-timeout 300
```

On Windows PowerShell, use `Copy-Item .env.example .env` for the first command. Run all commands from this repository's root.

- **Dashboard:** http://localhost:3000
- **Backend Swagger:** http://localhost:8080/swagger-ui/index.html — click Authorize and enter `local-demo-token` (or your `API_TOKEN`).
- **Backend health:** http://localhost:8080/actuator/health
- **PostgreSQL:** localhost:5432; defaults are in `.env.example`.
- The AI service runs on the internal Compose network at `agent:8000`.

Alternatively, on Linux/macOS: `bash scripts/start.sh`.

### Try the complete product

1. Open the dashboard and click **New incident**.
2. Select **Database pool exhaustion** and create it.
3. Click **Investigate incident**.
4. Inspect the hypothesis and **Evidence** tab, including runbook citations.
5. Enter your name and a decision note, then click **Approve plan**.
6. Click **Execute simulation**. Inspect before/after metrics and the **Activity** audit trail.
7. Try rejecting a different recommendation. Its action cannot execute.
8. Open **Runbook library** to ingest a custom procedure. Built-in `rb-` identifiers are reserved.

Each of the ten sample scenarios has simulated evidence, a matching runbook, a risk level, and a deterministic verified outcome. Instances you create remain in the PostgreSQL volume across restarts.

## Verify

```bash
bash scripts/verify.sh
```

Or on any platform:

```bash
docker compose up --build -d --wait --wait-timeout 300
docker compose --profile test run --build --rm tests
```

Backend and frontend tests run during their image builds. The test container runs Python unit tests and HTTP/database integration tests against the live services. It creates test incidents; it does not erase existing data.

Native commands, when you have Java 17+, Maven 3.9+, Python 3.12+, Node 22+, and a running PostgreSQL instance with pgvector:

```bash
cd backend
mvn verify
cd ../ai-service
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
cd ../frontend
npm ci
npm run build
npm test
```

For native development, first start the database with `docker compose up -d postgres`. Start the backend with `mvn spring-boot:run` in `backend/` (this applies Flyway migrations). Start `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` in `ai-service/`. Then run `npm run dev` in `frontend/` and open http://localhost:5173. Use a separate terminal for each. Default native credentials match `.env.example`; changed settings must be exported into each terminal because Maven, Vite, and the agent do not automatically read the root `.env`.

To run integration tests natively against those services, from the repository root:

```bash
RUN_INTEGRATION=1 python -m pytest -v scripts/e2e_test.py
```

On PowerShell, set `$env:RUN_INTEGRATION="1"` first, then run the Python command. The AI unit tests require `PYTHONPATH=ai-service` when invoked from the repository root.

### Optional browser smoke test

With the stack running, install Playwright locally and verify the product through Chromium:

```bash
cd frontend
npm install --no-save playwright
npx playwright install chromium
cd ..
node scripts/browser_smoke.mjs
```

This creates and resolves one simulated incident, checks the evidence and audit views, checks a 390-pixel mobile viewport for overflow, and writes screenshots into `docs/`. Set `UI_URL` if you changed the dashboard port.

## Demo mode and OpenAI mode

**Demo mode** uses a deterministic token-hashing vectorizer (1536 dimensions), real pgvector cosine retrieval, rule-based scenario diagnosis, and mock telemetry/remediation. It is fully offline after dependencies/images have downloaded. The demo's fixed 0.90 score is a fixture score, not a calibrated confidence probability. The application labels this clearly.

**OpenAI mode** replaces the vectorizer with OpenAI embeddings and the diagnosis text with schema-validated LLM reasoning grounded in supplied evidence and runbook references. Tools, risk levels, and approved actions remain constrained by the same trusted scenario allowlist. This is a fixed investigation pipeline; it does not implement autonomous planning, LangGraph, MCP, or real Kubernetes operations.

In `.env`, set:

```dotenv
AI_MODE=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

Then run `docker compose up -d --force-recreate agent`. This makes paid API calls to OpenAI for ten seed runbook embeddings on the first start and for subsequent analysis/retrieval/ingestion. An unavailable or invalid LLM response fails the analysis; no executable result is silently substituted. This optional live provider path was tested with mocked HTTP responses, not a real API key.

Embeddings are tagged by model and retrieval filters by that tag. Switching modes reindexes built-in runbooks at startup. Reingest your custom runbooks after switching modes or models. An embedding model must support 1536 dimensions and the configured reasoning model must support JSON schema responses.

## API example

```bash
curl -X POST http://localhost:8080/api/incidents \
  -H 'Authorization: Bearer local-demo-token' \
  -H 'Content-Type: application/json' \
  -d '{"service":"payment-service","title":"Database pool exhaustion","description":"Payment API latency is rising","severity":"P1","scenarioId":"db-pool"}'
```

Use the returned `id`:

```bash
curl -X POST http://localhost:8080/api/incidents/INCIDENT_ID/analyze -H 'Authorization: Bearer local-demo-token'
curl -X POST http://localhost:8080/api/incidents/INCIDENT_ID/approval \
  -H 'Authorization: Bearer local-demo-token' -H 'Content-Type: application/json' \
  -d '{"decision":"APPROVE","reviewer":"Local operator","note":"Reviewed logs, capacity, and rollback plan."}'
curl -X POST http://localhost:8080/api/incidents/INCIDENT_ID/execute -H 'Authorization: Bearer local-demo-token'
```

Incidents without `scenarioId` are supported by the API; without telemetry they produce a non-executable insufficient-evidence result. The dashboard creation dialog focuses on the ten reproducible scenarios.

## Repository

| Directory | Responsibility |
| --- | --- |
| `backend/` | Incident APIs, Flyway migrations, approval state machine, persisted audit/receipts, OpenAPI |
| `ai-service/app/` | Retrieval, embeddings, structured reasoning, evidence tools, approval verification, simulation |
| `frontend/` | Responsive incident workspace, decision form, citations, audit trail, runbook ingestion |
| `fixtures/` | Ten reproducible incidents and matching runbooks |
| `scripts/` | Start/stop/verification and full workflow integration tests |
| `docs/` | Architecture, API/state contract, troubleshooting and verification evidence |

## Boundaries

This is a localhost MVP. Host ports bind to `127.0.0.1`. The browser uses a local Nginx/Vite proxy that supplies the backend token; it is not a production login system. Reviewer names are operator-entered audit labels, not independently authenticated identities. The internal agent checks a service token and persisted approvals. Never expose these local demo proxies publicly.

All remediation is a simulation. No shell commands, cloud writes, or Kubernetes writes are executed. A resolved status means the simulation met its expected outcome; it does not mean a real service recovered. There are no AWS or Kubernetes production resources in this repository.

The control plane locks an incident row during each transition. External agent calls inside transitions are bounded by timeouts; this is acceptable at local MVP scale but should move to durable jobs/outbox processing before high-volume deployment. Repeated execution returns the saved receipt; concurrent execution produces one audit event. The simulation also returns a stable receipt after a lost response. That does not establish exactly-once semantics for future real tools.

## Stop and troubleshoot

`docker compose down` stops the stack and keeps data. `docker compose logs -f backend agent` shows service logs. If a port is occupied, stop its existing service or change only the host side of the Compose port mapping.

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md), [docs/architecture.md](docs/architecture.md), and [docs/VERIFICATION.md](docs/VERIFICATION.md).
