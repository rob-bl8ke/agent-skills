# Legacy And Anti-Patterns

Use when reviewing old idioms, generated code, broad refactors, or suspicious patterns that pre-date TypeScript 5.x conventions.

## MUST

- Keep compatibility with the repository's declared TypeScript baseline; for this skill, new code guidance assumes TypeScript 5.5.x.
- Treat TypeScript 4.x-era workarounds (pre-`satisfies`, pre-stage-3 decorators, manual type predicate annotations that are now inferred) as candidates for replacement only when touching that code.
- Preserve intentional legacy behavior when modifying old code unless modernization is part of the task.

## SHOULD

- Replace CommonJS `require()` calls in ESM-targeted files when doing so is local and behavior-preserving.
- Replace `namespace` declarations used as value containers with plain ES module exports in new and actively maintained code.
- Replace the legacy experimental decorator syntax (`"experimentalDecorators": true`) with stage-3 decorators in touched code when the repository has migrated or is migrating.
- Replace `as any` on caught errors with `unknown` narrowing now that `useUnknownInCatchVariables` is the strict default.
- Replace `Optional<T>` / home-grown nullable wrappers with `T | undefined` union types where the pattern adds no structural benefit.
- Prefer `T[]` or `Array<T>` consistently; pick the form that matches local convention rather than mixing both.

## CONSIDER

- Modernize touched code incrementally when it reduces complexity and does not broaden the change.
- Leave stable legacy patterns alone when the surrounding code relies on them and modernization would require a wider change than the task warrants.
- Convert `enum` declarations to `const` object maps or union literal types in actively changing modules; see guidance below.

## AVOID

- `enum` with computed or heterogeneous values; numeric enums silently accept any `number` due to structural assignability and reverse-mapping behavior is rarely needed.
- `namespace` as a substitute for ES modules; use `import`/`export` in new code.
- Triple-slash references (`/// <reference path="..." />`) in new code; use `import` or `types` in tsconfig.
- `declare module "*"` wildcard module declarations that turn every untyped import into `any`.
- `Object.assign` for deep merging objects without guarding against prototype pollution.
- Explicit type annotations that reconstruct what `tsc` infers accurately; remove annotation noise.
- `Function.prototype.apply` or `call` where a spread call achieves the same result more clearly.

## NEVER

- Use `any` as a migration shortcut without a plan to remove it; it disables type checking silently for all downstream code.
- Use pre-TypeScript-5 experimental decorator metadata (`reflect-metadata`, `emitDecoratorMetadata`) in new code that can use stage-3 decorators instead.
- Generate TypeScript with `"strict": false` or `"skipLibCheck": true` to work around type incompatibilities.
- Write `// @ts-ignore` without a comment; ignored errors become invisible failures.
- Use `eval` or `new Function(string)` to generate TypeScript-executed code at runtime.

## Agent Guardrails

- Do not modernize entire files because you touched one function; limit changes to what is directly relevant.
- Do not migrate `enum` to union literals without confirming the change is safe for all consumers; `enum` migration can be a breaking change at runtime.
- Do not remove triple-slash references that are the only mechanism ensuring a declaration file is loaded in a configuration that requires it.
- Do not replace `experimentalDecorators` without confirming the runtime and framework support stage-3 decorators.
