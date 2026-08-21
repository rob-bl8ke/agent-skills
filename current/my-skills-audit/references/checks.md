# Mechanical checks

Every check in `scripts/mechanical-checks.py`, what it proves, and where it is blind. Read this
before trusting or extending the script.

Invocation:

```
python3 <repo>/current/my-skills-audit/scripts/mechanical-checks.py --repo-root <repo>
```

`--repo-root` defaults to three levels up from the script, which is correct when the skill sits in
its normal place. Pass it explicitly in scheduled runs anyway — cheap insurance against a symlinked
install resolving somewhere unexpected.

## Frontmatter

| ID | Fires when | Severity | Why it matters |
|---|---|---|---|
| `C1-frontmatter` | No parseable `---` block | critical | The skill is never registered. Invisible failure: no error, the skill just isn't there. |
| `C1-name-dir-mismatch` | `name:` != directory name | critical | Hosts differ on which they address the skill by, so it becomes unreliably invocable. |
| `C1-name-charset` | Not lowercase alphanumeric + single hyphens | high | Rejected or normalised unpredictably. Note colons are invalid — you cannot self-namespace a skill this way. |
| `C1-no-description` | No `description:` | critical | The model has nothing to select on, so the skill is effectively user-invocable only. |
| `C1-description-length` | Description > 1024 chars | high | Risk of truncation at load; a truncated description changes selection behaviour silently. |

Frontmatter parsing tolerates quoted scalars and folded continuation lines. It is deliberately
not a full YAML parse — it reports what it cannot read rather than guessing.

## Links and references

| ID | Fires when | Severity |
|---|---|---|
| `C2-broken-link` | Relative link target missing | high |
| `C2b-broken-link-in-example` | Same, but under `examples/`/`templates/` | info |
| `C3-cross-skill-link` | Link starts `../..`, escaping its own skill | medium |

`C2` skips, by design: fenced code blocks, inline-code spans, and targets containing
`< > { } * ...`. All three were false-positive sources — a link inside backticks is being *shown*,
not followed, and `<folder>/<filename>.md` is a placeholder. `C2b` is separated because files under
`examples/` typically describe generated output, so a "missing" target is expected there.

`C3` matters because skills install individually (see any consumer's `skills-lock.json`). A
`../../other-skill/references/x.md` link resolves in this monorepo and dangles everywhere the skill
is installed alone. Fix by inlining the needed content or naming the other skill in prose instead
of linking to its files.

## Skill-to-skill references

| ID | Fires when | Severity |
|---|---|---|
| `C4a-dangling-skill-ref` | A backticked hyphenated token near the word "skill" names no existing skill | high |
| `C4b-unrecognised-vocab` | Any other unclassified hyphenated token | info (**not a finding**) |

`C4a` gates on two conditions to stay quiet: the token must sit within 45 characters of the word
"skill"/"skills", and the line must not carry a hypothetical/historical marker (`tomorrow`,
`replaces the earlier`, `could create`, `retired`, `superseded`, …). Both gates exist because the
ungated version produced false positives on every one of these real lines:

- `` `java-25-standards` tomorrow `` — a deliberate future example
- `` `set-field` `` — a CLI subcommand
- ``Replaces the earlier skills: `kafka-core-client` `` — correctly documented retirement
- `` `kafka-core` `` — an upstream library, not a skill

**Blind spot:** unbackticked prose references ("apply the initial testing framework skill") are
invisible to `C4a`. That is semantic check `S6`, and it must be done by reading.

`C4b` exists so tightening `C4a` did not cost recall. It is a review queue, not a finding list.
When you confirm a token is legitimate vocabulary, add it to `NOT_A_SKILL` in the script; the queue
shrinks and future runs get quieter.

## Silent-failure bugs

| ID | Fires when | Severity |
|---|---|---|
| `C5-cwd-relative-glob` | A `skills/*` glob with no `<skills-base>`/`$HOME`/`~/`/`.claude/skills` anchor | high |

The motivating defect: a skill discovered sibling skills with `grep -l '^name:.*-standards'
skills/*/SKILL.md`. Run from a consuming service repo — its normal case — the glob matched nothing,
and the skill continued into its sub-agents presenting a Standards review that had loaded no
standards. High severity is about the silence, not the path.

## Consistency

| ID | Fires when | Severity | Tuning |
|---|---|---|---|
| `C7-version-drift` | One technology stated at 2+ concrete versions | medium | Ignores `x` forms (`3.x`), trailing-hyphen comparisons (`Java 8-style`), and single mentions |
| `C8-config-key-drift` | One config key prefix written with inconsistent hyphenation | medium | Compares first three dot-segments, hyphens stripped |
| `C12-description-overlap` | Two descriptions ≥30% Jaccard on distinctive terms | medium | Stopword-filtered |

`C8`'s canonical case is `resilience4j.circuit-breaker` vs `resilience4j.circuitbreaker`. Spring's
relaxed binding accepts both, so runtime is unaffected — the cost is un-greppable docs and
copy-paste of the minority form. Compare on the prefix, not the whole key, or leaf differences mask
the drift.

`C12` matters because descriptions are the only thing the model selects on. When two read alike the
choice is effectively arbitrary, and the broader description tends to win regardless of which skill
is correct. Overlap is a prompt to make the *boundary* explicit in both, not automatically to merge.

## Upstream tracking

| ID | Fires when | Severity |
|---|---|---|
| `C10-sync-state` | `sync-state.json` is unparseable | high |
| `C10-affects-dangling` | An `affects` path does not exist | high |
| `C10-affects-gap` | A skill documents an upstream repo but is absent from its `affects` array | high (≥5 mentions) / low (2–4) |

`C10-affects-gap` encodes a root cause worth remembering: a skill omitted from `affects` is never
revisited when its upstream library changes, so its guidance freezes at whatever was current when
written — and nothing surfaces the staleness. That is precisely how a skill came to mandate
hand-writing classes that the library had since absorbed. Mention count is the proxy for
substantive coverage; single mentions are dropped as incidental.

## Hygiene

| ID | Fires when | Severity |
|---|---|---|
| `C11-model-invocation-disabled` | `disable-model-invocation: true` | info |
| `C13-missing-skill-md` | Directory with no `SKILL.md` | high (non-empty) / low (empty) |
| `C14-readme-coverage` | Skills unmentioned in root `README.md` | low |
| `C15-untracked-skill` | Untracked skill directory | low |
| `C15-uncommitted-deletion` | Staged-but-uncommitted skill deletion | info |

`C11` is info, not a defect — the flag is often deliberate. It is surfaced because it becomes a
problem in one specific situation: the skill is now the *sole* owner of a capability a retired skill
used to cover, so the model can no longer reach that capability at all. Check ownership, not the
flag.

`C15-untracked-skill` is low but real: untracked content loads locally and is invisible to anyone
installing from the remote, producing a skill that works only on the author's machine.

## Adding a check

1. Add the logic with a new `C<n>` ID and an `add(...)` call whose `detail` states the *mechanism*.
2. Build a fixture repo that makes it fire. Confirm it fires.
3. Run it against the real repo and read every hit. Anything that is not a genuine defect means the
   check needs narrowing — not the output filtering.
4. Document it here, including its blind spots.

Step 2 is not optional. A check that never fires is indistinguishable from a clean result and reads
as coverage you do not have.
