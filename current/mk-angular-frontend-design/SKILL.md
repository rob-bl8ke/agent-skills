---
name: mk-angular-frontend-design
description: >-
  Design system, styling and presentation rules for Angular + Material SPAs using
  the CSS-custom-property token architecture in src/styles/. Use when writing or
  reviewing any component SCSS or template markup: design tokens, colours, spacing,
  dark mode, brand palettes, theming, layout and page shells, responsive
  breakpoints, Angular Material overrides, status badges, error banners, cards,
  tables, empty states, loading states, focus rings, or accessible markup. Also
  use when bootstrapping a new Angular SPA that should adopt this design system.
---

# Angular Frontend Design

The design language for this codebase. **Architecture and TypeScript rules live in
`AGENTS.md`** — this skill covers only style, layout and presentation.

The system is built on CSS custom properties, not Sass variables. Three cascading
layers, all applied to `<html>`:

```
:root                  light theme defaults
[data-theme='dark']    dark theme overrides
[data-palette='...']   brand palette (7 of them), orthogonal to theme
```

A component that hardcodes a colour opts out of all three at once. That is the
single most common failure mode here — it is how `bulk-publish` shipped a page
that silently ignored dark mode and every palette.

## Hard rules

1. **Colour is always `var(--token)`.** Never a hex, `rgb()`, `rgba()` or a named
   colour in a component stylesheet. If no token fits, add one to
   `src/styles/_tokens.scss` — do not inline it.
2. **Dimensions are px on a 4px grid.** Use 4 / 8 / 12 / 16 / 24 / 32 / 48. 16px is
   the default unit (card padding, gaps, section rhythm); 24px separates page-level
   blocks. Never `rem` — this codebase is px throughout.
3. **A semantic state is a triplet.** `--success-bg` + `--success-text` +
   `--success-border`, all three or none. Same for `danger`, `warning`, `info`.
   Never mix a status background with an unrelated text colour.
4. **Palette tokens never express state.** `--primary*` / `--accent` / `--link` /
   `--focus-ring` / `--chip-accent-*` drive brand chrome only. A success message
   must read as success in all 7 palettes.
5. **Never `mat.get-theme-color()` in a component.** It appears nowhere in
   hand-written code. Use `var(--text-1)`, `var(--primary)`, etc.
6. **Reuse the global pattern, contribute only the delta.** If `.status-badge` or
   `.error-banner` already exists, do not re-declare its anatomy locally — a
   component should add only its own layout (margins, grid placement).
7. **Transitions list properties explicitly.** `0.2s ease` for theme-reactive
   properties (`background-color`, `color`, `border-color`), `0.15s ease` for tight
   interactions (row hover). Never `transition: all`. No `@keyframes`.
8. **Never change `ViewEncapsulation`.** For cross-boundary styling, prefer a global
   rule in `src/styles/`; reach for `::ng-deep` only for markup you inject yourself.
9. **`!important` belongs in `_material-overrides.scss`, not in a component.** A
   few Material shape/padding overrides genuinely need it (see the sidebar active
   state); those must carry a comment saying what they are fighting. `npm run
   audit:design` reports every occurrence so the count cannot quietly grow.
10. **Accessibility is part of the styling job.** A decorative `<mat-icon>` gets
    `aria-hidden="true"` and the label goes on the wrapper. Icon-only buttons get
    `aria-label`. `aria-current` binds to `null` when inactive, never `false`.

## Token quick reference

Enough to write a component without opening a reference file.

| Need | Token |
|---|---|
| App background | `--bg` |
| Page container | `--surface-1` |
| Card / panel | `--surface-2` |
| Code block, nested panel | `--surface-3` |
| Row hover | `--surface-hover` |
| Row selected | `--surface-selected` |
| Primary text | `--text-1` |
| Secondary text, labels, meta | `--text-2` |
| Muted / disabled | `--text-3` |
| Input & control borders | `--border` |
| Card & section dividers | `--divider` |
| Brand fill, active nav, links | `--primary`, `--primary-hover`, `--primary-active` |
| Alpha wash off brand | `rgba(var(--primary-rgb), 0.08)` hover, `0.12` selected |
| Status | `--{success,danger,warning,info}-{bg,text,border}` |
| Resting / raised elevation | `--shadow-1` / `--shadow-2` |
| Focus ring | `--focus-ring` |
| Monospace | `'Roboto Mono', monospace` |

