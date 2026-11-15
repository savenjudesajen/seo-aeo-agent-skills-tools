#!/usr/bin/env bash
# Turns on the pre-push check in this clone (maintainers only: it needs the key file).
#
#   bash tools/public-content-scan/install-hook.sh <absolute path to the key file>
#
# Sets core.hooksPath to .githooks and publicscan.keyfile to the key file, then runs the check on HEAD once.
# Refuses when this clone already has its own hooks (a hooks path elsewhere, or a non-sample hook in .git/hooks),
# because switching the hooks path would silently turn those off.
set -euo pipefail

key_file="${1:-}"
if [[ -z "$key_file" || "$key_file" != /* ]]; then
  echo "usage: bash tools/public-content-scan/install-hook.sh <absolute path to the key file>" >&2
  exit 2
fi
if [[ ! -f "$key_file" || -L "$key_file" ]]; then
  echo "$key_file is not a regular file" >&2
  exit 2
fi

top="$(git rev-parse --show-toplevel)"
cd "$top"
current="$(git config --get core.hooksPath || true)"
if [[ -n "$current" && "$current" != ".githooks" ]]; then
  echo "core.hooksPath is already $current; add .githooks/pre-push there by hand instead" >&2
  exit 2
fi
# The clone's own hooks folder (--git-path hooks would follow core.hooksPath once this is installed).
hooks_dir="$(git rev-parse --git-common-dir)/hooks"
if [[ -d "$hooks_dir" ]]; then
  for hook in "$hooks_dir"/*; do
    [[ -e "$hook" && "$hook" != *.sample ]] || continue
    echo "$hook exists and would stop running; chain it from .githooks/pre-push by hand instead" >&2
    exit 2
  done
fi

git config core.hooksPath .githooks
git config publicscan.keyfile "$key_file"
echo "Pre-push check on. Checking HEAD once…"
node tools/public-content-scan/scan.mjs tree HEAD
