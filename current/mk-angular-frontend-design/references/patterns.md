# UI pattern catalogue

The shared presentational vocabulary. Everything here is defined globally in
`src/styles/_patterns.scss` — **consume the class, don't re-declare its anatomy.**
A component contributes only its own layout delta (margin, grid placement).

---

## Status badge

The signature component: a 28px rounded-square icon chip. Used identically in
message tables, detail dialogs, dashboards and publish results.

```html
<span
  class="status-badge"
  [class.status-badge--success]="message.status === 'SUCCESS'"
  [class.status-badge--error]="message.status === 'FAILED'"
  [attr.aria-label]="message.status === 'SUCCESS' ? 'Success' : 'Failed'"
  [title]="message.status === 'SUCCESS' ? 'Success' : 'Failed'"
>
  <mat-icon aria-hidden="true">
    {{ message.status === 'SUCCESS' ? 'check' : 'close' }}
  </mat-icon>
</span>
```

Modifiers: `--success` `--error` `--failed` `--warning` `--info` `--pending`.
Each applies its status triplet; `--pending` uses `--chip-bg` / `--text-2`.

**The accessibility contract is part of the pattern.** `aria-label` *and* `title` on
the wrapper, `aria-hidden="true"` on the icon. The icon glyph alone conveys the
state, so without the label a screen reader announces nothing.

Note `mat-icon` inside carries `display: block` — a ligature font sits on the text
baseline and would otherwise be a pixel or two off centre inside the 28px box.

Usually paired with a text label:

```scss
.status-text {
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

Scaling up for `mat-card-avatar`: 40px box, 24px icon.

---

## Error banner

```html
<div class="error-banner" role="alert">
  <mat-icon aria-hidden="true">error_outline</mat-icon>
  <span>{{ service.error() }}</span>
  <button mat-button color="primary" (click)="retry()">
    <mat-icon>refresh</mat-icon> Retry
  </button>
</div>
```

The global rule gives it `--danger-*`, `gap: 12px`, `border-radius: 6px` and
`span { flex: 1 }` so a trailing action button sits flush right. In the component,
add only spacing:

```scss
.error-banner {
  margin-bottom: 24px;
}
```

`.error-banner--warning` is the amber variant, for degraded-but-recoverable states
(API unreachable, stale data) rather than outright failures. It also shrinks the icon
to 18px and the text to 14px:

```html
<div class="error-banner error-banner--warning" role="alert">
  <mat-icon aria-hidden="true">cloud_off</mat-icon>
  <span>Unable to connect to API server</span>
  <button mat-button color="primary" (click)="retryAll()">Retry</button>
</div>
```

`role="alert"` is required — it makes the message announce itself when it appears.

---

## Status pills

For chip-style text labels rather than icon badges: `.status-success`,
`.status-error` / `.status-failed`, `.status-warning`, `.status-info`, plus bare
`.success` / `.error` / `.warning` / `.info` aliases. Each applies its triplet.

These are the one place `!important` is used outside the Material override layer,
because they are frequently applied to a `mat-chip` whose own MDC styles would
otherwise win. Prefer applying them from a class-returning method:

```ts
protected statusClass(status: string): string {
  return status === 'SUCCESS' ? 'status-success' : 'status-error';
}
```

---

## Cards

`<mat-card>` is re-skinned globally — `--surface-2`, `--shadow-1`, and a
`1px solid var(--divider)` border. Do not restate any of that.

The recurring internal anatomy is hand-rolled rather than Material's, so a card can
host a flush list or table:

```scss
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--divider);
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-2);
}

.card-body {
  padding: 16px;
}
```

When the card wraps a table or list, kill Material's own padding so rows reach the
edge:

```scss
mat-card-content {
  padding: 0;
}
```

**Status accent:** result cards take a 4px left border rather than a tinted
background, so the content stays on a neutral surface:

```scss
.result-card {
  border-left: 4px solid var(--success-border);
}
```

**Stat tile**, the hover-elevation pattern:

```scss
.stat-item {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 12px 16px;
  background: var(--surface-2);
  border: 1px solid var(--divider);
  border-radius: 8px;
  box-shadow: var(--shadow-1);
  transition: box-shadow 0.2s, background-color 0.2s, border-color 0.2s;

  &:hover {
    box-shadow: var(--shadow-2);
  }

  .stat-value {
    font-size: 20px;
    font-weight: 600;
    line-height: 1;
    color: var(--text-1);
  }

  &.success {
    mat-icon,
    .stat-value {
      color: var(--success-text);
    }
  }
}
```

---

## Tables

`mat-table` with one `ng-container matColumnDef` per column, re-skinned globally to a
transparent background with `--surface-1` headers, `--surface-hover` row hover and
`--divider` cell borders. Always wrap in a scroll container and follow with a
paginator:

```html
<div class="table-container">
  <table mat-table [dataSource]="messages().content" aria-label="Published messages">
    <!-- columns -->
    <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
    <tr mat-row *matRowDef="let row; columns: displayedColumns"></tr>
    <tr class="mat-row" *matNoDataRow>
      <td class="mat-cell no-data" [attr.colspan]="displayedColumns.length">
        No messages found
      </td>
    </tr>
  </table>

  <mat-paginator
    [length]="messages().totalElements"
    [pageSize]="messages().size"
    [pageIndex]="messages().number"
    [pageSizeOptions]="[10, 20, 50, 100]"
    (page)="onPageChange($event)"
    showFirstLastButtons
    aria-label="Select page of messages"
  />
