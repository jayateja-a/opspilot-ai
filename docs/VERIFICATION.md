# Verification Guide

| Area | Command | Coverage |
|---|---|---|
| Spring Boot | `cd backend && mvn test` | Unit and MVC API contract tests |
| React | `cd frontend && npm ci && npm test && npm run build` | Component regressions and TypeScript production build |
| Lab | `python -m pytest -q lab/test_lab.py` | Domain allowlists, authentication, synthetic faults |
| Full stack | `docker compose --profile test run --build --rm tests` after `docker compose up --build --wait` | Lab tests plus API/database/pgvector black-box regressions, including all ten scenarios |
| CI | `.github/workflows/ci.yml` | Clean Compose build, full regression suite, teardown |

The integration suite checks ticket metadata, all scenario workflows, approval/rejection, insufficient evidence, idempotent simulation, audit history, vector retrieval, Problem/Change records, transition guards, CI inventory, and API validation/authentication.

This suite provides regression confidence, not a claim of 100% code coverage. Coverage should be measured in provisioned CI and expanded against meaningful branches; coverage alone does not establish correctness.
