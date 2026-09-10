#!/usr/bin/env bash
# One pass over watchlist.txt: check every employer directly, email what is new.
#
#   bin/watch-sites.sh              check, email the new ones
#   bin/watch-sites.sh --no-mail    same, but just print them
#   bin/watch-sites.sh --reset      forget data/seen_sites.json first
#
# No browser, no Cloudflare, no display variables — that is the whole point of this
# path, and why it is safe to run on a short timer. bin/watch.sh remains the slow, wide
# hiring.cafe sweep.
set -euo pipefail

ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$ROOT"

PY="$ROOT/.venv/bin/python"
[[ -x "$PY" ]] || PY="$(command -v python3)"

MAIL=1
ARGS=()
for arg in "$@"; do
  case "$arg" in
    --no-mail) MAIL=0 ;;
    --reset)   ARGS+=(--reset) ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

echo "=== $(date '+%F %T') · watchlist ==="
"$PY" -m jobwatch.watchlist.check "${ARGS[@]+"${ARGS[@]}"}"

if [[ "$MAIL" == "1" ]]; then
  "$PY" -m jobwatch.notify data/new_sites.json --label "watchlist · your bookmarked employers"
else
  echo "(--no-mail: skipping the email)"
fi
