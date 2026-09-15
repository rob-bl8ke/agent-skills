---
name: typescript-5-5-standards
description: Use when writing, reviewing, or refactoring TypeScript 5.5.x code. Applies language-level TypeScript standards, idiomatic type system usage, ESM module conventions, error and resource handling, async/await guardrails, and AI-agent anti-overengineering rules. Do not use as a substitute for React, Node.js, Angular, NestJS, Vitest, Jest, ESLint, Prettier, packaging, ORM, data-science, infrastructure, or deployment standards.
---

# TypeScript 5.5 Standards

Write idiomatic, maintainable TypeScript 5.5.x code using stable language features and the TypeScript standard type system. This skill is policy-oriented; load the referenced files only when the task touches that area.

## Target Environment

Target: TypeScript 5.5.x.
Compiler: `tsc` 5.5.x; assume `"strict": true` unless local tsconfig explicitly overrides individual checks.
Module system: ECMAScript Modules (ESM) by default; treat CommonJS as legacy unless the repository requires it.
Stable features: `using` / `await using` (Explicit Resource Management), `satisfies` operator, `const` type parameters, stage-3 decorators, `NoInfer<T>`, inferred type predicates, `--isolatedDeclarations`, import attributes, `verbatimModuleSyntax`, template literal types, mapped types, conditional types with `infer`, `RegExp` literal syntax checking.
Preview or experimental features: excluded unless explicitly requested.
Frameworks and tools: excluded; child skills handle React, Node.js, Angular, NestJS, testing frameworks, linters, formatters, ORMs, bundlers, and deployment.

## Operating Rules

- MUST preserve runtime behavior, public contracts, and repository conventions unless the task explicitly changes them.
- MUST assume `"strict": true` is active; never write code that relies on permissive compiler options being disabled.
- MUST prefer explicit, readable code over clever, overly-generic, or excessively mapped types.
- SHOULD follow the principle that types exist to model the domain, not to pass the compiler.
- SHOULD use stable TypeScript 5.5 features when they make code clearer or safer.
- SHOULD prefer built-in utility types before writing custom mapped or conditional equivalents.
- SHOULD make the smallest coherent change and avoid unrelated modernization.
- AVOID adding type-level abstractions, conditional type gymnastics, decorator layers, or dependency injection solely because they might be useful later.
- NEVER introduce pre-TypeScript-5 workarounds, CommonJS `require()` shims, or triple-slash directives in new ESM code.

## Classification Meanings

| Level | Meaning |
|---|---|
| MUST | Required for correctness, safety, type contracts, or strong platform guarantees. |
| SHOULD | Recommended default; deviate when there is a concrete reason. |
| CONSIDER | Useful technique whose value depends heavily on context. |
| AVOID | Usually produces worse code; use only with a specific justification. |
| NEVER | Essentially prohibited in normal application code for this TypeScript baseline. |

## Always-Loaded Baseline

- Prefer clear names, small functions, straightforward control flow, and types that document intent.
- Use `camelCase` for variables, functions, and properties; `PascalCase` for types, interfaces, classes, and enums; `UPPER_SNAKE_CASE` for module-level constants.
- Prefer type inference for local variables; annotate public function boundaries, return types of non-trivial functions, and non-obvious data shapes.
- Prefer `interface` for object shapes that may be extended or implemented; prefer `type` aliases for unions, intersections, mapped types, and conditional types.
- Use `const` by default; use `let` only when reassignment is required; never use `var`.
- Prefer `unknown` over `any` at trust boundaries; narrow explicitly before use.
- Keep async code explicit: do not mix synchronous and asynchronous APIs carelessly, and never leave floating promises.
- Use `using` / `await using` for resources that implement `Symbol.dispose` / `Symbol.asyncDispose`.

## Non-Standards

This skill refuses to universalize these choices:

- Formatter choice, including Prettier or dprint.
- Exact maximum line length beyond readability and repository convention as authority.
- Linter, type checker strictness beyond `strict: true`, or plugin selection.
- Testing framework choice, including Jest, Vitest, or Mocha.
- Project architecture, folder layout, service layering, or domain model pattern.
- Web framework, ORM, bundler, package manager, task runner, cloud provider, or deployment model.
- Runtime environment (Node.js, Deno, Bun, browser) specifics; I/O, path, subprocess, and platform APIs belong to child skills.
- Mandatory JSDoc comments for every private helper.
- Blanket rules for single versus double quotes beyond consistency and repository convention.

## Reference Guide

| Reference | Use When |
|---|---|
| [Language And Design](./references/language-and-design.md) | Modules, imports, exports, naming, functions, classes, interfaces, generics, decorators, structural typing, control flow. |
| [Types And Data](./references/types-and-data.md) | Type inference, narrowing, discriminated unions, utility types, mapped/conditional types, `satisfies`, `const` type params, `NoInfer`, inferred predicates. |
| [Errors And Resources](./references/errors-and-resources.md) | `unknown` in catch, error narrowing, `using`/`await using`, validation at system boundaries, cleanup discipline. |
| [Async And Concurrency](./references/async-and-concurrency.md) | Promises, async/await, `AbortController`, `AsyncDisposable`, microtask hazards, floating promises, event-loop blocking. |
| [Code Quality](./references/code-quality.md) | `strict` mode, `isolatedDeclarations`, tsconfig discipline, type-correctness over assertions, testability, security, import hygiene. |
| [Legacy And Anti-Patterns](./references/legacy-and-anti-patterns.md) | `any` overuse, non-null assertion abuse, `as`-assertion overuse, legacy `enum` pitfalls, `namespace`/`module` keyword, CommonJS remnants, pre-TS5 decorator syntax. |
| [Agent Behaviour](./references/agent-behaviour.md) | AI-specific constraints, modernization limits, composability, repository override rules. |

## Sources

- TypeScript 5.0–5.5 release notes and What's New documentation.
- TypeScript Handbook: Everyday Types, Narrowing, More on Functions, Object Types, Type Manipulation, Classes.
- TypeScript TSConfig Reference.
- TC39 proposals: Explicit Resource Management (`using`), Decorators (stage 3), Import Attributes.
- ECMAScript 2022–2024 specification for language primitives underlying the type system.

## Workflow

1. Identify whether the task is language-level TypeScript work or belongs to a framework, testing, tooling, or platform overlay.
2. Preserve local conventions first, then apply this skill where the repository is silent.
3. Load only the relevant reference files for the code being changed.
4. Classify proposed guidance as MUST, SHOULD, CONSIDER, AVOID, or NEVER.
5. Prefer the smallest clear change that preserves public behavior and type contracts.
6. Avoid unrelated modernization, dependency additions, and speculative type abstractions.
