#!/usr/bin/env python3
"""Mechanical (deterministic) checks for the my-skills repository.

Emits JSON to stdout: {"repo": ..., "skill_count": N, "findings": [...]}
Each finding: {"check", "severity", "skill", "file", "line", "detail"}

Read-only. Never edits. Safe to run unattended.
Usage: mechanical-checks.py [--repo-root PATH]
"""
import json, os, re, subprocess, sys, itertools
from collections import defaultdict

DESC_LIMIT = 1024
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def repo_root(argv):
    for i, a in enumerate(argv):
        if a == '--repo-root' and i + 1 < len(argv):
            return os.path.abspath(os.path.expanduser(argv[i + 1]))
    # default: two levels up from this script's skill dir
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, '..', '..', '..'))

ROOT = repo_root(sys.argv[1:])
SKILLS_DIR = os.path.join(ROOT, 'current')
F = []

def add(check, severity, detail, skill=None, file=None, line=None):
    F.append({"check": check, "severity": severity, "skill": skill,
              "file": file, "line": line, "detail": detail})

def rel(p):
    return os.path.relpath(p, ROOT)

# ---------- load skills ----------
skills = {}          # name -> {dir, skill_md, frontmatter, body}
dirs = sorted(d for d in os.listdir(SKILLS_DIR)
              if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith('.'))

def split_frontmatter(text):
    if not text.startswith('---'):
        return None, text
    m = re.match(r'^---[ \t]*\n(.*?)\n---[ \t]*\n?', text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]

def scalar(fm, key):
    """Grab a YAML scalar, tolerating quotes and folded continuation lines."""
    m = re.search(r'^%s:[ \t]*(.*)$' % re.escape(key), fm, re.M)
    if not m:
        return None
    val = m.group(1)
    start = m.end()
    for ln in fm[start:].split('\n')[1:]:
        if not ln.strip():
            break
        if re.match(r'^[A-Za-z0-9_-]+:', ln) or re.match(r'^\s*-\s', ln):
            break
        val += ' ' + ln.strip()
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in '"\'':
        val = val[1:-1]
    return val

for d in dirs:
    sdir = os.path.join(SKILLS_DIR, d)
    md = os.path.join(sdir, 'SKILL.md')
    if not os.path.isfile(md):
        contents = os.listdir(sdir)
        add("C13-missing-skill-md", "high" if contents else "low",
            "Directory has no SKILL.md, so it can never load."
            + (" Directory is empty." if not contents else " Contains: %s" % ", ".join(sorted(contents)[:6])),
            skill=d, file=rel(sdir))
        continue
    text = open(md, encoding='utf-8').read()
    fm, body = split_frontmatter(text)
    if fm is None:
        add("C1-frontmatter", "critical",
            "No parseable YAML frontmatter block; the skill will not be registered.",
            skill=d, file=rel(md), line=1)
        continue
    name = scalar(fm, 'name')
    desc = scalar(fm, 'description')
    skills[name or d] = {"dir": sdir, "md": md, "fm": fm, "body": body,
                         "text": text, "declared_name": name, "desc": desc, "dirname": d}

# ---------- C1 frontmatter validity ----------
for key, s in skills.items():
    d, md, name, desc = s['dirname'], s['md'], s['declared_name'], s['desc']
    if not name:
        add("C1-frontmatter", "critical", "Frontmatter has no `name:` field.",
            skill=d, file=rel(md), line=1)
    else:
        if name != d:
            add("C1-name-dir-mismatch", "critical",
                "Frontmatter `name: %s` does not match directory `%s`. Invocation uses the "
                "directory in some hosts and the name in others, so the skill becomes "
                "unreliably addressable." % (name, d), skill=d, file=rel(md), line=1)
        if not NAME_RE.match(name):
            add("C1-name-charset", "high",
                "`name: %s` is not lowercase-alphanumeric-with-single-hyphens." % name,
                skill=d, file=rel(md), line=1)
    if not desc:
        add("C1-no-description", "critical",
            "Frontmatter has no `description:`; the model has nothing to select the skill on.",
            skill=d, file=rel(md), line=1)
    elif len(desc) > DESC_LIMIT:
        add("C1-description-length", "high",
            "Description is %d chars, over the %d limit (excess: %d). It may be truncated or "
            "rejected at load." % (len(desc), DESC_LIMIT, len(desc) - DESC_LIMIT),
            skill=d, file=rel(md), line=1)

