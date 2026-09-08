"""Locating Chrome, on whichever machine this happens to be running."""

import os
import shutil
import sys
from pathlib import Path

MAC = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CANDIDATES = [
    MAC,
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def executable_path():
    """CHROME_PATH wins; otherwise the first candidate that exists."""
    override = os.getenv("CHROME_PATH")
    if override:
        if not Path(override).exists():
            sys.exit(f"CHROME_PATH points at nothing: {override}")
        return override
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit("no Chrome found — set CHROME_PATH in .env or the environment")
