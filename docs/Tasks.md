# Implementation and verification tasks

Updated: 2026-10-15. `[x]` means implemented/previously checked as stated; `[ ]` means still open. This is a status/backlog document, not permission to expand the project automatically.

## Local MVP build sequence — complete

| Step | Status | Deliverable and acceptance |
| --- | --- | --- |
| M1 | [x] | Shared lifecycle/schema: Flyway creates incidents, approvals, executions, audit records, and vector tables |
| M2 | [x] | Java APIs: create/read/investigate/decide/execute routes with validation and persisted transitions |
| M3 | [x] | Python evidence tools: ten fixture scenarios return reproducible logs and metrics |
| M4 | [x] | Retrieval: ingest/chunk/embed runbooks and run service/model-filtered pgvector search |
| M5 | [x] | Analysis modes: deterministic demo plus optional OpenAI embeddings/diagnosis with mocked provider tests |
| M6 | [x] | Human control: approve/reject; verify saved approval/context; simulate allowlisted actions and store receipts |
| M7 | [x] | React workspace: incident creation, analysis/evidence/activity, decisions, execution, runbook ingestion |
| M8 | [x] | Packaging/checks: Dockerfiles, Compose, setup guide, tests, architecture, and troubleshooting |
| M9 | [x] | AI handoff docs: PRD, architecture, rules, design, task status, and concise project memory |

The ten covered scenario IDs are listed in [architecture.md](architecture.md). Detailed historical test evidence is in [VERIFICATION.md](VERIFICATION.md); do not interpret M8 as a claim that Docker itself was run.

## Next validation, in order

- [ ] **V1 — Verify Compose locally.** Start with `docker compose up --build -d --wait --wait-timeout 300`, then run `docker compose --profile test run --build --rm tests`. Acceptance: services healthy, all workflow checks pass, and restart preserves records. Requires a Docker-capable environment.
- [ ] **V2 — Verify the optional live provider.** Only with the user's configured key and authorization for API usage, follow the README's OpenAI-mode instructions. Acceptance: actual 1536-dimension embeddings, valid grounded-reference diagnosis, and useful failure handling are observed. Keep demo behavior intact. This does not block key-free demo use.

## Scoped follow-ups — proposed, not implemented

- [ ] **F1 — Mobile navigation.** Add a compact menu linking both workspace pages below 500 pixels; verify keyboard operation and the 390-pixel runbook journey. See [Design.md](Design.md).
- [ ] **F2 — Provider time budget.** Align total embedding/diagnosis latency with the Java request deadline or introduce a separately designed background-job workflow. Test the slow-provider path before marking done.

## Future phases — only after a new scope decision

| Order | Proposed phase | Completion evidence needed |
| --- | --- | --- |
| 1 | Controlled real telemetry / tool adapters | Read-only evidence from a local test environment; explicit source labels and permission boundaries |
| 2 | Agent orchestration / MCP where useful | Bounded plans, persisted state, allowed tool selection, recoverable failures |
| 3 | AI evaluations | Separate held-out cases; retrieval/diagnosis/grounding/safety, latency, and cost measurements |
| 4 | Observability | Trace Java → Python → retrieval/provider/tool calls; useful metrics/log correlation |
| 5 | Production readiness and deployment | Real identity/RBAC, durable jobs, hardened execution, CI/CD, and a reviewed deployment/cost plan |

Do not silently add LangGraph, MCP, Kubernetes actions, Terraform, AWS, or real remediation while completing an unrelated MVP task.

## Per-task workflow

Read `memory.md` → `rules.md` → the relevant specification section → targeted source files. State the acceptance condition, implement the smallest complete change, and run relevant checks. Update only affected docs and the short memory ledger. Report blockers precisely; never convert an unrun check into a passed checkbox.
