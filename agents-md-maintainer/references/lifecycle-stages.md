# Lifecycle stages for AGENTS.md/CLAUDE.md

There's no formally standardized set of stages — this is a synthesis of published guidance
(the AGENTS.md open standard's own suggested content, plus the broader "map → boundaries →
checks → evidence" pattern), used here as a diagnostic rubric, not dogma. The point isn't to
force a project into one of five boxes; it's to have a vocabulary for talking about how a file's
*emphasis* should shift as a project ages.

## The five stages

| Stage | Dominant concern | Emphasis |
|---|---|---|
| 1. Greenfield / inception | Direction | Architecture, conventions, intended structure |
| 2. Early development | Consistency | Established patterns, commands, testing, boundaries |
| 3. Established product | Navigation | Repository map, authoritative patterns, subsystem boundaries |
| 4. Brownfield / mature | Preservation | Invariants, compatibility, migrations, dangerous areas |
| 5. Legacy / maintenance | Risk management | Characterization tests, blast radius, historical constraints, safe-change procedure |

Signals that suggest a stage (heuristics to check, then confirm with the user — never assert
silently):

- **Greenfield**: very shallow git history, few files, no ADRs, no migration directory.
- **Early development**: a handful of modules with visibly repeated patterns (multiple
  controllers/consumers/repositories that look alike), but no docs/adr yet.
- **Established**: enough modules/subsystems that a newcomer would need a map to navigate them;
  ADRs or an architecture doc exist; the root file is already leaning on links rather than
  inlined explanation.
- **Brownfield**: deprecated APIs still present, multiple migration generations, external
  consumers referenced in code/comments/tickets, "don't touch this" folklore visible in
  commit messages or existing comments.
- **Legacy**: the above plus low change velocity, characterization/regression tests standing in
  for lost domain knowledge, and explicit compatibility constraints on wire formats or schemas.

## Section weighting by stage

| Section | Greenfield | Early dev | Established | Brownfield | Legacy |
|---|---|---|---|---|---|
| Vision / intended design | High | Medium | Low | — | — |
| Architecture conventions | High | Medium | Low-Medium | Low | — |
| Repository map | Low | Medium | High | High | High |
| Example implementations / patterns | Low | High | High | High | High |
| Build/test commands | High | High | High | High | High |
| Invariants | Low | Medium | High | High | High |
| Compatibility constraints | — | Low | Medium | High | High |
| Dangerous areas / blast radius | — | Low | Medium | High | High |
| Historical quirks | — | — | Low | Medium | High |
| Migration rules | Low | Medium | Medium | High | High |
| Definition of Done / verification | High | High | High | High | High |

Read this as: the earlier stages carry more *forward-looking* content (what we intend to build
and how); the later stages carry more *protective* content (what must not break, and why). Build
commands, verification, and repository map stay important throughout — they don't fade, they
just change in nature (map goes from "here's the plan" to "here's what actually exists").

## Two mental-model shifts worth naming explicitly when reviewing a file

**Rules → invariants.** A rule states a practice ("use UUIDs for aggregate identifiers"). An
invariant states what must remain true and why ("order IDs are UUIDs and are persisted/published
as strings; changing their representation breaks persisted records and external event
consumers"). The second is far more useful to an agent deciding whether a "clean-up" is actually
safe — it tells the agent what would break, not just what to do.

**Explain → point.** A greenfield file can afford to inline 20 lines explaining the intended
architecture, because there's no other artifact that documents it yet. A mature file should
instead point at `docs/architecture/`, ADRs, or service-boundary docs — `AGENTS.md`/`CLAUDE.md`
is always-on context loaded into every session, so long-lived explanation belongs in docs that
are read on demand, not repeated in every prompt.
