"""Which postings are worth waking Armand up for.

The employer boards in watchlist.txt are unfiltered: Canada Post lists 260 postings and
almost all of them are letter carriers. hiring.cafe did this narrowing server-side; here
it has to happen after the fetch.

Kept as data in filters.txt rather than code, so the criteria can change without anyone
editing a module.
"""

import re
from pathlib import Path

# A comment starts a line or follows whitespace. Without that second rule the "#" in
# "+ c#" reads as a comment marker, leaving a bare "c" that matches almost every title.
COMMENT = re.compile(r"(?:^|\s)#")


class Filters:
    def __init__(self, include=(), exclude=(), places=()):
        self.include, self.exclude, self.places = list(include), list(exclude), list(places)

    def __bool__(self):
        return bool(self.include or self.exclude or self.places)

    @staticmethod
    def _hit(patterns, text):
        return next((p for p in patterns if re.search(Filters._pattern(p), text)), None)

    @staticmethod
    def _pattern(p):
        """Long words match their own plurals — "developer" should catch "developers".

        Short ones must not: a leading-only guard lets "it" match "Item" and "qa" match
        "Qatar", so anything three characters or shorter is pinned at both ends.
        """
        body = re.escape(p)
        return rf"(?<!\w){body}(?!\w)" if len(p) <= 3 else rf"(?<!\w){body}"

    def verdict(self, job):
        """(keep, why) — why names the rule that decided it, for the run summary."""
        title = (job.get("title") or "").lower()
        bad = self._hit(self.exclude, title)
        if bad:
            return False, f"excluded: {bad}"
        if self.include and not self._hit(self.include, title):
            return False, "no title match"
        if self.places:
            where = " ".join(str(job.get(k) or "") for k in ("location", "cities", "states")).lower()
            # An unknown location is not a reason to drop a hand-picked employer.
            if where.strip() and not self._hit(self.places, where):
                return False, "wrong place"
        return True, "kept"

    def apply(self, jobs):
        kept, dropped = [], {}
        for job in jobs:
            ok, why = self.verdict(job)
            if ok:
                kept.append(job)
            else:
                dropped[why] = dropped.get(why, 0) + 1
        return kept, dropped


def load(path):
    """+ keep-if-title-matches, - always-drop, @ acceptable place. # comments."""
    include, exclude, places = [], [], []
    for raw in Path(path).read_text().splitlines():
        line = COMMENT.split(raw, 1)[0].strip()
        if not line:
            continue
        mark, _, value = line.partition(" ")
        value = value.strip().lower()
        if not value:
            continue
        {"+": include, "-": exclude, "@": places}.get(mark, []).append(value)
    return Filters(include, exclude, places)
