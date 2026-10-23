# OpsPilot AI — Product Requirements

## What we are building
OpsPilot is a local incident investigation and workflow-automation workspace. It collects synthetic service telemetry, retrieves relevant runbooks, assembles a traceable diagnosis, presents a remediation proposal for human review, and records the decision and simulated outcome.

## Why
Support engineers spend time switching among alerts, metrics, procedures, tickets, and change records. OpsPilot demonstrates how evidence retrieval and constrained AI can reduce investigation time while keeping the engineer accountable for diagnosis and action.

## Users
- Primary: L1/L2 support engineers and incident responders who triage alerts and execute documented recovery steps.
- Secondary: problem managers who need recurring-cause tracking and searchable RCA records; change managers/CAB reviewers who assess remediation risk; service owners who maintain CIs and runbooks.
- Initial audience: engineering teams evaluating incident-assistant workflows locally. The MVP is not a production ITSM replacement.

## MVP capabilities
1. Create/list/read incidents using ITIL-inspired ticket fields: ticket ID, impact, urgency, derived priority, category, affected configuration item, and major-incident flag.
2. Investigate ten fintech/healthcare lab scenarios plus two e-commerce workload faults using collected service telemetry and runbook retrieval. E-commerce diagnoses require measured runtime indicators.
3. Optionally use Spring AI OpenAI chat/embeddings; deterministic demo mode works without credentials.
4. Show evidence, citations, root-cause hypothesis, cause/fix diagrams, risk, and short-term/corrective resolution classification.
5. Record approval or rejection before any allowlisted simulated remediation; audit every transition and return before/after checks.
6. Save a draft RCA for human review. A human-approved RCA summary can be retrieved later as a runbook reference.
7. Create Problem and Change records, link them to incidents, and gate change progression through assessment, authorization, schedule, implementation, review, and closure.
8. Maintain a local configuration-item inventory and synthetic workloads, including generated e-commerce traffic across cooperating services.

## Success measures
- All twelve scenarios complete investigation → approval → simulation in Compose integration tests, with runtime signal assertions for the two commerce cases.
- Unsupported incidents remain non-executable.
- Decisions, changes, and RCA review remain auditable.
- Clean local setup works through Compose without a model API key.
- Engineers can inspect observed evidence and supporting procedure.

## Out of scope
No production cloud/Kubernetes deployment, real infrastructure credentials, actual remediation, real patient/payment data, auto-approval, ticketing-system integration, model fine-tuning, or guarantee of ITIL certification/compliance. The data model is ITIL-inspired; mapping to an organization's practices requires customization.
