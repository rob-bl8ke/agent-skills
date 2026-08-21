# Vertical-slice issue breakdown methodology

Used only in breakdown mode (Stage 4 of SKILL.md), when the request describes a broader feature or spec area rather than one already-scoped item.

## Prefactor first

Make the change easy, then make the easy change. Before slicing the actual feature work, look for prefactoring that would simplify every slice that follows (extracting a shared helper, introducing a seam, aligning naming with the domain glossary). Any prefactoring identified becomes its own issue, sequenced first, blocking whichever slices depend on it.

## Tracer bullets (the default)

A tracer bullet issue cuts a **narrow but complete** path through every layer it touches — schema, API, service/domain logic, and tests, plus UI where relevant. It is a vertical slice, never a horizontal slice of just one layer.

Requirements for each tracer bullet issue:
- **Demoable or verifiable on its own** — you can show or test the behavior it delivers without needing later issues to land first.
- **Sized to fit a single fresh context window** — small enough that one focused implementation session can complete it end to end.
- **Explicit blocking edges** — list which other issues must complete before this one can start. An issue with no blockers can start immediately. Blocking edges should reflect genuine gating dependencies only — not would-be-nice-to-have ordering.

## Exception: wide mechanical refactors

A wide refactor is a single mechanical change — renaming a shared column or symbol, retyping something used everywhere — whose blast radius fans out across the whole codebase, breaking many call sites at once. No vertical slice can land green for this kind of change, so do not force it into a tracer bullet. Sequence it as **expand → migrate → contract** instead:

1. **Expand** — add the new form alongside the old one. Nothing breaks; this issue has no blockers (or only prefactoring blockers).
2. **Migrate** — move call sites over in batches sized by blast radius (for example per package or per directory). Each batch is its own issue, blocked by the expand issue. CI stays green batch to batch because the old form still exists throughout.
3. **Contract** — delete the old form once no caller remains. This issue is blocked by *every* migrate batch.

If even individual batches cannot stay green alone (for example the old and new forms genuinely cannot coexist for a stretch), let the batches share an integration branch that all block a final integrate-and-verify issue. In that case, green is promised only at the integrate-and-verify issue, not at each batch.

## Presenting the breakdown

Show the full breakdown as a numbered list. For every issue:

```
N. Title: {short descriptive name}
   Blocked by: {other issue numbers, or "none"}
   What it delivers: {the end-to-end behavior this issue makes work}
```

Then ask the user directly:
- Does the granularity feel right — too coarse, or too fine?
- Are the blocking edges correct — does each issue depend only on issues that genuinely gate it?
- Should any issues be merged or split further?

Iterate on the breakdown until the user approves it. Do not draft a full issue body, or create any GitHub issue, before that approval — Stage 5 (issue generation) only starts afterward, one pass per approved issue, carrying each issue's blocking edges into its `Dependencies/Blockers` field.

If the feature or spec being broken down is itself represented by a parent GitHub issue, reference that parent from each child issue where appropriate, but never close or modify the parent issue itself.
