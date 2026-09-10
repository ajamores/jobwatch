"""Where things live, anchored to the repo rather than to the working directory.

Cron hands a script an unhelpful `cwd`, so nothing here is relative.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "config"      # hand-edited: the watchlist, the filters, the profile
DATA = ROOT / "data"          # state and generated output; disposable, gitignored
EXPORTS = ROOT / "exports"    # spreadsheets meant for a human

for d in (DATA, EXPORTS):
    d.mkdir(exist_ok=True)