# ---------- walk every markdown file ----------
def md_files(sdir):
    for dirpath, _, files in os.walk(sdir):
        for f in files:
            if f.endswith('.md'):
                yield os.path.join(dirpath, f)

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+?)(?:\s+"[^"]*")?\)')
INLINE_CODE = re.compile(r'`[^`]*`')
PLACEHOLDER = re.compile(r'[<>{}*]|\.\.\.')

def strip_code_spans(line):
    """Blank out inline `code` spans. A link inside backticks is being *shown*, not followed."""
    return INLINE_CODE.sub(lambda m: ' ' * len(m.group(0)), line)

def illustrative(path):
    """Files under examples/ or templates/ document generated output, not repo content."""
    parts = os.path.relpath(path, ROOT).split(os.sep)
    return any(seg in ('examples', 'example', 'templates', 'template') for seg in parts)

for key, s in skills.items():
    d = s['dirname']
    for path in md_files(s['dir']):
        try:
            lines = open(path, encoding='utf-8').read().split('\n')
        except Exception:
            continue
        in_fence = False
        for i, ln in enumerate(lines, 1):
            if re.match(r'^\s*(```|~~~)', ln):
                in_fence = not in_fence
                continue
            if in_fence:
                continue                      # code blocks show syntax, they don't link
            for target in LINK_RE.findall(strip_code_spans(ln)):
                if re.match(r'^[a-z][a-z0-9+.-]*://', target) or target.startswith('#') \
                   or target.startswith('mailto:'):
                    continue
                if PLACEHOLDER.search(target):
                    continue                  # e.g. <folder>/<filename>.md
                frag = target.split('#')[0]
                if not frag:
                    continue
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), frag))
                if not os.path.exists(resolved):
                    escapes = not resolved.startswith(ROOT + os.sep)
                    if illustrative(path):
                        add("C2b-broken-link-in-example", "info",
                            "Link target `%s` does not exist. This file sits under an "
                            "examples/templates directory, so the link probably describes "
                            "generated output rather than repo content \u2014 confirm before "
                            "acting." % target, skill=d, file=rel(path), line=i)
                    else:
                        add("C2-broken-link", "high",
                            "Link target `%s` does not exist%s. Progressive disclosure depends on "
                            "these links: a dead one means the detail the skill promises is never "
                            "loaded, with no error." % (
                                target,
                                " and resolves outside the repository (%s)" % resolved
                                if escapes else ""),
                            skill=d, file=rel(path), line=i)
                elif frag.startswith('../..'):
                    add("C3-cross-skill-link", "medium",
                        "Link `%s` reaches outside its own skill directory. Skills are installed "
                        "individually (per `skills-lock.json`), so a sibling-skill path that "
                        "resolves in this repo will dangle wherever the skill is installed alone."
                        % target, skill=d, file=rel(path), line=i)

# ---------- C4 dangling skill references in prose ----------
# Two tiers, deliberately:
#   C4a (high)  - the token is used *as a skill reference* (sits within PROXIMITY chars of the
#                 word "skill") and the line carries no hypothetical/historical marker. These
#                 are actionable: an instruction pointing at a skill that does not exist.
#   C4b (info)  - every other unrecognised hyphenated token, grouped and counted, with no
#                 severity claim. This is the recall net for the semantic pass; expect most of
#                 it to be domain vocabulary, not defects. Do NOT report C4b items as findings
#                 without reading the line first.
real = set(skills.keys()) | set(s['dirname'] for s in skills.values())
TOKEN_RE = re.compile(r'`([a-z0-9]+(?:-[a-z0-9]+)+)`')
PROXIMITY = 45

