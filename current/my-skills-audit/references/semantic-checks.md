# Semantic checks

Defect classes that need reading and judgement. Each one below is grounded in a defect actually
found in this repository — none is hypothetical. Work them in order; S1–S3 are where the expensive
problems live.

For each check: find concrete instances with `file:line`, or report nothing. An unverifiable
suspicion is Info, not High.

---

## S1 — Competing implementations of the same thing

**Look for:** two skills that both tell the model how to build the same mechanism, but
differently. Symptoms: two skills covering one library or pattern; one mandating hand-written
classes another says the library now provides; a skill whose "common defects" list matches what
another skill instructs you to write.

**Why it is the worst class:** whichever skill loads first wins, and the loser's guidance doesn't
merely go unused — it becomes an active defect list. The two skills are individually coherent, so
nothing looks wrong from inside either one.

**Real instance:** a consumer circuit-breaker skill mandated four hand-written classes that a
sibling skill explicitly listed as defects, because the library had absorbed that functionality in
a later version. The skill was never in the upstream sync's `affects` array (`C10-affects-gap`), so
it froze while reality moved.

**How to check:** group skills by the library/pattern they document. Where two cover one thing,
read both procedures and diff the mandated shape. Then check whether one is tracked for upstream
changes and the other is not — the untracked one is usually the stale one.

**Recommend:** retire one and salvage anything unique from it, or make one delegate explicitly to
the other. State which to retire and why. Note salvageable content, because retirement loses it —
decision tables and exception-scoping guidance are the usual casualties.

---

## S2 — Contradictory guidance on one decision

**Look for:** two skills giving opposite answers to the same technical question. Also check
*within* a single skill: a decision table contradicting the prose above it is common and easy to
miss, since each reads fine alone.

**Real instance:** retry/circuit-breaker nesting order. Several skills touched it; one recommended
`@Retryable` outer in its prose and `@Retryable` inner in its own decision table, on the same page.

**How to check:** list cross-cutting technical decisions (annotation ordering, layering, transaction
boundaries, mocking strategy, test scope). For each, grep every skill that states a position and
compare. Read decision tables against their own surrounding prose — do not assume one skill is
self-consistent.

**Recommend:** pick the correct answer, then fix the contradiction *and* assign an owner (S3).
Fixing the statements without assigning ownership means the drift returns.

---

## S3 — Cross-cutting rules with no owner

**Look for:** a rule several skills could legitimately state, with no skill declared authoritative.

**Why:** with no owner, each skill restates the rule in its own words and they drift apart.
Detecting the drift later (S2) costs far more than declaring the owner now.

**How to check:** for each rule stated in more than one skill, find an explicit authority claim. If
none, that's the finding.

**Recommend:** name one skill as the single authority in its own text, and have the others defer in
one line rather than restating. The deferral must be explicit — "if these disagree, that skill
wins" — so a future reader knows which to trust without an audit.

---

## S4 — Forked near-duplicate skills

**Look for:** two skills with near-identical structure and drifted defaults. Near-identical
procedures are a fork, not a coincidence.

**Real instance:** an issue-writing skill that was a near-verbatim fork of another with contradicting
defaults, and which called a non-existent MCP tool (see S5).

**How to check:** compare descriptions (`C12` gives candidates), then section headings, then
defaults. Check git history for the copy.

**Recommend:** retire the fork, merging any genuine improvement into the original. Then check what
the survivor is missing — a fork often exists because the original lacked something, and deleting
the fork without merging that reintroduces the gap. Also check the survivor's
`disable-model-invocation` flag: if it is set and it is now the only skill covering the capability,
the model cannot reach it at all.

---

## S5 — Non-existent tools, APIs, and properties

**Look for:** named MCP tools, CLI subcommands, and config properties that do not exist. These are
plausible-looking and near-impossible to spot by reading, because a wrong name reads exactly like a
right one.

**Real instances:** `addJiraComment` (the real tool is `addCommentToJiraIssue`); a config property
belonging to a retired library that no longer had any effect.

