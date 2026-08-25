# Plan: `csharp-dotnet10-standards` skill

## Context

The skills base has `java-21-standards` (vanilla Java 21 language standards) and
`java-21-springboot-standards` (framework overlay). We need the same thing for C#: a skill that
carries the industry standards for writing maintainable, consistent C# on .NET 10 / C# 14.

Scope is **core C# language + BCL only**. Framework-specific skills (ASP.NET Core, EF Core) come
later as overlays, mirroring how `java-21-springboot-standards` overlays `java-21-standards`.

Research is complete. Every source URL is inlined in the **Reference sources** section at the end of
this document — that section is the authority for which source backs which section, and the plan is
self-contained without any scratchpad file.

### Decisions already made by the user

| Question | Decision |
|---|---|
| Docs conventions vs dotnet/runtime style when they conflict | **dotnet/runtime style wins** as the default; note the docs variant where it differs |
| Async / concurrency / performance | **In scope** — they are language-level in C# (`async`, `await`, `using`, `ref struct`, `stackalloc`) |
| Enforcement assets (.editorconfig, Directory.Build.props) | **Prose only.** Cite CA/IDE rule IDs inline; ship no copyable config |
| Ordering (`IComparable<T>`/`IComparer<T>`) | **Folded into section 14**, retitled "Equality, hashing, and ordering" — not a separate section |

## Structure

Mirror `skills/java-21-standards/` exactly: `SKILL.md` + `references/NN-topic.md`, progressive
disclosure via a Section Guide table.

```
skills/csharp-dotnet10-standards/
  SKILL.md
  references/03-immutability-and-state.md … 43-third-party-dependencies.md
```

### `SKILL.md` (always loaded)

Same seven parts as `skills/java-21-standards/SKILL.md`, C#-ified:

1. **Frontmatter** — `name: csharp-dotnet10-standards` (must match the directory name).
2. **Operating Rules** — target `net10.0` / C# 14; `<Nullable>enable</Nullable>` is assumed; no
   preview features unless requested; smallest coherent change; no speculative abstractions;
   prefer immutable state; async all the way, never sync-over-async; no unrelated modernization.
3. **Classification Meanings** — reuse the MUST / SHOULD / CONSIDER / AVOID / NEVER table verbatim.
4. **General Design** — carry over from the Java skill (it is language-neutral), plus the C#
   additions: prefer `sealed` for internal/private types, make dependencies explicit, keep the
   public API surface minimal.
5. **C# 14 Language Features** — SHOULD / CONSIDER / AVOID / NEVER over the verified C# 14 list:
   extension members, `field` keyword, implicit `Span<T>` conversions, `nameof` on unbound
   generics, modifiers on simple lambda params, partial constructors/events, user-defined compound
   assignment and `++`/`--`, null-conditional assignment. Explicitly AVOID adopting `extension`
   blocks and user-defined compound assignment reflexively.
6. **Agent change discipline + AI overengineering guardrails** — carry over from the Java skill;
   add the C#-specific anti-patterns (interface-per-service for DI, `IRepository<T>` over an ORM,
   AutoMapper for two-field projections, wrapping every method in `Task.Run`).
7. **Areas without universal rules** — the de-standardisation table. C# entries: `var` policy
   beyond the runtime baseline, expression-bodied members, `#region`, `ConfigureAwait(false)` in
   application (non-library) code, primary constructors vs explicit, records vs classes for DTOs,
   one-type-per-file, `this.` prefixing, file-scoped vs block namespaces, tabs/spaces, line length,
   MediatR/DI patterns, test framework choice, project layout.

### Frontmatter description

Verified against the audit's C12 overlap check (Jaccard ≥ 0.30 = medium finding). This candidate
peaks at **0.095 against `java-21-standards`** — well clear. Keep the C#-specific vocabulary
(`nullable`, `records`, `structs`, `LINQ`, `Span<T>`, `Roslyn`) if the wording is revised, because
that vocabulary is what keeps the two descriptions distinguishable:

> Use when writing, reviewing, or refactoring C# targeting .NET 10 and C# 14. Covers nullable
> reference types, records and structs, LINQ, async/await and cancellation, disposal, Span&lt;T&gt; and
> allocation, equality and ordering contracts, Roslyn analyzer enforcement, and retired .NET APIs.
> Core C# language and BCL only — no ASP.NET, EF Core, or other framework guidance.

### Reference files — 41 sections, numbered 3–43

Numbering starts at 3 to match the Java skill (1–2 are the always-loaded design/language sections).

| # | File | # | File |
|---|---|---|---|
| 3 | immutability-and-state | 24 | pattern-matching-and-switch |
| 4 | classes-structs-and-type-choice | 25 | method-and-api-design |
| 5 | records-and-value-objects | 26 | extension-members |
| 6 | enums-and-closed-hierarchies | 27 | naming |
| 7 | nullability | 28 | comments-and-xml-documentation |
| 8 | properties-fields-and-constructors | 29 | namespaces-files-and-usings |
| 9 | collections | 30 | assemblies-and-public-api-surface |
| 10 | generics | 31 | validation-and-defensive-programming |
| 11 | strings-and-text | 32 | logging |
| 12 | numbers-and-money | 33 | security |
| 13 | date-and-time | 34 | serialization |
| 14 | **equality-hashing-and-ordering** | 35 | reflection-dynamic-trimming-and-aot |
| 15 | tostring-and-formatting | 36 | attributes |
| 16 | exceptions | 37 | performance-and-allocations |
| 17 | disposal-and-resource-management | 38 | span-memory-and-unsafe-code |
| 18 | linq | 39 | testability |
| 19 | async-and-await | 40 | legacy-csharp-and-dotnet-practices |
| 20 | cancellation-and-timeouts | 41 | code-analysis-and-enforcement |
| 21 | concurrency-and-shared-state | 42 | language-version-and-preview-features |
| 22 | parallelism | 43 | third-party-dependencies |
| 23 | delegates-lambdas-and-events | | |

### Section 14 — equality, hashing, and ordering

Called out because it changed during planning. Content:

- **Equality contract** — `Equals`/`GetHashCode`/`IEquatable<T>` consistency, and the C#-specific
  trap that overriding `Equals` does **not** change `==`, so the same comparison yields two
  different answers unless the operator is overloaded too (`CA1815`, `CA2231`).
- **Reference vs value semantics** across the four options: plain class (reference), plain struct
  (reflection-based `ValueType.Equals` — slow, no operators), `record class`, `record struct`.
- **Hash stability** — never derive a hash from mutable state; what breaks when a dictionary key or
  set member mutates after insertion.
- **Alternate equality** — `IEqualityComparer<T>`; `StringComparer`/`StringComparison` for strings.
- **Ordering** — `IComparable<T>`/`IComparer<T>`; `CompareTo` returning 0 MUST agree with `Equals`;
  overload `<`, `<=`, `>`, `>=` consistently with `CompareTo` (`CA1036`); the silent-misbehaviour
  failure modes in `SortedDictionary`, `List.Sort`, `Array.BinarySearch` on an inconsistent
  comparer.

