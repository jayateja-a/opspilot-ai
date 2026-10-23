# OpsPilot AI — Local Incident Investigation MVP

OpsPilot is a local operations workspace for investigating synthetic service incidents. It connects incident/ticket records to container telemetry and runbooks, prepares an evidence-backed diagnosis and remediation proposal, and requires a human decision before running an allowlisted simulation.

## What runs locally

- **Spring Boot / Java 17** — REST API, ITIL-style incident records, retrieval and workflow orchestration, approval/rejection, audit events, RCA records, and simulated action verification.
- **Spring AI** — optional OpenAI chat and embedding providers. `AI_MODE=demo` is deterministic and makes no external AI calls.
- **PostgreSQL + pgvector** — incidents, ticket numbers, configuration items, problem/change records, approvals, RCA history, runbooks, and vectors.
- **React + TypeScript** — light operations dashboard with ticket priority, evidence, RCA/fix path diagrams, approval UI, and audit timeline.
- **Fintech and healthcare lab containers** — synthetic API traffic, logs, metrics, and allowlisted fault scenarios. They are isolated local test services; they are not real customer data or production systems.

All remediation remains a simulation. The application cannot access AWS, Kubernetes, host Docker, or external customer infrastructure.

## Start the local workspace

Requirements: Docker Engine/Desktop with Docker Compose v2, and about 4 GB available RAM for the first image build.

```bash
cp .env.example .env
docker compose up --build --wait
```

Open [http://localhost:3000](http://localhost:3000). The API and OpenAPI UI are at [http://localhost:8080](http://localhost:8080) and [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html). Default tokens in `.env.example` are for local development only.

To run the full black-box regression suite against the containers and database:

```bash
docker compose --profile test run --build --rm tests
```

To stop the lab and preserve its database, run `docker compose down`. To remove the local database volume too, run `docker compose down -v`.

## Optional OpenAI provider

Demo mode is the default and supports the complete workflow without network credentials. For provider-backed diagnosis and embeddings, set `AI_MODE=openai` and `OPENAI_API_KEY` in `.env`, then restart the backend. OpenAI usage may incur charges. Model output is constrained to supplied evidence and runbooks, and its cited evidence identifiers are validated before a proposal is accepted. The deterministic mode is suitable for repeatable tests and demos.

Spring AI 1.1.x is used with Spring Boot 3.5.x. RAG uses Spring AI's `EmbeddingModel` and `ChatClient` abstractions while PostgreSQL/pgvector storage and similarity search remain explicit SQL so the retrieval schema and filtering are visible.

## Workflow

1. Choose a scenario or create an incident. An ITIL-style `INC-` ticket number, impact, urgency, priority, category, and affected CI are stored.
2. Investigate. The backend activates only a named lab fault, reads the selected lab's synthetic telemetry, and retrieves matching runbook chunks from pgvector.
3. Review root-cause hypothesis, evidence, retrieved procedures, cause/fix diagrams, risk, and resolution type.
4. Approve or reject. Rejection blocks execution. Approval is persisted and audited.
5. Run the allowlisted local simulation and verify synthetic before/after metrics.
6. Review the generated RCA. An approved RCA summary is added to the retrieval library as reference material. This is RAG knowledge reuse, not model training.
7. Create linked Problem and Change records for recurring causes or proposed durable changes. Change progression is explicit and gated through assessment/authorization/review.

## Synthetic scenarios

The 10 cases cover database pool saturation, release regression, memory pressure, CPU saturation, disk pressure, Redis outage, Kafka lag, TLS expiry, DNS failure, and rate limiting. Fintech and healthcare lab containers accept only scenarios assigned to their domain. They serve synthetic endpoints (`/payments` and `/fhir/Patient`) and synthetic telemetry; injected faults never touch host or external infrastructure.

## Test coverage

- Java unit and MVC tests: `cd backend && mvn test`.
- Frontend component tests and production build: `cd frontend && npm ci && npm test && npm run build`.
- Lab service unit tests plus API/database/pgvector end-to-end regression tests: the Compose `test` profile.
- CI builds and starts the complete Compose stack, runs the integration profile, and tears down its database volume.

A CI run is the authoritative full-stack gate. The exact tests run locally depend on whether Maven, Node dependencies, and Docker are installed.

## Repository map

| Path | Responsibility |
|---|---|
| `backend/` | Spring Boot API, Spring AI, Flyway migrations, tests |
| `lab/` | Synthetic domain workload and telemetry containers plus lab tests |
| `frontend/` | Light React operations dashboard |
| `fixtures/` | 10 scenario definitions and local runbooks |
| `scripts/` | Local start/stop, Compose integration, smoke and load helpers |
| `docs/` | Product, architecture, safety, design, task plan, and decision memory |

See `docs/architecture.md` for flow and storage, `docs/rules.md` for AI/action boundaries, and `docs/Tasks.md` for remaining product work.
