---
name: skills-auditor
description: "Audits this skills repository for conflicts between skills, self-contradictions, dangling references, silent-failure bugs, and version/config drift, then writes a prioritised report to audits/skills-audit-<YYYY-MM-DD>.md. Combines deterministic mechanical checks (scripts/mechanical-checks.py) with a semantic conflict review that scripts cannot do. Strictly read-only: it reports and recommends, it never edits a skill. Use when the user asks to audit, health-check, or review the skills base, before publishing changes to it, or on a schedule."
argument-hint: "[quick|full|--include-consumers <path>...] - 'quick' runs mechanical checks only; default is full"
---

# my-skills Audit

Find everything wrong with this skills base, rank it by consequence, and write a report a human
can act on without re-deriving the analysis.

**Read-only contract.** This skill writes exactly one file: `audits/skills-audit-<YYYY-MM-DD>.md`.
It never edits a `SKILL.md`, never stages, never commits, never pushes. Fixes are the user's call,
because most findings here have more than one defensible resolution and picking one is a design
decision. Emit recommendations, not edits.

## Resolve paths from this file, never from the working directory

This skill may be invoked from anywhere — a consuming service repo, a scheduler with an arbitrary
CWD, or the skills base itself. **Do not use CWD-relative globs.** This `SKILL.md` lives at
`<repo>/skills/my-skills-audit/SKILL.md`, so:

- `<repo>` = this file's directory, two levels up
- checks script = `<repo>/skills/my-skills-audit/scripts/mechanical-checks.py`
- output = `<repo>/audits/skills-audit-<YYYY-MM-DD>.md`

Derive `<repo>` from the absolute path of this file and use absolute paths from then on. This is
not pedantry: a CWD-relative `skills/*/SKILL.md` glob that silently matches nothing is a bug this
repository has actually shipped, and a check that finds nothing looks identical to a clean result.

## Procedure

### 1. Locate and sanity-check

Resolve `<repo>` as above. Confirm `<repo>/skills/` exists and contains at least one
`*/SKILL.md`. **If it does not, stop and report that** — do not write an empty report, because an
empty report is indistinguishable from a clean bill of health. Create `<repo>/audits/` if absent.

Record for the report header: skill count, `git rev-parse --short HEAD`, current branch, and
whether the tree is dirty (`git status --porcelain` non-empty). An audit of an uncommitted tree is
still valid but the report must say so, since the findings may not match what consumers install.

### 2. Run the mechanical checks

```
python3 <repo>/skills/my-skills-audit/scripts/mechanical-checks.py --repo-root <repo>
```

Emits JSON: `{repo, skill_count, skill_names, findings[]}`, each finding carrying
`check / severity / skill / file / line / detail`. Deterministic, read-only, no network. See
[references/checks.md](./references/checks.md) for what each check ID means, its known blind
spots, and how to extend it.

Two check IDs are **not findings** and must never be reported as such:

- `C4b-unrecognised-vocab` — a recall net listing hyphenated tokens the script could not classify.
  Read each cited line; most are domain vocabulary. Real defects found here get promoted into the
  report under the appropriate semantic ID. Genuine vocabulary should be added to `NOT_A_SKILL` in
  the script so the list shrinks over time.
- `C2b-broken-link-in-example` — links under `examples/`/`templates/` usually describe *generated*
  output. Confirm against the surrounding text before believing it.

If a check produces an obvious false positive, **fix the script, don't hand-filter the output** —
otherwise the next scheduled run reproduces the noise.

### 3. Semantic review (skip only if the argument is `quick`)

The mechanical checks catch broken structure. They cannot catch two skills that are each
internally coherent but tell the model opposite things — historically the most damaging class of
defect here, and invisible to grep. Work through
[references/semantic-checks.md](./references/semantic-checks.md), which lists each check with the
real defect that motivated it.

Summarised, look for:

| ID | Looking for |
|---|---|
| S1 | Two skills mandating **different implementations of the same thing** — the worst case, because whichever loads first wins and the other's advice becomes a defect list. |
| S2 | **Contradictory guidance** on one technical decision, across skills *or inside a single skill* (a decision table that contradicts its own prose). |
| S3 | Cross-cutting rules with **no declared owner** — if two skills may both state a rule, one must be named as authority and the other must defer. |
| S4 | **Forked/near-duplicate skills** with drifted defaults; near-identical procedures are usually a fork, not a coincidence. |
| S5 | **Tool or API names that do not exist** (MCP tools, CLI subcommands, config properties). |
| S6 | **Prose references to skills** that no longer exist — unbackticked, so `C4a` cannot see them ("apply the initial testing framework skill"). |
| S7 | **Internal count/list mismatches** — "12 properties" above a table of 11. |
| S8 | **Staleness against upstream reality** — guidance frozen at a superseded library version. |
| S9 | **Silent-degradation steps** — any step that can find nothing, proceed anyway, and still present a confident result. |
| S10 | **Instructions leaking into emitted output** — a skill's report template telling the *reader* to apply a skill, so internal routing ends up in a user-facing document. |