Deliberately left in their own sections, not duplicated here: `record` semantics matching the
domain (§5), nullability quirks of `==` on annotated types (§7), culture-sensitive string
comparison (§11).

## Authoring conventions per reference file

Match `skills/java-21-standards/references/16-exceptions.md` — the richest existing example:

- `## N. Title` heading, then only the applicable `### MUST` / `### SHOULD` / `### CONSIDER` /
  `### AVOID` / `### NEVER` blocks, as terse bullet lists. Omit empty levels.
- Optional `### Examples` at the end with `WRONG` / `CORRECT` pairs in ```csharp fences. Reserve
  these for rules where prose alone fails to convey the trap — the Java skill only uses examples in
  ~6 of 36 files, and that ratio should hold.
- Cite the analyzer ID inline where one enforces the rule (`CA2007`, `CA1062`, `CA1309`, `CA1036`,
  `CA1848`, `IDE0090`). This is the main advantage over the Java skill: a reviewer can wire
  enforcement to the rule instead of arguing it.
- Keep files in the 15–65 line range the Java skill uses. Do not pad.

## Conflict rulings to apply while writing

1. **`var`** — dotnet/runtime rule: only when the right-hand side explicitly names the type (`new`
   or a cast). Note the docs variant ("obvious from the RHS", implicit typing in `for` loops) as a
   permitted project choice in the de-standardisation table, not as the default.
2. **Line length 65** — a docs-rendering artefact. Discard; list line length as a repo concern.
3. **Primary-constructor parameter casing** — runtime rule: camelCase, no `_` prefix. The docs
   PascalCase-for-records variant goes in §8 as a noted alternative.
4. **Framework Design Guidelines is 2008-era and library-oriented** — predates records, nullable
   reference types, `Span<T>`. Filter every borrowed rule for application-code relevance and
   cross-check against a modern analyzer before stating it.
5. **`secure-coding-guidelines` is stale** (Code Access Security era). Build §33 from the CA
   security rules + the OWASP .NET cheat sheet instead; do not cite the stale page as primary.

## Repo constraints (from `skills/my-skills-audit/scripts/mechanical-checks.py`)

The new skill must pass the repo's own audit. Verified against the script:

- **C1** — `name:` must equal the directory name, be kebab-case, and `description:` must be ≤1024 chars.
- **C2** — every `./references/NN-*.md` link in the Section Guide must resolve on disk. A dead link
  is a `high` finding: the promised detail silently never loads. External `https://` links are
  skipped by the checker, so inline Microsoft Learn citations are safe.
- **C3** — no `../..` paths reaching into sibling skill directories. Refer to other skills by
  **name** (`java-21-standards`), never by path, since skills install individually.
- **C4a** — do not reference skills that do not exist. In particular do **not** forward-reference a
  not-yet-written `csharp-aspnetcore-standards`.
- **C12** — description overlap; already verified above at 0.095.
- **C15** — `git add` the new directory, otherwise it reports as an untracked skill (`low`).

`skills-lock.json` tracks only externally-installed skills (currently just `my-skills-audit`), so
it needs **no** change. `README.md` documents only the `db-core` trio and already trips the `low`
C14 readme-coverage finding for every other skill — out of scope here.

## Execution order

1. `mkdir skills/csharp-dotnet10-standards/references`.
2. Write `SKILL.md` — frontmatter, operating rules, classification table, always-loaded sections,
   de-standardisation table, the 41-row Section Guide, workflow.
3. Write the 41 reference files. Batch by theme so related rulings stay consistent: types (3–10),
   data and text (11–15), failure and resources (16–17), queries and async (18–22), language
   surface (23–26), documentation and structure (27–30), cross-cutting (31–36), performance
   (37–38), discipline (39–43).
4. `git add` the directory.

## Verification

1. **Audit clean** — run the repo's own mechanical checks and confirm no new
   `critical`/`high`/`medium` findings attributable to this skill:
   ```bash
   python3 skills/my-skills-audit/scripts/mechanical-checks.py --repo-root . 
   ```
   Filter the JSON to `"skill": "csharp-dotnet10-standards"`. Expect zero findings above `low`.
2. **Link integrity** — confirm the Section Guide row count equals the file count, and that every
   linked file exists:
   ```bash
   ls skills/csharp-dotnet10-standards/references | wc -l
   ```
   should be 41, and every `./references/...` target in `SKILL.md` must resolve (C2 covers this).
3. **Structural parity** — diff the shape against the Java skill: every reference file starts with
   `## N. `, uses only the five classification headings, and no file is empty or a stub.
4. **Behavioural spot-check** — in a fresh session, ask for a C# change that should pull exactly one
   section (e.g. "implement `IComparable<T>` on this value type") and confirm the skill loads §14
   and applies the `CompareTo`/`Equals` consistency MUST plus `CA1036`. This is the real test of
   whether the Section Guide's "Consider When" column routes correctly.
5. **No framework bleed** — grep the finished skill for framework terms that signal scope creep:
   ```bash
   grep -rniE 'asp\.net|entity framework|ef core|iservicecollection|controller' skills/csharp-dotnet10-standards
   ```
   Hits are acceptable only inside §33/§40 as named anti-patterns or in the "use the overlay skill
   instead" pointer; anything else means core-language scope leaked.

---

# Reference sources

Researched 2026-08-25. All URLs below were surfaced directly by search or fetch during research,
except the three analyzer packages noted as NuGet IDs (deliberately given as package IDs rather than
guessed repository URLs). Microsoft Learn paths are given relative to `https://learn.microsoft.com/en-us/`
where marked with a leading `/`, to keep the tables readable.

## Tier 1 — normative, the skill's spine

