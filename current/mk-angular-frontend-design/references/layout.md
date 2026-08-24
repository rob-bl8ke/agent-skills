# Layout

## Page shell

Fixed toolbar over a CDK sidenav, with a skip link ahead of everything:

```html
<a class="skip-link" href="#main-content">Skip to main content</a>
<app-header (menuToggled)="toggleSidenav()" />
<mat-sidenav-container class="sidenav-container">
  <mat-sidenav
    #sidenav
    [mode]="isMobile() ? 'over' : 'side'"
    [opened]="!isMobile()"
    [fixedInViewport]="true"
    [fixedTopGap]="64"
    role="navigation"
  >
    <app-sidebar />
  </mat-sidenav>
  <mat-sidenav-content>
    <main id="main-content" class="main-content" role="main" tabindex="-1">
      <router-outlet />
    </main>
  </mat-sidenav-content>
</mat-sidenav-container>
```

```scss
@use 'breakpoints' as bp;

:host {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidenav-container {
  flex: 1;
  margin-top: 64px;          // clears the fixed header
  background-color: var(--bg);
}

mat-sidenav {
  width: 250px;
  background-color: var(--surface-2);
  border-right: 1px solid var(--divider);
}

.main-content {
  padding: 24px;
  min-height: calc(100vh - 64px - 48px);
  background-color: var(--bg);
}

@include bp.below(bp.$bp-sm) {
  .main-content {
    padding: 16px;
  }
}
```

**64px is the toolbar height and it appears in four coupled places**:
`[fixedTopGap]="64"`, `margin-top: 64px`, and twice inside
`calc(100vh - 64px - 48px)`. Change one and you must change all four. The header is
`position: fixed` at `z-index: 1000`; the skip link sits at `1100` so it lands above
it when focused.

Pages are full-bleed inside `.main-content`. Only add a `max-width` + `margin: 0 auto`
container when a page's content genuinely does not want the full width.

## Responsive: behaviour vs layout

Two different mechanisms, and picking the wrong one is a common mistake.

**Behaviour** — a component doing something structurally different. Use the CDK
observer, because it is state the template needs to read:

```ts
private readonly breakpointObserver = inject(BreakpointObserver);
protected readonly isMobile = signal(false);

constructor() {
  this.breakpointObserver.observe([Breakpoints.Handset]).subscribe((result) => {
    this.isMobile.set(result.matches);
  });
}
```

**Layout** — a grid reflowing, padding tightening. Use a media query via the mixin.

## Breakpoints

Defined in `src/styles/_breakpoints.scss`, the only Sass-variable file in the
codebase (custom properties cannot be used inside `@media`).

```scss
$bp-sm: 600px;   // Material Handset boundary — phone vs tablet
$bp-md: 768px;   // small tablet portrait
$bp-lg: 960px;   // tablet landscape — two-column shells collapse here
$bp-xl: 1280px;  // desktop — wide rails become viable
```

```scss
@use 'breakpoints' as bp;

.content-grid {
  grid-template-columns: 350px 1fr;

  @include bp.below(bp.$bp-lg) {
    grid-template-columns: 1fr;
  }
}
```

`below()` is mobile-last (`max-width: $bp - 1px`), matching the existing idiom.
`from()` is available for mobile-first when it reads better.

Never write a bare `@media (max-width: 800px)`. Ad-hoc values are exactly how this
codebase ended up with four mutually inconsistent breakpoints, none of which lined
up with the CDK boundary the sidenav was already using.

## Flex vs grid

A clear division of labour — follow it rather than picking by preference.

**Flex** for one-dimensional arrangement: toolbars, rows of chips, status cells,
button groups, vertical stacks. Always use `gap`, never margin chains.

```scss
.status-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}
```

For a flex row whose children must wrap and share space, the idiom is the
`flex: 1` + `min-width` + `max-width` triplet rather than a grid:

```scss
.filter-field {
  flex: 1;
  min-width: 200px;
  max-width: 300px;
}
```

**Grid** for page and data layouts, in two idioms.

### 1. `auto-fit` — the default, no media query needed

This is the dominant responsive tool in the codebase. It reflows intrinsically:

```scss
.info-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
```

Common minimums: `150px` (compact result details), `200px` (metadata, stat tiles),
`300px` (form rows). Span a full row with:

```scss
.full-width {
  grid-column: 1 / -1;
}
```

**Reach for this before reaching for a breakpoint.** Most "responsive" work here
needs no media query at all.

### 2. Fixed asymmetric two-column page shells

For a content area plus a fixed rail, where the rail's width is deliberate. These
*do* need a breakpoint, since `auto-fit` cannot express "collapse to one column":

```scss
// content, then a fixed rail on the right
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;

  @include bp.below(bp.$bp-lg) {
    grid-template-columns: 1fr;
  }
}

// fixed rail on the left, then content
.content-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 24px;

  @include bp.below(bp.$bp-lg) {
    grid-template-columns: 1fr;
  }
}
```

## Spacing rhythm

The 4px grid, in practice:

| Value | Used for |
|---|---|
| `4px` | icon-to-label, tight inline gaps, `dt`/`dd` |
| `8px` | chip gaps, button icon margins, list item padding |
| `12px` | card header padding (vertical), badge-to-text gaps |
| `16px` | **the default** — card body padding, grid gaps, section spacing |
| `24px` | page padding, block separation, heading margins |
| `32px` | major section separation on long forms |
| `48px` | empty-state padding |

Compact list rows use `padding: 8px 16px`; card headers `12px 16px`; card bodies a
flat `16px`. Page-level `24px` tightens to `16px` below `$bp-sm`.

## Overflow and truncation

Text that can be arbitrarily long inside a flex row needs `min-width: 0` on the
flex child, or the ellipsis never triggers:

```scss
.message-info {
  flex: 1;
  min-width: 0;   // required — flex items default to min-width: auto
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.message-topic {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

Tables get `overflow-x: auto` on a wrapper rather than shrinking columns.
