# Angular Material strategy

The governing idea: **Material supplies structure, the design tokens supply every
colour.** Material's own palette is essentially cosmetic here — it exists so
components have sane geometry, density and interaction states, and then a global
override layer re-skins all of it with `var(--*)`.

Understanding this split is what stops you fighting the framework.

## Theme definition

`src/styles/_material-theme.scss` uses the M3 API with prebuilt palettes — there are
no custom Material palettes, because colour comes from the token layer:

```scss
@use '@angular/material' as mat;

$light-theme: mat.define-theme((
  color: (theme-type: light, primary: mat.$azure-palette, tertiary: mat.$blue-palette),
  density: (scale: 0),
));

$dark-theme: mat.define-theme((
  color: (theme-type: dark, primary: mat.$azure-palette, tertiary: mat.$blue-palette),
  density: (scale: 0),
));
```

Applied with the all-themes / colors-only split, which is the correct pattern — it
emits structural CSS once and only re-emits colour for dark:

```scss
html                     { @include mat.all-component-themes($light-theme); }
html[data-theme='dark']  { @include mat.all-component-colors($dark-theme); }
```

Using `all-component-themes` twice would double every structural rule.

No typography config is passed, so Material typography stays at its defaults. Fonts
come from `body { font-family: Roboto, 'Helvetica Neue', sans-serif; }`.

## The override layer

`src/styles/_material-overrides.scss` re-skins 15+ Material components with tokens:
`mat-card`, dialogs, drawers, tables, paginators, form fields, select panels,
buttons, menus, chips, lists, expansion panels, progress bars, dividers.

**Before styling a Material component locally, check whether this file already
handles it.** It usually does, and a local rule then either duplicates it or fights
it. `mat-card` already has `--surface-2`, `--shadow-1` and a `--divider` border —
restating them in a component is pure noise.

### Known coverage gaps

These components are **not** in the override layer, so they render in Material's own
azure palette and do **not** follow `data-palette`:

`mat-checkbox` · `mat-radio-button` · `mat-slide-toggle` · `mat-datepicker` ·
`mat-tab-group`

A purple-palette page still shows blue checkboxes. If you need one of these to track
the palette, add a rule to `_material-overrides.scss` using its MDC custom
properties — for example:

```scss
.mat-mdc-checkbox {
  --mdc-checkbox-selected-icon-color: var(--primary);
  --mdc-checkbox-selected-hover-icon-color: var(--primary-hover);
  --mdc-checkbox-selected-focus-icon-color: var(--primary);
}
```

Do not patch it in a single component — that fixes one page and leaves the rest
inconsistent.

## The `!important` policy

- **Belongs in `_material-overrides.scss`.** MDC ships high-specificity selectors
  and its own custom properties; overriding them from a single global class
  genuinely requires it.
- **In a component stylesheet, treat it as a smell.** A small number are legitimate
  — overriding MDC's shape or internal padding, as the sidebar's
  `border-radius: 0 !important` does. Those must carry a comment naming what they
  fight. Anything else means the wrong element or the wrong layer.
- `npm run audit:design` lists every occurrence as a tracked warning, with
  `schema-list.component.scss` (74) and `sidebar.component.scss` (2) recorded as
  known legacy debt so new additions stand out.

Where you must reach past Material, prefer its **custom properties** over brute
force — they are designed as the extension point and need no `!important`:

```scss
.snackbar-success {
  --mdc-snackbar-container-color: #2e7d32;
  --mdc-snackbar-supporting-text-color: #fff;
  --mat-snack-bar-button-color: #fff;
}
```

### Anti-pattern to avoid

`schema-list.component.scss` carries **74 `!important` declarations**, suppresses
ripples (`.mat-ripple-element { display: none !important }`), zeroes state-layer
pseudo-elements and hides focus indicators. It also exceeds the 4kB
`anyComponentStyle` budget.

It is the clearest example of what fighting Material costs: it removes focus
indicators that the stated WCAG AA commitment requires, and it is unmaintainable
against any Material upgrade. **Do not imitate it, and do not extend it.** If a
Material component needs this much force, either use a plainer element or add one
targeted rule to the global override layer.

## Component conventions

### Form fields — `appearance="outline"`, universally

Every `mat-form-field` in the codebase uses it. Never mix appearances.

