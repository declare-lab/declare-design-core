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
  $font-serif: ("Source Serif 4", Georgia, serif),
  $font-sans: ("Inter", sans-serif),
  $body-size: 1.05rem,
  $section-title-size: 1.8rem,
  $stat-size: 2.2rem,
  $radius: 4px,
  $layout-max-width: 1280px,
  $sidebar-width: 300px,
  $shell-gap: 2.5rem,
  $section-space: 3.25rem
);
```

This is the supported argument surface:

| Concern | Arguments |
| --- | --- |
| Brand | `$accent`, `$accent-hover`, `$accent-light`, `$accent-contrast` and their `$dark-*` counterparts |
| Surfaces | `$background`, `$card-background`, `$soft-background`, `$text`, `$text-secondary`, `$border` and their `$dark-*` counterparts |
| Type | `$font-serif`, `$font-sans`, `$font-mono`, `$display-size`, `$page-title-size`, `$section-title-size`, `$feature-title-size`, `$card-title-size`, `$body-size`, `$supporting-size`, `$small-size`, `$control-size`, `$meta-size`, `$label-size`, `$stat-size`, `$content-leading` |
| Shape | `$radius` |
| Layout | `$max-width`, `$layout-max-width`, `$sidebar-width`, `$shell-gap` |
| Rhythm | `$section-space` |

Advanced consumers can override public CSS properties after the core import.
Useful layout properties include `--site-content-gap`, `--site-sidebar-top`,
`--chrome-height`, `--control-height`, and `--content-measure`. Prefer the mixin
when it exposes the value you need; direct properties are the escape hatch.

Do not redefine shared selectors such as `.site-header`, `.section-menu`,
`.site-shell`, `.btn-primary`, `.pub-card`, `.page-header`, or `.faq-list`.
Change their public properties instead. This keeps upgrades predictable.

### Semantic type roles

The core uses one type ladder everywhere. Choose a role by meaning, not by the
container that happens to surround the text:

| Role | Token | Utility class | Default |
| --- | --- | --- | --- |
| Page title | `--type-page-title` | `.type-page-title` | 48px |
| Section title | `--type-section-title` | `.type-section-title` | 28px |
| Feature title | `--type-feature-title` | `.type-feature-title` | 22px |
| Card title | `--type-card-title` | `.type-card-title` | 19px |
| Reading text | `--type-body` | `.type-body` | 17px |
| Supporting text | `--type-supporting` | `.type-supporting` | 16px |
| Card/list text | `--type-small` | `.type-small` | 14px |
| Metadata | `--type-meta` | `.type-meta` | 12px |
| Label | `--type-label` | `.type-label` | 11px |

Feature titles introduce a distinct subsection. Card titles name repeated
objects. Reading text carries the main narrative; supporting text belongs to
compact explanatory rows such as FAQs and service records. Reusable components
must use these tokens or utility classes instead of new numeric font sizes.

## Components

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

The verifier rejects local copies of shared selectors and design tokens. A
deliberate site-specific exception should use its own component class and
explain why it is local.
