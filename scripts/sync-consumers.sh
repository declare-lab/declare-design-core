#!/usr/bin/env sh
set -eu

core_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
workspace_root="$(dirname "$core_root")"
core_sha="$(git -C "$core_root" rev-parse HEAD)"

if ! git -C "$core_root" diff --quiet || ! git -C "$core_root" diff --cached --quiet; then
  echo "Commit the shared core before syncing consumers." >&2
  exit 1
fi

for site_name in declare-lab.github.io soujanyaporia.github.io; do
  site_root="$workspace_root/$site_name"
  submodule_root="$site_root/assets/declare-core"

  test -d "$site_root/.git"
  if git -C "$site_root" ls-files --error-unmatch assets/declare-core >/dev/null 2>&1; then
    git -C "$site_root" submodule update --init assets/declare-core
  else
    test -d "$submodule_root"
  fi
  git -C "$submodule_root" fetch origin main
  git -C "$submodule_root" switch --detach "$core_sha"
  "$submodule_root/scripts/verify-consumer.sh" "$site_root"
  echo "$site_name now pins $core_sha"
done
