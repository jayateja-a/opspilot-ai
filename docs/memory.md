# Project Memory / Decisions

## Current state
OpsPilot is a local-only incident investigation MVP using Spring Boot + Spring AI + PostgreSQL/pgvector + React. Python is used only for standard-library synthetic domain lab containers and integration tests. The former FastAPI AI service is removed.

## Decisions
- Use Spring AI 1.1.x with Spring Boot 3.5.x and keep the provider behind a Java adapter.
- Default `AI_MODE=demo` is deterministic and needs no API key. Optional `AI_MODE=openai` uses Spring AI chat and embeddings.
- All lab workloads are synthetic and all remediation is simulated. No AWS/Kubernetes/production infrastructure or credentials.
- Use ITIL-inspired incident, problem, change, CI, approval, and RCA records; this is not a complete or certified ITIL implementation.
- Human approval is mandatory. Only fixture-allowlisted simulations run; receipts support idempotent retries.
- RCA becomes reusable retrieval content only after human approval. This is RAG, not model training.
- User prefers a light/white interface, smooth but restrained transitions, clear buttons, and readable cause/fix diagrams.
- The original published state was preserved in a pre-change backup ZIP dated 2026-10-23.

## Limits
The isolated lab has no Docker socket, host mounts, or real customer data. Fault controls are token-protected and domain-allowlisted. Lab fault state is single-user demo state. Production requires separately designed identity, isolation, integrations, secret management, retention, and infrastructure safeguards.
