---
name: implement-github-issue
description: "Implement code from a GitHub issue end-to-end: read issue → explore codebase → apply TDD + standards → verify acceptance criteria → close issue. Use when the user asks to 'implement issue #N', 'work on issue #N', 'build issue #N', 'fix issue #N', 'implement GitHub issue', or any variation of implementing/building/fixing from a GitHub issue number or URL. This orchestrates the full implementation workflow, delegating to to-github-issues (reading), tdd-by-example (test-driven implementation), language-specific standards skills, and verification. Do NOT use for creating new issues (use to-github-issues) or reviewing code (use code-review)."
argument-hint: "GitHub issue number (#123) or URL to implement"
---

# Implement GitHub Issue

Orchestrate the complete workflow for implementing code from a GitHub issue: reading the issue specification, exploring the codebase, applying test-driven development and language-specific standards, verifying all acceptance criteria, and closing the issue with a summary.

This skill is an **orchestrator** — it does not duplicate the logic of other skills, but rather sequences them in the correct order for the "implement from issue" workflow.

## Operating Rules

These rules apply to every implementation, regardless of stage:

1. **One issue per invocation** — handle a single GitHub issue from start to finish. Multi-issue orchestration is out of scope.
2. **Read-only until closure** — never modify the issue during implementation. The issue body and acceptance criteria are the contract; implementation adapts to them, not vice versa.
3. **Verify all acceptance criteria** — before closing, confirm every checkbox in the issue's acceptance criteria section can be ticked. If any cannot, pause and ask the user how to proceed.
4. **Close with summary** — use `gh issue close --comment "..."` with a completion summary listing which acceptance criteria were verified and how. Never close silently.
5. **Check gh authentication** — before any `gh` command, verify `gh` is available and authenticated. If not, stop and tell the user.
6. **Respect existing context** — if the issue was already read earlier in this session, use that content instead of re-fetching. If codebase exploration already happened, use that knowledge.
7. **Pause on ambiguity** — if acceptance criteria are missing, incomplete, or contradict each other, stop and ask the user to clarify or update the issue before implementing. Do not invent requirements.
8. **Apply language-specific standards** — detect the project type (Java, TypeScript, Python, etc.) and search for matching `*-standards` skills dynamically. Apply them alongside implementation.
9. **Default to test-driven development** — unless the work is pure configuration/glue (see escape hatches below), apply the tdd-by-example skill for all behavior implementation.
10. **No branch creation** — focus on the implement → verify → close cycle. Branch-per-issue workflows are handled separately via git conventions or hooks.

---

## Stage 1 — Resolve the Issue

Fetch and read the GitHub issue in full before any implementation work.

### If the issue was already read this session
- Use the content already in conversation context
- Skip re-fetching unless the user explicitly asks to refresh

### If the issue has not been read yet
1. **Validate input** — ensure the user provided a GitHub issue number (e.g., `#123`, `123`) or URL
2. **Apply to-github-issues Stage 1** — use `gh issue view <number>` to fetch the full issue body, not a summary
3. **Read the entire issue** — including title, description, acceptance criteria, comments if needed for context
4. **Confirm acceptance criteria exist** — look for the `#### Acceptance Criteria` section with markdown checkboxes
   - If missing or empty, pause and ask: "This issue has no acceptance criteria. Should I suggest some based on the description, or would you like to update the issue first?"
   - If ambiguous or contradictory, pause and ask for clarification before proceeding

### Extract key information
- **What** — the behavior or feature to implement (from description and acceptance criteria)
- **Where** — which part of the codebase it affects (from task details or inferred from description)
- **How to verify** — the verification steps listed in the issue, or acceptance criteria checkboxes
- **Dependencies** — any "Blocked by #N" references or dependency notes

If dependencies exist and are not yet closed, stop and tell the user: "Issue #N is blocked by #M. Should I implement #M first, or has that dependency been resolved?"

---

## Stage 2 — Explore the Codebase

Understand the relevant area of the codebase before writing any code.

### Skip exploration only if
- The user explicitly requested "skip exploration" or "don't explore"
- AND the code area was already explored earlier in this session for this same issue

