# DeCLaRe Design Core

Shared visual and interaction primitives for:

- [DeCLaRe Lab](https://declare-lab.github.io)
- [Soujanya Poria](https://soujanyaporia.github.io)

The core owns design tokens, base typography, buttons and controls, page
headers, publication records, site chrome, theme behavior, in-page section
navigation, and the shared content-plus-right-rail page composition. Each
consumer keeps only identity-specific and domain-specific layouts.

## Quick start

Add this repository as a submodule:

```sh
git submodule add https://github.com/declare-lab/declare-design-core.git assets/declare-core
```

Expose the core Sass directory to Jekyll:

```yml
sass:
  load_paths:
    - assets/declare-core/scss
```

Import the core after any identity-specific component stylesheet:

```scss
@import "my-site-components";
@import "core";
```

Load the shared interaction script near the end of the page:

```html
<script src="/assets/declare-core/js/site.js"></script>
```

Select one reusable site shell on the document body:

```html
<body class="site-layout site-layout--lab">
```

or:

```html
<body class="site-layout site-layout--personal">
```

That single class selects the page geometry. The `lab` layout is a wide
institutional canvas; the `personal` layout adds an author rail.

Page-specific modules can add a semantic body class without changing the
selected shell:

```html
<body class="site-layout site-layout--lab project-demo-page">
```

Use that only to scope a genuinely page-specific component, never to recreate
shared chrome or typography.

Use the canonical shell structure in the page layout:

```html
<div class="page-wrapper site-shell has-sidebar">
  <aside class="sidebar site-shell__sidebar">...</aside>
  <article class="page-content site-shell__content">
    <div class="page-body site-content">...</div>
  </article>
</div>
```

## Customization

For ordinary changes, call the public mixin after importing the core. Every
argument is optional:

```scss
@import "my-site-components";
@import "core";

@include declare-customize(
  $accent: #006b5f,
  $accent-hover: #005248,
  $accent-light: #dcefeb,
  $dark-accent: #73d8ca,
  $dark-accent-hover: #9ce8de,
  $dark-accent-light: #153f3a,
  $background: #f4f6f5,
  $card-background: #ffffff,
  $text: #15201e,
  $font-sans: ("Archivo", sans-serif),
  $font-serif: ("Spectral", serif),
  $font-mono: ("IBM Plex Mono", monospace),
  $body-size: 1.05rem,
  $section-title-size: 1.8rem,
  $stat-size: 2.2rem,
  $radius: 4px,
  $layout-max-width: 1280px,
  $sidebar-width: 300px,
  $stacked-sidebar-width: 720px,
  $shell-gap: 2.5rem,
  $rail-width: 180px,
  $rail-gap: 1.5rem,
  $page-space-top: 2rem,
  $page-header-gap: 1.25rem,
  $page-lead-gap: 1.5rem,
  $section-space: 2.25rem,
  $section-boundary-before: 1.75rem,
  $section-boundary-after: 1.75rem,
  $card-padding-block: 0.95rem
);
```

This is the supported argument surface:

| Concern | Arguments |
| --- | --- |
| Brand | `$accent`, `$accent-hover`, `$accent-light`, `$accent-contrast` and their `$dark-*` counterparts |
| Surfaces | `$background`, `$card-background`, `$soft-background`, `$text`, `$text-secondary`, `$border` and their `$dark-*` counterparts |
| Type | `$font-sans`, `$font-serif`, `$font-mono`, `$font-family`, `$display-size`, `$page-title-size`, `$section-title-size`, `$feature-title-size`, `$card-title-size`, `$body-size`, `$supporting-size`, `$small-size`, `$control-size`, `$meta-size`, `$label-size`, `$stat-size`, `$content-leading`, `$prose-align`, `$prose-last-line-align` |

The core assigns families by semantic role: sans-serif for headings,
navigation, controls, and labels; serif for reading prose; monospace for quiet
metadata. Consumers can replace each family through the public mixin. The
legacy `$font-family` argument remains available as the general inherited
fallback.

`$prose-align` and `$prose-last-line-align` apply to body and supporting
prose. Compact metadata remains left-aligned so short affiliations, dates, and
profile details do not acquire exaggerated word spacing in narrow components.
Use `data-prose-align="left"` or `data-prose-align="center"` on concise copy
that should retain its semantic type role without inheriting the site's
longer-form prose alignment. Add `data-prose-align-mobile="left"` when the
same copy should use a left reading edge below the 720px mobile breakpoint.
| Shape | `$radius` |
| Layout | `$max-width`, `$layout-max-width`, `$sidebar-width`, `$stacked-sidebar-width`, `$shell-gap`, `$rail-width`, `$rail-gap`, `$publication-rail-width`, `$publication-rail-gap`, `$content-measure` |
| Page rhythm | `$page-space-top`, `$page-space-bottom`, `$page-header-gap`, `$page-meta-gap`, `$page-lead-gap`, `$page-lead-padding` |
| Section rhythm | `$section-space`, `$section-rule-space`, `$section-boundary-before`, `$section-boundary-after`, `$layout-gap`, `$card-gap` |
| Object density | `$panel-padding-block`, `$panel-padding-inline`, `$card-padding-block`, `$card-padding-inline` |

Advanced consumers can override public CSS properties after the core import.
Useful layout properties include `--site-content-gap`, `--site-sidebar-top`,
`--chrome-height`, `--control-height`, and `--content-measure`. Prefer the mixin
when it exposes the value you need; direct properties are the escape hatch.

Do not redefine shared selectors such as `.site-header`, `.section-menu`,
`.site-shell`, `.btn-primary`, `.pub-card`, `.page-header`, or `.faq-list`.
Change their public properties instead. This keeps upgrades predictable.

Use `.btn--compact` alongside a button class when a dense toolbar must keep
short labels on one line.

### Semantic type roles

The core uses one DOM-derived type ladder everywhere. Heading rank supplies the
default role, while repeated semantic records such as publications, projects,
updates, activities, and people use the compact item-title tier. Prose roles
follow semantic HTML: page copy is reading text, prose inside compact records is
supporting text, and `time`, `figcaption`, tables, labels, controls, and
statistics receive their corresponding roles.

| Role | Token | Utility class | Default |
| --- | --- | --- | --- |
| Page title | `--type-page-title` | `.type-page-title` | 48px |
| Section title | `--type-section-title` | `.type-section-title` | 28px |
| Subsection title (`h3`) | `--type-feature-title` | `.type-feature-title` | 22px |
| Item title (`h4`) | `--type-card-title` | `.type-card-title` | 19px |
| Reading text | `--type-body` | `.type-body` | 17px |
| Supporting text | `--type-supporting` | `.type-supporting` | 16px |
| Card/list text | `--type-small` | `.type-small` | 14px |
| Metadata | `--type-meta` | `.type-meta` | 12px |
| Label | `--type-label` | `.type-label` | 11px |

The single source of truth is
`config/typography-contract.json`. `js/site.js` applies the contract in local
and development views. Production builds must run the same contract through
the deterministic Python fixer and verifier:

```sh
python -m pip install -r assets/declare-core/requirements.txt
python assets/declare-core/scripts/typography_dom.py fix --site _site
python assets/declare-core/scripts/typography_dom.py verify --site _site
python assets/declare-core/scripts/typography_dom.py verify --site _site --json
```

The fixer assigns `data-type-role` from XPath rules and removes inline
typography declarations. The verifier checks those assignments, rejects stale
or unknown roles, rejects unclassified text and inline typography, requires one
non-empty root `h1`, and detects heading-level jumps.
Standalone project systems such as NORA are excluded by the contract.

Rendered pages also expose `window.DeclareTypography.audit()`. It checks every
assigned role against the shared size, weight, family, color, and line-height
expectations, then verifies that nested heading sizes decrease. This makes
computed-style regression checks possible across themes and responsive
viewports rather than limiting validation to source markup.

Site-specific styles may compose layout and domain visualizations. They do not
own typography, raw color constants, or cascade overrides. Typography includes
family, size, weight, line height, letter spacing, variation settings, style,
and text transform. To customize the hierarchy or palette, change the public
tokens through `declare-customize`; do not add wrapper-specific heading rules,
literal colors, or `!important`.

The ownership auditor enforces that boundary:

```sh
python assets/declare-core/scripts/style_ownership.py audit \
  --site-root . --built-site _site
```

`fix` mode mechanically removes typography declarations from consumer SCSS.
The audit rejects consumer typography, literal colors, `!important`,
non-data-driven inline styles, JavaScript style writes, and embedded style
blocks. It checks both active page sources and generated main-site pages.
Inline custom properties are permitted for content data such as per-person
image positioning.

## Components

### Page leads

Use one shared lead directly after the page header. It owns the divider and the
space before the first section, preventing a page header, introduction, and
first heading from each adding their own gap.

```html
<section class="page-lead page-lead--compact">
  <p>One concise orientation paragraph.</p>
</section>
```

For editorial pages with actions:

```html
<section class="page-lead page-lead--split">
  <p class="page-lead__copy">A short authored introduction.</p>
  <div class="page-lead__actions">
    <a class="btn btn-primary" href="/research/">Research</a>
    <a class="btn btn-secondary" href="/publications/">Publications</a>
  </div>
</section>
```

The lead becomes a single column at narrower widths. Tune it through the
`$page-lead-*` mixin arguments; do not recreate its margin, padding, or divider
in a consumer stylesheet.

On personal layouts with both an author rail and a contents rail, place the
lead above the content/rail split and add `page-lead--wide`. It uses the full
article width for prose and actions on wide screens, then stacks before either
column becomes cramped.

### Date markers

Use a date marker at the start of a chronological record. The primary line can
hold a month, venue, or year; add the secondary line when a separate year is
available.

```html
<time class="date-marker" datetime="2026-05">
  <span class="date-marker__primary">May</span>
  <span class="date-marker__secondary">2026</span>
</time>
```

For an activity feed, use the shared connected timeline. The timeline modifier
removes the calendar box and keeps the date as quiet metadata beside the dot.

```html
<div class="timeline-list">
  <article class="timeline-item">
    <div class="timeline-item__marker">
      <time class="date-marker date-marker--timeline" datetime="2026-05">
        <span class="date-marker__primary">May</span>
        <span class="date-marker__secondary">2026</span>
      </time>
    </div>
    <div class="timeline-item__content">
      <span class="record-badge">Media</span>
      <h3>Update title</h3>
      <p>Concise update text.</p>
    </div>
  </article>
</div>
```

### Density rules

Whitespace has one owner at each boundary:

- `--page-space-*` controls the canvas inside the header and footer.
- `--page-header-gap` separates the page title from the page lead.
- `--page-lead-*` separates orientation copy from the first section.

`$layout-max-width` controls the content canvas without forcing the navigation
chrome to use the same width. This is the preferred way to create generous
outer margins on an academic site. `$content-measure` independently limits
reading text; grids, publication controls, and other structured interfaces may
continue to use the full canvas. `$stacked-sidebar-width` constrains a personal
profile after the two-column shell collapses, preserving a readable identity
panel instead of stretching it across the full page.

The mixin writes public `--layout-*` configuration tokens. Layout profiles
derive their internal `--site-*` values from those tokens so profile defaults
remain overridable without consumer selectors.
- `--section-boundary-before` and `--section-boundary-after` place air on the
  two sides of a section rule.
- panel and card padding tokens control internal object density.

Local components may consume these properties, but should not introduce a
second page-level rhythm. This is the core maintenance rule behind the compact
layout profile.

Use the shared structural classes for in-page navigation:

```html
<nav class="section-menu section-menu--rail" data-section-menu>
  <span class="section-menu__label">Sections</span>
  <div class="section-menu__items" data-section-menu-scroll>...</div>
</nav>
```

Use `section-menu--inline` for an in-flow horizontal menu. Consumer stylesheets
must not redefine section-menu appearance or interaction states.

For a content page with a right-hand section rail, use the shared composition:

```html
<div class="page-rail-layout">
  <main class="page-rail-layout__main">...</main>
  <nav class="section-menu section-menu--rail" data-section-menu>...</nav>
</div>
```

The core also maps the lab's established `.side-layout` and `.pub-layout`
classes to this geometry. On smaller screens, the rail becomes the horizontal
sticky section menu above the main content.

Section headings can opt into the shared label treatment:

```html
<h2 id="methods" data-section-label="02">Methods</h2>
```

FAQ content uses the shared ruled-list pattern:

```html
<div class="faq-list">
  <article>
    <h3>Who can apply?</h3>
    <p>...</p>
  </article>
</div>
```

## Brand artwork

`brand/` holds the DeCLaRe robot: one themeable silhouette carved by a luminance
mask, in a display cut and a small cut of the same chest board. Both websites
show this mark, so it lives here.

Consume the vectors straight from the submodule:

```html
<img src="/assets/declare-core/brand/logos/declare-icon-light.svg" alt="DeCLaRe Lab">
```

Rasters stay local to each site — favicons, touch icons and Open Graph images
need pixel dimensions and framing that belong to the site, not to the mark.
`brand/tools/build_brand.py` regenerates those too. See `brand/README.md`.

## What remains local

Keep CSS local only when the object belongs to one site's identity or domain,
for example an author profile, a lab collaboration graph, a research map, or a
project-specific interactive demo. Typography, site chrome, buttons, records,
section navigation, content formatting, and common page geometry belong to the
core.

As a practical test: if another academic or lab website could use the object
without changing its meaning, it probably belongs in the core.

## Updating

Each parent repository pins a core commit through its submodule entry. From this
repository, run `scripts/sync-consumers.sh` to advance both local websites to
the same published core revision.

Run the contract verifier after changing either consumer:

```sh
./scripts/verify-consumer.sh /path/to/consumer
```

The verifier rejects local copies of shared selectors and design tokens, plus
all local typography declarations. A deliberate site-specific layout exception
should use its own component class and explain why it is local; typography
exceptions must be modeled as a semantic core role.