</div>
```

```scss
.table-container {
  overflow-x: auto;
}
```

Conventions: `aria-label` on the table, `aria-label` on the paginator,
`*matNoDataRow` for the empty case, `[pageSizeOptions]="[10, 20, 50, 100]"` and
`showFirstLastButtons` always. Row actions are `mat-icon-button` with both
`matTooltip` and a matching `aria-label`.

---

## Metadata / definition lists

For key–value detail panes, a real `<dl>` rather than divs:

```html
<dl class="info-grid">
  <div>
    <dt>Correlation ID</dt>
    <dd class="mono">{{ data.correlationId }}</dd>
  </div>
  <div class="full-width">
    <dt>Topic</dt>
    <dd>{{ data.topic }}</dd>
  </div>
</dl>
```

```scss
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 0 0 24px;

  dt {
    font-size: 12px;
    color: var(--text-2);
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  dd {
    margin: 0;
    color: var(--text-1);
  }
}

.full-width {
  grid-column: 1 / -1;
}

.mono {
  font-family: 'Roboto Mono', monospace;
  font-size: 13px;
}
```

IDs, correlation keys and payload fragments always get `.mono`.

---

## Empty states

Two flavours. **Rich** — for primary content areas, driven by `@for … @empty` with
copy that reflects *why* it is empty:

```html
} @empty {
  <div class="empty-state">
    @if (searchQuery()) {
      <mat-icon>search_off</mat-icon>
      <p>No schemas match "{{ searchQuery() }}"</p>
    } @else {
      <mat-icon>folder_off</mat-icon>
      <p>No schemas found</p>
    }
  </div>
}
```

```scss
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-2);

  mat-icon {
    font-size: 48px;
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}
```

The 48px icon at `opacity: 0.5` is the recognisable part — a full-strength icon reads
as an error, not an absence. Distinguishing "no results for your filter" from "no
data exists" is expected, not optional.

**Terse** — a centred `--text-2` paragraph (`.no-data`, `.empty-message`) for
secondary panes and table cells.

---

## Loading states

Three tiers, no skeletons anywhere in this system.

**1. Page / section** — the shared spinner component:

```html
<app-loading-spinner />
<app-loading-spinner [diameter]="24" message="Loading messages..." />
```

It ships `role="status"`, `aria-live="polite"` and an `aria-label` from the message,
so the load announces itself. Inline/compact use passes `[diameter]="24"`.

**2. In-place progress** — for an action already under way:

```html
<mat-progress-bar mode="indeterminate" />
```

**3. Button label swap** — for submits, paired with `[disabled]`:

```html
<button mat-flat-button color="primary" [disabled]="!canPublish()">
  {{ eventService.publishing() ? 'Publishing...' : 'Publish Event' }}
</button>
```

---

## Snackbars

Go through `NotificationService`, never `MatSnackBar` directly. Four typed methods,
5000ms default, positioned top-end, dispatching a `panelClass`:

```ts
this.notificationService.showSuccess('Event published');
this.notificationService.showError('Failed to publish event');
```

`.snackbar-success` / `-error` / `-warning` / `-info` set MDC custom properties
(`--mdc-snackbar-container-color`, `--mdc-snackbar-supporting-text-color`,
`--mat-snack-bar-button-color`) rather than raw CSS.

These are the one deliberate exception to the token rule: they use solid Material
palette colours (`#2e7d32`, `#c62828`, `#e65100`, `#0d47a1`) because a snackbar
floats over arbitrary content and needs a fully opaque, high-contrast surface in
both themes. Do not "fix" them to alpha tokens.

---

## Sidebar navigation

The active item is deliberately squared off with a left indicator bar, against
Material's default pill:

```scss
.active {
  background-color: rgba(var(--primary-rgb), 0.12);
  color: var(--primary);
  font-weight: 500;
  border-radius: 0 !important;             // no pill shape
  border-left: 4px solid var(--primary);   // solid indicator
  padding-left: calc(16px - 4px);          // compensate so text doesn't shift
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}
```

The `calc(16px - 4px)` matters: without it, text jumps 4px when an item becomes
active. Hover is the same wash at `0.08`.

```html
<a mat-list-item [routerLink]="item.route"
   [class.active]="isActive(item.route)"
   [attr.aria-current]="isActive(item.route) ? 'page' : null">
```

`aria-current` binds to **`null`** when inactive. `false` would serialise to the
string `"false"`, which assistive tech reads as a *present* attribute.

---

## Code and JSON

`<pre>` / `<code>` are styled globally with `--code-bg`, `--code-border`, 4px radius
and `'Roboto Mono'`. Nested `code` inside `pre` is reset to transparent.

JSON syntax highlighting uses `.json-key`, `.json-string`, `.json-number`,
`.json-boolean`, `.json-null`, mapped to the `--json-*` tokens. `JsonViewerComponent`
injects these spans as trusted HTML, so the classes are declared **both** globally
and via `:host ::ng-deep` — injected markup does not carry the component's
encapsulation attribute. This is the one legitimate `::ng-deep` case.
