---
name: java-springboot-unit-tests
description: 'Apply Java unit test code style rules: AssertJ assertions, BDD GIVEN/WHEN/THEN comments, should...When naming, @DisplayName, @MockitoBean, Awaitility, Clock injection, class structure (constants → fields → tests → helpers), no public modifiers on test classes, no redundant eq() matchers, no Thread.sleep. Use when writing, reviewing, or refactoring Java test code. For test-first workflow, if the tdd-by-example skill is available, apply it alongside this skill for the Red-Green-Refactor cycle.'
argument-hint: 'What test class or scenario are you working on?'
---

# Java Unit Test Code Style

Apply these rules when writing, reviewing, or refactoring Java test code.

## Class Structure

Organize every test class in this order:
1. **Constants and fields** at the top (private, static final where applicable)
2. **Test methods** (`@Test`) below
3. **Private helper methods** at the bottom

```java
// --- Constants ---
private static final UUID DEFAULT_APPLICATION_ID = TestConstants.DEFAULT_APPLICATION_ID;

// --- Fields ---
private ApplicationEnricherImpl applicationEnricher;

// --- Test Methods ---

// --- Private Helper Methods ---
```

- Test classes and nested test classes must **not** have the `public` access modifier — remove it if present.
- Mark method parameters as `final` in private helper methods.

## Naming and Annotations

- Use the `should...When...` pattern for test method names: `shouldReturnTrueWhenInputIsValid()`.
- Add `@DisplayName` with a clear, human-readable description to every test method.

## Assertions

- Prefer **AssertJ** as the default assertion style.
- Chain assertions on the same object using fluent syntax: `assertThat(obj).isNotNull().isInstanceOf(Type.class)`.
- Avoid redundant assertions — do not test the same code, scenario, and outcome more than once.

## BDD-Style Comments (Mandatory)

Replace simple `// Arrange`, `// Act`, `// Assert` comments with meaningful BDD-style narrative comments. This is mandatory for every test.

Format:
```
// GIVEN (context)
// AND (further context)
// WHEN (action/event)
// AND (further action/event)
// THEN (outcome)
// AND (further outcome)
```

Example:
```java
// GIVEN John is on the LinkedIn Registration page
// WHEN he enters all required registration information
// AND he hits 'join now'
// THEN his LinkedIn account is created
// AND he is directed to the profile creation page
// AND his confirmation email is sent
```

## Mocks and Stubs

- Define shared mocks and common context in `@BeforeEach` or `@BeforeAll`. Configure scenario-specific stubs inline within each test.
- For stubs/mocks shared across multiple tests or nested classes, define them as private helper methods in the outermost test class.
- Do **not** make stubs lenient unless necessary.
- For Spring-managed mocks use:
  - `@MockitoBean` in Spring Boot 3.4+ codebases
  - `@MockBean` only in older repositories that do not yet support `@MockitoBean`
- Remove redundant Mockito `eq()` matchers: if all arguments in a `when()` or `verify()` call are literal values, pass them directly.

## Test Layers

Keep **one primary test layer per test class**:
- Unit tests for business logic (mocked collaborators)
- `WebMvcTest` for controller slice behavior
- `DataJpaTest` for repository slice behavior
- `SpringBootTest` only when behavior genuinely crosses layers

## Time-Sensitive Code

- Prefer injecting `Clock` in production code and use `Clock.fixed(...)` in tests.
- If time must progress within a scenario (retry windows, expiry, polling), use a reusable `MutableClock` rather than ad hoc time mocking. See [time-handling](./references/time-handling.md) for the full implementation.
- Replace `Thread.sleep()` with **Awaitility** for eventual-outcome verification. Use `CountDownLatch` with a timeout only for coordinating imperative callback or signal-style completion. See [async-testing](./references/async-testing.md) for Awaitility defaults and examples.

## Code Quality Rules

- Adhere to DRY — extract reused values to constants or helper methods.
- Do **not** use fully qualified class names; use import declarations instead. Remove all unused imports after refactoring.
- Do **not** use Javadoc comments on test methods; use regular single-line comments.
- Do **not** put `verify` or `assert` statements in `@BeforeEach` / `@BeforeAll` methods — only set up context there.
- Only declare checked exceptions in a test method signature if the test actually throws them; remove generic `throws Exception` declarations.
- Delete commented-out code; do not leave commented-out blocks in committed files.
- Avoid empty catch blocks; handle exceptions meaningfully or let them propagate.
- Eliminate duplicate test methods — each test should cover a unique scenario or outcome.
- Do **not** write tests for DTOs, records, or Lombok-generated artifacts unless the behavior under test genuinely depends on them.
- Avoid `ReflectionTestUtils` — prefer constructor injection or test-only configuration. Exception: use it for `@Value` fields that Mockito cannot inject without a Spring context.
- Do not use coverage targets as the primary measure of test quality — coverage is a signal, not a goal.
- When asserting that a runtime exception is thrown, isolate the single method call expected to throw inside the `assertThrows` lambda. Resolve any preceding calls to local variables first, so it is unambiguous which call raises the exception (SonarQube S5778).

```java
// Non-compliant — unclear whether get() or toString() throws
assertThrows(IndexOutOfBoundsException.class, () -> get().toString());

// Compliant — only the method expected to throw is inside the lambda
Object obj = get();
assertThrows(IndexOutOfBoundsException.class, () -> obj.toString());
```