# Upstream library / module / CLI names that are shaped like skill names but are not skills.
NOT_A_SKILL = {
    'kafka-core', 'outbox-core', 'kafka-core-client', 'set-field', 'set-fields', 'set-body',
    'spring-boot', 'spring-boot-starter-parent', 'spring-boot-maven-plugin',
    'circuit-breaker', 'record-exceptions', 'ignore-exceptions', 'retry-aspect-order',
    'circuit-breaker-aspect-order', 'sliding-window-size', 'sliding-window-type',
    'failure-rate-threshold', 'wait-duration-in-open-state', 'minimum-number-of-calls',
    'permitted-number-of-calls-in-half-open-state', 'application-yml', 'application-yaml',
    'group-id', 'artifact-id', 'auto-offset-reset', 'max-poll-records',
    'enable-auto-commit', 'bootstrap-servers', 'content-type', 'user-agent',
    'read-only', 'write-only', 'three-dot', 'up-to-date', 'per-file', 'end-to-end',
    'argument-hint', 'user-invocable', 'disable-model-invocation', 'allowed-tools',
    'code-first', 'test-first', 'red-green-refactor', 'double-loop',
    'structure-insensitive', 'half-open', 'half-open-state', 'e2e-tests',
    'connection-timeout', 'read-timeout', 'request-timeout', 'follow-redirects',
    'no-cache', 'json-schema', 'pre-commit', 'well-known', 'x-request-id',
    'automatic-transition-from-open-to-half-open-enabled', 'kebab-case', 'snake-case',
    'camel-case', 'lower-case', 'multi-instance', 'single-instance', 'mockoon-env',
}

# Phrasing that marks a name as deliberately non-existent: a future example, a proposal, or a
# correctly-documented retirement. Flagging these is a false positive.
HYPOTHETICAL = re.compile(
    r'tomorrow|replaces the earlier|replaced by|could create|companion skill|hypothetical|'
    r'formerly|retired|used to |no longer|deprecat|supersed|previously|earlier skill|'
    r'future|would be|might be|for example a|imagin', re.I)

seen4 = set()
vocab = defaultdict(list)
for key, s in skills.items():
    d = s['dirname']
    for path in md_files(s['dir']):
        try:
            lines = open(path, encoding='utf-8').read().split('\n')
        except Exception:
            continue
        for i, ln in enumerate(lines, 1):
            for m in TOKEN_RE.finditer(ln):
                tok = m.group(1)
                if tok in real or tok in NOT_A_SKILL or tok == d:
                    continue
                # is the word "skill" close enough to read this as a skill reference?
                lo = max(0, m.start() - PROXIMITY)
                hi = min(len(ln), m.end() + PROXIMITY)
                near_skill = re.search(r'\bskills?\b', ln[lo:hi], re.I)
                if near_skill and not HYPOTHETICAL.search(ln):
                    k = (d, rel(path), i, tok)
                    if k in seen4:
                        continue
                    seen4.add(k)
                    add("C4a-dangling-skill-ref", "high",
                        "Refers to a skill `%s` that does not exist in this repository. An "
                        "instruction that routes to a non-existent skill does not fail loudly "
                        "\u2014 it silently does nothing, so the guidance is simply lost." % tok,
                        skill=d, file=rel(path), line=i)
                else:
                    vocab[tok].append("%s:%d" % (rel(path), i))
if vocab:
    top = sorted(vocab.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:40]
    add("C4b-unrecognised-vocab", "info",
        "%d hyphenated backticked token(s) are not skill names and not in the known-vocabulary "
        "list. This is a RECALL NET for the semantic pass, not a finding list \u2014 most will be "
        "domain vocabulary. Read the cited line before treating any as a defect; if it is real "
        "vocabulary, add it to NOT_A_SKILL in this script. Top by frequency: %s"
        % (len(vocab), "; ".join("`%s` x%d (%s)" % (t, len(l), l[0]) for t, l in top)))

