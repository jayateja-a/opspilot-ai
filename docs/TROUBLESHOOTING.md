# Troubleshooting

| Symptom | Check / action |
| --- | --- |
| Docker unavailable | Install and start Docker Desktop or Docker Engine + Compose v2. |
| Port already allocated | Check localhost ports 3000, 8080, 5432. Change the host side of `ports`, or stop the conflicting local service. |
| Agent unhealthy during startup | Inspect `docker compose logs agent`. Demo mode seeds ten runbooks quickly. OpenAI mode needs a valid API key and network access. |
| vector extension missing | Use the supplied `pgvector/pgvector:pg16` image. Native PostgreSQL must have the pgvector extension installed before Flyway starts. |
| Backend unhealthy | Inspect `docker compose logs backend postgres`. Flyway failures stop startup; do not edit an applied migration, add a new version. |
| Analysis failed | Check `last_error`, inspect agent logs, fix provider/DB connectivity, and click Investigate again. |
| Approval disabled | The plan must be executable and the reviewer/note fields must be nonblank. Unknown incidents without telemetry cannot be approved. |
| Cannot execute | Verify status=APPROVED, an APPROVE record exists, and approved context is unchanged. |
| No custom runbook retrieved after changing modes | Reingest it to generate vectors for the active embedding model. |
| Unauthorized API | Match API_TOKEN in `.env`, your curl/Swagger request, and the running backend/proxy. Recreate services after changing tokens. |
| Database password changed on existing volume | PostgreSQL initialization variables apply only to a fresh database. Change the database role password explicitly; editing `.env` alone does not change it. |
| Need a fresh demo database | Export anything needed first. `docker compose down -v` deliberately deletes this project's database volume. |

Container images and dependency installation need network access on first use. Demo operation itself needs no external service. Host ports are localhost-only; opening this stack to a network would also require real identity, authorization, TLS, and deployment hardening.