| Source | URL |
|---|---|
| .NET Coding Conventions (C#) | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions |
| Identifier names — rules and conventions | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names |
| Framework Design Guidelines (index) | https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/ |
| dotnet/runtime C# Coding Style (20 rules) | https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md |
| dotnet/runtime FDG digest | https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/framework-design-guidelines-digest.md |
| dotnet/roslyn contributing (C# section) | https://github.com/dotnet/roslyn/blob/main/CONTRIBUTING.md#csharp |
| dotnet/docs reference `.editorconfig` | https://github.com/dotnet/docs/blob/main/.editorconfig |
| Code analysis in .NET (overview) | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview |
| Rule categories | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/categories |
| CA quality rules index | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ |
| IDE style rules index | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/ |
| Code style rule options | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/code-style-rule-options |
| Code quality rule options | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/code-quality-rule-options |
| Configure code analysis rules | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/configuration-options |
| Configuration files for code analysis | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/configuration-files |
| Roslyn analyzers overview | https://learn.microsoft.com/en-us/visualstudio/code-quality/roslyn-analyzers-overview |
| What's new in C# 14 | https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14 |
| What's new in .NET 10 (overview) | https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview |
| What's new in .NET 10 libraries | https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/libraries |
| What's new in .NET 10 runtime | https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/runtime |

### Framework Design Guidelines — full subsection map

All relative to `https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/`. Verified
against the published `toc.json`.

- **Naming** — `naming-guidelines`, `capitalization-conventions`, `general-naming-conventions`,
  `names-of-assemblies-and-dlls`, `names-of-namespaces`, `names-of-classes-structs-and-interfaces`,
  `names-of-type-members`, `naming-parameters`, `naming-resources`
- **Type design** — `type`, `choosing-between-class-and-struct`, `abstract-class`, `static-class`,
  `interface`, `struct`, `enum`, `nested-types`
- **Member design** — `member`, `member-overloading`, `property`, `constructor`, `event`, `field`,
  `extension-methods`, `operator-overloads`, `parameter-design`
- **Extensibility** — `designing-for-extensibility`, `unsealed-classes`, `protected-members`,
  `events-and-callbacks`, `virtual-members`, `abstractions-abstract-types-and-interfaces`,
  `base-classes-for-implementing-abstractions`, `sealing`
- **Exceptions** — `exceptions`, `exception-throwing`, `using-standard-exception-types`,
  `exceptions-and-performance`
- **Usage** — `usage-guidelines`, `arrays`, `attributes`, `guidelines-for-collections`,
  `serialization`, `system-xml-usage`, `equality-operators`
- **Patterns** — `common-design-patterns`, `dependency-properties`, `dispose-pattern`

> Caveat to carry into every borrowed rule: this corpus is excerpted from the 2008 2nd edition and
> predates records, nullable reference types and `Span<T>`. The revised 3rd edition (2024) is a
> paid book: https://www.informit.com/store/framework-design-guidelines-conventions-idioms-and-9780135896464

## Tier 2 — official topic guidance, mapped to sections

| § | Topic | URLs |
|---|---|---|
| 7 | Nullable reference types | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types · https://learn.microsoft.com/en-us/dotnet/csharp/nullable-migration-strategies · https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/common-tasks/resolve-warnings · https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-reference-types · https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-messages/nullable-warnings · https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/tutorials/nullable-reference-types |
| 4, 5 | Type choice, records | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/tutorials/choosing-types · https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/records · https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record · https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/ |
| 14 | Equality, hashing | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/expressions/equality · https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/statements-expressions-operators/how-to-define-value-equality-for-a-type · https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/equality-operators |
| 14 | Ordering | https://learn.microsoft.com/en-us/dotnet/api/system.icomparable-1 · https://learn.microsoft.com/en-us/dotnet/standard/collections/comparisons-and-sorts-within-collections · https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1036 · https://learn.microsoft.com/en-us/troubleshoot/developer/visualstudio/csharp/language-compilers/use-icomparable-icomparer |
| 16 | Exceptions | https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions · https://learn.microsoft.com/en-us/dotnet/standard/exceptions/ |
| 17 | Disposal | https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose · https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-disposeasync · https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/using-objects · https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-iasyncdisposable |
| 18 | LINQ | https://learn.microsoft.com/en-us/dotnet/csharp/linq/ · https://learn.microsoft.com/en-us/dotnet/standard/linq/deferred-execution-lazy-evaluation · https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/classification-of-standard-query-operators-by-manner-of-execution |
| 19 | Async / TAP | https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap · https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/consuming-the-task-based-asynchronous-pattern · https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/implementing-the-task-based-asynchronous-pattern · https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios |
| 20 | Cancellation | https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/cancel-an-async-task-or-a-list-of-tasks · https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/cancel-async-tasks-after-a-period-of-time · https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/coalesce-cancellation-tokens-from-timeouts · https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/cancel-non-cancelable-async-operations |
| 21, 22 | Threading, parallelism | https://learn.microsoft.com/en-us/dotnet/standard/threading/managed-threading-best-practices · https://learn.microsoft.com/en-us/dotnet/standard/threading/the-managed-thread-pool · https://learn.microsoft.com/en-us/dotnet/standard/threading/managed-threading-basics |
| 13 | Date and time | https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview · https://learn.microsoft.com/en-us/dotnet/core/extensions/timeprovider-testing |
| 11 | Strings, globalization | https://learn.microsoft.com/en-us/dotnet/standard/base-types/best-practices-strings · https://learn.microsoft.com/en-us/dotnet/standard/base-types/comparing · https://learn.microsoft.com/en-us/dotnet/csharp/how-to/compare-strings · https://learn.microsoft.com/en-us/dotnet/core/extensions/globalization · https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-globalization-cultureinfo-invariantculture · https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1309 |
| 37, 38 | Performance, Span/Memory | https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/performance/ · https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines · https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/ · https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1 |
| 28 | XML documentation | https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/ · https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/documentation-warnings |
| 33 | Security | https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/security-warnings · https://learn.microsoft.com/en-us/dotnet/standard/security/secure-coding-guidelines *(stale, CAS-era — do not cite as primary)* |
| 42 | Language version, breaking changes | https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version · https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning · https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/version-update-considerations · https://learn.microsoft.com/en-us/dotnet/core/compatibility/10 · https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/breaking-changes/compiler%20breaking%20changes%20-%20dotnet%2010 |

## Tier 3 — community / industry, non-normative but widely followed

| Source | URL |
|---|---|
| David Fowler, AsyncGuidance.md | https://github.com/davidfowl/AspNetCoreDiagnosticScenarios/blob/master/AsyncGuidance.md |
| Cleary, "Async/Await Best Practices" (MSDN Mag, archived) | https://learn.microsoft.com/en-us/archive/msdn-magazine/2013/march/async-await-best-practices-in-asynchronous-programming |
| Cleary, "Don't Block on Async Code" | https://blog.stephencleary.com/2012/07/dont-block-on-async-code.html |
| Cleary, "Async and Await" | https://blog.stephencleary.com/2012/02/async-and-await.html |
| OWASP .NET Security Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/DotNet_Security_Cheat_Sheet.html |
| awesome-analyzers (curated analyzer list) | https://github.com/cybermaxs/awesome-analyzers |
| Roslynator | https://github.com/dotnet/Roslynator |
| Meziantou, "The Roslyn analyzers I use" | https://www.meziantou.net/the-roslyn-analyzers-i-use.htm |
| Analyzer packages worth naming in §41 | NuGet IDs: `Microsoft.CodeAnalysis.NetAnalyzers` (built into the SDK), `StyleCop.Analyzers`, `Roslynator.Analyzers`, `Meziantou.Analyzer`, `SonarAnalyzer.CSharp` |

## Verified C# 14 feature list

C# 14 ships with .NET 10 and is the **default `LangVersion` for `net10.0`**. Confirmed against the
official *What's new in C# 14* and *What's new in .NET 10* pages:

extension members (`extension` blocks — extension properties, static extension members, extension
operators) · `field` keyword for field-backed properties · implicit conversions among `Span<T>`,
`ReadOnlySpan<T>` and `T[]` · `nameof` on unbound generic types (`nameof(List<>)`) · `ref`/`out`/
`in`/`scoped`/`ref readonly` modifiers on simple (untyped) lambda parameters · partial instance
constructors and partial events · user-defined compound assignment operators · user-defined `++`
and `--` · null-conditional assignment (`customer?.Order = …`) · new preprocessor directives for
file-based apps.

Breaking changes to note in §42: `scoped` is now always a modifier in a lambda parameter list; new
span conversions and inference rules can break overload resolution; partial interface properties and
events are now implicitly virtual and public (partial *methods* keep the old behaviour).

---
---

# Plan: `csharp-dotnet10-linq-standards` skill

## Context

LINQ is the largest single topic inside the C# core-language plan above — it sits there as one
section (§18) among 41, which is not enough room for it. It has its own execution model (deferred
vs immediate), its own two competing syntaxes, its own failure modes that produce no compiler
warning (repeat enumeration, silent client evaluation, deferred exception sites), and its own
analyzer catalogue. It earns a skill.

This skill is the **overlay**, `csharp-dotnet10-standards` is the **base** — the same relationship
`java-21-springboot-standards` has to `java-21-standards`. It must work standalone when the base is
absent, and must never contradict the base when both load.

Scope is **core LINQ**: LINQ to Objects, plus the `IQueryable<T>` *boundary* rules, plus LINQ over
`IAsyncEnumerable<T>`, plus PLINQ. Provider-specific querying (EF Core) is a later skill.

Research is complete. Every source URL is inlined in the **LINQ reference sources** section at the
end of this document.

### Decisions already made by the user

| Question | Decision |
|---|---|
| Style when the codebase has no LINQ, or an even query/method split | **Never ask. Default to method chaining.** It covers the whole operator surface (`Count`, `Max`, `Aggregate`, `Chunk`, `LeftJoin`, `Shuffle` have no query keyword) and every query expression compiles to it anyway |
| Querying surfaces in scope | **All four**: LINQ to Objects, `IQueryable<T>` boundary rules only, LINQ over `IAsyncEnumerable<T>`, PLINQ |
| How the codebase style check works | **Documented grep commands in `SKILL.md`.** No shipped script — nothing to install, nothing to go stale, consistent with the base skill's prose-only decision |

## Structure

```
skills/csharp-dotnet10-linq-standards/
  SKILL.md
  references/03-query-syntax-and-method-syntax.md … 27-analyzer-enforcement.md
```

### `SKILL.md` (always loaded)

Follows `skills/java-21-springboot-standards/SKILL.md` — the overlay shape — rather than the base
shape, because this skill is an overlay:

1. **Frontmatter** — `name: csharp-dotnet10-linq-standards` (must equal the directory name).
2. **Overlay preamble** — "If the csharp-dotnet10-standards skill is available, apply it first."
   Then the standalone fallback, listing the baseline it still holds without the base skill:
   nullable enabled, immutable state where practical, no speculative abstractions, no unrelated
   modernization, no silent behaviour changes.
3. **Target Environment** table — .NET 10 / C# 14; `System.Linq.Enumerable`;
   `System.Linq.AsyncEnumerable` **in-box as of .NET 10**; `System.Linq.ParallelEnumerable`;
   `System.Linq.Queryable` boundary only.
4. **Operating Rules** — ~16 numbered rules, active before writing any query. Includes: match the
   prevailing query style; treat a query as deferred until proven otherwise; never enumerate a
   sequence twice; no side effects in a query; materialize before crossing an API boundary; keep
   `IQueryable` out of return types that outlive the provider; no PLINQ without measurement.
5. **Query Style Consistency** — always-loaded, because it is this skill's headline behaviour. Spec
   below.
6. **Classification Meanings** — MUST / SHOULD / CONSIDER / AVOID / NEVER, reused verbatim.
7. **General Query Design** — the rules that apply to every query regardless of operator: one
   query does one thing; filter before projecting; name the query variable for its result; extract
   a named method when a pipeline stops being readable.
8. **Agent change discipline + AI overengineering guardrails** — LINQ-specific. AVOID: rewriting
   working loops into LINQ (or LINQ into loops) as drive-by cleanup; building a private
   `EnumerableExtensions` operator library; adding `.AsParallel()`; building expression-tree
   machinery to make a query "generic"; a `Select` that only re-wraps the element.
9. **Areas without universal rules** — the de-standardisation table (below).
10. **Section Guide** — 25 rows, `./references/NN-*.md` + a "Consider When" routing column.
11. **Workflow** — 5 steps, matching the base skill's, with style detection inserted as step 1.

### Frontmatter description

Verified against the audit's C12 overlap check (Jaccard ≥ 0.30 is a `medium` finding). Peaks at
**0.164 against `csharp-dotnet10-standards`** and 0.082 against `java-21-standards` — clear. The
distinguishing tokens are `deferred`, `enumeration`, `iqueryable`, `chaining`, `joins`, `plinq`,
`iasyncenumerable`; keep them if the wording is revised.

> Use when writing, reviewing, or refactoring LINQ queries in C# on .NET 10. Covers query syntax
> versus method chaining and matching the existing codebase, deferred versus immediate execution,
> multiple enumeration, IEnumerable and IQueryable boundaries, grouping, joins, sorting, projection,
> custom operators, LINQ over IAsyncEnumerable, PLINQ, and analyzer rules for query performance.
> In-memory LINQ to Objects only — no Entity Framework Core or database provider guidance.

Note: the base skill is named **without backticks** here and in the overlay preamble. The audit's
C4a check fires `high` on a backticked skill name that does not exist in the repo, and this skill
may well be built before `csharp-dotnet10-standards`. Once the base skill exists, backticks are
safe to add.

### Query Style Consistency — the always-loaded spec

This is the part the user asked for explicitly: the skill checks the codebase rather than imposing
a house style.

**Step 1 — detect.** Run both counts, scoped to the repo under edit:

```bash
grep -rInE '(^|[^.[:alnum:]_])from[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]+in[[:space:]]' \
  --include='*.cs' . | grep -vE '/(obj|bin)/' | wc -l
```

```bash
grep -rInE '\.(Where|Select|SelectMany|OrderBy|OrderByDescending|GroupBy|Join|GroupJoin|Any|All|First|FirstOrDefault|Single|SingleOrDefault|Sum|Count)\(' \
  --include='*.cs' . | grep -vE '/(obj|bin)/' | wc -l
```

Both are ratio heuristics, not parsers — `.Select(` matches non-LINQ methods too, and one query
expression contributes one `from` hit per clause group. That is fine; only the ratio is used. State
that limitation in the file so the number is not over-trusted.

**Step 2 — decide, narrowest scope first.**

1. The file being edited already contains queries → **match that file**, unconditionally.
2. Otherwise the containing project/folder is ≥ 60% one style → use it.
3. Otherwise the repo is ≥ 60% one style → use it.
4. Otherwise, or both counts are zero → **method chaining**. Do not ask.

**Step 3 — record the verdict** once per session so it is not re-derived per edit.

**Per-query overrides**, which outrank the prevailing style only when the style genuinely cannot
carry the query:

- MUST use method syntax when the operator has no query keyword — `Count`, `Max`, `Sum`,
  `Aggregate`, `Chunk`, `DistinctBy`, `CountBy`, `AggregateBy`, `Index`, `LeftJoin`, `RightJoin`,
  `Shuffle`, `Sequence`, `ToLookup`, `TryGetNonEnumeratedCount`.
- CONSIDER query syntax, even in a method-chaining codebase, for a query with a `join` /
  `group … by … into` / multiple `from` / `let` that would otherwise need nested lambdas plumbing
  anonymous types through several stages.
- AVOID mixing the two forms inside one statement, except the documented hybrid of a query
  expression wrapped by a single terminal method call: `(from … select …).Count()`.

**Style rules that apply once query syntax is in play** (all from the official coding conventions):
align clauses under `from`; `where` before other clauses so later clauses see the reduced set; use
aliases so anonymous-type members are Pascal-cased; rename ambiguous result members
(`CustomerName` / `DistributorName`, not two `Name`s); access an element's inner collection with a
second `from`, not a `join`.

### Reference files — 25 sections, numbered 3–27

Numbering starts at 3 to match both existing standards skills.

| # | File | # | File |
|---|---|---|---|
| 3 | query-syntax-and-method-syntax | 16 | partitioning-and-generation |
| 4 | query-naming-and-readability | 17 | comparers-in-queries |
| 5 | deferred-and-immediate-execution | 18 | purity-and-side-effects |
| 6 | multiple-enumeration-and-materialization | 19 | nullability-in-queries |
| 7 | ienumerable-iqueryable-and-expression-trees | 20 | exceptions-in-queries |
| 8 | filtering-and-projection | 21 | performance-and-allocations |
| 9 | element-operators | 22 | linq-versus-loops |
| 10 | quantifiers-and-counting | 23 | custom-query-operators |
| 11 | sorting | 24 | linq-over-iasyncenumerable |
| 12 | grouping | 25 | plinq |
| 13 | joins | 26 | testing-and-reviewing-queries |
| 14 | set-operations | 27 | analyzer-enforcement |
| 15 | aggregation | | |

Sections worth pinning down now, because they carry the rules that have no compiler backstop:

- **§5 deferred and immediate execution** — operators returning `IEnumerable<T>` /
  `IOrderedEnumerable<T>` defer; scalar-returning operators (`Count`, `Max`, `Average`, `First`)
  and the `To*` materializers execute immediately. Lazy vs eager *within* deferred operators:
  `OrderBy` must consume the whole source before yielding its first element. A query variable is
  a recipe, not a result — the source can change underneath it between definition and enumeration.
- **§6 multiple enumeration and materialization** — `CA1851`, with the fact that it is **not
  enabled by default in .NET 10** stated plainly, since the prose rule is the only guard by
  default. `ToList` vs `ToArray` vs `ToHashSet` vs `ToDictionary` vs `ToLookup`;
  `TryGetNonEnumeratedCount` for the count-without-enumerating case; the MUST to materialize
  before returning a sequence whose source is a `using`-scoped resource, and before handing a
  sequence to code that may enumerate it more than once.
- **§7 `IEnumerable` / `IQueryable` / expression trees** — where the boundary sits and who owns
  it; `AsEnumerable()` as the deliberate switch to client evaluation and `AsQueryable()` as the
  usually-wrong inverse; the `foreach` typing trap the coding conventions call out by name
  (accidentally binding an `IQueryable` as `IEnumerable` silently changes when and where the query
  runs); the expression-tree limitation list — no statement lambdas, no `async`/`await`, no `?.`,
  no interpolated strings, no collection expressions, no tuple literals, no pattern matching, no
  local functions, no `ref struct` values. Provider guidance stays out; the boundary rule stays in.
- **§10 quantifiers and counting** — this is where two analyzer rules read as contradicting each
  other and must be reconciled once, explicitly, or the skill will emit both: `CA1827` forbids
  `Count()` as an emptiness test on an `IEnumerable`; `CA1860` forbids `Any()` on a type that
  exposes `Count` / `Length` / `IsEmpty`. Single resolution: **prefer the type's own member when
  one exists (`.Count == 0`, `.IsEmpty`), otherwise `Any()`, never `Count()`.** Plus `CA1826`,
  `CA1829`, `CA1836`, and `IDE0120` (`Where(p).Any()` → `Any(p)`).
- **§19 nullability in queries** — `Where(x => x is not null)` does **not** narrow the element
  type for the compiler; the sequence stays `IEnumerable<T?>` and the next `Select` warns. Use
  `OfType<T>()`, or a `WhereNotNull` operator that does the `!` once in one audited place. NEVER
  scatter `!` through a pipeline to silence it.
- **§20 exceptions in queries** — a deferred query throws at the *enumeration* site, not the
  definition site, so `try`/`catch` around query construction catches nothing. Custom operators
  must validate arguments eagerly and defer the rest (§23). PLINQ wraps in `AggregateException`.
- **§24 LINQ over `IAsyncEnumerable`** — `System.Linq.AsyncEnumerable` ships in-box in .NET 10 and
  supersedes the community `System.Linq.Async` package; the migration rules (drop the package
  reference or move to 7.0.0; `<ExcludeAssets>` for transitive pulls; `SelectAwait` → `Select`);
  `await foreach`, `WithCancellation`, cancellation flowing into the operator delegates; the
  deferred-execution trap where async work does not start until enumeration, so creating tasks
  with LINQ needs an eager `ToArray`/`ToList` to get concurrency.
- **§25 PLINQ** — `AsParallel` / `AsOrdered` / `AsUnordered` / `AsSequential` / `ForAll` /
  `WithDegreeOfParallelism` / `WithCancellation` / `WithExecutionMode`; PLINQ is conservative by
  default and silently runs sequentially; ordered parallel queries buffer and sort, so they can be
  slower; PLINQ's sort is **not stable** where `Enumerable.OrderBy` is; exceptions arrive as
  `AggregateException`; elements may still be processed after cancellation or after a throw. NEVER
  add `.AsParallel()` without measurement; NEVER use it for I/O-bound work.
- **§27 analyzer enforcement** — the LINQ-relevant rule catalogue with IDs, and which of them are
  off by default. This is the advantage over prose: a reviewer can wire enforcement instead of
  arguing.

## Authoring conventions per reference file

Identical to the base plan, so the two skills read as one family:

- `## N. Title`, then only the applicable `### MUST` / `### SHOULD` / `### CONSIDER` / `### AVOID` /
  `### NEVER` blocks as terse bullets. Omit empty levels.
- Optional `### Examples` with `WRONG` / `CORRECT` pairs in ```csharp fences, reserved for traps
  prose cannot convey. Budget ~8 of 25 files — higher than the Java skill's ~6 of 36, because LINQ's
  worst failures are invisible in prose (repeat enumeration, deferred throw site, the NRT
  `Where`-null gap, the `foreach` `IQueryable`→`IEnumerable` slip).
- Cite the analyzer ID inline wherever one enforces the rule.
- 15–65 lines per file. Do not pad.

## Areas without universal rules (the de-standardisation table)

| Topic | Why |
|---|---|
| Query syntax vs method chaining as a house style | Project decision — this skill detects it, it does not impose one |
| One operator per line vs packed chains | Formatter/repository concern |
| Where to break a chain, indentation of `.Where(` | Repository concern |
| `ToList()` vs `ToArray()` as the default materializer | Context: `ToArray` is cheaper to re-enumerate, `ToList` allows mutation |
| Naming every intermediate query variable | Context dependent |
| Maximum operators per chain | No universal number |
| Whether service/repository methods return `IEnumerable<T>` or a materialized collection | Architectural decision — but the choice MUST be consistent and documented |
| `MoreLINQ` and other operator libraries | Dependency decision |
| PLINQ adoption | Measurement, not policy |
| Using LINQ at all in hot paths | Measurement, not policy |
| Anonymous types vs named records for projections | Context dependent |

## Complement, not conflict — the contract with the base skill

Four places where the two skills touch. Each is resolved in one direction only, and the resolution
is stated in the text so a reader never sees two answers:

1. **`var` for query and range variables.** The official LINQ convention says to use implicit
   typing for query and range variables and states that this *overrides* the general implicitly-
   typed-local rule. The base skill's `var` rule comes from dotnet/runtime and is stricter (only
   when the right-hand side names the type). **Ruling: inside a LINQ query, the LINQ convention
   wins** — `var` for query variables and range variables, always. This must be written in the
   LINQ skill as an explicit, cited override, and the base skill's §18 must not restate the strict
   rule for queries. This is the one real conflict; everything else is a division of labour.
2. **Base skill §18 stays, trimmed to essentials.** It keeps only what a developer needs without
   loading this skill: deferred execution exists; do not enumerate twice; no side effects in a
   pipeline; materialize before crossing an API boundary; name the query variable for its result.
   Every one of those must be a verbatim-compatible subset of a rule in this skill. Nothing in §18
   contradicts anything here; anything deeper lives here only.
3. **Equality and ordering.** `Distinct`, `GroupBy`, `Join`, `ToDictionary` and `ToLookup` all
   depend on `Equals`/`GetHashCode`, and `OrderBy` on `IComparable<T>`. The base skill's §14 owns
   *how to implement* those contracts. This skill's §17 owns *how to supply a comparer to an
   operator* and what breaks when the contract is wrong — referring to the base skill by name, not
   by path (audit C3).
4. **Async and cancellation.** The base skill owns `async`/`await`, TAP, and `CancellationToken`
   plumbing. This skill's §24 owns only the querying of async streams. No restatement of TAP rules.

## Conflict rulings to apply while writing

1. **`where` before other clauses** — official, keep as SHOULD, but scope it: it is a readability
   and reduce-the-set heuristic for in-memory queries. Over `IQueryable`, the provider reorders
   anyway, so do not present clause order as a performance rule there.
2. **"Multiple `from` clauses instead of `join`"** — official, but it is about reaching an
   element's *inner collection* (`SelectMany`). It is not advice for correlating two independent
   sequences, where `Join` is correct and O(n+m) rather than O(n×m). Scope the rule or it becomes
   wrong advice.
3. **`orderby` before a join** — the docs say they generally do not recommend it because some
   providers do not preserve ordering after the join. Record as AVOID.
4. **65-character line limit** — a docs-rendering artefact, as in the base plan. Discard.
5. **`CA1827` vs `CA1860`** — reconciled once in §10 as above. Never state both raw.
6. **`CA1851` is off by default in .NET 10** — so state the multiple-enumeration rule as a prose
   MUST and note that the analyzer is opt-in. Do not imply the build catches it.
7. **The PLINQ page is 2017-era** (`ms.date: 2017-03-30`) and its tooling references are stale
   (Concurrency Visualizer, "Visual Studio Team Server"). The operator semantics are current; the
   tooling advice is not. Cite the semantics, drop the tooling.

## Repo constraints (from `skills/my-skills-audit/scripts/mechanical-checks.py`)

Verified against the script:

- **C1** — `name:` equals the directory name, kebab-case; `description:` ≤ 1024 chars.
- **C2** — every `./references/NN-*.md` link in the Section Guide must resolve on disk (`high` if
  not). External `https://` links are skipped, so inline Microsoft Learn citations are safe.
- **C3** — no `../..` paths into sibling skill directories. Name other skills, never path them.
- **C4a** — a backticked skill name that does not exist is a `high` finding, and the word "skill"
  within 45 characters is what makes it read as a reference. Hence the unbackticked mention of the
  base skill until that skill exists.
- **C12** — description overlap, verified at 0.164 above.
- **C15** — `git add` the new directory or it reports as untracked (`low`).

`skills-lock.json` tracks only externally-installed skills, so no change. `README.md` already trips
the `low` C14 readme-coverage finding for every skill but the `db-core` trio — out of scope.

**No change needed to `code-review`**: it discovers standards skills with
`grep -l '^name:.*-standards$'`, and `csharp-dotnet10-linq-standards` matches by construction.

## Execution order

1. `mkdir -p skills/csharp-dotnet10-linq-standards/references`.
2. Write `SKILL.md` — frontmatter, overlay preamble, target environment, operating rules, the Query
   Style Consistency spec, classification table, general query design, discipline sections,
   de-standardisation table, the 25-row Section Guide, workflow.
3. Write the 25 reference files, batched by theme so rulings stay consistent across neighbours:
   syntax and readability (3–4), execution model (5–7), operator families (8–17), correctness
   (18–20), cost and shape (21–22), extension (23), async and parallel (24–25), discipline (26–27).
4. `git add` the directory.

## Verification

1. **Audit clean** — run the repo's own mechanical checks; filter the JSON to this skill and expect
   nothing above `low`:
   ```bash
   python3 skills/my-skills-audit/scripts/mechanical-checks.py --repo-root .
   ```
2. **Link integrity** — the Section Guide row count equals the file count:
   ```bash
   ls skills/csharp-dotnet10-linq-standards/references | wc -l
   ```
   should be 25, and every `./references/...` target must resolve (C2 covers this).
3. **Structural parity** — every reference file opens with `## N. `, uses only the five
   classification headings, and no file is a stub.
4. **Style detection behaves** — three spot-checks in fresh sessions, because this is the
   behaviour the user asked for and the only part that is not just prose:
   - a repo with method chains only → the skill writes method chains, silently;
   - a repo whose joins are written in query syntax → the skill matches query syntax there;
   - an empty repo → the skill writes method chaining and **does not ask**.
5. **No provider bleed** — grep the finished skill for EF Core vocabulary:
   ```bash
   grep -rniE 'ef core|entity framework|dbcontext|dbset|tolistasync|includable|migrations' skills/csharp-dotnet10-linq-standards
   ```
   Hits are acceptable only in the scope disclaimer and in §7 as the named boundary example.
   Anything else means provider scope leaked in.
6. **No conflict with the base skill** — once both exist, diff the two on their shared vocabulary
   and confirm each overlap is a labelled override or a division of labour, never a silent
   contradiction:
   ```bash
   grep -rn 'var\b' skills/csharp-dotnet10-linq-standards skills/csharp-dotnet10-standards | grep -iE 'implicit|query|range variable'
   ```
   The `var`-in-queries override must appear as an override in this skill and must not be
   contradicted in the base skill's §18.

---

# LINQ reference sources

Researched 2026-08-25. Every URL below was surfaced by search or fetch during research; the
`Enumerable` operator set was verified against the .NET 10 API page rather than inferred.

## Tier 1 — normative

| Source | URL |
|---|---|
| Language Integrated Query (LINQ) — C# | https://learn.microsoft.com/en-us/dotnet/csharp/linq/ |
| LINQ overview — .NET | https://learn.microsoft.com/en-us/dotnet/standard/linq/ |
| Standard query operators overview | https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/ |
| Introduction to LINQ queries | https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries |
| Write LINQ queries | https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/write-linq-queries |
| Walkthrough: writing queries | https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/walkthrough-writing-queries-linq |
| Working with LINQ (tutorial) | https://learn.microsoft.com/en-us/dotnet/csharp/tutorials/working-with-linq |
| Language features that support LINQ | https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/features-that-support-linq |
| .NET Coding Conventions — the *LINQ queries* section is the style authority | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions |
| LINQ query keywords (C# reference) | https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/query-keywords |
| `System.Linq.Enumerable` (.NET 10 operator surface) | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable?view=net-10.0 |
| `System.Linq.Queryable` | https://learn.microsoft.com/en-us/dotnet/api/system.linq.queryable |
| `System.Linq.AsyncEnumerable` | https://learn.microsoft.com/en-us/dotnet/api/system.linq.asyncenumerable |
| `System.Linq.ParallelEnumerable` | https://learn.microsoft.com/en-us/dotnet/api/system.linq.parallelenumerable |

### Operator category pages

All under `https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/`. The
complete set, verified against the `dotnet/docs` folder listing — there are ten, and there is no
separate element-operations or aggregation-operations page in the current docs:

`filtering-data` · `projection-operations` · `sorting-data` · `grouping-data` · `join-operations` ·
`set-operations` · `partitioning-data` · `quantifier-operations` · `converting-data-types` · `index`

### Execution model

| Topic | URL |
|---|---|
| Deferred execution and lazy evaluation | https://learn.microsoft.com/en-us/dotnet/standard/linq/deferred-execution-lazy-evaluation |
| Deferred execution example | https://learn.microsoft.com/en-us/dotnet/standard/linq/deferred-execution-example |
| Classification of operators by manner of execution | https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/classification-of-standard-query-operators-by-manner-of-execution |
| Expression trees (see the *Limitations* section) | https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/expression-trees/ |
| How to use expression trees to build dynamic queries | https://learn.microsoft.com/en-us/dotnet/csharp/linq/how-to-build-dynamic-queries |

### Extending LINQ and querying other sources

| Topic | URL |
|---|---|
| Write your own extensions to LINQ (custom operators, C# 14 `extension` blocks) | https://learn.microsoft.com/en-us/dotnet/csharp/linq/how-to-extend-linq |
| How to query collections | https://learn.microsoft.com/en-us/dotnet/csharp/linq/how-to-query-collections |
| How to query strings | https://learn.microsoft.com/en-us/dotnet/csharp/linq/how-to-query-strings |
| How to query files and directories | https://learn.microsoft.com/en-us/dotnet/csharp/linq/how-to-query-files-and-directories |

### LINQ over `IAsyncEnumerable<T>` (§24)

| Topic | URL |
|---|---|
| Breaking change: `System.Linq.AsyncEnumerable` in .NET 10 | https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/asyncenumerable |
| `System.Linq.AsyncEnumerable` package (for multitargeting) | https://www.nuget.org/packages/System.Linq.AsyncEnumerable/ |
| `System.Linq.Async` — the community package it supersedes | https://www.nuget.org/packages/System.Linq.Async |
| Ix.NET v7.0 migration write-up (community, cited by the breaking-change page) | https://endjin.com/blog/2025/11/ix-v7-dotnet-10-linq-iasyncenumerable |

### PLINQ (§25)

All under `https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/`:

`introduction-to-plinq` · `understanding-speedup-in-plinq` · `order-preservation-in-plinq` ·
`merge-options-in-plinq` · `how-to-specify-the-execution-mode-in-plinq` ·
`how-to-combine-parallel-and-sequential-linq-queries` · `how-to-handle-exceptions-in-a-plinq-query` ·
`how-to-cancel-a-plinq-query` · `how-to-measure-plinq-query-performance` ·
`custom-partitioners-for-plinq-and-tpl` · `lambda-expressions-in-plinq-and-tpl`

Plus `https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads`
for the cancellation contract, and
`https://learn.microsoft.com/en-us/dotnet/api/system.linq.parallelenumerable.orderby?view=net-10.0`
for the not-stable-sort statement.

### Analyzer rules (§27, cited inline throughout)

All under `https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/`:

| Rule | Title | Path |
|---|---|---|
| CA1826 | Use property instead of LINQ `Enumerable` method | `quality-rules/ca1826` |
| CA1827 | Do not use `Count`/`LongCount` when `Any` can be used | `quality-rules/ca1827` |
| CA1828 | Do not use `CountAsync`/`LongCountAsync` when `AnyAsync` can be used | `quality-rules/ca1828` |
| CA1829 | Use `Length`/`Count` property instead of `Enumerable.Count` | `quality-rules/ca1829` |
| CA1836 | Prefer `IsEmpty` over `Count` when available | `quality-rules/ca1836` |
| CA1841 | Prefer `Dictionary` `Contains` methods | `quality-rules/ca1841` |
| CA1851 | Possible multiple enumerations of `IEnumerable` collection — **not enabled by default in .NET 10** | `quality-rules/ca1851` |
| CA1860 | Avoid using `Enumerable.Any()` extension method | `quality-rules/ca1860` |
| CA1862 | Use `StringComparison` overloads for case-insensitive comparison | `quality-rules/ca1862` |
| CA1806 | Do not ignore method results (catches a discarded query) | `quality-rules/ca1806` |
| IDE0120 | Simplify LINQ expression (`Where(p).Any()` → `Any(p)`) | `style-rules/ide0120` |
| — | Performance rules index | `quality-rules/performance-warnings` |
| — | Quality rules index | `quality-rules/` |
| — | Style rules index | `style-rules/` |

`CA1851` configuration knobs, for teams with custom operators —
`enumeration_methods`, `linq_chain_methods`, `assume_method_enumerates_parameters`:
https://github.com/dotnet/roslyn-analyzers/blob/main/docs/Analyzer%20Configuration.md

### Operator semantics verified against the API docs

| Claim | URL |
|---|---|
| `OrderBy`/`OrderByDescending`/`ThenBy`/`ThenByDescending` are **stable** sorts | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.orderby?view=net-10.0 |
| `Order`/`OrderDescending` (no key selector) exist | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.order |
| `Shuffle` (new in .NET 10) | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.shuffle |
| `LeftJoin` / `RightJoin` (new in .NET 10) | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.leftjoin · https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.rightjoin |
| `Sequence` (new in .NET 10) | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.sequence |
| `CountBy` / `AggregateBy` / `Index` (.NET 9) | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.countby · https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.aggregateby · https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.index |
| `TryGetNonEnumeratedCount` | https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.trygetnonenumeratedcount |

Confirmed present on `Enumerable` in .NET 10 by inspecting the API page's method table:
`Shuffle`, `Sequence`, `LeftJoin`, `RightJoin`, `CountBy`, `AggregateBy`, `Index`, `Order`,
`OrderDescending`, `TryGetNonEnumeratedCount`, `Chunk`, `DistinctBy`, `MaxBy`, `MinBy`, `ExceptBy`,
`IntersectBy`, `UnionBy`, `Zip`, `ToLookup`, `AsEnumerable`.

### Tier 3 — community, non-normative

| Source | URL |
|---|---|
| Roslyn issue: nullable tracking does not work well with LINQ (the §19 gap, from the compiler team's own tracker) | https://github.com/dotnet/roslyn/issues/37468 |
| `WhereNotNull` / nullable references in enumerables | https://rendle.dev/posts/where-not-null/ |
| `awesome-analyzers` (curated analyzer list, shared with the base plan) | https://github.com/cybermaxs/awesome-analyzers |

---
---

# Roadmap: remaining core C# skills, before any framework skill

Not planned yet — recorded here so the sequencing is not lost. Nothing below is approved or
researched to the depth of the two plans above.

## The test each candidate has to pass

The same one LINQ passed: the topic is big enough that the base skill can only afford one to four of
its 41 sections; it has its own API surface and its own **silent** failure modes (no compiler
warning); and it is framework-independent. Everything failing that test stays a section in
`csharp-dotnet10-standards`.

Checked against the existing repo: `unit-testing`, `rest-client`, `rest-client-integration-testing`,
`resiliency-patterns-guide`, `logging-mdc-best-practices` and `check-diagnostics` are all
Java/Spring-specific, so every candidate below is greenfield — no duplication, no C12 overlap risk
from them.

## Tier 1 — prerequisites for an ASP.NET Core skill

| Skill | Why it cannot stay a section | Base skill sections it absorbs |
|---|---|---|
| `csharp-dotnet10-async-standards` | The largest gap, arguably larger than LINQ. `ValueTask`, `ConfigureAwait`, sync-over-async deadlock, `async void`, `TaskCompletionSource`, `WhenAll`/`WhenAny` error aggregation, thread-pool starvation, `SemaphoreSlim` and channels, `IAsyncEnumerable` production, `CancellationTokenSource` lifetime and leaks, `Parallel.ForEachAsync`, `TimeProvider`/`FakeTimeProvider`, async disposal. Strong authorities already gathered in the base plan's Tier 3 (Fowler's AsyncGuidance, Cleary ×3, the TAP docs). LINQ defects are usually performance; async defects are incidents | §19 async, §20 cancellation, §21 concurrency, §22 parallelism |
| `csharp-dotnet10-json-standards` | `System.Text.Json` sits under every service boundary: source-generated contexts vs reflection, options caching, polymorphism, custom converters, naming policies, `required`/`init`/records, unmapped-member handling, wire compatibility and versioning, trimming/AOT, `Utf8JsonReader`/`Utf8JsonWriter` in hot paths, Newtonsoft migration traps | §34 serialization |
| `csharp-dotnet10-host-and-di-standards` | The layer directly beneath every framework: generic host, service lifetimes, captive dependencies, `IServiceScopeFactory`, `IOptions` vs `IOptionsSnapshot` vs `IOptionsMonitor`, options validation and `ValidateOnStart`, configuration layering and secrets, `BackgroundService`/`IHostedService` (swallowed-exception and blocked-startup traps), `IHostApplicationLifetime`, graceful shutdown. ASP.NET Core, worker services and console tools all sit *on* this, so it is a base, not an overlay | none — currently unowned |

## Tier 2 — high value, narrower

| Skill | Scope sketch | Open question to settle first |
|---|---|---|
| `csharp-dotnet10-observability-standards` | Source-generated `LoggerMessage` (`CA1848`), structured logging and scopes, log levels, PII/secret redaction, `ActivitySource`/`Activity`, OpenTelemetry semantic conventions, `System.Diagnostics.Metrics`, `IMeterFactory`. The C# counterpart to `logging-mdc-best-practices` | Is OpenTelemetry in play, or `ILogger` only? |
| `csharp-dotnet10-testing-standards` | The sibling to `unit-testing`. `tdd-by-example` already establishes the "apply alongside a language-specific test-style skill" pattern, so this slots in without changing that skill | Which test framework and assertion library — that choice drives most of the content |
| `csharp-dotnet10-http-client-standards` | `IHttpClientFactory`, and why both `new HttpClient()` per call and a long-lived static instance are wrong in different ways (socket exhaustion vs stale DNS); `SocketsHttpHandler` tuning, `Microsoft.Extensions.Http.Resilience`, handler vs per-request timeouts, `HttpCompletionOption.ResponseHeadersRead` for streaming, reading a problem body instead of `EnsureSuccessStatusCode`, cancellation propagation | Resilience library: `Microsoft.Extensions.Http.Resilience`, raw Polly, or neither? |
| `csharp-dotnet10-build-and-project-standards` | Where the base plan's **deliberately omitted** enforcement assets belong: SDK-style csproj, `Directory.Build.props`, central package management via `Directory.Packages.props`, `TreatWarningsAsErrors`, `AnalysisLevel` and `EnforceCodeStyleInBuild`, the shipped `.editorconfig`, NuGet auditing, deterministic builds, SourceLink, trimming/AOT publish switches | The base plan ruled "prose only, ship no copyable config". This skill is the place that ruling defers to — confirm that is still the intent |

## Tier 3 — only if the work actually calls for it

Source generators and Roslyn analyzer authoring · P/Invoke and native interop ·
a `Span<T>`/`Memory<T>` deep dive (largely already covered by base §37–38).

## Sequencing

Tier 1 before any framework skill. If an ASP.NET Core skill lands first, it will end up re-teaching
DI lifetimes, options validation and async correctness *inside* a framework overlay — the same
mistake as leaving LINQ inside the base skill, which is why this repo is getting a LINQ skill at
all. Tier 2 can follow in any order; each has one open question that should be answered before its
plan is written, since the answer changes most of the content.
