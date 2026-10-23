# Architecture

## Runtime topology

```mermaid
flowchart TD
  UI["React dashboard"] --> API["Spring Boot API"]
  API --> DB["PostgreSQL + pgvector"]
  API --> FIN["Fintech synthetic lab"]
  API --> HC["Healthcare synthetic lab"]
  API --> AI["Spring AI provider, optional"]
```

Compose starts PostgreSQL, two isolated synthetic lab containers, Spring Boot, and the frontend. The test profile runs lab unit tests and black-box API regression tests against the same stack.

## Investigation flow

```mermaid
sequenceDiagram
  participant H as Human
  participant UI as React UI
  participant S as Spring Boot
  participant L as Synthetic lab
  participant P as PostgreSQL/pgvector
  H->>UI: Create incident and request investigation
  UI->>S: Incident API request
  S->>L: Activate named fault and read telemetry
  S->>P: Search runbook vectors by service and model
  S->>S: Build diagnosis and remediation proposal
  S->>P: Persist evidence, RCA draft, and audit event
  S-->>UI: Report, diagrams, approval request
  H->>UI: Approve or reject
  UI->>S: Persist human decision
  S->>P: Audit decision and simulated verification
```

## Components
| Component | Responsibility |
|---|---|
| `Api.java` | Bearer-protected incidents, runbooks, configuration items, problem/change records, and RCA review |
| `IncidentService` | Incident state machine, ticket metadata, orchestration, approval checks, simulation, audit, RCA draft creation |
| `AgentClient` | Spring AI adapter, deterministic embeddings/diagnosis, OpenAI embeddings/chat, pgvector SQL search, allowlisted simulated outcomes |
| `LabClient` | Select lab by scenario domain, activate only allowlisted faults, fetch synthetic telemetry |
| `ItsmService` | CI inventory, linked problem/change records, guarded change transitions, RCA review and RAG promotion |
| `lab/app.py` | Synthetic HTTP workload, fault controls, logs, metrics, domain endpoints |
| PostgreSQL/Flyway | Ticket and workflow records, JSON evidence, audit, runbooks and 1536-dimension vector chunks |
| React | Light dashboard for queue, report, evidence, approval/rejection, runbooks and audit history |

## Storage and RAG
`V1__schema.sql` creates incident/workflow/runbook schema and pgvector. `V2__itsm_records.sql` adds ITIL fields, CIs, problem/change tables, links, and RCA records. Flyway owns schema changes.

Runbooks are split into overlapping chunks stored with embedding model identifiers. Retrieval filters by service/model and sorts by cosine distance. Demo embeddings are deterministic token-hash vectors for repeatable tests; they are not semantically equivalent to learned embeddings. OpenAI mode uses Spring AI's embedding model. Reviewed RCA summaries may become retrieval text; this does not train/fine-tune a model.

## Trust boundaries
The browser uses the local Spring API through the frontend proxy. API requests use a local bearer token. Fault-control requests use a separate token and scenario allowlists. Lab containers have no Docker socket or host mount. The external AI provider is contacted only in `openai` mode.

## Limitations
The lab is synthetic and fixture-driven, not a production-like financial/healthcare application. Lab fault state is singleton and intended for a single-user local demo. ITIL fields/workflows are a lightweight local model, not every ITIL practice or a certified ITSM integration.
