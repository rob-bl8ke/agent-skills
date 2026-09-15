# Language And Design

Use when changing TypeScript modules, public APIs, imports, exports, naming, functions, classes, interfaces, generics, decorators, or control flow.

## MUST

- Preserve public API behavior, type contracts, and compatibility unless the task explicitly changes them.
- Use named exports by default; reserve default exports for modules where a single canonical export is both obvious and stable.
- Keep imports explicit: every imported name must be traceable to its source module without ambiguity.
- Annotate public function signatures with explicit parameter types and return types; do not rely on callers to infer them.
- Use `interface` for shapes that define object contracts, especially when other code may implement or extend them.
- Use `type` aliases for unions, intersections, mapped types, conditional types, and cases where `interface` syntax cannot express the shape.
- Distinguish public surface from internal implementation: exported names are public; unexported names are internal.
- Use `readonly` on properties and array types where mutation is not intended, especially in shared data structures.
- Use `const` for all bindings that are not reassigned; use `let` only when reassignment is required.

## SHOULD

- Follow naming conventions: `camelCase` for variables, functions, and properties; `PascalCase` for types, interfaces, classes, enums, and type parameters; `UPPER_SNAKE_CASE` for module-level constants.
- Prefer type parameter names that carry meaning (`TItem`, `TKey`) over single-letter names (`T`, `K`) when the parameter's role is not immediately obvious from context.
- Prefer simple functions and composition over class hierarchies when no shared behavioral contract requires inheritance.
- Use `class` for entities with encapsulated mutable state, lifecycle methods, or when implementing an interface contract; prefer plain objects and functions otherwise.
- Write JSDoc comments for public modules, functions, classes, and types; document non-obvious parameters, return values, and thrown errors.
- Use `abstract` classes only when a genuine partial-implementation contract exists; prefer `interface` when only shape is required.
- Use stage-3 decorators (`@decorator`) when the repository already uses them and the purpose is a real cross-cutting concern; do not introduce decorators for single-use behavior.
- Prefer explicit control flow (early returns, guard clauses) over deeply nested conditionals.
- Use optional chaining (`?.`) and nullish coalescing (`??`) for safe property access and defaults; prefer them over manual null checks.
- Use `satisfies` to validate a value matches a type while preserving its inferred literal type.

## CONSIDER

- Use `namespace` merging to augment existing module types when extending a third-party module's declarations; avoid `namespace` as a replacement for ES modules in new code.
- Use `abstract` classes with protected template methods when a base class genuinely provides shared algorithm structure.
- Define type parameters with constraints (`T extends SomeType`) to tighten inference and prevent invalid usages at call sites.
- Use function overloads when a function has genuinely distinct call signatures that cannot be expressed as a single union.

## AVOID

- Barrel (`index.ts`) re-export files that accumulate large surfaces without clear ownership boundaries.
- Import-time side effects beyond registering well-defined module initializers that callers expect.
- Deep class hierarchies; prefer composition, interfaces, or structural typing to model shared behavior.
- Assigning `this` context to variables to work around callback binding; use arrow functions or explicit `.bind()` only when required.
- `enum` for open-ended string sets; prefer `const` object maps or union literal types (see [Legacy And Anti-Patterns](./legacy-and-anti-patterns.md)).
- Generic type parameters with no constraint and no semantic purpose; they add noise without safety.

## NEVER

- Use `var`; use `const` or `let`.
- Re-export everything from a module using `export * from` in ordinary implementation code where the surface is not deliberately curated.
- Change public behavior or exported names only to satisfy style guidance.
- Use `Function` (capital-F) as a type; use a specific call signature instead.
- Use `Object` (capital-O) or `{}` as a type to mean "any non-nullish value"; use `unknown` or a specific shape.

## Agent Guardrails

- Do not rename public exports for style unless the user requested an API-breaking change.
- Do not introduce framework patterns (DI containers, decorators, metadata reflection) into language-only code.
- Prefer local consistency over broad naming convention rewrites in untouched code.
