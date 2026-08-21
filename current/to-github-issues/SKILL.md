---
name: to-github-issues
description: Create or evolve a single, well-structured GitHub issue (business content above technical task content) via the GitHub CLI, from a phase/task reference, a free-text requirement, a broader feature that needs breaking into vertical-slice issues, or an existing live GitHub issue. Use when the user wants a GitHub issue written up or created, a requirement turned into an issue, a phase/spec broken into issues, or an existing live GitHub issue updated because requirements changed. The GitHub issue itself is the source of truth — no local file is generated.
argument-hint: A phase/task reference (3.3, Phase 3, 3.1-3.4), a free-text requirement, a broader feature description to break into issues, or a GitHub issue number/URL.
---

## Default instructions (always apply)

- Produce **one GitHub issue per item**: a single combined issue body that reads business context first, then implementation detail, so the whole issue can be created in one shot instead of being scattered across separate documents. See [references/templates.md](references/templates.md) for the exact structure.
- The GitHub issue is the source of truth — do not write a local `.md` file mirroring it. Draft the body in the conversation for the user to review before it is created or updated.
- A diagram, when warranted, is embedded directly in the issue body's Task Details (see references/templates.md) rather than kept as a separate file, since there is no local artifact for it to live alongside.
- Size single issues to roughly 2-3 days for an average developer (about 5 hours/day) as a rule of thumb — in breakdown mode this is superseded by the tracer-bullet sizing rule in Stage 4 below.
- For verification steps, use `mvn` (not `./mvnw`) when the codebase is Maven-based. Otherwise use the narrowest concrete verification command the stack supports.
- Output markdown only, no implementation code.
- Do not invent architecture, dependencies, deliverables, acceptance criteria, labels, or diagrams that are not supported by the resolved source material.
- **GitHub write guardrail:** you may *read* any GitHub issue/comment freely, and *edit* an existing issue when the user is explicitly evolving it (with confirmation — see Stage 6). You must **never create a new GitHub issue** unless the user explicitly asks you to create one.
- **Always report the issue number and URL back to the requestor immediately after creating a new GitHub issue** — this is the one piece of information the user needs to find their issue, and it must never be left implicit in a longer message.
- **GitHub authentication guardrail:** before any create or edit operation, check that `gh` is available and authenticated. If it is not, stop the write path and return the drafted body plus the intended `gh` command shape for manual use.
- **GitHub issue type:** default to the `type:story` label. Only use a different type label (for example `type:bug` or `type:spike`) when the requester specifically asks for that type — never infer bug or spike from the content alone.
- **Acceptance Criteria location:** the acceptance criteria live in the issue body only, in the `#### Acceptance Criteria` section, as markdown checkboxes. Do not assume any separate GitHub field exists for them.
- **Dependency representation:** when blockers are supported by the source material or approved breakdown, represent them in the issue body as explicit references such as `Blocked by #123`. Also add matching dependency labels such as `blocked-by:123` when those labels already exist or the user has asked for that convention. If label management is out of scope, keep the body references and do not invent label-creation work.
- **No separate task-spec comment:** the task detail already lives in the issue body itself (below the business content, in the same issue), so do not post a duplicate task write-up as a comment.
- **Never close or modify a parent issue.** When breaking a phase/spec down into child issues, or evolving a child issue, leave any parent grouping issue untouched — only the issue actually being created or edited changes.
- Default to the current repository context. If the user explicitly supplies a different repository, use `gh` with the corresponding `--repo owner/name` override.

---

## Stage 1 — Resolve the source

Work from whatever is already in the conversation context first — do not ask the user to re-supply a spec/plan already read this session, a requirement already discussed, or an issue already shown earlier in the conversation.

