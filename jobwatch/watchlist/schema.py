"""The one job shape everything downstream already expects.

`parse.py` flattens hiring.cafe's records into this dict; `export.py` and `notify.py`
read it. Adapters here produce the same dict from a different source, so nothing
downstream has to know where a posting came from.
"""

import re
import time
from datetime import datetime

DAY_MS = 86_400_000

EMPTY_SALARY = {"min": None, "max": None, "currency": None, "frequency": None,
                "text": None, "transparent": False}


def blank(**over):
    """A job record with every key present, so no consumer can KeyError."""
    job = {
        "id": None, "collapse_key": None, "title": None, "company": None,
        "company_site": None, "tagline": None, "location": None,
        "cities": [], "states": [], "countries": [], "workplace_type": None,
        "commitment": None, "seniority": None, "yoe": None, "salary": dict(EMPTY_SALARY),
        "category": None, "role_type": None, "tech": [], "requirements": None,
        "visa_sponsorship": None, "published": None, "published_millis": None,
        "age_days": None, "expired": False, "source": None, "applies": None,
        "views": None, "apply_url": None, "first_seen": None,
    }
    job.update(over)
    return job


DATE_FORMATS = (
    "%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d/%m/%Y", "%m/%d/%Y",
    "%d-%b-%Y", "%Y/%m/%d",
)


def parse_date(text):
    """(iso, millis, age_days) from whatever the board felt like printing."""
    if not text:
        return None, None, None
    t = " ".join(str(text).split()).strip(" .,")
    t = re.sub(r"^(posted|posting date|date posted)\s*:?\s*", "", t, flags=re.I)
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(t, fmt)
        except ValueError:
            continue
        ms = int(dt.timestamp() * 1000)
        return dt.strftime("%Y-%m-%d"), ms, round((time.time() * 1000 - ms) / DAY_MS)
    return None, None, None


MONEY = re.compile(r"\$?\s*([\d][\d,\.]*)\s*(?:-|–|to)?\s*\$?\s*([\d][\d,\.]*)?", re.I)
FREQ = (("Hourly", r"hour|hourly|/\s*hr|per hour"), ("Yearly", r"year|annum|annual|yearly|/\s*yr"),
        ("Monthly", r"month|monthly"), ("Weekly", r"week|weekly"))


def parse_salary(text):
    """Boards print compensation as prose. Read what is readable, invent nothing."""
    if not text:
        return dict(EMPTY_SALARY)
    t = " ".join(str(text).split())
    m = MONEY.search(t)
    if not m:
        return dict(EMPTY_SALARY, text=t or None)

    def num(s):
        if not s:
            return None
        try:
            return float(s.replace(",", ""))
        except ValueError:
            return None

    lo, hi = num(m.group(1)), num(m.group(2))
    freq = next((label for label, pat in FREQ if re.search(pat, t, re.I)), None)
    if freq is None and lo is not None:
        freq = "Hourly" if lo < 500 else "Yearly"   # nobody earns $40/yr or $40k/hr
    cur = "CAD" if re.search(r"\bcad\b|\bc\$", t, re.I) else ("USD" if "$" in t else None)
    return {"min": lo, "max": hi, "currency": cur, "frequency": freq,
            "text": t, "transparent": lo is not None}


def clean(text):
    return " ".join(str(text).split()).strip() or None if text else None
