# Changelog

## 2.3.2

- Page leads fill their column. `.page-lead p` and `.page-lead__copy` no longer
  cap at `--content-measure`; a lead is one or two sentences of display copy, and
  the cap left dead space to the right of every line once a lead wrapped (260px
  in an 804px column). The measure continues to govern body prose.

## 2.5.0

- Changed the unified default family from Archivo to Spectral for a more
  scholarly, editorial voice across both sites.
- Removed Archivo-specific variable-width settings; every semantic role now
  inherits the same family without font-specific axes.

## 2.4.2

- Made native code and keyboard elements inherit the single site family,
  removing the browser's implicit monospace exception.

## 2.4.1

- Narrowed the single-family verifier to real `font-family` declarations so it
  does not mistake the `--font-family` token definition for an override.

## 2.4.0

- Replaced the serif, sans-serif, monospace, display, and Bengali family tokens
  with one public `--font-family` token.
- Made every semantic type role inherit the same Archivo family, including
  prose, metadata, navigation, controls, publications, and code.
- Replaced the three family customization arguments with `$font-family`.
- Added consumer checks that reject legacy family tokens and multiple web-font
  imports.

## 2.3.1

- Added `--rule-heavy` token (`2px solid var(--rule-strong)`) for the heavy ink
  rule that closes a page header. Routed the page-header divider and the
  publication-card top rule through it, so the 2px structural weight is defined
  in one place instead of being repeated as a literal in consuming sites.

## 2.3.0

- Added reusable compact and split page-lead compositions.
- Added a public density API for page insets, title-to-lead spacing, section
  boundaries, object padding, layout gaps, and content measure.
- Reduced duplicated whitespace in the default desktop and mobile rhythm.

## 2.2.2

- Audit active page sources for inline style attributes and JavaScript style
  writes before those declarations can reach the rendered DOM.
- Continue to permit custom-property-only inline content data, such as
  per-person portrait positioning.

## 2.2.1

- Centralize shared color constants used by both sites.
- Make the ownership verifier reject literal consumer colors and `!important`
  overrides in addition to local typography and inline visual styles.

## 2.2.0

- Enforce single ownership of typography by rejecting all consumer declarations.
- Add a deterministic style-ownership auditor and mechanical cleanup mode.
- Promote multilingual personal-hero text to explicit shared semantic roles.
- Add compact semantic roles for academic-activity records.

## 2.1.5

- Classify update-category tags as shared labels rather than wrapper metadata.
- Keep update dates on the metadata tier while removing local visual drift.
- Assign compact item and supporting roles to mentorship and academic-contribution groups.

## 2.1.4

- Use regular weight for inactive contextual navigation.
- Preserve semibold emphasis for the active section only.

## 2.1.3

- Lower structural-fallback specificity so explicit semantic roles always win.

## 2.1.2

- Remove the legacy article-wide supporting-text fallback.
- Align structural CSS fallbacks with the compact-content DOM roles.

## 2.1.1

- Keep page-level narrative prose on the body tier.
- Reserve supporting typography for repeated records, cards, FAQs, openings, and compact content groups.

## 2.1.0

- Separate quiet navigation typography from primary action controls.
- Map repeated record and card headings to the shared item-title role.
- Preserve subsection scale for explanatory structures such as FAQs and openings.

## 2.0.0

- Replace wrapper-specific typography with one hierarchy derived from semantic HTML.
- Add a shared XPath contract consumed by both the browser and build pipeline.
- Add a deterministic Python fixer/verifier for roles, inline typography, and heading order.
- Exclude standalone project systems from the two-site typography audit.

## 1.8.1

- Extend literal typography checks to standalone project HTML pages.

## 1.8.0

- Define and document one semantic type ladder from display titles through labels.
- Add utility classes and customization arguments for every public type role.
- Normalize service rows, update-card lists, lab-note heroes, and people captions.
- Reject consumer CSS that introduces literal pixel/rem font sizes or numeric weights.

## 1.7.1

