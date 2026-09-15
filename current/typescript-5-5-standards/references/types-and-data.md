# Types And Data

Use when changing type annotations, data models, generics, utility types, narrowing, discriminated unions, or object representations.

## MUST

- Enable and comply with `"strict": true`; all narrower strict flags (`strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, `useUnknownInCatchVariables`) are assumed active.
- Use `unknown` at trust boundaries (parsed JSON, external APIs, user input) and narrow before use; never widen directly to `any`.
- Distinguish absence from falsiness: `""`, `0`, `false`, and `null` are valid values and must not be conflated with `undefined`.
- Use `undefined` for optional absence; use `null` only when `null` is an explicit domain value or a third-party API requires it.
- Preserve structural compatibility: do not change the shape of exported types in ways that silently break assignability for callers.
- Use discriminated unions with a literal `kind`, `type`, or `tag` field to model mutually exclusive states; narrow by that discriminant.
- Use `as const` on object or array literals to produce narrow literal types and readonly tuples.
- Annotate function return types when the inferred type would be imprecise, overly broad, or surprising to callers.

## SHOULD

- Prefer type inference for local `const` bindings where the type is immediately obvious from the right-hand side.
- Use built-in utility types (`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `ReturnType`, `Parameters`, `Awaited`, `NonNullable`) before writing custom mapped type equivalents.
- Use `satisfies` to validate that a value conforms to a type while keeping the narrower inferred literal type for downstream use.
- Use `const` type parameters on generic functions to capture literal types from call sites without requiring callers to use `as const`.
- Use `NoInfer<T>` in generic constraints when a type parameter should be inferred from one argument only and not widened by other arguments.
- Use inferred type predicates (TypeScript 5.5): let `tsc` infer the return type as a type predicate from narrowing-based return structures before writing manual `x is T` annotations.
- Use template literal types to model string-shaped APIs and constrained key patterns.
- Use `readonly` arrays (`readonly T[]` or `ReadonlyArray<T>`) for parameters that must not be mutated by the callee.
- Prefer union literals (`"pending" | "active" | "closed"`) over `enum` for closed string-valued sets.
- Use `interface` to describe the shape of objects received from or sent to external systems; they provide better error messages and mergeability than anonymous object types.

## CONSIDER

- Use mapped types (`{ [K in keyof T]: ... }`) when transforming all properties of a type systematically.
- Use conditional types (`T extends U ? A : B`) when the output type genuinely depends on the structure of the input type; keep them readable and avoid nesting beyond two levels.
- Use `infer` inside conditional types to extract sub-types; assign a meaningful name to the inferred type variable.
- Use `Extract<T, U>` and `Exclude<T, U>` rather than hand-written conditional types for filtering unions.
- Use `newtype`-style branded types (`type UserId = string & { readonly _brand: "UserId" }`) for semantically distinct primitive identifiers to prevent accidental interchange at compile time.
- Use `WeakMap` and `WeakRef` for associating data with objects when the object lifetime should not be extended by the association.

## AVOID

- `any`; when type information is genuinely unavailable, use `unknown` and narrow.
- Type assertions (`as SomeType`) to silence compiler errors; narrow the value correctly instead.
- Non-null assertions (`!`) on values that might legitimately be null or undefined in production; narrow with a guard.
- Overly complex nested conditional types that require reading inside-out to understand; break them into named intermediates.
- Annotating obvious local variable types when the inferred type is already precise and readable.
- Widening a type with an `as` assertion to make a value assignable without understanding why the types diverge.
- `object` (lowercase) as a type; use a specific shape, `Record<string, unknown>`, or a structural interface.

## NEVER

- Use `any` to silence a type error without understanding its source.
- Use `@ts-ignore` or `@ts-expect-error` on new production code without a short comment explaining why the suppression is legitimate and safe.
- Conflate `null`, `undefined`, `false`, `0`, and `""` as equivalent absence; treat each as a distinct state.
- Rely on `enum` reverse-mapping behavior as part of a public API contract.

## Agent Guardrails

- Do not add type annotations to every local variable; annotate boundaries and non-obvious shapes only.
- Do not refactor working mapped or conditional types into alternative styles unless correctness or readability is materially improved.
- Do not introduce branded types speculatively; apply them where real type confusion has occurred or is a documented risk.
