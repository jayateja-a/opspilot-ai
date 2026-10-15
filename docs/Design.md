# Interface design

Current direction and change constraints, updated 2026-10-15. Source: `frontend/src/App.tsx` and `frontend/public/styles.css`.

## Look and feel

Use a calm, dark operations workspace with clear hierarchy and compact information. Make evidence and decisions easy to scan. Prefer restrained transitions; keep content readable and scrollable without overlapping sections.

| Token | Existing direction |
| --- | --- |
| Page background | `#101519` |
| Panel background | `#151c21` |
| Primary text | `#dfe4e6` |
| Secondary text | `#8b989f` |
| Primary action / success | Mint `#a4e4c9` |
| Pending / medium risk | Amber `#d8bf82` |
| Type | DM Sans / Manrope names with system sans-serif fallbacks; no external font request required |

Use thin borders, modest corner radii, readable spacing, and monospace for identifiers, tool names, and metrics. Label severity, risk, and lifecycle status separately; do not rely on color alone.

## Information structure

- Desktop sidebar: OpsPilot identity, incident queue navigation, runbook library, local operator context.
- Header: workspace breadcrumb and LOCAL SIMULATION environment marker.
- Overview: incident count, awaiting approval, resolved simulations, scenario availability.
- Workspace: incident queue beside selected incident details. The queue scrolls when long.
- Detail tabs: Analysis, Evidence, Activity.
- Runbook library: expandable procedures plus custom-ingestion form.

## Interaction behavior

1. New incident opens a scenario chooser; creation leads to an OPEN incident.
2. Investigate shows busy feedback and prevents duplicate UI submissions.
3. Analysis presents mode, hypothesis, explanation, score label, action, risk, and simulation warnings.
4. Evidence exposes source data and retrieved chunks, not just a diagnosis summary.
5. Approval requires reviewer and note. Disable Approve when evidence is insufficient; allow rejection with a decision note.
6. Approval does not execute automatically. Show a separate Execute simulation action.
7. Resolved view shows simulated before/after values, receipt, and verification text. Activity shows ordered audit events.

Empty, loading, provider/analysis failure, rejected, approved, and resolved states must remain understandable. Use RESOLVED to describe the incident status while explicitly labeling its simulation outcome.

## Responsive and accessible behavior

Existing breakpoints adapt at 1100, 800, and 500 pixels; queue/details stack on narrower screens. Keep forms full-width, long evidence wrapped, and document width within the viewport. Preserve focus indicators, labeled fields, keyboard-operable controls, and reduced-motion handling.

Desktop and a 390-pixel viewport were checked in the original browser smoke run. This is not a full accessibility audit. The sidebar is hidden below 500 pixels; equivalent mobile navigation to the runbook library remains a follow-up, not a completed mobile feature-parity claim.

## When changing the UI

Preserve mode/simulation labels, citations, approval gates, and failure visibility. Recheck the affected user journey on desktop and mobile. Do not add fake operational metrics, fabricated customer data, or production authentication claims. No visual redesign is required by the documentation update.
