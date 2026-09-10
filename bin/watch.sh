#!/usr/bin/env bash
# One hiring.cafe check: scrape, filter, report what is new.
#
#   bin/watch.sh                 scrape, filter, email the new ones
#   bin/watch.sh --no-mail       same, but just print them (manual use)
#   bin/watch.sh --reset         forget data/seen.json first, so everything counts as new
#
# Safe to run from cron or by hand. Under cron on Linux/WSL the display variables
# below are essential — cron hands a script almost no environment, and without them
# Chrome cannot reach WSLg and the run dies.
set -euo pipefail

ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  export DISPLAY="${DISPLAY:-:0}"
  export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
fi

PY="$ROOT/.venv/bin/python"
[[ -x "$PY" ]] || PY="$(command -v python3)"

MAIL=1
for arg in "$@"; do
  case "$arg" in
    --no-mail) MAIL=0 ;;
    --reset)   rm -f data/seen.json ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# Keep these fixed. data/seen.json is keyed on the filtered set, so changing them
# makes the next run report a burst of jobs that are not actually new.
FILTERS=(--location "Toronto,Hamilton,Burlington,Oakville,Mississauga,Ontario"
         --workplace "Remote,Hybrid"
         --max-age 14)

echo "=== $(date '+%F %T') ==="
"$PY" -m jobwatch.hiringcafe.scrape
"$PY" -m jobwatch.hiringcafe.parse "${FILTERS[@]}"
if [[ "$MAIL" == "1" ]]; then
  "$PY" -m jobwatch.notify
else
  echo "(--no-mail: skipping the email)"
fi