# ---------- C5 CWD-relative skill globs ----------
# Fire only where the glob is actually being *executed*: the line invokes a shell command, or sits
# inside a fenced block (a multi-line command). Prose that names the anti-pattern in order to warn
# against it is not the anti-pattern, and this file itself is full of such prose.
GLOB_RE = re.compile(r'(?<![\w/$}<>.-])skills/\*')
ANCHORED = re.compile(r'(skills-base|\$HOME|~/|\.claude/skills|<[a-z-]+>)')
COMMANDISH = re.compile(r'(?:^|[\s|;&(`$])(?:grep|ls|find|cat|head|sed|awk|for|rg|fd|python3?)\b')
DESCRIPTIVE = re.compile(
    r"do not use|don't use|never use|avoid|anti-pattern|matches nothing|matched nothing|"
    r"no cwd|cwd-relative|fires when|silently|defect|instead of|rather than|bug", re.I)
for key, s_ in skills.items():
    d = s_['dirname']
    for path in md_files(s_['dir']):
        lines = open(path, encoding='utf-8').read().split('\n')
        in_fence = False
        for i, ln in enumerate(lines, 1):
            if re.match(r'^\s*(```|~~~)', ln):
                in_fence = not in_fence
                continue
            if not GLOB_RE.search(ln) or ANCHORED.search(ln):
                continue
            if DESCRIPTIVE.search(ln):
                continue
            if not (in_fence or COMMANDISH.search(ln)):
                continue
            add("C5-cwd-relative-glob", "high",
                "Executes a CWD-relative `skills/*` glob. Skills routinely run with the working "
                "directory set to a consuming service repo rather than the skills base, where "
                "this matches nothing \u2014 and a glob that matches nothing does not error, so "
                "the step appears to succeed having found no input. Anchor it to an absolute "
                "skills-base path resolved from the SKILL.md's own location.",
                skill=d, file=rel(path), line=i)

# ---------- C7 version baseline drift ----------
# Only concrete, repeatedly-stated versions count as a "pinned baseline". Generic forms (3.x,
# 3.5.x) are deliberate, and "Java 8-style" is a comparison, not a target.
VER_RE = re.compile(r'\b(Spring Boot|Java|Resilience4j|JUnit|Testcontainers)\s+v?(\d[\w.]*)(-?)', re.I)
MIN_MENTIONS = 2
versions = defaultdict(lambda: defaultdict(list))
for key, s_ in skills.items():
    for path in md_files(s_['dir']):
        lines = open(path, encoding='utf-8').read().split('\n')
        for i, ln in enumerate(lines, 1):
            for tech, ver, trailing_hyphen in VER_RE.findall(ln):
                if trailing_hyphen:
                    continue                      # "Java 8-style", "Boot 3-era"
                ver = ver.rstrip('.')
                if 'x' in ver.lower() or '.' not in ver:
                    continue                      # 3.x / 3.5.x / bare "3" are generic, not pins
                t = 'Spring Boot' if tech.lower() == 'spring boot' else tech.title()
                versions[t][ver].append("%s:%d" % (rel(path), i))
for tech, vmap in sorted(versions.items()):
    pinned = {v: l for v, l in vmap.items() if len(l) >= MIN_MENTIONS}
    singles = {v: l for v, l in vmap.items() if len(l) < MIN_MENTIONS}
    if len(pinned) > 1:
        ranked = sorted(pinned.items(), key=lambda kv: -len(kv[1]))
        bits = ", ".join("**%s** (%d mentions, e.g. %s)" % (v, len(l), l[0]) for v, l in ranked)
        extra = ("" if not singles else
                 " One-off mentions also present (likely incidental): %s."
                 % ", ".join("%s (%s)" % (v, l[0]) for v, l in sorted(singles.items())))
        add("C7-version-drift", "medium",
            "%s is stated as %d different concrete versions across the skills base: %s.%s "
            "Skills that disagree on the target version generate mutually incompatible code, and "
            "whichever skill the model happens to load decides which version the user gets."
            % (tech, len(pinned), bits, extra))

