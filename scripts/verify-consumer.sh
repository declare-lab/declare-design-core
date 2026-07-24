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
done

echo "Shared design core is wired correctly in $site_root"
