"""The watchlist stream: named employers, checked on their own boards.

`check` runs one pass over every site in watchlist.txt; the vendor-specific work
lives in `adapters`, so `check` never needs to know which vendor it is talking
to. Every adapter returns the record defined in `schema.py` — the same shape
`hiringcafe.parse` produces, so `notify` and `export` work against either stream.
"""

import re
from dataclasses import dataclass, field

from .adapters import adp, bamboohr, greenhouse, successfactors, ukg, workday

ADAPTERS = {m.ATS: m for m in (adp, bamboohr, greenhouse, successfactors, ukg, workday)}


@dataclass
class Site:
    ats: str
    host: str
    label: str
    extra: dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.label} ({self.host})"


def parse_watchlist(text):
    """ats  host  label  [key=value,key=value]  — blank lines and # comments ignored.

    Fields are separated by two or more spaces so labels may contain single spaces.
    """
    sites, problems = [], []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = [p.strip() for p in re.split(r"\s{2,}", line) if p.strip()]
        if len(parts) < 2:
            problems.append(f"line {n}: need at least 'ats  host' — {raw.strip()!r}")
            continue
        ats, host, *rest = parts
        if ats not in ADAPTERS:
            problems.append(f"line {n}: no adapter for {ats!r} (have: "
                            f"{', '.join(sorted(ADAPTERS))})")
            continue
        extra = {}
        # Extras may carry a place with a space in it — where=St. Catharines — so
        # recognise them by a leading key= rather than by having no spaces.
        if rest and re.match(r"^[a-z_]+=", rest[-1]):
            for pair in rest.pop().split(","):
                k, _, v = pair.partition("=")
                extra[k.strip()] = v.strip()
        sites.append(Site(ats, host, rest[0] if rest else host, extra))
    return sites, problems
