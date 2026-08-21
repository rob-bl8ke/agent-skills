# Combined issue template

Every item produces one combined issue body — business content and task content live in the same document, business content first, and that body becomes the Jira issue's description directly. There is no local file: the drafted body is shown to the user in conversation for review, then used as-is for `createJiraIssue` (or `editJiraIssue` in evolve mode).

## The issue body

This is the exact content used for `createJiraIssue`'s description field; the `### {title}` line becomes the Jira issue's summary/title field instead of staying in the body.

**Issue type:** defaults to **Story**; only use another type (Bug, Spike, etc.) if the requester specifically asked for it.

**Acceptance Criteria field:** when the Jira MCP connector is used to create or update the ticket, the acceptance criteria bullet list must exist in **both** the description body's `#### Acceptance Criteria` section **and** the dedicated Jira `acceptance criteria` field, written as checkboxes in each place — never only one or the other.

Exact structure, top to bottom — business content above, technical task content below the `## Task Details` divider:

```markdown
### {Concise title using the project's domain glossary vocabulary}

{Write as a user story grounded in the resolved source material: "As a {role}, I want {capability}, so that {value}."}

#### Short Description
{A concise paragraph summary of the work}

#### Estimation Points
1. {Concrete factor that affects effort}
2. {Concrete factor that affects effort}

{Very short paragraph noting real dependency/blocker context, or that there is none — one or two sentences, not a list}

---

## Task Details

#### Goal
{2-4 sentences describing the outcome and why it exists}

#### Spec Foundation
- {Relevant requirement or decision from the resolved source material}
- {Optional second supporting reference}

#### Inputs
- {Upstream task, spec section, or artifact}
- {Upstream task, spec section, or artifact}

#### Scope Included
- {Required item}
- {Required item}
- {Required item}

#### Scope Excluded
- {Explicit non-goal}
- {Explicit non-goal}

#### Deliverables
- {Code, config, doc, or test artifact}
- {Code, config, doc, or test artifact}

#### Acceptance Criteria
- [ ] {Observable done condition}
- [ ] {Observable done condition}
- [ ] {Observable done condition}

#### Dependencies/Blockers
- {Only include this section when there are real dependencies or blockers supported by the source material or an approved breakdown's blocking edges}

#### Verification
- {`mvn` command, or other automated check}
- {Manual check if needed}

#### Notes / Risks
- {Optional edge case, ambiguity, or follow-up concern}

#### Diagram
{Only include this section when a sequence/state/activity diagram would materially reduce ambiguity. Embed it directly, in the diagram's own fenced code block, e.g.:}
```plantuml
{PlantUML script}
```
{Followed by a one-line summary of what it shows. Cross-check PlantUML syntax for correctness before including it. If no diagram adds meaningful clarity, omit this whole section.}
```

Notes on filling this in:
- The number of bullets in each list section should match what the source material actually supports — the counts shown above are typical, not fixed quotas. Don't pad to hit a number, and don't omit a real item to stay short.
- Acceptance Criteria items are checkboxes (`- [ ] ...`) in the body because they're mirrored into Jira's dedicated AC field as action items; keep the two in sync.
- Omit the entire `#### Dependencies/Blockers` subsection when there are no supported dependencies or blockers — don't write "None" as a placeholder.
- The short dependency/blocker paragraph directly under Estimation Points is a *narrative* heads-up for business readers (e.g. "This depends on the notification service work landing first"), distinct from the structured `#### Dependencies/Blockers` list under Task Details, which is the precise, ticket-referenced version for the implementer.
- The `---` divider between the dependency paragraph and `## Task Details` is a hard scope boundary: everything above it must stay readable by someone with no codebase context, and everything below it can freely use technical/domain vocabulary.
- Keep everything above the `---` divider (title, story, short description, estimation points, dependency note) at a level a non-technical stakeholder or estimator can skim in under a minute — enough to gauge impact, scope, and rough size, without implementation detail. Push anything requiring codebase or architecture knowledge below the divider into `## Task Details`.
- Omit `#### Verification` only if the item truly has no automated or manual check (rare) — otherwise always include at least one concrete check.
- Omit `#### Notes / Risks` entirely when there's nothing genuinely worth flagging — don't manufacture a risk to fill the section.
- Omit `#### Diagram` entirely unless a diagram materially improves understanding — most issues won't need one.

## Requirement-mode specifics

When the item comes from a free-text requirement rather than a plan phase/task:
- Derive a concise task title from the requirement if one isn't explicit.
- Dependencies are referenced descriptively (e.g. "Upstream auth service task") rather than by plan-task number.