# ---------- C8 config-key hyphenation drift ----------
KEY_RE = re.compile(r'\b([a-z][a-z0-9]*(?:[.-][a-z0-9]+){2,})\b')
keys = defaultdict(lambda: defaultdict(list))
for key, s in skills.items():
    for path in md_files(s['dir']):
        lines = open(path, encoding='utf-8').read().split('\n')
        for i, ln in enumerate(lines, 1):
            # A key quoted inside a warning ("Using X (no hyphen) | may not bind | use Y") is
            # documenting the wrong form on purpose, not drifting into it.
            if re.search(r"mistake|don't|do not|wrong|incorrect|avoid|deprecat|instead|"
                         r"dead config|no effect|legacy|old library", ln, re.I):
                continue
            for k in KEY_RE.findall(ln):
                if '.' not in k:
                    continue
                # Compare on the first three dot-segments: drift lives in the prefix
                # (resilience4j.circuit-breaker vs resilience4j.circuitbreaker), not the leaf.
                prefix = '.'.join(k.split('.')[:3])
                keys[prefix.replace('-', '')][prefix].append("%s:%d" % (rel(path), i))
for norm, variants in sorted(keys.items()):
    if len(variants) > 1:
        bits = "; ".join("`%s` (%d, e.g. %s)" % (v, len(l), l[0])
                         for v, l in sorted(variants.items(), key=lambda kv: -len(kv[1])))
        add("C8-config-key-drift", "medium",
            "The same configuration key is written with inconsistent hyphenation: %s. Spring's "
            "relaxed binding accepts both, so this is cosmetic at runtime but makes the docs "
            "un-greppable and invites copy-paste of the minority form." % bits)

# ---------- C10 sync-dependent-skills affects coverage ----------
state = os.path.join(SKILLS_DIR, 'sync-dependent-skills', 'state', 'sync-state.json')
if os.path.isfile(state):
    try:
        st = json.load(open(state, encoding='utf-8'))
    except Exception as e:
        add("C10-sync-state", "high", "sync-state.json is not valid JSON: %s" % e,
            skill='sync-dependent-skills', file=rel(state))
        st = None
    if st:
        for repo, cfg in sorted(st.get('repos', {}).items()):
            affects = set(cfg.get('affects', []))
            listed = set(a.split('/')[1] for a in affects if '/' in a)
            for a in sorted(affects):
                if not os.path.exists(os.path.join(ROOT, a)):
                    add("C10-affects-dangling", "high",
                        "`%s` lists `%s` in its `affects` array, but that file does not exist. "
                        "The sync will never be able to update it." % (repo, a),
                        skill='sync-dependent-skills', file=rel(state))
            # which skills actually talk about this library but aren't tracked?
            # Weight by how much a skill actually documents the library. A single passing
            # mention is not ownership; heavy coverage that is untracked is the real defect
            # (this is the exact failure mode that let a retired skill freeze at an old version).
            SUBSTANTIVE, PASSING = 5, 2
            mentions = []
            for key, sk in skills.items():
                d = sk['dirname']
                # Exclude the sync skill (it owns the mapping) and this audit skill (it
                # documents skills, so library names appear as examples, not as guidance).
                if d in listed or d in ('sync-dependent-skills', 'my-skills-audit'):
                    continue
                hits = 0
                for pth in md_files(sk['dir']):
                    hits += len(re.findall(r'\b%s\b' % re.escape(repo),
                                           open(pth, encoding='utf-8').read(), re.I))
                if hits >= PASSING:
                    mentions.append((d, hits))
            mentions.sort(key=lambda kv: -kv[1])
            heavy = [m for m in mentions if m[1] >= SUBSTANTIVE]
            if mentions:
                add("C10-affects-gap", "high" if heavy else "low",
                    "`%s` is documented by %d skill(s) absent from its `affects` array: %s. "
                    "A skill outside the array is never revisited when the upstream library "
                    "changes, so its guidance silently freezes at whatever version was current "
                    "when it was written \u2014 and nothing surfaces the staleness. %s"
                    % (repo, len(mentions),
                       ", ".join("`%s` (%d mentions)" % (d, h) for d, h in mentions),
                       ("Treat the >=%d-mention entries as substantive coverage that should be "
                        "tracked." % SUBSTANTIVE) if heavy else
                       "All are light mentions; likely incidental, verify before adding."),
                    skill='sync-dependent-skills', file=rel(state))

