# Verification — 2026-10-07

The local MVP was built and exercised against running services. **42 automated tests passed**, plus a real Chromium browser workflow.

| Check | Result |
| --- | --- |
| Java 17 / Spring Boot Maven verify | 6 tests passed; executable JAR built |
| Python / FastAPI unit tests | 19 passed |
| HTTP/database integration tests | 15 passed against Spring Boot + FastAPI + PostgreSQL 16.15 + pgvector 0.8.1 |
| React / TypeScript build and Vitest | Production bundle built; 2 tests passed |
| Browser workflow | Create → investigate → view evidence → approve → execute → inspect audit passed |
| Mobile viewport | 390 × 844; no horizontal document overflow |
| Desktop viewport | 1440 × 1080; inspected screenshot |
| Compose and shell configuration | YAML parsed; shell syntax checked |

The integration suite covers all ten scenarios, execution before approval, repeated execution, concurrent duplicate execution, rejection, forged approval IDs, missing telemetry, unauthorized API access, invalid payloads, unknown incidents, mismatched services, runbook replacement, and service-filtered pgvector retrieval. Unit tests also cover provider failures, retrieval failures, invented citation IDs, and embedding dimension mismatches.

OpenAI requests were tested using mocked HTTP responses. No real API key or paid provider call was used. Docker was not installed in the build environment, so the full workflow ran natively; Docker images and Compose startup were not executed here. PostgreSQL and pgvector were used directly, not replaced with SQLite or an in-memory mock.

Screenshots from the running production React bundle:

- [Desktop workspace](dashboard-desktop.png)
- [Mobile workspace](dashboard-mobile.png)

Run `scripts/verify.sh` to repeat the API/database tests with Docker locally. The optional `scripts/browser_smoke.mjs` repeats the browser flow with a locally installed Playwright browser. A Starlette HTTPX compatibility deprecation warning appeared in Python tests; it did not fail any tests.
