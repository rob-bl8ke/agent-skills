# Vertical-slice ticket breakdown methodology

Used only in breakdown mode (Stage 4 of SKILL.md), when the request describes a broader feature or spec area rather than one already-scoped item.

## Prefactor first

"Make the change easy, then make the easy change." Before slicing the actual feature work, look for prefactoring that would simplify every slice that follows (extracting a shared helper, introducing a seam, aligning naming with the domain glossary). Any prefactoring identified becomes its own ticket, sequenced first, blocking whichever slices depend on it.

## Tracer bullets (the default)

A tracer bullet ticket cuts a **narrow but complete** path through every layer it touches — schema, API, service/domain logic, and tests, plus UI where relevant. It is a vertical slice, never a horizontal slice of just one layer.

Requirements for each tracer bullet ticket:
- **Demoable or verifiable on its own** — you can show or test the behaviour it delivers without needing later tickets to land first.
- **Sized to fit a single fresh context window** — small enough that one focused implementation session can complete it end-to-end.
- **Explicit blocking edges** — list which other tickets must complete before this one can start. A ticket with no blockers can start immediately. Blocking edges should reflect genuine gating dependencies only — not "would be nice to have first."

## Exception: wide mechanical refactors

A wide refactor is a single mechanical change — renaming a shared column or symbol, retyping something used everywhere — whose blast radius fans out across the whole codebase, breaking many call sites at once. No vertical slice can land green for this kind of change, so don't force it into a tracer bullet. Sequence it as **expand → migrate → contract** instead:

1. **Expand** — add the new form alongside the old one. Nothing breaks; this ticket has no blockers (or only prefactoring blockers).
2. **Migrate** — move call sites over in batches sized by blast radius (e.g. per package, per directory). Each batch is its own ticket, blocked by the expand ticket. CI stays green batch to batch because the old form still exists throughout.
3. **Contract** — delete the old form once no caller remains. This ticket is blocked by *every* migrate batch.

If even individual batches can't stay green alone (e.g. the old and new forms genuinely can't coexist for a stretch), let the batches share an integration branch that all block a final integrate-and-verify ticket. In that case, green is promised only at the integrate-and-verify ticket, not at each batch.

## Presenting the breakdown

Show the full breakdown as a numbered list. For every ticket:

```
N. Title: {short descriptive name}
   Blocked by: {other ticket numbers, or "none"}
   What it delivers: {the end-to-end behaviour this ticket makes work}
```

Then ask the user directly:
- Does the granularity feel right — too coarse, or too fine?
- Are the blocking edges correct — does each ticket depend only on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate on the breakdown until the user approves it. Do not draft a full issue body, or create any Jira issue, before that approval — Stage 5 (issue generation) only starts afterward, one pass per approved ticket, carrying each ticket's blocking edges into its `Dependencies/Blockers` field.

If the feature/spec being broken down is itself a parent issue or epic in Jira, link each new child ticket to it as normal, but never close or modify the parent issue itself.
