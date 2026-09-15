# Async And Concurrency

Use when changing Promise-based code, async/await patterns, cancellation, async resource cleanup, or code that touches the event loop.

## MUST

- Await every `Promise` that can reject; unhandled rejections are errors and must not be left floating.
- Return `Promise<void>` or `Promise<T>` from async functions; never return `Promise<any>`.
- Propagate cancellation via `AbortController` / `AbortSignal`; check `signal.aborted` or pass the signal to underlying APIs that accept it.
- Use `await using` for resources that implement `Symbol.asyncDispose`; do not skip the `await` on `AsyncDisposable` teardown.
- Do not call blocking synchronous operations (large loops, synchronous file I/O, CPU-heavy computation) on the main thread or event loop without delegation to a worker.
- Handle rejections in `Promise.all` / `Promise.allSettled` / `Promise.race` / `Promise.any` explicitly; know which combinator you need before reaching for `Promise.all`.

## SHOULD

- Prefer `async`/`await` over raw `.then()`/`.catch()` chains for sequential async logic; chains remain acceptable for simple one-step transformations.
- Use `Promise.all` to await independent concurrent operations; do not sequentially `await` operations that can run in parallel.
- Use `Promise.allSettled` when all results are needed regardless of individual failures.
- Use `Promise.any` when the first success is sufficient and failures are expected.
- Use `AbortSignal.timeout(ms)` for simple deadline-bounded operations instead of manual timer + abort wiring.
- Prefer `AsyncDisposable` and `await using` over callback-based teardown for new async resource abstractions.
- Mark the top-level module entry point `await` usage clearly; top-level `await` has module-graph implications and should not be used casually in shared library code.

## CONSIDER

- Use `structuredClone` to pass data across worker boundaries when transferable objects are not appropriate.
- Use a task queue or bounded concurrency helper when fan-out of parallel operations must be limited.
- Model long-running async operations as `AsyncIterable<T>` when the consumer needs to process results incrementally.

## AVOID

- `Promise` constructors (`new Promise(...)`) except when wrapping a callback-based API that has no native promise counterpart.
- Mixing `async/await` and `.then()`/`.catch()` on the same call chain; pick one style per expression.
- Relying on microtask ordering as part of a correctness guarantee; treat microtask scheduling as an implementation detail.
- Shared mutable state accessed by concurrent async operations without explicit coordination; prefer message passing, immutable snapshots, or atomic updates.
- Catching and discarding `AbortError` on cancelled operations; propagate it or handle it as the intended clean exit.
- Using `setTimeout(fn, 0)` to "yield" the event loop as a substitute for proper async decomposition.

## NEVER

- Leave a `Promise`-returning function call without `await`, `.then()`, `.catch()`, or an explicit `void` annotation; floating promises hide errors.
- Ignore rejection from `Promise.all`; a single rejection rejects the whole batch and unhandled rejections are errors.
- Perform synchronous file I/O, `execSync`, or equivalent blocking calls in a server or event-loop context where latency matters.
- Use `async` on a function that contains no `await` and does not need the `Promise` wrapping; it misleads callers about the execution model.

## Agent Guardrails

- Do not convert synchronous code to async speculatively; only introduce `async`/`await` where genuinely async work is required.
- Do not add `AbortController` wiring unless the operation is long-running or the repository already uses cancellation.
- Do not use `Promise.all` where sequential ordering or error isolation between steps is required.
