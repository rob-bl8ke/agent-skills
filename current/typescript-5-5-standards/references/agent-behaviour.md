# Agent Behaviour

Use when deciding how an AI coding agent should apply TypeScript 5.5 standards without overreaching.

## MUST

- Determine whether the change is language-level TypeScript or belongs to a child framework, testing, tooling, platform, or infrastructure skill.
- Preserve repository conventions over generic guidance when they conflict.
- Make the smallest coherent change that solves the task.
- Preserve public behavior, exported names, data shapes, and type contracts unless explicitly changing them.
- Keep generated code compatible with TypeScript 5.5.x and the project's declared `target` and `moduleResolution` settings.
- Load only reference files relevant to the code being changed.

## SHOULD

- Prefer built-in TypeScript utility types and language features before adding helper libraries.
- Match surrounding code style in touched files, even when it differs from generic guidance.
- Improve nearby clarity when it directly supports the requested change.
- Run `tsc --noEmit` or the repository's existing type-check command to validate generated code when the repository already has one.
- Explain deviations from this skill when correctness, compatibility, or local convention requires them.

## CONSIDER

- Suggest a child skill when the work clearly depends on React, Node.js, NestJS, Angular, Vitest, Jest, Prisma, or deployment conventions.
- Propose broader modernization (e.g., migrating `enum` to union literals, removing barrel files) separately when discovered issues are real but outside the task scope.

## AVOID

- Repository-wide import reorganization, type annotation additions, or async conversions unless explicitly requested.
- Adding validation frameworks, DI containers, abstract base classes, or configuration systems for simple code.
- Treating style preferences as type-contract mandates.
- Replacing stable local idioms without a concrete correctness or maintainability reason.

## NEVER

- Modify unrelated files to satisfy this skill.
- Add a package manager, bundler, linter, formatter, test framework, web framework, ORM, or cloud deployment tool from this skill alone.
- Break runtime or type compatibility only to make code look more modern.
- Suppress type errors with `@ts-ignore` or `as any` to make generated code compile without understanding the root cause.

## Composability Checks

- A React, Node.js, NestJS, or Angular skill can add ecosystem-specific rules without contradicting this base skill.
- A testing skill (Vitest, Jest) can define test-specific compiler options, assertion patterns, and mock conventions without changing this skill's language-level guidance.
- A formatter or linter skill (Prettier, ESLint) can define exact quote style, line length, and rule selection without conflicting with this skill's type-system guidance.
- A deployment or infrastructure skill can define environment variables, logging, secrets management, and process rules without this skill taking ownership of those concerns.
- If an overlay needs to contradict a MUST or NEVER here, re-check whether the base rule is too broad or the overlay is relying on unsafe behavior.