If the args (or the user's message) contain a reference, fetch and read it **in full** before doing anything else:

| Reference looks like | Action |
|---|---|
| A local file path (spec/plan doc) | `Read` it in full |
| A GitHub issue number or GitHub issue URL | Use `gh issue view` and read the full issue body and any comments needed for context, not a summary |
| Any other URL (doc link, wiki, etc.) | Fetch it and read the full body |

Fetched content becomes input to whichever stage runs next — single-item generation, breakdown drafting, or evolve mode's new information.

If no spec plan document is available and one is needed to resolve a phase/task reference, ask the user to supply it before drafting anything.

## Stage 2 — Explore the codebase (when the work touches code)

Skip this stage only for a pure requirement clarification with no code impact. Otherwise, before drafting any title, story, or task detail:

1. Explore the relevant area of the codebase if it has not already been explored this session (use the Explore agent for anything broader than a couple of targeted lookups).
2. Extract the domain glossary vocabulary already in use — entity names, status enum values, event names, field names. Use these exact terms in the issue title and body instead of paraphrasing them. The title must be concise and use this vocabulary rather than generic phrasing.
3. Check for and respect any ADRs relevant to the area being touched.
4. Look for prefactoring opportunities: make the change easy, then make the easy change. Anything found becomes its own issue, sequenced first, blocking whatever it unblocks.

## Stage 3 — Classify the request

Decide which mode applies before drafting output:

1. **Evolve mode** — the reference resolved in Stage 1 is a live GitHub issue, and the user is supplying new information (changed requirements) to fold into it. → Stage 6.
2. **Breakdown mode** — the request describes a broader feature or spec area that is not already a single scoped item (for example a whole phase that itself is not one task, or a wide free-text feature ask). → Stage 4, then Stage 5 after approval.
3. **Single-item mode** — the request already resolves to one scoped item:
   - A phase/task reference, range, or list (`3.3`, `Phase 3`, `3.1-3.4`, `3.1, 3.3, 4.2`) — expand a phase-with-tasks into one generated item per task; a phase without tasks is itself the item. If any part is ambiguous or unresolvable against the active plan, ask a short clarifying question instead of guessing.
   - A free-text requirement — if it was explicitly provided, use it directly. If it had to be inferred from chat context, state the inferred requirement as one clearly labelled sentence and get user confirmation before drafting.
   → Stage 5 directly.

Never merge multiple adjacent tasks/items into one generated item, and never expand scope beyond what the resolved source actually supports.

## Stage 4 — Breakdown drafting (breakdown mode only)

Full methodology: [references/slicing.md](references/slicing.md). Summary:

- Draft **tracer-bullet issues**: each is a vertical slice cutting a narrow but *complete* path through every layer it touches (schema, API, service, tests, UI where relevant) — never a horizontal single-layer slice.
- Each slice must be demoable or verifiable on its own, and sized to fit a single fresh context window.
- **Exception — wide mechanical refactors** (one change whose blast radius fans across the whole codebase): sequence as expand → migrate batches → contract instead of forcing a tracer bullet. See the reference doc for the full rule, including the integration-branch fallback when batches cannot stay green alone.
- Prefactoring issues from Stage 2 come first, blocking the slices or batches they unblock.
- Give every issue explicit **blocking edges** — which other issues must complete before it can start; an issue with no blockers can start immediately.
- Present the breakdown as a numbered list. For each issue show: **Title**, **Blocked by**, **What it delivers**.
- Ask the user: does the granularity feel right (too coarse or too fine)? Are the blocking edges correct? Should anything merge or split? Iterate until the user approves.
- **Do not draft a full issue body, and do not create any GitHub issue, until the breakdown is approved.**

Once approved, treat each approved issue as a single-item generation pass through Stage 5, carrying its blocking edges into that issue's `Dependencies/Blockers` field and body-level `Blocked by #...` notes when referenced issues already exist.

## Stage 5 — Generate and create the issue

Full template: [references/templates.md](references/templates.md). In short, for each item (from single-item mode, or an approved breakdown issue):

1. Draft the combined issue body — business content (title, user story, short description, estimation factors, blocker note), kept high-level enough that the team can gauge impact and scope for estimation without reading code, then a horizontal rule, then `## Task Details` (goal, spec foundation, inputs, scope, deliverables, acceptance criteria, dependencies/blockers, verification, notes/risks, and an embedded diagram if one is warranted).
2. Show the drafted body to the user in the conversation for review — this is the only draft artifact; nothing is written to disk.
3. Per the GitHub write guardrail, do **not** call `gh issue create` unless the user explicitly asks you to create the GitHub issue — ask `Want me to create this as a GitHub issue?` if they have not already said so in this request. Once confirmed:
   - Validate `gh` availability and auth state first.
   - Resolve the target repository from the current directory unless the user explicitly supplied `--repo owner/name`.
   - Create the issue with title = the concise domain-vocabulary title, body = the full combined body, and labels including the default `type:story` label unless the user requested a different type label.
   - Carry approved dependency labels such as `blocked-by:123` when they are part of the repo's working convention or the user explicitly asked for them.
   - If this issue was carried over from an approved breakdown with a parent grouping issue, reference that parent in the body as context if the source material supports it — but never modify the parent issue itself.
   - **Immediately report the created issue number and URL back to the user** — every first-time creation must end with this, not just a general completion message.
   - If `gh` is unavailable or unauthenticated, tell the user and offer the drafted body plus the intended `gh issue create` command shape for manual use.

## Stage 6 — Evolve mode

- The target is always a live GitHub issue — use the body and comments already fetched in Stage 1 as the existing artifact being evolved.
- Merge the new information into the existing structure: update only the sections it actually affects, leave everything else untouched. This is an edit, not a regeneration — never rewrite the issue from scratch when evolving it.
- **Before writing an update back to the live GitHub issue**, draft the change and show it to the user, then get explicit confirmation before calling the edit command — this is a side-effectful action on a shared system.
- If the change affects the Acceptance Criteria section, update the issue body so the checklists stay accurate.
- If the change affects dependency references or type labels, update those too, but only where the new information actually justifies it.
- Never create a new GitHub issue while evolving (or in any other mode) unless the user explicitly asks for that.
- If `gh` is unavailable or unauthenticated, stop before the write and return the revised body plus the intended `gh issue edit` command shape for manual use.