### Otherwise, always explore
1. **Invoke the Explore agent** with `thoroughness: medium` and a query describing:
   - The feature/behavior being implemented (from the issue)
   - The likely codebase area it touches (inferred from issue description or task details)
   - What you need to understand: existing structure, naming conventions, similar implementations

2. **Extract domain vocabulary** — entity names, field names, enum values, event names, method names already in use
   - Use these exact terms in implementation instead of paraphrasing or inventing new names
   
3. **Check for architectural decision records (ADRs)** — if the codebase has an ADRs directory, check for decisions relevant to the area being changed

4. **Look for prefactoring opportunities** — "make the change easy, then make the easy change"
   - If the change would be significantly easier after a preparatory refactor (extract a method, introduce a parameter, etc.), note it
   - Prefactoring becomes a separate verification step, done first, with its own test cycle

### Report findings briefly
Show the user a 2-3 sentence summary of what you learned:
- Key files/classes involved
- Existing patterns to follow
- Any prefactoring needed

---

## Stage 3 — Classify the Implementation Approach

Decide which implementation mode applies before writing code.

### Test-Driven Development (default)
Apply the **tdd-by-example** skill when implementing:
- New behavior (business logic, API endpoints, transformations, calculations)
- Bug fixes (write a failing regression test first, then fix)
- Data transformations or integrations with branching logic

### Configuration/Glue (escape hatch)
Skip TDD and write code directly when implementing:
- Pure configuration (application.properties, YAML files, JSON config)
- Dependency wiring with no logic (Spring bean definitions, dependency injection setup)
- Boilerplate with no branching (DTOs, simple getters/setters, trivial mappers)
- The user explicitly requested "just implement it" or "skip tests for this"

**Signal that glue has become logic:** you're about to write a conditional, a loop with more than one branch, or any step that transforms/reconciles data from multiple sources. None of those are glue — switch to TDD mode.

### Language-Specific Standards
Detect the project type and apply matching standards skills:

1. **Search for available standards skills** — look for files matching `.agents/skills/*-standards/SKILL.md` or `.github/skills/*-standards/SKILL.md`
2. **Apply all that match the project** — for example:
   - Java + Spring Boot → apply `java-21-standards` and `java-21-springboot-standards`
   - Java + Spring Boot + tests → also apply `java-springboot-unit-tests`
   - TypeScript + React → apply `typescript-standards` and `react-standards` (if they exist)
3. **If no standards skills exist** — proceed with general best practices for the detected language

---

## Stage 4 — Implement with Test-Driven Development

Apply the **tdd-by-example** skill's Red-Green-Refactor cycle for all behavior implementation.

### If using TDD mode
1. **Make a test list** — based on acceptance criteria and the behavior described in the issue, list 3-7 test cases in English (not code yet)
2. **Show the test list to the user** — brief confirmation, 3-5 lines
3. **Pick the first test** — the simplest, most obvious case
4. **RED** — write a failing test, run it, watch it fail
5. **GREEN** — write minimum code to pass, run it, watch it pass
6. **REFACTOR** — clean up duplication, run tests, keep them green
7. **Repeat** — pick next test from the list, go back to step 4

See the **tdd-by-example** skill for full cycle details, including:
- When to use Fake It vs Obvious Implementation vs Triangulate
- How to keep steps small (Child Test pattern)
- How to refactor only on green
- When property-based testing applies

### If using configuration/glue mode
1. Write the code directly
2. Verify it's actually right (check output values, not just exit code)
3. If branching logic appears, stop and switch to TDD mode for that part

### Apply language-specific standards
- Follow naming conventions from the standards skills
- Use idiomatic patterns for the language/framework
- Respect immutability, error handling, and design principles from the standards

---

## Stage 5 — Verify Acceptance Criteria

Before closing the issue, confirm every acceptance criterion can be verified.

### For each checkbox in the issue's acceptance criteria section
1. **Identify the verification method** — from the issue's "Verification" section, or infer from the criterion itself:
   - Build succeeds → run the build command (`mvn clean compile`, `npm run build`, etc.)
   - Tests pass → run the test suite (`mvn test`, `npm test`, `pytest`, etc.)
   - Feature works → manual verification or acceptance test
   - File exists → check the filesystem
   
2. **Execute the verification** — actually run the command or check the condition
   - For build/test commands, use the execution subagent or run_in_terminal
   - Show the result (exit code, relevant output lines)
   
