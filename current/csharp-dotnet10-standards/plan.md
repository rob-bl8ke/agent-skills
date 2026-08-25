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
