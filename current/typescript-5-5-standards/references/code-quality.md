# Code Quality

Use when evaluating compiler configuration, type-level correctness, import discipline, testability, security, or code maintainability.

## MUST

- Enable `"strict": true` in `tsconfig.json`; do not disable individual strict flags without a documented, repository-wide reason.
- Never use `@ts-ignore` on new production code; use `@ts-expect-error` with a one-line comment explaining why the suppression is safe when unavoidable.
- Do not introduce `"skipLibCheck": true` as a workaround for type errors in your own code.
- Treat type assertions (`as SomeType`) as a correctness risk; every assertion should be justified at the use site.
- Ensure every module has a single, clear responsibility; split files that accumulate unrelated exports.
- Do not access `prototype` for runtime property manipulation on types you do not own.
- Sanitize or validate all user-controlled input before it reaches database queries, template strings, dynamic `import()`, `eval`, or `Function` constructors.

## SHOULD

- Enable `"isolatedDeclarations": true` on library code and packages with a public API; it enforces that declaration files can be generated without full type-checking and makes distributed types more reliable.
- Use `"verbatimModuleSyntax": true` to eliminate import elision surprises and enforce explicit `import type` for type-only imports.
- Use `import type { T }` for imports used only at the type level; it produces no runtime code and clarifies intent.
- Prefer `"moduleResolution": "bundler"` or `"node16"` / `"nodenext"` over legacy `"node"` in new projects to align with modern module resolution semantics.
- Keep `tsconfig.json` paths explicit; avoid overly broad `include` globs that pull in test fixtures or generated files into the main program.
- Write code that is testable by default: pure functions, injected dependencies, and minimal global state.
- Co-locate tests with the code they test unless the repository establishes a different convention.
- Prefer checking with `tsc --noEmit` in CI to catch type regressions before they reach production.

## CONSIDER

- Split tsconfig into base + environment overlays (`tsconfig.base.json`, `tsconfig.app.json`, `tsconfig.test.json`) when test code requires different compiler options from production code.
- Use project references (`"references"` in tsconfig) for monorepo setups to enable incremental builds and proper dependency ordering.
- Add `"exactOptionalPropertyTypes": true` for stricter optional property handling when the codebase models absence precisely.
- Use `"noUncheckedIndexedAccess": true` to force narrowing when accessing array elements and index-signature values.

## AVOID

- Accumulating type assertions in a module as a pattern; each `as` is a gap in the type system that must be justified.
- Disabling `strictNullChecks` to silence null-related errors; fix the types and guards instead.
- Implicit `any` from untyped third-party imports; install `@types/` packages or write a minimal local declaration.
- Circular import dependencies; restructure modules to break cycles or extract shared types to a dedicated module.
- Re-exporting every import from a barrel file without intentional API curation; barrels slow editors and compilers on large codebases.
- Dynamic `eval()`, `new Function(string)`, or `import(userControlledString)` without strict validation and sandboxing.
- Prototype pollution: never merge user-controlled keys into plain objects without an allowlist.

## NEVER

- Disable `strictNullChecks` or `noImplicitAny` in production source code to make type errors go away.
- Commit code with `@ts-ignore` suppressions without explanation.
- Use `innerHTML = userInput` or equivalent DOM sinks with unescaped user-controlled content.
- Construct SQL queries, shell commands, or dynamic `import` paths by concatenating untrusted strings.

## Agent Guardrails

- Do not add `"strict": false` or disable individual checks to make generated code compile.
- Do not rewrite tsconfig files wholesale; make targeted additions unless a comprehensive review was requested.
- Do not introduce barrel index files speculatively; create them only when a deliberate public API surface is required.
