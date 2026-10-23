# Product Task Plan

## Delivered in the local MVP
- [x] Spring Boot API, local bearer protection, and Flyway schema.
- [x] Spring AI provider adapter with deterministic demo mode and optional OpenAI chat/embeddings.
- [x] PostgreSQL/pgvector runbook chunking and retrieval.
- [x] Ten synthetic fintech/healthcare incident scenarios.
- [x] Cooperating e-commerce storefront, checkout, inventory, continuous traffic generator, and 12 measurable fault families with P0-P5 catalog variants.
- [x] Provider-backed labeled AI evaluation report for diagnosis, runbook, grounding, action, signal, latency, and confidence metrics.
- [x] Isolated fintech and healthcare workload containers with allowlisted faults, logs, metrics, and endpoints.
- [x] ITIL-inspired incident number, impact, urgency, derived priority, CI, and major-incident marker.
- [x] Human approve/reject, allowlisted simulation, audit, and idempotent execution.
- [x] RCA draft persistence/review and human-approved RAG promotion.
- [x] Problem and Change records, incident links, guarded change transitions.
- [x] Light responsive React dashboard with causal and fix diagrams.
- [x] Backend, frontend, lab, Compose regression test paths and CI workflow.
- [x] Product, architecture, safety, design, task, and memory docs.

## Next engineering phase
1. Replace remaining fintech/healthcare scenario fixtures with configurable workloads and event streams while retaining safe defaults.
2. Add CI relationship/dependency maps and cross-service impact propagation.
3. Add OpenTelemetry/Prometheus and ticketing adapters behind explicit configuration.
4. Add role identity, reviewer separation, tenant isolation, secret management, and audit retention before shared deployment.
5. Improve RAG evaluation with labeled queries, recall/grounding tests, embedding migration, and access filters.
6. Expand Problem lifecycle, known-error database, CAB scheduling, blackout windows, and emergency change controls.
7. Add RCA templates/export, reviewer comments, versioning, and knowledge expiry/ownership.
8. Add browser E2E, performance, accessibility, mutation tests, and coverage reporting.
9. Validate full Compose integration in CI; Docker/Maven may be unavailable in local execution environments.
10. Threat-model and design production deployment separately; cloud/Kubernetes remains out of scope.