# ---------- C11 invocation flags ----------
for key, s in skills.items():
    fm, d = s['fm'], s['dirname']
    if re.search(r'^disable-model-invocation:[ \t]*true', fm, re.M):
        add("C11-model-invocation-disabled", "info",
            "Has `disable-model-invocation: true`, so the model can never select it — only the "
            "user can, by name. Verify this is still intended, especially if it is now the sole "
            "owner of a capability another (retired) skill used to cover.",
            skill=d, file=rel(s['md']), line=1)

# ---------- C12 description overlap ----------
STOP = set('''a an the and or of to for in on with when use uses using this that it its is are be
was were as at by from into use-when user asks ask should skill skills apply applies code'''.split())
def toks(t):
    return set(w for w in re.findall(r'[a-z][a-z0-9]{2,}', (t or '').lower()) if w not in STOP)
names = sorted(skills)
for a, b in itertools.combinations(names, 2):
    ta, tb = toks(skills[a]['desc']), toks(skills[b]['desc'])
    if not ta or not tb:
        continue
    j = len(ta & tb) / len(ta | tb)
    if j >= 0.30:
        add("C12-description-overlap", "medium",
            "Descriptions of `%s` and `%s` overlap %.0f%% on distinctive terms. When two "
            "descriptions read alike the model's choice between them is effectively arbitrary; "
            "the broader one tends to win regardless of which is correct. Shared terms: %s"
            % (a, b, j * 100, ", ".join(sorted(ta & tb)[:12])))

# ---------- C14 README coverage ----------
readme = os.path.join(ROOT, 'README.md')
if os.path.isfile(readme):
    rt = open(readme, encoding='utf-8').read()
    missing = [d for d in sorted(s['dirname'] for s in skills.values()) if d not in rt]
    if missing:
        add("C14-readme-coverage", "low",
            "README.md does not mention %d of %d skills (%s%s). A reader cannot discover them "
            "without listing the directory." % (
                len(missing), len(skills), ", ".join(missing[:8]),
                ", …" if len(missing) > 8 else ""), file='README.md')
else:
    add("C14-readme-coverage", "low", "No README.md at the repository root.")

# ---------- C15 git hygiene ----------
def git(*a):
    try:
        return subprocess.run(('git', '-C', ROOT) + a, capture_output=True,
                              text=True, timeout=30).stdout
    except Exception:
        return ''
porcelain = git('status', '--porcelain')
untracked_skills, staged_deletes = set(), set()
for ln in porcelain.split('\n'):
    if not ln.strip():
        continue
    code, path = ln[:2], ln[3:].strip().strip('"')
    m = re.match(r'current/([^/]+)/', path + '/')
    if not m:
        continue
    sk = m.group(1)
    if code.strip() == '??':
        untracked_skills.add(sk)
    if code[0] == 'D':
        staged_deletes.add(sk)
if untracked_skills:
    add("C15-untracked-skill", "low",
        "Untracked skill director%s: %s. Untracked content still loads locally but is invisible "
        "to anyone installing from the remote — a skill that works only on this machine."
        % ("y" if len(untracked_skills) == 1 else "ies",
           ", ".join("`%s`" % s for s in sorted(untracked_skills))))
if staged_deletes:
    add("C15-uncommitted-deletion", "info",
        "Staged but uncommitted deletion%s: %s. Consumers keep the retired skill until this is "
        "committed and pushed." % ("" if len(staged_deletes) == 1 else "s",
                                   ", ".join("`%s`" % s for s in sorted(staged_deletes))))

order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
F.sort(key=lambda f: (order.get(f['severity'], 9), f['check'], f.get('skill') or '',
                      f.get('file') or '', f.get('line') or 0))
print(json.dumps({"repo": ROOT, "skill_count": len(skills),
                  "skill_names": sorted(s['dirname'] for s in skills.values()),
                  "findings": F}, indent=2))