For a large base, fan these out: give each sub-agent the skill inventory plus one or two S-checks
and have it report only concrete instances with file:line. Keep the aggregation here so severity
stays consistently applied. Do not spawn sub-agents on a `quick` run.

### 4. Optional: consuming repositories

Only when `--include-consumers <path>...` is passed. For each path, read `skills-lock.json` and
compare its keys against `<repo>/skills/*/`. A key with no corresponding directory means a
**retired skill still installed downstream** — it keeps loading from `.agents/skills/` until
cleared, so a skill deleted here can still be steering work there. Report per repo. Never modify a
consuming repo.

### 5. Assign severity by consequence

Severity is about what goes wrong in practice, never about how many lines it takes to fix:

| Severity | Test |
|---|---|
| **Critical** | The skill cannot load, or actively produces wrong code/config that ships. |
| **High** | Guidance is silently lost or contradicted: the model reads it and does the wrong thing, or a step degrades without erroring. |
| **Medium** | Real inconsistency that costs correctness or trust but has a workaround, and the failure is visible when it happens. |
| **Low** | Hygiene, discoverability, cosmetics. Nothing breaks. |
| **Info** | Verified-intentional, or a review queue needing human judgement before it counts. |

Two rules that keep this honest:

- **Silent failure outranks loud failure.** A wrong path someone notices is Medium; a glob that
  matches nothing and lets the run continue is High. Loud wrongness gets fixed; quiet wrongness
  accumulates.
- **Do not inflate a finding you cannot demonstrate.** If you cannot cite file:line or quote the
  contradiction, it is Info and labelled unverified. A confident audit that is wrong costs more
  than a hedged one that is right.

### 6. Write the report

Write `<repo>/audits/skills-audit-<YYYY-MM-DD>.md` following
[references/report-template.md](./references/report-template.md). Same-day reruns **overwrite**;
history lives in git, so the filename stays one-per-day and stable for schedulers.

Every finding carries all five of these — a finding without a recommendation is a complaint:

1. **ID and title** — `H3`, `M1`, stable within one report.
2. **Location** — `file:line`, or the skill pair for a cross-skill conflict.
3. **What's wrong** — the mechanism, not the symptom. Not "broken link" but "the reference the
   skill promises is never loaded, and nothing errors".
4. **Why it matters** — the concrete consequence. If you cannot state one, drop the severity.
5. **Recommendation** — one clear action where there is a right answer. Where the choice is
   genuinely the user's (retire A vs. retire B; make A authoritative vs. split the concern), give
   the options with the trade-off of each and **state which you would pick and why**. Options
   without a recommendation just moves the work back to the reader.

Close with a **Verified clean** section listing what was checked and found sound. Without it a
reader cannot tell a passing check from a check that never ran — the same ambiguity step 1 guards
against.

### 7. Report back in chat

Print the output path, counts per severity, and the top three findings by severity with one line
each. Do not paste the whole report. If nothing above Low was found, say that plainly.

## Running on a schedule

Safe unattended because it is read-only, needs no network, prompts for nothing, and writes one
deterministic path. For an unattended run:

- Invoke with an explicit absolute repo path; never rely on the scheduler's CWD.
- Prefer `quick` for high-frequency runs (mechanical checks are seconds and need no sub-agents);
  reserve `full` for weekly or pre-publish runs, since the semantic pass is the expensive half.
- Permissions needed: read over `<repo>`, write limited to `<repo>/audits/`, plus read-only git
  (`rev-parse`, `status`, `branch`). Nothing else.
- **Never auto-fix, auto-stage, or auto-commit**, even when a fix looks trivial. This skill's
  value is that its output is trustworthy; a skill that edits skills unattended is a skill that
  can quietly corrupt the base it audits.
- If a scheduled run finds nothing above Low, still write the report — an unbroken series of clean
  reports is how you know the schedule is alive. Silence should mean *broken*, not *fine*.

## Extending

New defect classes are expected. Route mechanical, greppable ones into
`scripts/mechanical-checks.py` with a new `C<n>` ID and document them in `references/checks.md`;
route judgement-dependent ones into `references/semantic-checks.md` as a new `S<n>`. When adding a
mechanical check, first construct a fixture that makes it fire, then confirm it stays quiet on the
real repo — an untested check that silently never fires is worse than no check, because it reads as
coverage.
