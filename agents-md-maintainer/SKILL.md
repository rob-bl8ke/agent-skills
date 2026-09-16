---
name: agents-md-maintainer
description: Maintain a repository's AGENTS.md/CLAUDE.md as the project matures — judge whether its content still fits the project's actual lifecycle stage (greenfield/growing/established/brownfield/legacy), convert stale rules into invariants, replace explanations with pointers to docs once they exist, flag prose rules that a lint/CI check should enforce instead, and keep AGENTS.md and CLAUDE.md from drifting apart. Use when asked to review, audit, update, restructure, or "clean up" AGENTS.md or CLAUDE.md, when a rule in either file is clearly stale or contradicted by the current code, or when work in a session repeatedly needed context that wasn't in either file. NOT for generating a brand-new CLAUDE.md from scratch (that's Claude Code's own `/init`) and NOT for one-time copying of another agent's instruction file into CLAUDE.md (that's `/import`) — this skill is the ongoing maintenance layer above both.
---

# AGENTS.md / CLAUDE.md maintainer

`AGENTS.md`/`CLAUDE.md` is written once, early, and then either frozen or randomly appended to.
Nobody revisits its *shape* as the project matures. This skill is the discipline that does:
judge whether the file's content and emphasis still match what the project actually needs today,
and evolve it deliberately rather than letting it drift or bloat.

This is a judgement-driven maintenance skill, not a mechanical linter — there's no script here
because "does this file's shape fit this project's maturity" is a call an agent has to make by
reading the repo, not something a regex can decide.

## Which file is canonical

Claude Code reads `CLAUDE.md`, not `AGENTS.md`, natively. The open `AGENTS.md` standard is read
by other coding agents. When a repo wants both:

- **Both files exist at the same directory level** → `AGENTS.md` holds the real content.
  `CLAUDE.md` must be *just* the import line `@AGENTS.md` at the top, optionally followed by
  genuinely Claude-specific additions below it (or a symlink, `ln -s AGENTS.md CLAUDE.md`, on
  Unix/macOS). If you find `CLAUDE.md` duplicating content instead of importing it, flag this and
  offer to collapse it down to the import line, moving anything Claude-specific-only below the
  import.
- **Only one of the two exists** → leave it as the sole file. Do not proactively create the
  other one. Only add the counterpart if the user explicitly asks for dual-tool support.
- Nested files each follow their own tool's precedence (Claude Code loads `CLAUDE.md`
  hierarchically root-down and concatenates; the open standard uses nearest-file-wins) — this
  skill doesn't need to reconcile those mechanics, only keep the import/symlink relationship
  correct at whichever directory levels both files coexist.

## Not a replacement for `/init` or `/import`

`/init` already generates a baseline `CLAUDE.md` from the codebase (and reads `AGENTS.md` if
present); `/import` already does a one-time copy of another agent's instruction file into
`CLAUDE.md`. Neither makes an ongoing judgement about whether the file's *shape* still matches
the project's current maturity, converts stale rules into invariants, or decides when prose
should become a mechanical check instead — that's this skill's actual job, not theirs. Don't use
this skill to generate a CLAUDE.md from nothing; point the user at `/init` for that.

## The stable core

Whatever stage a project is in, the canonical file should let an agent answer seven questions:

| Section | Question it answers |
|---|---|
| PROJECT | What is this? |
| MAP | Where is everything? |
| BOUNDARIES | What may/may not be changed? |
| COMMANDS | How do I build/test/check it? |
| CONVENTIONS | What repository-specific practices matter? |
| INVARIANTS | What must remain true, and why? |
| VERIFICATION | How do I prove the change works? |

What changes across a project's life isn't whether these sections exist — it's how much weight
each one carries. See [references/lifecycle-stages.md](references/lifecycle-stages.md) for the
five-stage model and the weighting table.

## Reviewing an existing file

1. **Read the file(s)** — root, and any nested `AGENTS.md`/`CLAUDE.md` files.
2. **Infer the lifecycle stage** from cheap repo signals — commit history depth, module/file
   count, presence of ADRs or migration directories, deprecation markers, whether nested files
   already exist. State the inferred stage as a proposal ("this reads like an established
   project moving into brownfield — agree?") and let the user confirm or correct it. Never assert
   a stage silently and rewrite around it.
3. **Walk the file section by section** against the stable core and the confirmed stage's
   weighting, and look for:
   - **Missing sections** the stage calls for (e.g. a five-year-old service with no
     BOUNDARIES/dangerous-areas section).
   - **Rules that should be invariants** — a bare imperative ("use UUIDs for order IDs") versus
     a stated invariant with a reason ("order IDs are UUIDs and are persisted/published as
     strings — changing the representation breaks persisted records and external consumers").
     Prefer rewriting a rule as an invariant once its reason is discoverable (git blame, an ADR,
     PR history, or by asking the user) rather than leaving it a bare "do this."
   - **Explanation that should be a pointer** — if a section re-explains an architecture that
     `docs/`, an ADR, or the README already documents at length, replace the explanation with a
     link. `AGENTS.md`/`CLAUDE.md` is always-on context; long-lived explanation belongs in docs,
     not in every prompt.
   - **Prose that could be a mechanical check** — before keeping or adding a rule, ask whether a
     test, lint, ArchUnit rule, or CI check could enforce it instead. If so, recommend "the file
     states the invariant, tooling enforces it" rather than prose alone. A rule nothing enforces
     is the first thing that goes stale.
   - **A root file straining under multiple subsystems** — split into nested `AGENTS.md`/
     `CLAUDE.md` files once subsystems genuinely need different commands, conventions, or
     restrictions, not merely because the repo has gotten large.
4. **Present findings as a prioritized list of proposed edits**, not a wholesale rewrite. Apply
   them incrementally with the user's confirmation — propose, don't silently overwrite.
5. **Check the AGENTS.md/CLAUDE.md relationship** per the canonical-file rule above, if both
   exist.

## Reactive use (outside a standalone review)

While doing other work in a repo, if you hit a case where `AGENTS.md`/`CLAUDE.md` was missing the
information that would have prevented a misstep, or a section is clearly following the wrong
stage's emphasis (e.g. long architecture prose in a five-year-old brownfield service, or a
"preserve backwards compatibility" invariant in a greenfield repo with no external consumers yet),
flag it in the moment and offer to fix it there rather than waiting for a dedicated review pass.

Before adding anything, ask: **"Was this repository-wide context missing, or something
narrower?"** Repository-wide → root file. Subsystem-specific → nested file. Detailed knowledge →
docs/ADR. A repeatable procedure → a skill. Something a test could catch → a mechanical check, not
another line of prose. Don't let this file become a graveyard of rules that should be tests.
