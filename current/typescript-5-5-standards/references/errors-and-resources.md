# Errors And Resources

Use when changing error handling, validation, resource acquisition and cleanup, or system boundaries where failures must be surfaced.

## MUST

- Type caught errors as `unknown` (enforced by `useUnknownInCatchVariables`); narrow before accessing any property.
- Narrow caught errors with `instanceof Error` before accessing `.message`, `.stack`, or custom properties; handle non-`Error` throws explicitly.
- Use `using` for synchronous resources implementing `Symbol.dispose`; use `await using` for asynchronous resources implementing `Symbol.asyncDispose`.
- Keep `try` blocks as narrow as practical so handlers do not mask unrelated errors.
- Do not swallow errors silently in normal application code; surface, translate, or propagate every failure.
- Validate untrusted input at system boundaries (HTTP handlers, IPC, deserialized data) before passing data into typed internal code.
- Use `finally` or `using` for cleanup; do not rely on a `catch` block reaching the cleanup path since exceptions in `catch` skip it.

## SHOULD

- Derive application-specific error classes from `Error`; set `name` to a stable string and pass `{ cause }` when wrapping a lower-level error.
- Design error types around what callers can act on, not around what the implementation throws.
- Include actionable context in error messages without leaking secrets or PII.
- Prefer `Symbol.dispose` on resource objects over manual teardown calls when defining new resource abstractions.
- Log or report errors at the boundary where recovery decisions are made; propagate otherwise and let callers decide.
- Use `AggregateError` when multiple independent errors occur and all must be surfaced to the caller.

## CONSIDER

- Use a discriminated-union `Result<T, E>` type (`{ ok: true; value: T } | { ok: false; error: E }`) for expected, recoverable failure paths where throwing is too disruptive to control flow.
- Use `DisposableStack` or `AsyncDisposableStack` when managing a dynamic set of resources that must be released in reverse-acquisition order.
- Define validation helpers that return `unknown`-narrowing type predicates so internal code can trust the validated type.

## AVOID

- Catching `Error` broadly and continuing as if no error occurred without logging, translating, or re-throwing.
- Returning `null`, `undefined`, `false`, or magic sentinel strings for exceptional failures where callers need failure details.
- Control-flow statements (`return`, `break`, `continue`) in `finally` blocks; they suppress in-flight exceptions.
- Logging and re-throwing the same error at every layer; log at the boundary and propagate everywhere else.
- Validating domain invariants inside deeply nested business logic; push validation to the boundary.

## NEVER

- Catch all exceptions at a low-level helper just to keep execution going; this hides real failures.
- Use `as SomeType` on parsed or deserialized data to assert validity without actual validation.
- Rely on garbage collection for timely release of file handles, network sockets, locks, or other external resources; use `using` or explicit cleanup.
- Leak secrets, tokens, or PII in error messages or stack traces that cross trust boundaries.

## Agent Guardrails

- Do not introduce a `Result` type speculatively; apply it where throwing creates genuine control-flow complexity and the repository does not already prefer exceptions.
- Do not add error handling for failures that cannot happen in the current code path.
- Do not wrap every function call in try/catch; handle errors at the layer where recovery decisions belong.
