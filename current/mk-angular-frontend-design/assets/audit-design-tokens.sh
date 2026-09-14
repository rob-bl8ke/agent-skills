#!/usr/bin/env bash
#
# Design token audit.
#
# Enforces the rules in .claude/skills/angular-frontend-design/SKILL.md that can be
# checked mechanically. Documentation nothing verifies decays - this is the check
# that would have caught both the untokenized bulk-publish page and the
# `var(--surface-selected)` reference that was never defined.
#
# Usage: npm run audit:design
#
# Exits non-zero on any ERROR. `!important` in a component stylesheet is reported
# as a tracked warning instead: a few Material shape overrides legitimately need
# it, so it is kept visible rather than blocking.

set -uo pipefail
cd "$(dirname "$0")/.."

python3 - "$@" <<'PY'
import os
import re
import sys

TOKEN_DIR = 'src/styles'
APP_DIR = 'src/app'

RED = '\033[0;31m'
YELLOW = '\033[0;33m'
GREEN = '\033[0;32m'
DIM = '\033[2m'
NC = '\033[0m'

findings = []

# `!important` in a component stylesheet is tracked but non-blocking: a handful of
# Material shape/padding overrides legitimately need it (see the sidebar active
# state). It stays visible here so the count cannot quietly grow, and so the two
# known-heavy legacy files stay on the record.
WARN_ONLY = {'important'}

LEGACY_IMPORTANT = {
    'src/app/features/schemas/components/schema-list/schema-list.component.scss',
    'src/app/layout/sidebar/sidebar.component.scss',
}


def report(path, lineno, rule, detail):
    findings.append((path, lineno, rule, detail))


