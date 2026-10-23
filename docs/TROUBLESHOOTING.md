# Troubleshooting

| Symptom | Check / action |
|---|---|
| Docker unavailable | Install and start Docker Desktop or Docker Engine + Compose v2. |
| Port already allocated | Check localhost ports 3000, 8080, 5432; change the host-side port or stop the conflicting service. |
| Lab unhealthy during startup | Inspect `docker compose logs fintech-lab healthcare-lab`; each service serves `/health` on port 8081 inside its container. |
| Commerce telemetry unavailable | Inspect `docker compose ps commerce-inventory commerce-checkout commerce-storefront commerce-controller commerce-load-generator` and their logs. The controller serves `/ops/telemetry`; faults are controlled through it. |
| Vector extension missing | Use the supplied `pgvector/pgvector:pg16` image. Native PostgreSQL must have pgvector installed before Flyway starts. |
| Backend unhealthy | Inspect `docker compose logs backend postgres`. Flyway failures stop startup; add a new migration instead of editing an applied version. |
| Analysis failed | Check the incident's `last_error`, inspect backend logs, and verify database/lab connectivity. Retry after correcting the cause. |
| OpenAI analysis fails | Confirm `AI_MODE=openai`, a valid `OPENAI_API_KEY`, allowed provider egress, and supported model names. Demo mode requires no key. |
| Approval disabled | A supported proposal must be executable and reviewer/note must be nonblank. Unknown incidents without evidence cannot be approved. |
| Cannot execute | Confirm incident status is `APPROVED`, persisted approval exists, and approved action context matches. |
| RCA is absent from retrieval | Review the draft first; only a human-approved RCA is promoted as retrieval material. |
| Custom runbook retrieval changes after mode switch | Reingest it so vectors are generated for the active embedding model. |
| Lab rejects a scenario | Check that the scenario belongs to the matching domain. Fintech, healthcare, and commerce controls have separate allowlists. |
| Unauthorized API | Match `API_TOKEN` in `.env`, request headers, and running backend/proxy; recreate services after changing tokens. |
| Database password changed on existing volume | Initialization variables apply only to a new database. Change the DB role password or recreate the local volume. |
| Need a fresh demo database | Export anything needed first, then `docker compose down -v` removes this project's database volume. |

First builds need package/image network access. Demo operation needs no external AI provider. Host ports bind to localhost; exposing this stack to a network requires identity, authorization, TLS, and production hardening.
