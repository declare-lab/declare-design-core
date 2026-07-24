#!/usr/bin/env sh
set -eu

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM

read_pin() {
  repo_url="$1"
  repo_name="$2"
  git clone --quiet --depth 1 --filter=blob:none --no-checkout "$repo_url" "$tmp_root/$repo_name"
  git -C "$tmp_root/$repo_name" ls-tree HEAD assets/declare-core | awk '{print $3}'
}

lab_pin="$(read_pin https://github.com/declare-lab/declare-lab.github.io.git lab)"
personal_pin="$(read_pin https://github.com/soujanyaporia/soujanyaporia.github.io.git personal)"

if test -z "$lab_pin" || test -z "$personal_pin"; then
  echo "One or both consumer repositories do not pin assets/declare-core." >&2
  exit 1
fi

if test "$lab_pin" != "$personal_pin"; then
  echo "Design core drift detected:" >&2
  echo "  declare-lab.github.io: $lab_pin" >&2
  echo "  soujanyaporia.github.io: $personal_pin" >&2
  exit 1
fi

echo "Both consumers pin $lab_pin"
