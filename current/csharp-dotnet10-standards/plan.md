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

---
---

# Decision: skill depth

Raised and settled 2026-08-25. Recorded so it is not re-opened without new information.

**The challenge.** Language standards skills should arguably be thin policy layers, not
knowledge bases — the model already knows C#, so re-teaching it duplicates training data, burns
tokens, and creates documentation to maintain. Depth belongs in process skills (code review,
refactoring, TDD, DDD) where judgement and sequencing matter, not in language skills where the
valuable part is only *constraining choices for this environment*.

**Decision: keep the depth as planned.** 41 base sections, 25 LINQ sections, full reference corpus.

**Reasoning behind the decision:**

1. **Progressive disclosure means reference files are near-free in context.** Only `SKILL.md` is
   always loaded; `references/NN-*.md` files cost tokens only when the Section Guide routes to
   them. The "miniature textbook" cost applies to a monolithic skill, not a routed one. What
   remains is a maintenance cost, which was accepted.
2. **The reference corpus is `code-review`'s checklist.** That skill discovers `*-standards` skills
   and reads their `references/` when the diff touches an area detailed enough to need them. A thin
   policy layer alone gives the reviewer nothing to check against. Thinning would trade
   agent-writing efficiency for review depth.
3. **Consistency with the existing repo.** `java-21-standards` (36 references) and
   `java-21-springboot-standards` (40) already total 76 files. Thinning C# alone would give the
   same reviewer asymmetric depth by language.
4. **Version-specific facts are not duplicated training data.** A May-2026 model cannot be trusted
   on what actually shipped in .NET 10 / C# 14. Verified, cited facts — `System.Linq.AsyncEnumerable`
   in-box, `LeftJoin`/`RightJoin`/`Shuffle`/`Sequence` on `Enumerable`, `CA1851` off by default,
   the `CA1827`/`CA1860` reconciliation, `var` for query variables as a documented override — are
   the highest-value content in either plan precisely because they are not general knowledge.

**Acknowledged costs, accepted rather than solved:**

- **Signal dilution.** Where a reference file's rules are largely what the model would do anyway,
  the rules that genuinely constrain it are weighted lower. Mitigation while writing: lead each
  file with its MUST/NEVER rules and keep SHOULD/CONSIDER terse, so the binding rules sit first.
- **Always-loaded generic prose.** The General Design and AI-guardrail blocks are the most generic
  content in the skill and the only part paying context rent every turn. Mitigation: keep those
  blocks at or below the Java skill's current length; put new material in reference files, never in
  `SKILL.md`.
- **Maintenance surface.** 66 new reference files across the two C# skills. The repo's own audit
  (`my-skills-audit`) is the control for drift.

**What would reopen this:** evidence that a thinner skill produces equal or better outcomes on the
behavioural spot-checks in either plan's Verification section, or a `code-review` run that shows
the reference corpus is not actually being consulted.

---
---

# Plan: `csharp-dotnet10-winui3-standards` skill

## Context

The two C# plans above cover the language and its query surface. Neither says anything about the
presentation layer, and WinUI 3 is the platform where a C#-competent model most reliably produces
code that **compiles and then fails at runtime** — because a decade of UWP answers still type-check
against the Windows projection but throw in a desktop app.

This is the second overlay on `csharp-dotnet10-standards`, alongside the LINQ skill. Same
relationship `java-21-springboot-standards` has to `java-21-standards`: works standalone, never
contradicts the base, and states every point of contact as a one-directional ruling.

Research is complete. Every source URL is inlined in the **WinUI reference sources** section at the
end of this document.

### Version investigation — the answer is "no LTS, and the line moved to 2.x"

The user's question was whether an LTS version exists. It does not.

| WinAppSDK | Released | Latest patch | Support level | End of servicing |
|---|---|---|---|---|
| 2.0 | 2026-04-29 | **2.4.0** (2026-08-13) | **Current** | 2027-04-29 |
| 1.8 | 2025-09-09 | 1.8.260804001 | Maintenance | **2026-09-09** |
| 1.7 | 2025-03-18 | 1.7.260224002 | Out of support | 2026-03-18 |

