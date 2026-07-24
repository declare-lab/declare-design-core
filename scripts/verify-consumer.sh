#!/usr/bin/env sh
set -eu

site_root="${1:-.}"
style_file="$site_root/assets/css/style.scss"
layout_file="$site_root/_layouts/default.html"
core_root="$site_root/assets/declare-core"

test -f "$core_root/scss/core.scss"
test -f "$core_root/js/site.js"
test -f "$style_file"
test -f "$layout_file"

import_count="$(grep -c '@import "core";' "$style_file" || true)"
test "$import_count" -eq 1

grep -q "/assets/declare-core/js/site.js" "$layout_file"
grep -q 'class="declare-core"' "$layout_file"

if test -e "$site_root/assets/js/section-navigation.js"; then
  echo "Legacy section-navigation.js still exists in $site_root" >&2
  exit 1
fi

if grep -Eq \
  "Shared DeCLaRe / Soujanya interface contract|Shared typography contract|Final enforcement for the shared two-site interface contract" \
  "$style_file" "$site_root/_sass/"*.scss 2>/dev/null; then
  echo "A migrated shared-contract block has reappeared in $site_root" >&2
  exit 1
fi

for consumer_style in "$style_file" "$site_root/_sass/"*.scss; do
  test -f "$consumer_style" || continue
  if grep -Eq \
    '\.(section-nav|pub-year-nav|home-section-nav|toc-nav|toc-title|toc-list|toc-level-3|toc-sticky)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared section-menu styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    '\.(site-header|header-inner|site-title|site-logo-title|site-logo|site-logo--light|site-logo--dark|theme-logo-light|theme-logo-dark|nav-links|nav-icon|nav-external|menu-toggle|nav-scrim|menu-icon-open|menu-icon-close|theme-toggle|theme-icon|icon-sun|icon-moon|theme-toggle-label|theme-toggle-value|site-main|site-footer|footer-inner|footer-links|menu-open)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared site-chrome styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    '\.(btn|btn-primary|btn-secondary|lab-link|lab-link-secondary)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared control styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    '\.(pub-toolbar|pub-toolbar__row|pub-search|pub-filter-row|pub-filter|pub-count-display|pub-cat-row|pub-cat-btn|pub-cat-count|pub-year-heading|pub-card|pub-card__top|pub-title-line|pub-title|pub-hot-star|pub-authors|pub-meta|pub-venue|pub-year-tag|pub-citation-badge|pub-award|pub-links|pub-abstract-toggle|pub-link-primary|pub-cats|pub-cat-badge|pub-abstract)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared publication styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    '\.(page-header|page-meta-strip)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared page-header styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    '\.(page-rail-layout|page-rail-layout__main)([[:space:]:>,+~.{#]|$)' \
    "$consumer_style"; then
    echo "Shared page-rail layout styling has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq \
    -- '--(accent|accent-hover|accent-light|accent-contrast|accent-2|accent-2-light|accent-3|accent-3-light|ink|ink-soft|paper|paper-2|paper-card|rule|rule-strong|text|text-secondary|text-muted|bg|bg-page|bg-card|bg-soft|border|border-hover|radius|radius-lg|shadow-sm|shadow-md|shadow-lg|transition|font|font-serif|font-sans|font-display|font-mono|heading-width|type-display|type-page-title|type-section-title|type-feature-title|type-card-title|type-body|type-supporting|type-small|type-control|type-meta|type-label|type-context-nav|type-navigation|content-leading|card-leading|compact-leading|weight-body|weight-meta|weight-emphasis|weight-label|weight-card|weight-section|weight-display|display-weight|section-weight|card-title-weight|max-width|chrome-height|control-height|compact-control-height|theme-toggle-size|footer-type|section-space|section-rule-space|section-nav-offset|panel-padding-block|panel-padding-inline|card-padding-block|card-padding-inline|layout-gap|card-gap|card-border|featured-border)[[:space:]]*:' \
    "$consumer_style"; then
    echo "A shared design token has reappeared in $consumer_style" >&2
    exit 1
  fi

  if grep -Eq '(^|[;{[:space:]])scroll-margin-top[[:space:]]*:' "$consumer_style"; then
    echo "Shared anchor-offset styling has reappeared in $consumer_style" >&2
    exit 1
  fi
done

echo "Shared design core is wired correctly in $site_root"
