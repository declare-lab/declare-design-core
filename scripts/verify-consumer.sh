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

echo "Shared design core is wired correctly in $site_root"
