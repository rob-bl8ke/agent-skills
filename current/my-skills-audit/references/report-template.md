# Report template

Structure for `audits/skills-audit-<YYYY-MM-DD>.md`. Follow the shape; the prose is the auditor's.

Ordering principle: **severity first, always.** Never group by skill or by check ID — a reader
scanning for what to fix next must find it at the top, not assembled from sections.

````markdown
# my-skills audit — <YYYY-MM-DD>

| | |
|---|---|
| Repository | `<abs path>` |
| Commit | `<short sha>` on `<branch>` |
| Working tree | clean / **dirty (findings may not match what consumers install)** |
| Skills audited | `<n>` |
| Mode | full / quick (mechanical only) |
| Consumers checked | none / `<paths>` |

**<n> findings:** <c> critical, <h> high, <m> medium, <l> low, <i> info.

<One paragraph: the single most important thing to fix and why. If nothing above Low, say so
plainly and stop the summary there.>

---

## Critical

### C1 — <short title>

- **Severity:** Critical
- **Location:** `skills/<skill>/SKILL.md:<line>` <or: skill pair for a cross-skill conflict>
- **Check:** `<C-id or S-id>`

**What's wrong.** The mechanism, not the symptom. Name what fails and how it fails. If it fails
silently, say so explicitly — that is usually the reason for the severity.

**Why it matters.** The concrete consequence: what wrong code gets generated, what guidance is
lost, what a user sees. If no consequence can be stated, the severity is wrong.

**Evidence.**

> quoted line or diff, enough to confirm without opening the file

**Recommendation.** One clear action where there is a right answer.

Where the choice is genuinely the user's, present the options and pick one:

- **Option A — <name>.** What it costs, what it gains.
- **Option B — <name>.** What it costs, what it gains.

**Recommended: A**, because <reason grounded in this repo, not general principle>.

<Note any content that would be lost by the recommended option, so the user can salvage it.>

---

## High
<same finding shape, IDs H1, H2, …>

## Medium
<M1, M2, …>

## Low
<L1, L2, … — one paragraph each is enough; do not pad>

## Info / review queue
<I1, I2, … Verified-intentional items and anything needing human judgement before it counts as a
finding. `C4b-unrecognised-vocab` output belongs here, described as a queue, never as defects.>

---

## Verified clean

Checks that ran and found nothing. Without this a reader cannot distinguish a passing check from
one that never ran.

- **Frontmatter** — all `<n>` skills have valid frontmatter; every `name:` matches its directory;
  longest description `<n>` chars (limit 1024).
- **Skill references** — no dangling backticked skill references (`C4a`).
- **Links** — all `references/` links resolve.
- **Discovery globs** — no CWD-relative `skills/*` globs (`C5`).
- <continue for every check that ran clean, including semantic ones on a full run>

## Not checked

Anything deliberately out of scope this run, so a reader does not over-read the result.

- Semantic checks S1–S10 <if quick mode>
- Consuming repositories <if --include-consumers not passed>
- <anything skipped for another reason, with the reason>

---

## Reproducing

```
python3 <repo>/current/my-skills-audit/scripts/mechanical-checks.py --repo-root <repo>
```

Full run: invoke the `my-skills-audit` skill.
````

## Writing notes

**One finding per defect, not per occurrence.** Fourteen dead links in one file are one finding
with fourteen locations. Splitting them inflates the count and buries the real problems.

**Do not carry a finding forward once fixed.** Git holds the history. A report listing fixed items
alongside live ones makes the live ones harder to find. If a previous finding was fixed since the
last run, one line in the summary is enough.

**Recommendations must be decidable.** "Consider reviewing the overlap" is not a recommendation.
"Narrow `generate-comm-manual-tests`' description to name the communication domain explicitly, so it
stops outbidding `generate-manual-test-pack` on generic test-pack requests" is.

**State uncertainty as uncertainty.** If a finding rests on an assumption about how the host
resolves skills, say so and put it in Info. The value of this report is that its High findings are
reliably real — that is worth more than a longer list.