The Windows App SDK is governed by the [Microsoft Modern
Lifecycle](https://learn.microsoft.com/en-us/lifecycle/policies/modern) with only two servicing
tiers — *Current* (latest stable, frequent fixes) and *Maintenance* (critical fixes only, higher
bar). There is no LTS or LTSC channel; a major line gets roughly twelve months. The nearest thing
to a long-term anchor is **.NET 10 (LTS)** paired with whichever WinAppSDK line is *Current*, on a
Windows 10 1809 (build 17763) floor.

Facts that follow, and that a May-2026 model will get wrong:

- **WinAppSDK 2.0 (Apr 2026) is the first major bump since 1.0** and adopted SemVer 2.0.0, so the
  NuGet version and the product version now agree (`2.4.0`, not `1.8.260804001`). The package
  family name is tied to the major version; the next side-by-side major is 3.0.0.
- **WinUI 3 keeps its name** in 2.0 — the release notes say so explicitly. Do not invent "WinUI 4".
- **1.8 leaves support on 2026-09-09**, roughly two weeks after this plan was written. Anchoring
  the skill to 1.8 would ship it stale.
- Build 2026 designated WinUI as the native production platform for modern Windows apps, so the
  platform is not a dead end — the churn is in the SDK version, not the framework.

**Therefore: the version lives in a Target Environment table, not the skill name.** `winui3` is
durable; `winappsdk2` is not.

### Decisions already made by the user

| Question | Decision |
|---|---|
| Name | **`csharp-dotnet10-winui3-standards`** — base name + framework, mirroring `java-21-springboot-standards` |
| Scope beyond XAML and view models | **Windowing, app lifecycle, and UI-thread dispatch only.** Localization/MRT, packaging/deployment, and notifications/widgets/AI APIs are all out |
| MVVM library stance | **`CommunityToolkit.Mvvm` is the documented default** — `ObservableObject`, `[ObservableProperty]`, `[RelayCommand]`, with the MVVMTK diagnostics cited as enforcement |
| UWP → WinUI 3 migration | **One legacy-API section**, framed as forbidden APIs rather than a migration walkthrough |

Explicit scope exclusions, recorded so they are not quietly re-added while writing:

- **Localization and MRT** (`x:Uid`, `.resw`, `Microsoft.Windows.ApplicationModel.Resources`,
  `FlowDirection`/RTL) — out, despite `x:Uid` being XAML markup. Added to the roadmap below.
- **Packaging and deployment** (MSIX, packaged-with-external-location, unpackaged, framework-
  dependent vs self-contained, Bootstrapper API, single-project MSIX, publish switches) — out,
  deferred to the roadmap's build-and-project skill.
- **Notifications, widgets, Windows AI APIs** — out; Windows App SDK surface that is not the UI
  framework.
- **Native AOT is a partial exception.** The *publish switches* are out with the rest of
  deployment, but the *code-shape* rules that make a WinUI app AOT-viable (§29) are in, because
  they change how bindings, converters and serialization are written — which is a standards
  question, not a build question.

## The content filter — what earns a section

The base skill's rule was "big enough that the base can only afford a few sections." Here the rule
is sharper, because the user asked not to rehash the obvious. A rule earns space only if it is in
one of four classes:

1. **Compiles, then fails at runtime.** WinUI 3's signature defect class. UWP types still resolve,
   so decade-old answers type-check and then throw: `Window.Current`, `CoreDispatcher.RunAsync`,
   `ContentDialog` without `XamlRoot`, `Windows.Storage.Pickers` without an HWND, `ApplicationView`,
   `Window.Resources`, Visual State Manager on `Window`.
2. **Silent misbehaviour with no compiler or analyzer backstop.** `x:Bind` defaulting to `OneTime`
   while `Binding` defaults to `OneWay`; silent binding failures; `StaticResource` where
   `ThemeResource` was required; unremoved event subscriptions; `ObservableCollection<T>` mutated
   off the UI thread or bulk-loaded one item at a time.
3. **Version-specific facts.** The 2.x lifecycle above; `SystemBackdropElement` (new in 2.0,
   closing the in-app acrylic gap); `IXamlCondition` replacing the experimental `IXamlPredicate`;
   `FileSavePicker` no longer creating an empty file (a behavioural break in 2.0);
   `Microsoft.Windows.Storage.Pickers` taking a `WindowId` instead of an HWND and working elevated;
   `TitleBar` custom drag regions; `ApplicationData` for unpackaged apps; `[ObservableProperty]` on
   `partial` properties (Toolkit 8.4+), which supersedes the field form in nearly all existing
   material.
4. **Judgement the model gets wrong by default.** Accessibility, where to stop abstracting, and
   which of three navigation/DI reconciliations to pick.

Everything else — XAML syntax, what MVVM is, "await instead of blocking" — gets one line in an
always-loaded block or nothing at all.

## Structure

```
skills/csharp-dotnet10-winui3-standards/
  SKILL.md
  references/03-mvvm-layering-and-boundaries.md … 32-enforcement-and-diagnostics.md
```

### `SKILL.md` (always loaded)

Follows `skills/java-21-springboot-standards/SKILL.md` — the overlay shape.

1. **Frontmatter** — `name: csharp-dotnet10-winui3-standards` (must equal the directory name).
2. **Overlay preamble** — "If the csharp-dotnet10-standards skill is available, apply it first."
   Then the standalone fallback listing the baseline it holds without the base skill: nullable
   enabled, async all the way, no speculative abstractions, no unrelated modernization, no silent
   behaviour changes. Base skill named **without backticks** — see the C4a note below.
3. **Target Environment** table — WinUI 3 in Windows App SDK **2.x (Current line; 2.4.0 at time of
   writing)**; .NET 10 / C# 14; `net10.0-windows10.0.26100.0` with
   `TargetPlatformMinVersion` 10.0.17763.0; `Microsoft.WindowsAppSDK` and
   `CommunityToolkit.Mvvm` as the two assumed packages; a line stating there is no LTS channel and
   the Current line rolls roughly annually.
4. **Operating Rules** — ~18 numbered rules active before writing any WinUI code. Includes: never
   reach for a `Windows.UI.Xaml.*` or UWP-lifecycle API; every `ContentDialog`/`Popup`/`Flyout`
   gets a `XamlRoot`; every cross-thread UI update goes through the owning `DispatcherQueue`; view
   models never reference `Microsoft.UI.Xaml`; `x:Bind` with an explicit `Mode`; every `+=` in a
   view has a matching `-=`; no async work in a constructor; no `ConfigureAwait(false)` on a path
   that resumes on the UI thread.
5. **Forbidden UWP-era APIs** — always-loaded, and this skill's headline behaviour. Spec below.
6. **Classification Meanings** — MUST / SHOULD / CONSIDER / AVOID / NEVER, reused verbatim.
7. **General UI Design** — the rules that apply to every WinUI change: the MVVM layering contract,
   the five sanctioned service abstractions, and the code-behind boundary.
8. **Agent change discipline + AI overengineering guardrails** — WinUI-specific. AVOID: a
   converter for something a view-model property could expose; a base view-model class with one
   subclass; wrapping every control in a `UserControl`; re-templating a control to change a colour
   lightweight styling already exposes; `IMessenger` where a direct reference would do; a
   `Task.Run` in a click handler for I/O-bound work; an abstraction over `DispatcherQueue`
   invented before a test needs it.
9. **Areas without universal rules** — the de-standardisation table (below).
10. **Section Guide** — 30 rows, `./references/NN-*.md` + a "Consider When" routing column.
11. **Workflow** — 5 steps matching the other two skills.

### Frontmatter description

Verified against the audit's C12 overlap check with the script's own tokenizer. Peaks at **0.113
against `java-21-springboot-standards`** (shared boilerplate only: *complements, standalone,
refactoring, reviewing, writing*), 0.095 against `csharp-dotnet10-standards`, 0.085 against
`csharp-dotnet10-linq-standards`. Threshold is 0.30. Length 574 of 1024.

> Use when writing, reviewing, or refactoring WinUI 3 desktop apps built on the Windows App SDK and
> .NET 10. Covers XAML markup, x:Bind compiled bindings, MVVM with the CommunityToolkit.Mvvm
> generators, AppWindow and title bars, UI-thread dispatch, activation and single-instancing, page
> navigation, theming and resource lookup, accessibility, visual-tree performance, view leaks, and
> forbidden UWP-era APIs. Presentation layer only — no packaging, deployment, or localization
> guidance. Complements csharp-dotnet10-standards when available and works standalone when it is not.

The distinguishing tokens are `winui`, `xaml`, `bind`, `appwindow`, `dispatch`, `instancing`,
`navigation`, `theming`, `leaks`, `uwp`; keep them if the wording is revised.

**C4a note, same as the LINQ plan.** The audit flags a backticked skill name that does not exist on
disk as `high` when the word "skill" appears within 45 characters. `csharp-dotnet10-standards` may
not exist yet, so it is named unbackticked in the description and the preamble. Backticks become
safe once the base skill lands.

### Forbidden UWP-era APIs — the always-loaded table

This is the analogue of the LINQ skill's Query Style Consistency block, and it is always loaded for
the same reason: **routing to a reference file is too late.** The model emits `Window.Current`
unprompted, before any Section Guide lookup happens. The table has to be in working context from
the first token.

Compact, one line per row — banned API, replacement, and the failure mode:

| Do not use | Use instead | What happens if you don't |
|---|---|---|
| `Window.Current` | a window tracked by the app (e.g. `App.MainWindow`) | no desktop equivalent; null or unavailable |
| `CoreDispatcher` / `Dispatcher.RunAsync` | `DispatcherQueue.TryEnqueue` | no `CoreDispatcher` on a desktop window |
| `ContentDialog` / `Popup` / `Flyout` with no `XamlRoot` | set `XamlRoot` from the owning element | runtime exception, not a hidden dialog |
| `Windows.Storage.Pickers.*` | `Microsoft.Windows.Storage.Pickers.*` (takes a `WindowId`) | UWP pickers need HWND interop and fail elevated |
| `MessageDialog` | `ContentDialog` | needs `InitializeWithWindow`; wrong visual language |
| `ApplicationView` / `CoreWindow` | `AppWindow`, `Microsoft.UI.Windowing` | not available to desktop apps |
| `Window.Resources` / `Window.DataContext` / VSM on `Window` | a root `Grid` or `Page` inside the window | property does not exist; VSM silently does nothing |
| `Application.Suspending` / `Resuming` | `AppInstance` activation, `AppLifecycle` APIs | desktop apps are not suspended; handler never fires |
| `AcrylicBrush.BackgroundSource` | `SystemBackdropElement` (2.0+) or `DesktopAcrylicBackdrop` | property removed |
| `DataTransferManager.ShowShareUI` | HWND-associated interop call | throws without window association |

The full reasoning, the interop helpers (`WindowNative.GetWindowHandle`,
`Win32Interop.GetWindowIdFromWindow`), and the `WRONG`/`CORRECT` pairs live in §31; the table is the
guard rail, §31 is the explanation.

### Reference files — 30 sections, numbered 3–32

Numbering starts at 3 to match the other two standards skills.

| # | File | # | File |
|---|---|---|---|
| 3 | mvvm-layering-and-boundaries | 18 | control-selection |
| 4 | view-models-and-observable-state | 19 | ui-thread-and-dispatcherqueue |
| 5 | commands-and-user-actions | 20 | windowing-appwindow-and-title-bar |
| 6 | messaging-between-view-models | 21 | multiple-windows-and-xamlroot |
| 7 | dependency-injection-and-composition | 22 | app-activation-and-instancing |
| 8 | asynchronous-initialization-and-loading | 23 | page-navigation |
| 9 | compiled-bindings-and-x-bind | 24 | dialogs-pickers-and-win32-interop |
| 10 | classic-binding-and-datacontext | 25 | accessibility |
| 11 | value-converters-and-formatting | 26 | exceptions-and-failure-handling |
| 12 | collections-and-itemssource | 27 | element-lifetime-and-memory-leaks |
| 13 | input-validation-and-error-display | 28 | performance-and-responsiveness |
| 14 | xaml-file-structure-and-naming | 29 | aot-and-trimming-compatibility |
| 15 | layout-and-panels | 30 | testability-and-view-model-testing |
| 16 | styles-templates-and-lightweight-styling | 31 | forbidden-uwp-era-apis |
| 17 | resources-and-theming | 32 | enforcement-and-diagnostics |

Sections worth pinning down now, because they carry the rulings that have no compiler backstop or
where the plan takes a position the docs decline to take:

- **§3 MVVM layering.** The official `data-binding-and-mvvm` page describes the three layers and
  then declines to recommend a framework, saying most of the benefit comes from data binding alone.
  This skill goes further, because "no opinion" is what produces inconsistent codebases. The
  layering MUSTs: a view model never references `Microsoft.UI.Xaml` or `Microsoft.UI.Windowing`;
  the model layer knows nothing of either. **Code-behind is explicitly permitted for view
  concerns** — focus, animation, visual states, `AutomationPeer`, drag/drop mechanics. The common
  failure is not too little MVVM; it is a `ContentDialog` shown from a view model.
- **§3 the five sanctioned services.** Navigation, dialog, UI-thread dispatch, settings, theme —
  and *no others* without a concrete second implementation or test seam. Each of the five exists
  because a view model must not touch what it wraps. Anything beyond is the speculative-abstraction
  anti-pattern the base skill already forbids, and WinUI attracts it badly.
- **§4 view models and observable state.** `ObservableObject` + **`[ObservableProperty]` on
  `partial` properties**, not on fields — the field form predates Toolkit 8.4 and C# 13 partial
  properties and dominates existing material, so this must be stated as the default with the field
  form marked AVOID (legacy). `[NotifyPropertyChangedFor]`, `[NotifyCanExecuteChangedFor]`.
  `MVVMTK0034` (referencing the backing field instead of the generated property, and so raising no
  notification) cited inline. Also the NRT friction: a view model property bound from XAML but
  assigned after construction needs `required` or a nullable annotation, not a `!`.
- **§5 commands.** `[RelayCommand]`, `CanExecute` wiring, async commands with
  `[RelayCommand(AllowConcurrentExecutions = false)]`, `IsRunning` for busy state, cancellation via
  the generated `Cancel` command. NEVER: a command body that catches nothing (see §26).
- **§6 messaging.** `IMessenger` is written up as a trap, not a feature: it is the fastest route to
  an untraceable global event bus. CONSIDER only where a direct reference is genuinely wrong.
  MUST unregister — `ObservableRecipient` handles it only if the lifetime is actually managed.
- **§7 DI and composition.** `Microsoft.Extensions.DependencyInjection` wired in `App`; there is no
  request scope in a desktop app, so the base skill's captive-dependency reasoning applies
  differently and must be restated in WinUI terms. Division of labour with a future host/DI skill
  is described in prose **without naming that skill**, because it does not exist (C4a).
- **§8 asynchronous initialization.** There is no async constructor and no async property getter,
  so the skill picks one pattern rather than leaving it open: a `[RelayCommand] LoadAsync` invoked
  from `Loaded` or `OnNavigatedTo`. NEVER fire-and-forget in a constructor. This is also where the
  `async void` override lands (see the conflict contract).
- **§9 compiled bindings.** **`x:Bind` defaults to `OneTime`; `Binding` defaults to `OneWay`.**
  Converting one to the other silently stops the UI updating, and nothing warns. Stated as a MUST:
  always write `Mode` explicitly, or set `x:DefaultBindMode` at a container. Plus `x:DataType`
  required in a `DataTemplate`; function bindings; `x:Load`/`x:DeferLoadStrategy`; `x:Bind` is
  generated code, so it is compile-checked and AOT-friendly where `Binding` is reflection (→ §29);
  and `x:Bind` event bindings hold strong references (→ §27).
- **§12 collections and `ItemsSource`.** `ObservableCollection<T>` MUST be mutated on the UI
  thread, and it raises one notification per item — so a bulk load is N layout passes. The LINQ
  complement lives here: **NEVER bind `ItemsSource` to a deferred query**, because it re-enumerates;
  materialize first. Referenced to the LINQ skill by name, never by path (C3).
- **§17 resources and theming.** `StaticResource` resolves once; `ThemeResource` re-resolves on
  theme change. Using `StaticResource` for a theme-varying brush is correct in light mode and wrong
  in dark, with no diagnostic. Plus `ThemeDictionaries`, merge order, `x:Key` vs `x:Name` in a
  dictionary, and high contrast (→ §25).
- **§19 UI thread and `DispatcherQueue`.** `DispatcherQueue.GetForCurrentThread()`,
  `HasThreadAccess`, and the fact that **`TryEnqueue` returns `bool`** and legitimately fails during
  shutdown — ignoring the result is a silent dropped update. WinUI objects are thread-affine (STA).
  `DispatcherQueueSynchronizationContext`. This is also where the `ConfigureAwait(false)` override
  lands.
- **§21 multiple windows and `XamlRoot`.** Each window has its own `XamlRoot` *and* its own
  `DispatcherQueue`, so any static "current window" or "the dispatcher" thinking breaks the moment a
  second window exists. This is the section that makes §24's dialog rules make sense.
- **§23 page navigation — the one genuine structural conflict, resolved.**
  `Frame.Navigate(typeof(Page), param)` requires a parameterless page constructor, which is
  incompatible with constructor injection. Three real answers exist; the skill names one as the
  default rather than surveying them: **the page's parameterless constructor resolves its view model
  from the container**, and `Frame.Navigate` is retained so the back stack keeps working. Written
  honestly as a service locator confined to one line, with `ActivatorUtilities`-based page creation
  as the CONSIDER for when pages themselves need constructor injection. Also: `NavigationCacheMode`,
  and the requirement that a navigation parameter be serializable if `GetNavigationState` is used.
- **§26 exceptions and failure handling.** An escaped exception in an `async void` event handler
  **terminates the process**; `Application.UnhandledException` does not reliably catch it. So the
  `async void` allowance in §8 comes with a MUST: the handler body is fully guarded. Plus the UX
  half — what a user sees (`InfoBar` vs `ContentDialog` vs a inline field error) is a standards
  question, not just a design one.
- **§27 element lifetime and memory leaks.** The classic XAML leak set, none of which the compiler
  sees: view-model-to-view subscriptions, `Loaded` without `Unloaded` teardown, static event
  sources, `x:Bind` event bindings, `CompositionTarget.Rendering`, a retained `ItemsSource`. MUST:
  every `+=` in a view has a matching `-=`.
- **§28 performance.** Built on the official `develop/performance` corpus rather than folklore —
  `winui-perf` frames everything as a frame budget (a frame should finish inside one refresh
  interval or input stalls) and points at WPR plus the XAML Frame Analysis plugin;
  `optimize-xaml-loading` (element count, `x:Load`), `optimize-xaml-layout` (Grid over nested
  StackPanel, avoid forced re-layout), `optimize-gridview-and-listview` and
  `listview-and-gridview-data-optimization` (template complexity, `ItemsStackPanel`,
  `ContainerContentChanging`, incremental loading), `mvvm-performance-tips`,
  `app-startup-performance`, `improve-garbage-collection-performance`.
- **§29 AOT and trimming compatibility** — code shape only. `x:Bind` over `Binding`;
  source-generated `System.Text.Json` over reflection; no reflection-based converters; the
  `IL2026`/`IL3050` analyzer warnings as the signal. Native AOT has been supported since WinAppSDK
  1.6; **the current caveats need re-verification before this file is written** (see Open items).
- **§30 testability.** View models are plain .NET and belong in an ordinary test project; that is
  the main argument for §3's boundaries. `TimeProvider` for time (deferring to the base skill).
  The one WinUI-specific seam worth abstracting is `DispatcherQueue`, and only when a test needs
  it — consistent with §3's "five services and no more".
- **§32 enforcement and diagnostics — stated honestly as weaker than in C#.** XAML has no CA
  rules. What genuinely exists: the MVVMTK diagnostics (`MVVMTK0034` and siblings), XAML compiler
  errors, **`CA1416` platform compatibility** (which actually bites given a 17763 floor against a
  26100 SDK), the trim/AOT analyzers, and the `Microsoft.Windows.CsWinRT` diagnostics. Prose rules
  carry more weight here than in the base skill, and the file should say so rather than implying a
  build gate exists.

## Authoring conventions per reference file

Identical to both plans above, so the three skills read as one family:

- `## N. Title`, then only the applicable `### MUST` / `### SHOULD` / `### CONSIDER` / `### AVOID` /
  `### NEVER` blocks as terse bullets. Omit empty levels. Lead with MUST/NEVER, per the depth
  decision's signal-dilution mitigation.
- Optional `### Examples` with `WRONG` / `CORRECT` pairs, reserved for traps prose cannot convey.
  Budget ~10 of 30 files — the highest ratio of the three skills, because WinUI's worst failures are
  invisible in prose: the `x:Bind` `OneTime` default, the missing `XamlRoot`, the `StaticResource`
  theme bug, the unremoved handler, the off-thread `ObservableCollection` mutation. Fences are
  ```csharp and ```xml (XAML is XML — do not invent a ```xaml fence, it will not highlight).
- Cite the diagnostic ID inline wherever one exists, and say so when none does.
- 15–65 lines per file. Do not pad.

## Areas without universal rules (the de-standardisation table)

| Topic | Why |
|---|---|
| `Views/`+`ViewModels/` folders vs feature folders | Architectural decision |
| One `ResourceDictionary` vs many merged | Project scale |
| `x:DefaultBindMode="OneWay"` at page root vs per-binding `Mode` | Either satisfies the §9 MUST |
| Converter vs function binding vs a computed view-model property | Context dependent |
| `ContentDialog` vs `InfoBar` vs `TeachingTip` for a given message | Design decision |
| `Page` vs `UserControl` as the navigation unit | Project convention |
| Threshold for replacing `ObservableCollection<T>` with an incremental source | Measurement |
| Whether the view or the view model owns visual state | Context dependent |
| Mica vs Acrylic vs a solid backdrop | Design decision |
| Windows Community Toolkit (`CommunityToolkit.WinUI.*`) adoption | Dependency decision |
| Test framework and UI-automation tooling | Separate concern |
| Adopting Native AOT | Measurement, not policy |
| Tabs/spaces, XAML attribute-per-line, line length | Formatter/repository concern |

## Complement, not conflict — the contract with the base skill

Six points of contact. Each resolved in one direction only, written so a reader never sees two
answers. Items 1–3 are genuine reversals of a base-skill rule and must be written as **cited
overrides in both directions** — the base skill's corresponding section must not restate its rule
in a way that covers WinUI event handlers or UI-thread continuations.

1. **`async void`.** The base skill forbids it. WinUI event-handler delegate signatures require it.
   **Ruling: permitted for event handlers only**, and only with a fully guarded body, because an
   escaped exception terminates the process (§8, §26). Not permitted anywhere else, including
   commands — `[RelayCommand]` already returns a `Task`.
2. **`ConfigureAwait(false)`.** Inverted here. On any path that resumes on the UI thread — view
   models, code-behind, command bodies — `ConfigureAwait(false)` loses the UI context and is a bug.
   **Ruling: do not use it in presentation-layer code**; the base skill's library-oriented guidance
   applies below the view-model boundary (§19).
3. **`partial` types.** Base skills discourage them. WinUI *requires* them: XAML code-behind, and
   `[ObservableProperty]` on partial properties. **Ruling: partial is the norm here**, and the
   related base rule on private-field naming simply does not arise, because the field form of
   `[ObservableProperty]` is marked AVOID in §4.
4. **Immutability.** The base skill prefers immutable state; a view model is inherently mutable
   observable state. This is scope, not contradiction — but it must be said explicitly, or the two
   skills read as opposed. Models and DTOs stay immutable; view models do not.
5. **LINQ.** Complement, not conflict, and the only touchpoint with
   `csharp-dotnet10-linq-standards`: never bind `ItemsSource` to a deferred query, materialize
   first (§12). One rule, referencing that skill by name, not by path (C3).
6. **Equality, disposal, cancellation, `TimeProvider`.** All owned by the base skill. This skill
   references them by name and adds only the WinUI-specific consequence (e.g. `Unloaded` as the
   disposal trigger for a view, §27).

## Conflict rulings to apply while writing

1. **The official docs decline to recommend an MVVM framework.** `data-binding-and-mvvm` says most
   of the benefit comes from data binding "without using any external frameworks". This skill takes
   a stronger position by user decision. Record the divergence honestly in §3 rather than implying
   Microsoft mandates the Toolkit.
2. **`x:Bind` is not universally better than `Binding`.** It cannot bind element-to-element without
   help, does not inherit `DataContext`, and needs a compile-time-known type. §10 must give
   `Binding` a real remit rather than framing it as legacy.
3. **The `github/awesome-copilot` WinUI 3 instructions are prior art, not a source.** They are
   ~2,000 words over ~20 topics and contain at least one claim to check rather than copy
   (`Window.Current` → "`App.Window`" as though that were a platform API; it is a convention the
   app defines). Useful as a coverage cross-check; not citable.
4. **The UWP docs are a partial trap.** Many XAML concepts are documented only under
   `/windows/uwp/`, and most of it transfers — but lifecycle, dispatcher, windowing and pickers do
   not. Prefer a `/windows/apps/` page whenever one exists; when citing a UWP page, verify the API
   is not on the §31 forbidden list.
5. **The Windows App SDK version will drift.** Every version-specific claim goes in the Target
   Environment table or is written with its version named inline, so a future reader can tell what
   is stale. Do not scatter bare "new in 2.0" without the number.

## Repo constraints (from `skills/my-skills-audit/scripts/mechanical-checks.py`)

Verified against the script:

- **C1** — `name:` equals the directory name, kebab-case; `description:` ≤ 1024 chars (574 above).
- **C2** — every `./references/NN-*.md` link in the Section Guide must resolve on disk (`high` if
  not). External `https://` links are skipped, so inline Microsoft Learn citations are safe.
- **C3** — no `../..` paths into sibling skill directories. Name other skills, never path them.
- **C4a** — a backticked skill name that does not exist, with "skill" within 45 characters, is a
  `high` finding. Hence the unbackticked base-skill mentions, and no named reference to any
  roadmap skill that has not been built.
- **C12** — description overlap, verified above: peak 0.113 against `java-21-springboot-standards`.
- **C15** — `git add` the new directory or it reports as untracked (`low`).

`skills-lock.json` tracks only externally-installed skills, so no change. `README.md` already trips
the `low` C14 finding for every skill but the `db-core` trio — out of scope.

**No change needed to `code-review`**: it discovers standards skills with
`grep -l '^name:.*-standards$'`, and `csharp-dotnet10-winui3-standards` matches by construction.

## Open items to re-verify at writing time

Recorded rather than guessed, so nothing unverified reaches the skill:

- **Native AOT status for WinUI 3 on .NET 10 / WinAppSDK 2.x.** Supported since 1.6 per the
  Windows Developer Blog, but the only current-state signals found were issue reports
  (`dotnet/sdk#53387`: cross-architecture AOT publish via `.wapproj` regressed in .NET 10.0.103;
  reports that AOT worked only for packaged apps in some .NET 10 previews). Find the Learn page if
  one now exists, and state the caveats with versions attached. **Do not assert blanket AOT
  support in §29.**
- **`Microsoft.Windows.CsWinRT` diagnostic IDs.** Named as a package, not by rule ID, because no ID
  was verified. Either verify IDs or keep it at package level in §32.
- **`x:DefaultBindMode`** was confirmed from community sources and the UWP-era docs; confirm it on a
  current `/windows/apps/` page before stating it as the sanctioned alternative in §9.
- **`develop/ui/controls/`, `design/style/`, `design/layout/`, `design/basics/`** were verified to
  exist as folders but their file lists were not enumerated. Enumerate before writing §15–§18.

## Execution order

1. `mkdir -p skills/csharp-dotnet10-winui3-standards/references`.
2. Resolve the four Open items above.
3. Write `SKILL.md` — frontmatter, overlay preamble, target environment, operating rules, the
   forbidden-API table, classification table, general UI design, discipline sections,
   de-standardisation table, the 30-row Section Guide, workflow.
4. Write the 30 reference files, batched by theme so rulings stay consistent across neighbours:
   architecture (3–8), binding (9–13), XAML surface (14–18), threading and windowing (19–24),
   quality (25–30), legacy and enforcement (31–32).
5. `git add` the directory.

## Verification

1. **Audit clean** — run the repo's own mechanical checks; filter the JSON to this skill and expect
   nothing above `low`:
   ```bash
   python3 skills/my-skills-audit/scripts/mechanical-checks.py --repo-root .
   ```
2. **Link integrity** — the Section Guide row count equals the file count:
   ```bash
   ls skills/csharp-dotnet10-winui3-standards/references | wc -l
   ```
   should be 30, and every `./references/...` target must resolve (C2 covers this).
3. **Structural parity** — every reference file opens with `## N. `, uses only the five
   classification headings, and no file is a stub.
4. **The forbidden-API guard actually fires** — the behavioural test that matters, because it is
   the reason the table is always-loaded rather than routed. In fresh sessions, ask for code that a
   UWP-trained answer would write with a banned API, and confirm the correct replacement without
   prompting:
   - "show a confirmation dialog from this button handler" → `ContentDialog` **with `XamlRoot` set**,
     not `MessageDialog`;
   - "update the list when the background download finishes" → `DispatcherQueue.TryEnqueue`, not
     `CoreDispatcher.RunAsync`;
   - "let the user pick a file to open" → `Microsoft.Windows.Storage.Pickers`, not
     `Windows.Storage.Pickers` plus HWND interop;
   - "centre the main window on screen" → `AppWindow`, not `ApplicationView`.
5. **The `x:Bind` mode rule fires** — ask for a XAML fragment bound to a view-model property that
   changes at runtime, and confirm an explicit `Mode=OneWay` rather than a bare `{x:Bind Prop}`.
6. **No scope bleed** — grep for the three excluded areas:
   ```bash
   grep -rniE 'msix|wapproj|self-contained|bootstrapper|x:uid|\.resw|resourceloader|apptoast|widgetprovider' skills/csharp-dotnet10-winui3-standards
   ```
   Hits are acceptable only in the scope disclaimer and in §29's AOT caveat. Anything else means
   packaging, localization, or the notification surface leaked in.
7. **No conflict with the base skill** — once both exist, confirm each of the three reversals is a
   labelled override on both sides, never a silent contradiction:
   ```bash
   grep -rn -iE 'async void|configureawait|partial' \
     skills/csharp-dotnet10-winui3-standards skills/csharp-dotnet10-standards
   ```

---

# WinUI reference sources

Researched 2026-08-25. Microsoft Learn URLs are relative to `https://learn.microsoft.com/en-us/`.
Where a source is given as a docs-repo path, the file's existence was verified by enumerating the
`MicrosoftDocs/windows-dev-docs` folder listing on the `docs` branch; the corresponding Learn URL is
that path minus `hub/` and the `.md` extension. Anything not verified is called out in **Open
items** above rather than cited.

## Tier 1 — normative, the skill's spine

| Source | URL |
|---|---|
| WinUI 3 (index) | `windows/apps/winui/winui3/` |
| Build desktop Windows apps with the Windows App SDK | `windows/apps/windows-app-sdk/` |
| **Windows App SDK release channels + release-lifecycle table** | `windows/apps/windows-app-sdk/release-channels` |
| Windows App SDK and supported Windows releases (OS matrix) | `windows/apps/windows-app-sdk/support` |
| Windows App SDK 2.0 release notes (all channels, pivoted) | `windows/apps/windows-app-sdk/release-notes/windows-app-sdk-2-0` |
| Stable channel release notes | `windows/apps/windows-app-sdk/stable-channel` |
| What's new: SDK, WinUI, tools | `windows/apps/whats-new/whats-new-for-developers` |
| Downloads for the Windows App SDK | `windows/apps/windows-app-sdk/downloads` |
| Microsoft Modern Lifecycle (the governing policy) | `lifecycle/policies/modern` |
| Windows versions and SDK overview | `windows/apps/get-started/versioning-overview` |
| Design principles / guidelines overview | `windows/apps/design/design-principles` · `windows/apps/design/guidelines-overview` |
| Windows App SDK features overview | `windows/apps/develop/features-overview` · `windows/apps/develop/user-interface` |

## Tier 2 — official topic guidance, mapped to sections

| § | Topic | Source paths (under `windows/apps/`) |
|---|---|---|
| 3 | MVVM layering | `develop/data-binding/data-binding-and-mvvm` · `develop/data-binding/index` |
| 3, 4, 5 | MVVM tutorial with the Toolkit | `windows/apps/tutorials/winui-mvvm-toolkit/mvvm-implementation` |
| 9, 10, 11 | Binding | `develop/data-binding/data-binding-overview` · `develop/data-binding/data-binding-in-depth` · `develop/data-binding/function-bindings` · `develop/data-binding/bind-to-hierarchical-data-and-create-a-master-details-view` · `develop/platform/xaml/x-bind-markup-extension` |
| 14–18 | XAML surface, layout, theming, materials | `develop/ui/layouts-with-xaml` · `develop/ui/layout-panels` · `develop/ui/alignment-margin-padding` · `develop/ui/theming` · `develop/ui/materials` · `develop/ui/system-backdrops` · `develop/ui/in-app-acrylic` · `develop/ui/shadows` · `develop/ui/visual-tree` · `develop/ui/display-ui-objects` · `develop/ui/xaml-runtime-design-tools` · `develop/ui/controls/` *(folder — enumerate before writing)* · `design/style/` · `design/layout/` · `design/basics/` · `design/motion/` · `design/iconography/` *(folders — enumerate)* |
| 19 | UI thread and dispatch | `develop/dispatcherqueue` |
| 20, 21 | Windowing, title bar, HWND | `develop/ui/windowing-overview` · `develop/ui/manage-app-windows` · `develop/ui/multiple-windows` · `develop/ui/retrieve-hwnd` · `develop/title-bar` |
| 22 | Activation, instancing, lifecycle | `windows-app-sdk/applifecycle/applifecycle` · `…/applifecycle-instancing` · `…/applifecycle-single-instance` · `…/applifecycle-rich-activation` · `…/applifecycle-restart` · `…/applifecycle-power` · `…/background-tasks` · `develop/app-lifecycle-and-system-services` |
| 23 | Navigation | `develop/ui/navigation/navigate-between-two-pages` · `develop/ui/navigation/navigation-history-and-backwards-navigation` |
| 24 | Pickers and interop | `develop/files/using-file-folder-pickers` · `develop/files/pickers-save-file` · `develop/ui/retrieve-hwnd` |
| 25 | Accessibility | `develop/accessibility` · `design/accessibility/accessibility-overview` · `…/accessibility-checklist` · `…/accessibility-testing` · `…/basic-accessibility-information` · `…/keyboard-accessibility` · `…/high-contrast-themes` · `…/accessible-text-requirements` · `…/control-patterns-and-interfaces` · `…/custom-automation-peers` · `…/landmarks-and-headings` · `…/designing-inclusive-software` · `…/system-button-narration` |
| 28 | Performance | `develop/performance/index` · `…/winui-perf` · `…/optimize-xaml-loading` · `…/optimize-xaml-layout` · `…/optimize-gridview-and-listview` · `…/listview-and-gridview-data-optimization` · `…/mvvm-performance-tips` · `…/app-startup-performance` · `…/improve-garbage-collection-performance` · `…/responsive` · `…/disk-memory` · `…/optimize-animations-and-media` · `…/optimize-file-access` · `…/power` · `…/choose-between-tools` |
| 30 | Testing | `develop/testing/index` *(one page only — thin; expect to reason from §3 instead)* |
| 31 | Forbidden UWP-era APIs | `windows-app-sdk/migrate-to-windows-app-sdk/guides/winui3` · `develop/ai-assisted/migrate/uwp-to-winui` · `develop/ai-assisted/migrate/wpf-to-winui` |
| 32 | Platform compatibility analyzer | `dotnet/fundamentals/code-analysis/quality-rules/ca1416` |

### MVVM Toolkit (§4, §5, §6, §13, §32)

All under `https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/`:

`index` · `observableobject` · `observablerecipient` · `observablevalidator` · `relaycommand` ·
`messenger` · `ioc` · `generators/overview` · `generators/observableproperty` ·
`generators/relaycommand` · `generators/errors/mvvmtk0034`

Plus the release that introduced partial-property support, which is the basis for the §4 ruling:
https://devblogs.microsoft.com/dotnet/announcing-the-dotnet-community-toolkit-840/

### Version-specific claims and where they were verified

| Claim | Source |
|---|---|
| No LTS channel; Current vs Maintenance only; 2.0 line Current to 2027-04-29; 1.8 Maintenance to 2026-09-09 | `windows/apps/windows-app-sdk/release-channels` (release-lifecycle table, page dated 2026-08-13) |
| Latest stable 2.4.0, released 2026-08-13 | same page, Stable channel row |
| 2.0 adopted SemVer 2.0.0; package family name tied to major; next SxS major is 3.0.0; **WinUI 3 name unchanged**; `IXamlPredicate` → `IXamlCondition`; `FileSavePicker` no longer creates an empty file; `SystemBackdropElement` added | `windows/apps/windows-app-sdk/release-notes/windows-app-sdk-2-0` |
| `Microsoft.Windows.Storage.Pickers` takes a `WindowId`, needs no HWND init, works elevated, returns paths | `windows/apps/windows-app-sdk/release-notes/windows-app-sdk-1-8` · `windows/apps/develop/files/using-file-folder-pickers` · spec: https://github.com/microsoft/WindowsAppSDK/blob/main/specs/Storage.Pickers/Microsoft.Windows.Storage.Pickers.md |
| Windows 10 1809 (17763) floor; OS support matrix | `windows/apps/windows-app-sdk/support` |
| Native AOT supported since WinAppSDK 1.6 (~50% startup reduction, ~8× package-size reduction in the Contoso Camera sample) | https://blogs.windows.com/windowsdeveloper/2024/09/04/whats-new-in-windows-app-sdk-1-6/ — **current-state caveats unverified, see Open items** |
| `[ObservableProperty]` on partial properties (Toolkit 8.4+, C# 13 partial properties) | https://devblogs.microsoft.com/dotnet/announcing-the-dotnet-community-toolkit-840/ |
| `x:Bind` defaults to `OneTime`, `Binding` defaults to `OneWay` | `windows/apps/develop/platform/xaml/x-bind-markup-extension` |
| The UWP→WinUI 3 change list (`Window.Current`, `CoreDispatcher.RunAsync`, `XamlRoot` on `ContentDialog`/`Popup`, HWND for pickers/`MessageDialog`/`DataTransferManager`, `Window` has no `Resources`/`DataContext`/`Loaded`, no VSM on `Window`, `AcrylicBrush.BackgroundSource` removed, manual `Frame` navigation) | `windows/apps/windows-app-sdk/migrate-to-windows-app-sdk/guides/winui3` |

### Tier 3 — community and reference implementations, non-normative

| Source | URL |
|---|---|
| WinUI 3 Gallery (the reference app; 2.9 is the first build on WinAppSDK 2.0) | https://github.com/microsoft/WinUI-Gallery |
| Template Studio for WinUI (the de facto reference for navigation + DI wiring) | https://github.com/microsoft/TemplateStudio |
| Windows App SDK repo (issues, specs, release discussions) | https://github.com/microsoft/WindowsAppSDK |
| `microsoft-ui-xaml` repo (WinUI issues and release tags) | https://github.com/microsoft/microsoft-ui-xaml |
| Windows Community Toolkit (`CommunityToolkit.WinUI.*`) | https://github.com/CommunityToolkit/Windows |
| `github/awesome-copilot` WinUI 3 instructions + migration skill — **prior-art coverage check only, not citable** | https://github.com/github/awesome-copilot/blob/main/instructions/winui3.instructions.md · https://github.com/github/awesome-copilot/blob/main/skills/winui3-migration-guide/SKILL.md |
| `dotnet/sdk#53387` — .NET 10 cross-arch Native AOT regression via `.wapproj` | https://github.com/dotnet/sdk/issues/53387 |

---

# Roadmap amendments (2026-08-25)

Following the WinUI scope decisions above, two changes to the roadmap recorded earlier in this file:

- **`csharp-dotnet10-winui3-standards` is now planned** (this document). It is a Tier-1-equivalent
  overlay in its own right; the sequencing argument that Tier 1 precedes framework skills does not
  apply to it, because WinUI *is* the framework and the user has an immediate need.
- **New Tier 2 candidate: a WinUI localization and resources skill.** `x:Uid`, `.resw`,
  `Microsoft.Windows.ApplicationModel.Resources.ResourceManager` (MRT Core, *not* the UWP
  `ResourceLoader`), PRI files, `FlowDirection`/RTL, pseudo-localisation. Deliberately excluded
  from the WinUI skill by user decision. Small, self-contained, and currently unowned — nothing
  else in the repo or the roadmap covers it.
- **Confirmed: packaging and deployment belong to `csharp-dotnet10-build-and-project-standards`.**
  MSIX, packaged-with-external-location, unpackaged, framework-dependent vs self-contained, the
  Bootstrapper API, single-project MSIX, and the AOT publish switches all land there rather than in
  the WinUI skill. That skill's open question ("prose only, ship no copyable config?") now has a
  second consumer, so answer it before writing either.
