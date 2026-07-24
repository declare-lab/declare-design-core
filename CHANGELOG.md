# Changelog

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
