# Design tokens

Everything lives in `src/styles/_tokens.scss`. CSS custom properties are the single
source of truth; there is no Sass colour layer. The only Sass variables in the
codebase are the breakpoints, because `@media` cannot read custom properties.

## The three layers

All three apply to the `<html>` element, so they resolve against each other on the
same node:

```
:root                  light theme + the blue palette default
[data-theme='dark']    dark overrides (surfaces, text, borders, status, shadows)
[data-palette='<id>']  brand palette — applies in BOTH themes
```

`[data-theme]` and `[data-palette]` are both single attribute selectors, so they
carry equal specificity and **source order decides**. The palette layer is emitted
last in `_tokens.scss` and therefore wins for any token both layers declare. This is
deliberate: it is what lets a palette recolour dark mode.

Consequence to respect: **never redeclare a palette-owned token inside `:root` or
`[data-theme='dark']`.** It looks like it works and then the palette switcher
silently stops affecting that token. The light block used to duplicate all nine blue
defaults; they were dead weight and have been removed.

## Surfaces, text, borders

| Token | Light | Dark | Use for |
|---|---|---|---|
| `--bg` | `#f5f5f5` | `#121212` | app background, `<main>` |
| `--surface-1` | `#fafafa` | `#1a1a1a` | page containers, table headers |
| `--surface-2` | `#ffffff` | `#242424` | cards, dialogs, sidenav |
| `--surface-3` | `#f8f9fa` | `#2d2d2d` | code blocks, nested panels, stat tiles |
| `--surface-hover` | `rgba(0,0,0,.04)` | `rgba(255,255,255,.08)` | row/list hover |
| `--surface-selected` | `rgba(var(--primary-rgb),.12)` | `…,.16` | selected row |
| `--text-1` | `rgba(0,0,0,.87)` | `rgba(255,255,255,.92)` | body, headings, values |
| `--text-2` | `rgba(0,0,0,.6)` | `rgba(255,255,255,.7)` | labels, meta, captions |
| `--text-3` | `rgba(0,0,0,.38)` | `rgba(255,255,255,.5)` | disabled, placeholder |
| `--text-inverse` | `#ffffff` | `#121212` | text on a filled brand surface |
| `--border` | `rgba(0,0,0,.12)` | `rgba(255,255,255,.16)` | inputs, controls |
| `--divider` | `rgba(0,0,0,.08)` | `rgba(255,255,255,.1)` | card borders, separators |

The surface ramp is a depth ladder: `--bg` behind `--surface-2` cards, with
`--surface-3` for anything nested *inside* a card. Card borders use `--divider`
(subtler); interactive control borders use `--border`.

## Status triplets

Four states, each three tokens. Alpha backgrounds so they composite correctly over
any surface in either theme.

| State | Light bg / text / border | Dark bg / text / border |
|---|---|---|
| success | `rgba(34,197,94,.15)` / `#16a34a` / `rgba(34,197,94,.5)` | `…,.12` / `#4ade80` / `…,.4` |
| danger | `rgba(239,68,68,.15)` / `#dc2626` / `rgba(239,68,68,.5)` | `…,.12` / `#f87171` / `…,.4` |
| warning | `rgba(245,158,11,.15)` / `#d97706` / `rgba(245,158,11,.5)` | `…,.12` / `#fbbf24` / `…,.4` |
| info | `rgba(59,130,246,.15)` / `#2563eb` / `rgba(59,130,246,.5)` | `…,.12` / `#60a5fa` / `…,.4` |

The pattern is Tailwind hues: 500 for the alpha base, 600 for light text, 400 for
dark text. Dark mode drops alpha `.15 → .12` and `.5 → .4` because a dark surface
needs less tint to read.

Always use all three. `background: var(--success-bg)` with `color: var(--text-1)`
produces a green box with grey text — legible but off-system, and it loses the
colour-coded scanning that makes status columns readable.

## Palettes

Seven, generated from a Sass map. Each emits a 12-token contract:

```
--primary  --primary-rgb  --primary-hover  --primary-active  --primary-contrast
--accent   --accent-contrast
--link     --focus-ring
--chip-accent-bg  --chip-accent-border  --chip-accent-text
```