**How to check:** extract every tool/property name a skill instructs the model to call. Verify MCP
tool names against the live tool list for that connector. Verify library properties against the
upstream repo or its README at the version the skill targets. Do not verify a name by finding it in
another skill — a wrong name propagates by copy-paste.

**Recommend:** correct to the verified name and cite where you verified it, so the next audit does
not redo the work.

---

## S6 — Prose references to skills that don't exist

**Look for:** unbackticked references — "apply the initial testing framework skill", "use the
standards skill". `C4a` only sees backticked tokens, so these are invisible to it.

**Real instances:** a routing table pointing at ~10 skills that never existed; two remediation
pointers naming a skill by prose description.

**How to check:** grep for `skill` and read the surrounding sentence wherever no backticked name
follows. Pay particular attention to routing tables and "next steps" sections.

**Recommend:** re-point at a real skill, or delete the pointer. Deleting is often better — a vague
pointer is worse than none, because it reads as a real route.

---

## S7 — Internal count and list mismatches

**Look for:** a stated count that does not match the list beneath it. Also totals in tables,
"three rules" above four bullets, and step numbering with gaps.

**Real instance:** "refined his thinking into 12 properties" above a table of 11.

**How to check:** grep for number words and digits followed by a countable noun, then count the
list. Cheap to check, and it directly undermines trust in the skill's factual accuracy.

**Recommend:** verify against the primary source and fix whichever is wrong. Prefer restoring the
missing item over lowering the count — the count is usually right and the list lost something.

---

## S8 — Staleness against upstream reality

**Look for:** guidance describing a library version older than the one the repo now targets;
upgrade notes never folded into the main procedure; workarounds for bugs since fixed.

**How to check:** cross-reference `sync-state.json` against each skill's stated baseline version.
Any skill documenting an upstream library but absent from its `affects` array (`C10-affects-gap`) is
a prime candidate — it has no mechanism to ever be updated.

**Recommend:** update the content and add the skill to the right `affects` array so it does not
re-freeze. Content fix and tracking fix are one finding, not two.

---

## S9 — Silent-degradation steps

**Look for:** any step that can find nothing and continue anyway. Discovery globs, optional file
reads, "if present" lookups, sub-agent hand-offs that pass whatever was found without checking that
anything was.

**Why:** the output looks authoritative while resting on nothing. A hard failure gets fixed in
minutes; this can run wrong for months.

**Real instance:** a standards-discovery glob that matched nothing when run from a consuming repo,
after which the skill continued into its sub-agents and reported a Standards review with no
standards loaded.

**How to check:** for every discovery or lookup step, ask "what happens on zero results?" If the
answer is not "stop and say so", it is a finding.

**Recommend:** add an explicit zero-result stop that reports what was searched. Do not settle for a
warning: a warning inside a long run is not read.

---

## S10 — Instructions leaking into emitted output

**Look for:** internal routing inside a template the skill emits — a report template telling the
*reader* to apply another skill.

**Why:** it escapes the skills base. The instruction lands in a document handed to a colleague, who
sees a reference to a skill they cannot access, in a report that was supposed to be about their
coverage.

**Real instance:** a coverage-report template whose "Next Steps" told the reader to apply a testing
framework skill, so it appeared in every generated report.

**How to check:** read every emitted template and ask whether each line makes sense to someone
outside this repo. Note this survives fixes to the surrounding skill, since the template is a
distinct region.

**Recommend:** drop the skill reference from the template, keeping the underlying advice in
skill-agnostic words if it is useful to the reader.

---

## Fanning out

For a base of this size, one sub-agent per one-or-two S-checks works well. Give each: the skill
inventory, the specific check text, and the instruction to report only concrete `file:line`
instances with the contradiction quoted. Aggregate and assign severity centrally so it stays
consistent — sub-agents systematically over-rate their own findings, since each sees its check in
isolation.

Do not fan out on a `quick` run.