Font sizes: 11 / 12 / 13 / 14 / 16 / 18 / 20 / 24px. Weights: **400, 500, 600 only**
— never 700. Radii: 4px (inputs, code), 6px (banners), 8px (cards, badges, tiles).

## Decision checklist

**Styling a new component**
`<name>.component.scss` beside the `.ts`, referenced with singular `styleUrl`.
Add `:host` only when the component needs a layout contract (`display: block`).
One block selector per concern, nested 1–2 levels deep, state as `&.success` /
`&:hover`. Semantic single-dash class names (`.stat-item`, `.card-header`) — this is
BEM-lite, not utility classes. Reserve `--` modifiers for variant families.

**Showing a status** → `references/patterns.md` § Status badge. Use the global
`.status-badge` + `--success`/`--error`/`--warning`/`--info`/`--pending` modifier.
Do not invent a new status treatment.

**Reporting an error** → global `.error-banner` with `role="alert"`. Use
`.error-banner--warning` for degraded-but-recoverable conditions.

**Building a page** → `references/layout.md`. Default to
`grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`, which is responsive
with no media query. Only reach for a breakpoint when the layout genuinely breaks.

**Needing a media query** → `@use 'breakpoints' as bp;` then
`@include bp.below(bp.$bp-lg) { ... }`. Never a bare `@media (max-width: 800px)`.
For *behavioural* changes (sidenav mode) use the CDK `BreakpointObserver` instead.

**Fighting Material** → `references/material.md`. Check whether
`_material-overrides.scss` already handles it globally before adding anything local.

**Adding a token or palette** → `references/tokens.md`.

## Review checklist

Run before calling any styling work done:

- [ ] `grep -nE '#[0-9a-fA-F]{3,8}|rgba?\(' ` on the component SCSS returns nothing
      (or only `rgba(var(--primary-rgb), …)`).
- [ ] No `rem`, no `transition: all`. Any `!important` carries a comment saying
      what Material behaviour it is overriding.
- [ ] Every `var(--…)` used is actually defined in `_tokens.scss`. An undefined
      token fails silently — this exact bug hid a missing selected-row background
      in `schema-list` for months.
- [ ] Renders correctly in **light and dark**, and in at least two palettes.
- [ ] Decorative icons `aria-hidden`; icon-only buttons labelled; interactive
      elements show the `--focus-ring` on `:focus-visible`.
- [ ] `npm run audit:design` passes.

## Bootstrapping a new Angular SPA

`assets/` is a working copy of the system, app-agnostic.

1. Copy `assets/styles/` → `src/styles/` and point `angular.json` at
   `src/styles.scss`, adding:
   ```json
   "stylePreprocessorOptions": { "includePaths": ["src/styles"] }
   ```
   so components can `@use 'breakpoints' as bp;` without relative paths.
2. Copy `assets/theming/` → `src/app/core/` (services + models) and
   `src/app/shared/components/` (the toggle and selector).
3. Paste `assets/theme-boot.html` into `<head>` **before** any stylesheet. Without
   it the app flashes light on every dark-mode reload — the script sets
   `data-theme` and `data-palette` before first paint.
4. Add the Google Fonts links for `Roboto:wght@300;400;500`,
   `Roboto+Mono:wght@400;500` and `Material+Icons`, plus
   `<meta name="color-scheme" content="light dark">`.
5. Copy `assets/audit-design-tokens.sh` → `scripts/` and wire an `audit:design`
   npm script. Do this on day one; the rules decay without it.

To restyle for a different brand, edit the `$palettes` map in `_tokens.scss`. The
semantic status triplets are deliberately brand-independent — leave them alone.

## References

- `references/tokens.md` — full token contract, both themes, the palette map, how
  to add tokens and palettes, the theming mechanism.
- `references/patterns.md` — copy-paste catalogue: status badge, banners, cards,
  tables, metadata lists, empty and loading states, snackbars, sidebar nav.
- `references/layout.md` — page shell, flex vs grid, responsive idioms, breakpoints.
- `references/material.md` — Material theming strategy, override policy, button and
  form-field conventions, the `!important` rule.
