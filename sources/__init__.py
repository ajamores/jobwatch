"""Adapters: one module per job-board vendor, not one per employer.

Every adapter exposes the same two things, so `sites.py` never needs to know which
vendor it is talking to:

    fetch(site)          -> [job, ...]   cheap; runs on every check
    enrich(site, jobs)   -> None         optional; per-posting detail, new postings only

`job` is the dict defined in schema.py — the same shape parse.py produces for
hiring.cafe, so export.py and notify.py work unchanged.
"""

from dataclasses import dataclass, field

from . import bamboohr, greenhouse, successfactors

ADAPTERS = {m.ATS: m for m in (bamboohr, greenhouse, successfactors)}


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
        parts = [p.strip() for p in __import__("re").split(r"\s{2,}", line) if p.strip()]
        if len(parts) < 2:
            problems.append(f"line {n}: need at least 'ats  host' — {raw.strip()!r}")
            continue
        ats, host, *rest = parts
        if ats not in ADAPTERS:
            problems.append(f"line {n}: no adapter for {ats!r} (have: "
                            f"{', '.join(sorted(ADAPTERS))})")
            continue
        extra = {}
        if rest and "=" in rest[-1] and " " not in rest[-1]:
            for pair in rest.pop().split(","):
                k, _, v = pair.partition("=")
                extra[k.strip()] = v.strip()
        sites.append(Site(ats, host, rest[0] if rest else host, extra))
    return sites, problems