```html
<mat-form-field appearance="outline" class="full-width">
  <mat-label>Topic</mat-label>
  <input matInput [formControl]="topicControl" placeholder="Select a topic" />
  <mat-hint>The Kafka topic to publish to</mat-hint>
  @if (topicControl.hasError('required')) {
    <mat-error>Topic is required</mat-error>
  }
</mat-form-field>
```

Outline borders are recoloured to `--input-border` globally and go `--primary` on
both hover and focus.

### Buttons — a three-tier hierarchy

| Variant | Use for |
|---|---|
| `mat-flat-button color="primary"` | the **one** primary action on the view |
| `mat-stroked-button` | secondary actions |
| `mat-button` | tertiary / inline (Retry, View All) |
| `mat-icon-button` | table row actions, toolbar controls |

One flat button per view. Icons always precede the label inside a button:

```html
<button mat-flat-button color="primary" [disabled]="!canPublish()">
  <mat-icon>send</mat-icon>
  {{ publishing() ? 'Publishing...' : 'Publish Event' }}
</button>
```

Every `mat-icon-button` needs an `aria-label`, and normally a `matTooltip` with
matching text:

```html
<button mat-icon-button (click)="viewDetails.emit(row)"
        matTooltip="View details" aria-label="View message details">
  <mat-icon>visibility</mat-icon>
</button>
```

Globally: text/outlined buttons get `--primary` text and `--surface-hover` on hover;
flat/raised/fab get `--primary` going `--primary-hover`; icon buttons go `--text-2`
→ `--primary` with an `rgba(var(--primary-rgb), 0.08)` wash.

### Icons — the sizing triplet

Material Icons is a **ligature font**, so `font-size` controls the glyph but the box
is sized by `width`/`height`. Set all three to the same value or the icon will not
centre and will not reserve correct space:

```scss
mat-icon {
  font-size: 18px;
  width: 18px;
  height: 18px;
}
```

Sizes in use: 16px (in-chip), 18px (in badges, inline), 20px (stat tiles), 24px
(Material default), 48px (empty states).

### Dialogs

Standard Material anatomy, with `align="end"` actions, cancel as `mat-button`,
confirm as `mat-flat-button` carrying `cdkFocusInitial`:

```html
<h2 mat-dialog-title>{{ data.title }}</h2>
<mat-dialog-content>
  <p>{{ data.message }}</p>
</mat-dialog-content>
<mat-dialog-actions align="end">
  <button mat-button mat-dialog-close>{{ data.cancelText || 'Cancel' }}</button>
  <button mat-flat-button color="primary" [mat-dialog-close]="true" cdkFocusInitial>
    {{ data.confirmText || 'Confirm' }}
  </button>
</mat-dialog-actions>
```

Reuse `ConfirmationDialogComponent` for yes/no prompts rather than writing another —
it takes `{ title, message, confirmText?, cancelText?, confirmColor? }` and resolves
`true`/`false`. Focus trap and restore come from the CDK; don't hand-roll them.

Any inline `styles:` block in a dialog component is still a component stylesheet —
the token rules apply there too.

## Animations

`provideAnimationsAsync()` is wired in `app.config.ts` purely to power Material's
built-in motion (ripples, sidenav slide, expansion, menus, snackbar). There are **no
Angular animation triggers and no `@keyframes`** anywhere, and none should be added
without a clear reason.

All bespoke motion is CSS transitions on a two-value scale:

- **`0.2s ease`** — theme-reactive properties. This is what makes the light/dark and
  palette switch animate rather than snap. Always list the properties:
  ```scss
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
  ```
- **`0.15s ease`** — tighter, higher-frequency interactions (row hover, checkbox
  scale).

Never `transition: all` — it catches layout properties and causes jank on reflow.

`_a11y.scss` neutralises all of it under `prefers-reduced-motion: reduce`, and is
loaded last so it wins. Any new transition is covered automatically.

## Checking a Material override

1. Is it already in `_material-overrides.scss`? Usually yes.
2. Can it be done with a Material custom property (`--mdc-*` / `--mat-*`)?
3. Does it belong globally (every instance) or locally (this view only)? Global
   changes go in the override layer, not into one component's stylesheet.
4. If the only route is `!important` in a component — stop. That is the signal that
   the wrong element or the wrong layer is being used.
