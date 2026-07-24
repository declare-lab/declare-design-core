# DeCLaRe Design Core

Shared visual and interaction primitives for:

- [DeCLaRe Lab](https://declare-lab.github.io)
- [Soujanya Poria](https://soujanyaporia.github.io)

The core owns design tokens, base typography, buttons and controls, site chrome,
theme behavior, and in-page section navigation. Each consumer keeps its own
content layouts and domain-specific components.

## Consumer setup

Add this repository as `assets/declare-core`, add `scss` to Jekyll's Sass load
paths, and import the core after the site's local stylesheet:

```scss
@import "core";
```

Load the shared interaction script near the end of the page:

```html
<script src="/assets/declare-core/js/site.js"></script>
```

Use the shared structural classes for in-page navigation:

```html
<nav class="section-menu section-menu--rail" data-section-menu>
  <span class="section-menu__label">Sections</span>
  <div class="section-menu__items" data-section-menu-scroll>...</div>
</nav>
```

Use `section-menu--inline` for an in-flow horizontal menu. Consumer stylesheets
must not redefine section-menu appearance or interaction states.

Each parent repository pins a core commit through its submodule entry. From this
repository, run `scripts/sync-consumers.sh` to advance both local websites to
the same published core revision.

## Ownership rule

If an object has the same purpose on both sites, it belongs here. A deliberate
site-specific exception should stay in that site's stylesheet and explain why.
