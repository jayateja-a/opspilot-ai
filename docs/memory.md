# Project memory — read first

Snapshot: 2026-10-15. Keep this file short; record durable decisions and evidence, not chat transcripts. User instructions and tool policies take precedence over repository guidance.

## Current checkpoint

OpsPilot AI Local MVP is implemented: Spring Boot → FastAPI investigation → PostgreSQL/pgvector retrieval → React review → human approval/rejection → allowlisted simulated execution → audit history. Ten fixture scenarios are included. The current request adds handoff documentation only; it does not change application behavior or authorize a larger product phase.

## Decisions to retain

- Java 17/Spring Boot owns incident lifecycle, decisions, execution records, and audit.
- Python/FastAPI owns evidence/retrieval/diagnosis/simulation. Flyway alone owns schema migrations.
- Demo is key-free and deterministic: fixture diagnosis, lexical hash vectors, real pgvector search. Its 0.90 score is not AI accuracy.
- Optional OpenAI supplies semantic vectors and diagnosis text; fixture definitions still control actions/risk.
- Every executable proposal needs a persisted human decision and matching context. Rejection blocks execution.
- Remediation and before/after metrics are simulated. No real cluster/cloud writes exist.
- Local token proxies are not user authentication; reviewer names are self-entered labels.
- Embeddings use 1536 dimensions and model tags. Custom runbooks need reingestion after switching models.

## Resolved implementation issues / documentation decisions

- Production React bundling is finalized as `tsc` + esbuild (`frontend/build.mjs`); Vite remains for development/Vitest. Do not assume production uses `vite build`.
- Java tests use the subclass Mockito mock maker in test resources so they do not depend on JVM self-attachment in restricted environments.
- Styles use system fallbacks without fetching external fonts.
- Canonical architecture filename is now `docs/architecture.md`; the former uppercase file is consolidated to avoid case-only duplicates on Windows.

## Verification and open limits

- 2026-10-07: 42 tests passed (6 Java, 19 Python, 2 React, 15 integration), plus desktop/mobile Chromium flow using native services.
- 2026-10-15 scope review: Java/React builds and all 27 unit tests passed again; the 15 integration checks were historical, not rerun in that review.
- 2026-10-15 documentation handoff: six canonical docs and README reading guide added; links, fenced blocks, and filename compatibility checked. Application source is unchanged; application tests were not rerun for this documentation edit.
- Docker startup and live OpenAI calls remain unverified here. Provider behavior was tested with mocks.
- Mobile overflow was checked, not full accessibility or mobile navigation parity. Further known follow-ups are in `Tasks.md`.

## Read only what the task needs

Always begin with this file and [rules.md](rules.md). Then select:

| Question | Read next |
| --- | --- |
| What/why/scope? | [PRD.md](PRD.md) |
| Data flow, ownership, source locations? | [architecture.md](architecture.md); [API.md](API.md) for route details |
| UI behavior or styling? | [Design.md](Design.md) |
| What is done or next? | [Tasks.md](Tasks.md) |
| How to run or diagnose startup? | Root [README](../README.md), then [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| What actually passed? | [VERIFICATION.md](VERIFICATION.md) and dated entries above |

After an accepted change, update the relevant spec/task and replace obsolete memory entries. Keep completed facts separate from proposals and never store secrets here. These files support smaller context reads; they do not guarantee automatic loading or a fixed token saving in every AI tool.