3. **Mark the criterion** — track which ones pass and which ones fail or are ambiguous

### If all criteria are verified
Proceed to Stage 6 (close the issue).

### If any criterion cannot be verified
Pause and ask the user:
- "Acceptance criterion 'X' cannot be verified because Y. Should I attempt to fix this, or mark the issue as partially complete?"

Do not invent or skip criteria to force a green status.

---

## Stage 6 — Close the Issue

Close the issue with a completion summary listing what was verified.

### Before closing
1. **Check gh authentication** — verify `gh` is available and authenticated
   - If not: tell the user and stop (do not attempt to close)
   
2. **Confirm all acceptance criteria verified** — from Stage 5
   - If any are unverified, do not close without user confirmation

3. **Draft the close comment** — format as a completion summary:
   ```
   Completed all acceptance criteria:
   - ✓ Criterion 1 description
   - ✓ Criterion 2 description
   - ✓ Criterion 3 description
   
   Verified via: <verification method, e.g., "mvn test" passes, "mvn clean compile" exit code 0>
   ```

### Close the issue
1. Use `gh issue close <number> --comment "<summary>"`
2. Report the result to the user: "✓ Closed issue #N"

### If closing fails
- Show the error message
- Tell the user they can close manually with the drafted comment

---

## Skill Delegation

This skill orchestrates other skills rather than duplicating their logic:

| Stage | Delegates to | When |
|---|---|---|
| Stage 1 | **to-github-issues** Stage 1 | Always — to read the issue via `gh issue view` |
| Stage 2 | **Explore** subagent | Always (unless user skips or already explored) |
| Stage 3 | Skill discovery (`*-standards`) | Always — dynamically find and apply language-specific standards |
| Stage 4 | **tdd-by-example** | When implementing behavior (not config/glue) |
| Stage 4 | **java-springboot-unit-tests** | When implementing Java Spring Boot tests |
| Stage 4 | Language-specific standards skills | When writing code in that language |
| Stage 6 | **to-github-issues** (gh commands) | Always — to close the issue |

**Symmetric collaboration:**
- **tdd-by-example** says "For Java projects, apply alongside java-springboot-unit-tests"
- **java-springboot-unit-tests** says "For test-first workflow, apply tdd-by-example alongside"
- This skill invokes both when detected (Java + Spring Boot + TDD mode)

---

## Anti-Patterns

**Do NOT do these:**

- **Creating the issue** — that's to-github-issues' job. This skill only implements existing issues.
- **Skipping codebase exploration** — even when the issue seems clear, always explore (unless user explicitly skips). Missing context leads to mismatched naming and incorrect assumptions.
- **Inventing acceptance criteria** — if the issue lacks them, pause and ask. Do not guess what "done" means.
- **Closing without verification** — never close an issue without executing the verification steps and confirming they pass.
- **Modifying the issue during implementation** — the issue is the contract. If requirements change mid-implementation, stop and tell the user to update the issue first (via to-github-issues Stage 6 evolve mode).
- **Implementing multiple issues at once** — this skill handles one issue per invocation. For multiple issues, run this skill multiple times.
- **Silent closure** — always close with `--comment` including a summary. Never just `gh issue close <number>`.
- **Skipping TDD for "simple" logic** — if it has a conditional, loop, or transformation, it's not glue. Apply the TDD cycle.
- **Hardcoding language assumptions** — dynamically detect project type and discover standards skills. Do not assume Java or any specific stack.

---

## Quick Reference

**Trigger phrases:**
- "implement issue #123"
- "work on issue #456"  
- "build issue #789"
- "fix issue #42"
- "implement GitHub issue"
- "implement #1"

**Not this skill:**
- "create an issue for X" → use **to-github-issues**
- "review my code" → use **code-review**
- "write tests for X" → use **tdd-by-example** directly
- "close issue #N" → direct `gh` command (no implementation needed)

**Workflow summary:**
1. Read issue (gh issue view)
2. Explore codebase (Explore agent, medium thoroughness)
3. Classify approach (TDD vs glue, detect language standards)
4. Implement (Red-Green-Refactor cycle via tdd-by-example)
5. Verify acceptance criteria (run builds, tests, checks)
6. Close issue (gh issue close --comment with summary)
