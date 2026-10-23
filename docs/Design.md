# Product Design

## Visual direction
Use a light, calm operations console: white surfaces, cool gray canvas, navy text, blue primary actions, and restrained green/amber/red status colors. The interface should feel like polished enterprise software rather than a cinematic AI visualization.

## Information hierarchy
1. Incident queue and ticket identity/priority.
2. Workflow status and the engineer's next action.
3. Root-cause hypothesis with confidence caveat and plain-language reasoning.
4. Evidence and retrieved runbooks with source IDs.
5. Cause/impact path and proposed recovery diagrams.
6. Remediation risk, approval form, simulated verification result, RCA review state, audit timeline.

## Interaction design
- Persistent sidebar for incidents and runbooks with compact workspace context.
- Clear blue primary actions with subtle hover/focus transitions; support keyboard focus and reduced motion.
- Keep approve and reject separate and equally visible; require reviewer and decision note.
- Show simulated impact as before/after data and label it synthetic.
- Use simple node-and-arrow diagrams from report data, with text labels for accessibility.
- Collapse the sidebar and stack panels on narrow screens.

## Accessibility and tone
Use semantic headings, labeled controls, readable contrast, visible focus rings, responsive layouts, and `prefers-reduced-motion`. Use concise non-alarmist language. Separate observed facts from hypotheses; never present model confidence as certainty.
