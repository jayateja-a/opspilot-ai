# Product requirements — OpsPilot AI

Status: implemented Local MVP. Updated: 2026-10-15.

## Product and purpose

OpsPilot AI is an incident investigation and workflow automation workspace built with Java/Spring Boot, Python/FastAPI, PostgreSQL/pgvector, and React. It connects incident records, operational procedures, evidence, diagnosis text, human decisions, and simulated remediation in one auditable workflow.

Engineers investigating an incident usually switch between logs, metrics, runbooks, and incident records. This product demonstrates how to collect that context and present a reviewable proposal while keeping a person responsible for the decision. Reducing investigation effort is the intended benefit; no production time-saving or accuracy improvement has been measured.

## Users and value

| User | Job to accomplish |
| --- | --- |
| On-call/SRE engineer | Review evidence and a proposed response to an incident |
| DevOps or application support engineer | Locate relevant procedures and document a decision |
| Developer/evaluator | Run reproducible incidents and inspect the integration and controls |

Current use is local development, learning, and portfolio demonstration. Potential future customers are teams operating multiple services; customer demand and willingness to pay have not been validated.

## Current requirements

| ID | Requirement | Acceptance condition |
| --- | --- | --- |
| FR-01 | Record incidents | Service, title, description, severity, UUID, timestamps, and status persist |
| FR-02 | Investigate supported scenarios | Retrieve fixture logs/metrics and relevant runbook chunks; return a hypothesis, citations, and proposal |
| FR-03 | Retrieve with pgvector | Chunk/embedding records persist; search filters by service and embedding model |
| FR-04 | Support two analysis modes | Demo needs no API key; optional OpenAI uses embeddings and schema-validated diagnosis text |
| FR-05 | Require a human decision | Reviewer and note required; approve/reject are enforced in the backend |
| FR-06 | Simulate allowed actions | Saved approval and matching context required; repeated execution returns the saved result |
| FR-07 | Show audit history | Creation, analysis, decision, and execution events appear chronologically |
| FR-08 | Ingest runbooks | Custom procedures are chunked and embedded; built-in identifiers cannot be overwritten through the API |

## Main user journey

1. Create one of ten sample incidents.
2. Investigate; inspect the hypothesis, telemetry, citations, and risk.
3. Enter a reviewer label and decision note.
4. Approve an executable plan or reject it.
5. Execute an approved simulation; inspect before/after values and audit history.

Missing telemetry produces a non-executable result. Rejection prevents execution. Analysis failure is recorded and may be retried.

## Operating requirements and boundaries

- Runs locally with persistent PostgreSQL storage and documented startup commands.
- Uses validated request fields, service tokens, and bounded database/HTTP connection timeouts.
- Presents loading, failure, approval, and resolved states clearly.
- Contains ten reproducible scenarios and automated unit/integration checks; see [verification evidence](VERIFICATION.md).
- Demo diagnosis/actions are fixture-driven. Demo vectors are lexical hashes; the fixed 0.90 score is not measured accuracy.
- OpenAI mode changes embeddings and diagnosis text; executable actions remain fixture-controlled.
- Remediation changes simulated values only. RESOLVED does not mean a real system recovered.
- No production login, RBAC, real infrastructure actions, autonomous planning, MCP, cloud deployment, or AI quality benchmark is included.

## Completion and change control

The implementation meets the Local MVP scope. Docker startup and live OpenAI calls remain unverified in this environment. Keep those validation gaps separate from implemented features. Use [Tasks.md](Tasks.md) for work status; any broader product phase needs an explicit user request.
