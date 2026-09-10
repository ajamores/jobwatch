"""BambooHR careers sites.

Two public JSON endpoints, no auth, no browser:

    /careers/list          every open posting (id, title, department, location)
    /careers/<id>/detail   datePosted, compensation, full description

The list call is cheap, so it runs every time. Detail is one request per posting, so
it only runs for postings the watchlist has not seen before.
"""

import re
from html import unescape

from . import http
from .schema import blank, clean, parse_date, parse_salary

ATS = "bamboohr"

REMOTE = {"1": "Remote", "2": "Hybrid", "0": "Onsite"}


def _base(site):
    return f"https://{site.host}"


def fetch(site):
    data = http.get_json(f"{_base(site)}/careers/list")
    jobs = []
    for r in data.get("result") or []:
        loc = r.get("location") or {}
        city, state = clean(loc.get("city")), clean(loc.get("state"))
        native = str(r.get("id"))
        jobs.append(blank(
            id=f"{ATS}:{site.host}:{native}",
            collapse_key=f"{ATS}:{site.host}:{native}",
            title=clean(r.get("jobOpeningName")),
            company=site.label,
            company_site=_base(site),
            location=", ".join(x for x in (city, state) if x) or None,
            cities=[city] if city else [],
            states=[state] if state else [],
            workplace_type=("Remote" if r.get("isRemote")
                            else REMOTE.get(str(r.get("locationType")))),
            commitment=clean(r.get("employmentStatusLabel")),
            category=clean(r.get("departmentLabel")),
            source=ATS,
            apply_url=f"{_base(site)}/careers/{native}",
        ))
    return jobs


def _summary(html_text, limit=400):
    """The description is HTML. Keep a readable opening line, not the markup."""
    if not html_text:
        return None
    text = re.sub(r"<br\s*/?>|</p>|</li>", " ", str(html_text))
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return (clean(text) or "")[:limit] or None


def enrich(site, jobs):
    """Fill in posting date and pay. One request per job, so only ever the new ones."""
    for job in jobs:
        native = job["id"].rsplit(":", 1)[-1]
        try:
            d = http.get_json(f"{_base(site)}/careers/{native}/detail")
        except http.Unavailable:
            continue   # a missing detail is a thinner row, not a failed run
        opening = ((d.get("result") or {}).get("jobOpening")) or {}
        iso, ms, age = parse_date(opening.get("datePosted"))
        job["published"], job["published_millis"], job["age_days"] = iso, ms, age
        job["salary"] = parse_salary(opening.get("compensation"))
        job["seniority"] = clean(opening.get("minimumExperience"))
        job["requirements"] = _summary(opening.get("description"))
        loc = opening.get("location") or {}
        if not job["location"]:
            job["location"] = clean(", ".join(
                str(x) for x in (loc.get("city"), loc.get("state")) if x))