def strip_comments(text):
    """Remove // line comments and /* */ blocks so they don't trip the scanners."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return '\n'.join(re.sub(r'//.*$', '', line) for line in text.split('\n'))


def component_style_files():
    """Component SCSS, plus inline `styles:` blocks in component TS."""
    for root, _dirs, files in os.walk(APP_DIR):
        for f in sorted(files):
            if f.endswith('.scss'):
                yield os.path.join(root, f), None
            elif f.endswith('.ts'):
                path = os.path.join(root, f)
                src = open(path).read()
                for m in re.finditer(r'styles:\s*`(.*?)`', src, flags=re.S):
                    yield path, (m.group(1), src[:m.start()].count('\n') + 1)


def iter_blocks():
    for path, inline in component_style_files():
        if inline is None:
            yield path, open(path).read(), 0
        else:
            body, offset = inline
            yield path, body, offset


# ---------------------------------------------------------------------------
# 1. Literal colours in component styles (colour must come from a token)
# ---------------------------------------------------------------------------
HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC = re.compile(r'\brgba?\(')
NAMED = re.compile(r':\s*(white|black|red|green|blue|gray|grey|orange|yellow)\s*[;!]')

for path, body, offset in iter_blocks():
    clean = strip_comments(body)
    for i, line in enumerate(clean.split('\n'), start=1 + offset):
        # rgba(var(--primary-rgb), a) is the one sanctioned colour function
        probe = re.sub(r'rgba?\(\s*var\(--[a-z0-9-]+\)\s*,[^)]*\)', '', line)
        if HEX.search(probe):
            report(path, i, 'literal-colour', HEX.search(probe).group(0))
        elif FUNC.search(probe):
            report(path, i, 'literal-colour', probe.strip()[:70])
        elif NAMED.search(probe):
            report(path, i, 'literal-colour', NAMED.search(probe).group(1))

# ---------------------------------------------------------------------------
# 2. var(--x) references with no definition anywhere in src/styles
#    These fail SILENTLY in the browser - the property is simply dropped.
# ---------------------------------------------------------------------------
defined = set()
for root, _dirs, files in os.walk(TOKEN_DIR):
    for f in files:
        if f.endswith('.scss'):
            text = open(os.path.join(root, f)).read()
            defined.update(re.findall(r'^\s*(--[a-z0-9-]+)\s*:', text, flags=re.M))
            # tokens emitted from a mixin body
            defined.update(re.findall(r'(--[a-z0-9-]+)\s*:\s*#\{', text))

MDC_PREFIXES = ('--mdc-', '--mat-')
for path, body, offset in iter_blocks():
    clean = strip_comments(body)
    for i, line in enumerate(clean.split('\n'), start=1 + offset):
        for tok in re.findall(r'var\((--[a-z0-9-]+)', line):
            if tok.startswith(MDC_PREFIXES):
                continue  # Material's own properties, defined by the framework
            if tok not in defined:
                report(path, i, 'undefined-token', tok)

# ---------------------------------------------------------------------------
# 3. Rules that only ever produce off-system output
# ---------------------------------------------------------------------------
for path, body, offset in iter_blocks():
    clean = strip_comments(body)
    for i, line in enumerate(clean.split('\n'), start=1 + offset):
        if 'mat.get-theme-color' in line:
            report(path, i, 'mat-get-theme-color', line.strip()[:70])
        if re.search(r':\s*[\d.]+rem\b', line) or re.search(r'\s[\d.]+rem\b', line):
            report(path, i, 'rem-unit', line.strip()[:70])
        if '!important' in line:
            report(path, i, 'important', line.strip()[:70])
        if re.search(r'transition:\s*all\b', line):
            report(path, i, 'transition-all', line.strip()[:70])

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
RULES = {
    'literal-colour': 'Hardcoded colour - use a var(--token) from src/styles/_tokens.scss',
    'undefined-token': 'var() references a token that is not defined - fails silently',
    'mat-get-theme-color': 'Use var(--text-1) / var(--primary) instead of the Sass theme API',
    'rem-unit': 'This codebase is px on a 4px grid - no rem',
    'important': 'Prefer _material-overrides.scss or an --mdc-*/--mat-* property; comment any that remain',
    'transition-all': 'List transitioned properties explicitly (0.2s theme / 0.15s interaction)',
}

errors = [f for f in findings if f[2] not in WARN_ONLY]
warnings = [f for f in findings if f[2] in WARN_ONLY]


def group(items):
    out = {}
    for path, lineno, rule, detail in items:
        out.setdefault(rule, []).append((path, lineno, detail))
    return out


def emit(title, colour, items, limit=15):
    for rule, hits in sorted(group(items).items(), key=lambda kv: -len(kv[1])):
        print(f'{colour}{rule}{NC} ({len(hits)})')
        print(f'  {DIM}{RULES[rule]}{NC}')
        for path, lineno, detail in hits[:limit]:
            print(f'    {path}:{lineno}  {DIM}{detail}{NC}')
        if len(hits) > limit:
            print(f'    {DIM}... and {len(hits) - limit} more{NC}')
        print()


if warnings:
    legacy = [w for w in warnings if w[0] in LEGACY_IMPORTANT]
    fresh = [w for w in warnings if w[0] not in LEGACY_IMPORTANT]
    print(f'{YELLOW}! {len(warnings)} tracked warning(s){NC} '
          f'{DIM}({len(legacy)} in known legacy files, {len(fresh)} elsewhere){NC}\n')
    emit('warnings', YELLOW, fresh, limit=20)
    if legacy:
        counts = {}
        for path, _l, _r, _d in legacy:
            counts[path] = counts.get(path, 0) + 1
        print(f'{YELLOW}important{NC} {DIM}- known legacy debt, not counted as new{NC}')
        for path, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f'    {path}  {DIM}({n}){NC}')
        print()

if errors:
    print(f'{RED}✗ design token audit found {len(errors)} error(s){NC}\n')
    emit('errors', RED, errors)
    print(f'{DIM}See .claude/skills/angular-frontend-design/SKILL.md{NC}')
    sys.exit(1)

print(f'{GREEN}✓{NC} design token audit passed'
      + (f' {DIM}({len(warnings)} tracked warning(s)){NC}' if warnings else ''))
sys.exit(0)
PY