| id | primary (500) | hover (600) | active (700) | accent (400) |
|---|---|---|---|---|
| blue *(default)* | `#3b82f6` | `#2563eb` | `#1d4ed8` | `#60a5fa` |
| green | `#22c55e` | `#16a34a` | `#15803d` | `#4ade80` |
| teal | `#14b8a6` | `#0d9488` | `#0f766e` | `#2dd4bf` |
| purple | `#a855f7` | `#9333ea` | `#7e22ce` | `#c084fc` |
| pink | `#ec4899` | `#db2777` | `#be185d` | `#f472b6` |
| gold | `#eab308` | `#ca8a04` | `#a16207` | `#fde047` |
| red | `#ef4444` | `#dc2626` | `#b91c1c` | `#f87171` |

**`--primary-rgb` is a bare `r, g, b` triplet, not a colour.** It exists so brand
colour can be composited at low alpha without a second token per opacity:

```scss
&:hover    { background-color: rgba(var(--primary-rgb), 0.08); }
&.selected { background-color: rgba(var(--primary-rgb), 0.12); } // = --surface-selected
```

This is the only sanctioned use of `rgba()` in a component stylesheet.

### The palette / semantic boundary

Palette tokens drive **brand chrome**: buttons, icons, links, focus rings, active
nav, selected rows, accent chips. They must never express meaning. A destructive
action in the green palette still uses `--danger-*`; a success chip in the red
palette still reads green. Breaking this makes the palette switcher change what the
UI *means*, not just how it looks.

### Adding a palette

One map entry in `_tokens.scss` — every derived token is computed, so a palette
cannot be half-defined:

```scss
$palettes: (
  indigo: (
    primary: #6366f1,
    primary-rgb: (99, 102, 241),
    primary-hover: #4f46e5,
    primary-active: #4338ca,
    primary-contrast: #10102b,   // very dark tint of the hue, for text on primary
    accent: #818cf8,             // the 400 stop
    focus-rgb: (129, 140, 248),
    chip-accent-text: #c7d2fe,   // the 200/300 stop
  ),
);
```

Then add it to the `Palette` enum and the `PALETTES` table in
`core/models/palette.model.ts`, and to the `validPalettes` array in the
`index.html` boot script. All three must agree or the palette will not survive a
page reload.

## Other token groups

- **Inputs** — `--input-bg`, `--input-border`, `--input-text`,
  `--input-placeholder`. Material's outline is recoloured to `--input-border` and
  goes `--primary` on hover and focus.
- **Shadows** — only `--shadow-1` (resting) and `--shadow-2` (hover/raised), used as
  a pair. Dark mode raises the opacities rather than changing the geometry.
- **Top bar** — `--topbar-bg` / `--topbar-text` / `--topbar-border`. Note this is
  bright blue `#1976d2` in light but neutral `#1e1e1e` in dark, and is deliberately
  *not* palette-driven.
- **Code / JSON** — `--code-bg`, `--code-border`, `--json-key`, `--json-string`,
  `--json-number`, `--json-boolean`. Light mirrors VS Code light, dark mirrors VS
  Code dark.
- **Chips** — `--chip-bg` / `--chip-text` / `--chip-border` for neutral chips;
  `--chip-accent-*` for brand-tinted ones.

## Adding a token

1. Define it in **both** `:root` and `[data-theme='dark']` in `_tokens.scss`. A
   token defined in only one theme is a dark-mode bug waiting to happen.
2. Name it by role, not appearance — `--surface-selected`, not `--light-blue`.
3. If it is brand-derived, express it from `var(--primary-rgb)` so it follows the
   palette automatically instead of pinning a hue.
4. Never define a token inside a component stylesheet. It will not exist for any
   other component and `var()` failures are silent.

## The theming mechanism

`ThemeService` (`core/services/theme.service.ts`) owns `data-theme`. Three modes —
`light`, `dark`, `system` — persisted to `localStorage['theme-mode']`, with `system`
resolved against `prefers-color-scheme` and re-resolved when the OS flips. It also
keeps `<meta name="color-scheme">` in sync so browser-native scrollbars and form
controls match. `PaletteService` mirrors this for `localStorage['palette']` →
`data-palette`.

**The boot script is mandatory.** An inline IIFE in `index.html` reads both
localStorage keys and sets both attributes before the first paint. Without it every
reload in dark mode flashes white. Because it duplicates the resolution logic, its
`validPalettes` array must be kept in step with the `$palettes` map.
