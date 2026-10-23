# API and State Contract

All `/api/*` routes require `Authorization: Bearer <API_TOKEN>`. The local frontend proxy supplies this header. Swagger's Authorize button accepts the raw token.

| Method | Route | Behavior |
|---|---|---|
| GET/POST | `/api/incidents` | List latest incidents / create ITIL-inspired ticket; create returns 201 |
| GET | `/api/incidents/{id}` | Ticket, analysis, approval, execution, RCA drafts, and audit events |
| POST | `/api/incidents/{id}/analyze` | Collect lab telemetry, retrieve runbooks, propose diagnosis and RCA |
| POST | `/api/incidents/{id}/approval` | Persist `APPROVE` or `REJECT` with reviewer and note |
| POST | `/api/incidents/{id}/execute` | Run allowlisted simulation only after persisted approval; idempotent after resolution |
| GET | `/api/scenarios` | Ten synthetic scenario summaries |
| GET/POST | `/api/runbooks` | List and ingest custom runbook content for retrieval |
| GET | `/api/configuration-items` | Local fintech and healthcare CI inventory |
| GET/POST | `/api/problems` | List and create Problem records; optional linked incident |
| GET/POST | `/api/changes` | List and create Change records; optional linked incident |
| POST | `/api/changes/{id}/transition` | Move change through validated assessment/authorization/implementation/review states |
| GET | `/api/incidents/{id}/rca` | List saved RCA documents |
| POST | `/api/rca/{id}/review` | Mark an RCA reviewed or approve it for RAG reference reuse |
| GET | `/actuator/health` | Backend health |
| GET | `/v3/api-docs` | Generated OpenAPI document |

Incident creation accepts service/title/description/severity (`P1`/`P2`/`P3`) and optional `scenarioId`. The response includes `INC-` ticket number, impact, urgency, priority, category, affected CI, and major-incident flag. Investigation returns observed `evidence`, retrieved `citations`, a root-cause hypothesis, recommendation, `causal_graph`, `fix_graph`, and resolution classification. In demo mode the diagnosis and token-hash embeddings are deterministic. Provider mode validates model evidence and runbook citations before returning a supported proposal.

Execution results are labeled simulated and include before/after metric snapshots and a stable receipt. RCA promotion copies the reviewed summary into the runbook retrieval library; it does not train the model.

Invalid payloads return 400; missing/invalid tokens return 401; unknown records return 404; invalid lifecycle transitions return 409. An investigation failure is persisted as `ANALYSIS_FAILED`, which clients must inspect. Decision labels and notes are required. One decision is allowed per incident in this MVP.