- Extend customization arguments to light and dark surfaces, text, borders, and complete accent palettes.
- Strengthen metadata typography selectors so semantic roles beat generic card-paragraph rules.
- Add shared statistic sizing and compact-control coverage for note links.

## 1.7.0

- Add the public `declare-customize` mixin for brand, typography, shape, layout, and rhythm arguments.
- Document layout selection, consumer setup, supported customization, ownership, and upgrades.
- Preserve clicked section-menu targets when multiple sections share a horizontal row.
- Ensure inline menus reach their docked state before scroll-spy selection resumes.
- Centralize section-label chips, compact list grids, technical content formatting, and mobile content wrapping.
- Strengthen consumer verification against local copies of shared content and token rules.

## 1.6.0

- Add selectable lab and personal site shells with documented customization variables.
- Centralize wrapper columns, author-sidebar geometry, responsive stacking, and print behavior.
- Correct inline and mobile submenu targeting by measuring the menu's docked position.
- Center both footer text and footer links.
- Promote FAQ answers to supporting-text size and centralize the FAQ row pattern.
- Reject consumer redefinitions of shared shell and FAQ selectors.

## 1.5.0

- Add a shared right-rail page composition for contents and publication-year navigation.
- Make rail placement independent of DOM source order and stack it consistently on smaller screens.
- Keep long desktop rail labels inside their boundary while preserving horizontal mobile navigation.
- Centralize muted, parenthesized publication-category counts and sticky archive controls.
- Guard the canonical shared layout classes against consumer redefinition.

## 1.4.1

- Give the shared page composition classes one inherited width-safety baseline.
- Leave flex/grid geometry and sidebar placement explicitly site-specific.

## 1.4.0

- Make global design tokens and base element rules core-only.
- Centralize inner-page metadata strips, title spacing, and divider treatment.
- Reject consumer redefinitions of shared tokens and page headers.
- Remove obsolete personal-site component styles from the lab consumer.

## 1.3.0

- Add one shared publication archive component family.
- Centralize publication search, filters, records, metadata, links, and abstracts.
- Keep archive composition and year-rail placement site-specific.
- Enforce single ownership for shared primary and secondary controls.

## 1.2.4

- Position anchored content from the rendered bottom of a sticky inline menu.

## 1.2.3

- Detect horizontal menus by layout rather than only by overflow.
- Apply the correct sticky-menu offset even when every item already fits.

## 1.2.2

- Reserve anchor offset ownership for the shared section-menu component.
- Reject consumer `scroll-margin-top` declarations that can hide headings.

## 1.2.1

- Keep anchored section headings clear of sticky inline section menus.

## 1.2.0

- Move site titles, logo variants, and theme-aware logo switching into core.
- Centralize footer link states and responsive masthead logo dimensions.
- Reject consumer stylesheet definitions of shared site-chrome selectors.

## 1.1.0

- Introduce one inherited section-menu component with rail and inline variants.
- Centralize sticky, active, hover, focus, and mobile overflow behavior.
- Prevent consumer stylesheets from redefining shared section-menu classes.
- Preserve the first mobile item border by removing edge-clipping masks.

## 1.0.6

- Correct the consumer update instructions to reference the shared sync helper.

## 1.0.5

- Allow the sync helper to update initialized consumers before their first
  parent-repository commit.

## 1.0.4

- Remove selectors absent from the combined generated output of both sites.

## 1.0.3

- Normalize nested lab call-to-action controls to the shared control scale.
- Reject reintroduced duplicate shared-contract blocks in consumer CSS.

## 1.0.2

- Enforce semantic type roles against legacy high-specificity component rules.
- Require the explicit `declare-core` document inheritance contract.

## 1.0.1

- Preserve the established 1.65 baseline leading outside content regions.
- Add consumer synchronization and cross-repository alignment checks.

## 1.0.0

- Establish shared color, type, spacing, control, and chrome tokens.
- Unify base typography, buttons, navigation, footer, and theme controls.
- Centralize mobile primary-menu and in-page section-menu behavior.
