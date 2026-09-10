"""Greenhouse job boards.

The friendliest source in the whole watchlist: a public JSON API, no auth, no browser,
and — unlike every SuccessFactors tenant — a real `first_published` timestamp, which is
the field the rest of this project keeps wishing for.

    /v1/boards/<token>/jobs             every open posting
    /v1/boards/<token>/jobs/<id>        the same plus the description

`<token>` is the board name in the company's Greenhouse URL, so the watchlist carries the
token where other adapters carry a hostname:

    greenhouse  faire  Faire
"""

import re
from html import unescape

from . import http
from .schema import blank, clean, parse_date, parse_salary

ATS = "greenhouse"

API = "https://boards-api.greenhouse.io/v1/boards"

REMOTE = re.compile(r"\bremote\b", re.I)
HYBRID = re.compile(r"\bhybrid\b", re.I)


def _meta(job, name):
    for m in job.get("metadata") or []:
        if (m.get("name") or "").lower() == name and m.get("value") not in (None, ""):
            return clean(str(m["value"]))
    return None


def fetch(site):
    data = http.get_json(f"{API}/{site.host}/jobs")
    jobs = []
    for r in data.get("jobs") or []:
        where = clean((r.get("location") or {}).get("name"))
        # Greenhouse lists multi-site roles as "New York City, NY; Toronto, ON".
        places = [clean(p) for p in (where or "").split(";") if clean(p)]
        published, ms, age = parse_date((r.get("first_published") or "")[:10])
        jobs.append(blank(
            id=f"{ATS}:{site.host}:{r.get('id')}",
            collapse_key=f"{ATS}:{site.host}:{r.get('id')}",
            title=clean(r.get("title")),
            company=clean(r.get("company_name")) or site.label,
            company_site=f"https://boards.greenhouse.io/{site.host}",
            location=where,
            cities=[p.split(",")[0].strip() for p in places],
            workplace_type=("Remote" if where and REMOTE.search(where)
                            else "Hybrid" if where and HYBRID.search(where) else None),
            commitment=_meta(r, "employment type"),
            published=published, published_millis=ms, age_days=age,
            source=ATS,
            apply_url=r.get("absolute_url"),
        ))
    return jobs


def enrich(site, jobs):
    """Pull the description for postings we have not reported before."""
    for job in jobs:
        native = job["id"].rsplit(":", 1)[-1]
        try:
            d = http.get_json(f"{API}/{site.host}/jobs/{native}")
        except http.Unavailable:
            continue
        # Greenhouse stores the description HTML-escaped, so unescape first or the
        # tags come back to life after stripping and end up inside the salary.
        body = d.get("content") or ""
        for _ in range(2):
            body = re.sub(r"<[^>]+>", " ", unescape(body))
        job["requirements"] = (clean(body) or "")[:400] or None
        pay = re.search(r"\$[\d,]{4,}(?:\s*(?:-|–|to)\s*\$?[\d,]{4,})?[^.\n]{0,40}", body)
        if pay:
            job["salary"] = parse_salary(pay.group(0))
