#!/usr/bin/env bash
# One pass over watchlist.txt: check every employer directly, email what is new.
#
#   ./watch_sites.sh              check, email the new ones
#   ./watch_sites.sh --no-mail    same, but just print them
#   ./watch_sites.sh --reset      forget seen_sites.json first
#
# No browser, no Cloudflare, no display variables — that is the whole point of this
# path, and why it is safe to run on a short timer. watch.sh remains the slow, wide
# hiring.cafe sweep.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

PY="$(dirname "$(readlink -f "$0")")/.venv/bin/python"
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
"$PY" sites.py "${ARGS[@]+"${ARGS[@]}"}"

if [[ "$MAIL" == "1" ]]; then
  "$PY" notify.py new_sites.json --label "watchlist · your bookmarked employers"
else
  echo "(--no-mail: skipping the email)"
fi
