"""Workday job boards — `<tenant>.wd<N>.myworkdayjobs.com`.

The biggest vendor in the institutional census by a distance: the pension plans, the
LCBO-and-OLG tier of provincial agencies, hospitals, towns, Stelco, Enbridge. Every
tenant sits on the same public JSON API the careers page itself calls, so one adapter
covers all of them. No browser, no auth.

    POST /wday/cxs/<tenant>/<site>/jobs       twenty postings a page, by offset
    GET  /wday/cxs/<tenant>/<site><path>      one posting, with the description

The watchlist carries the host plus the site — the first path segment of the board's
public URL. The tenant is the host's first label unless `tenant=` says otherwise:

    workday  stelco.wd3.myworkdayjobs.com  Stelco  site=Stelco
    workday  wd3.myworkdaysite.com         Magna   site=Magna,tenant=magna

Global boards are narrowed server-side with `facet=<parameter>:<id>`, using the board's
own filter. Magna posts 1,428 jobs worldwide and 203 in Canada; only the second number
is worth paging through every fifteen minutes:

    workday  wd3.myworkdaysite.com  Magna  site=Magna,tenant=magna,facet=Country:a30a...

The parameter is whatever the facet itself calls itself, and for location that is the
*child*: `locationCountry`, not the `locationMainGroup` group it sits inside, which
answers 400. Magna is the odd one out in exposing `Country` at the top level.

Two quirks. `total` is only reported on the first page — later pages claim 0 — so
paging stops on a short page, never on the count. And the listing only says "Posted 3
Days Ago"; the real date arrives with the detail call in `enrich`.
"""

import re
import time
from datetime import date, timedelta
from html import unescape

from .. import http
from ..schema import blank, clean, parse_date, parse_salary

ATS = "workday"

PAGE = 20
MAX_PAGES = 50        # a thousand postings — nobody on this list is that big

REMOTE = re.compile(r"\bremote\b", re.I)
HYBRID = re.compile(r"\bhybrid\b", re.I)
AGO = re.compile(r"(\d+)\+?\s*days?\s*ago", re.I)
MULTI = re.compile(r"^\d+\s+locations?$", re.I)
PAY = re.compile(r"\$\s?(?:\d{1,3}(?:,\d{3})+|\d{4,}|\d{2,3}\.\d{2})(?:\.\d{2})?"
                 r"(?:\s*(?:-|–|to)\s*\$?\s?[\d,]+(?:\.\d{2})?)?[^.\n]{0,40}")


def _age(text):
    """'Posted Today', 'Posted Yesterday', 'Posted 3 Days Ago', 'Posted 30+ Days Ago'."""
    t = (text or "").lower()
    if "today" in t:
        return 0
    if "yesterday" in t:
        return 1
    m = AGO.search(t)
    return int(m.group(1)) if m else None


def _dated(days):
    """An age in days, as the (iso, millis, age_days) triple the schema carries."""
    if days is None:
        return None, None, None
    d = date.today() - timedelta(days=days)
    return d.isoformat(), int(time.mktime(d.timetuple()) * 1000), days


def _workplace(text):
    if not text:
        return None
    if REMOTE.search(text):
        return "Remote"
    if HYBRID.search(text):
        return "Hybrid"
    return "Onsite" if re.search(r"on[-\s]?site|in[-\s]office", text, re.I) else None


def _urls(site):
    """(api_base, public_base) for one tenant."""
    name = site.extra.get("site")
    if not name:
        raise http.Unavailable(f"{site}: workday needs site=<name> in watchlist.txt")
    shared = "myworkdaysite" in site.host
    if shared and not site.extra.get("tenant"):
        raise http.Unavailable(f"{site}: myworkdaysite.com hosts need tenant=<name>")
    tenant = site.extra.get("tenant") or site.host.split(".")[0]
    # A few tenants live on the shared myworkdaysite.com host instead of their own
    # subdomain. There the tenant cannot be read off the host, and the public URL
    # carries it: wd3.myworkdaysite.com/recruiting/magna/Magna.
    public = (f"https://{site.host}/recruiting/{tenant}/{name}" if shared
              else f"https://{site.host}/{name}")
    return f"https://{site.host}/wday/cxs/{tenant}/{name}", public


def _facets(site):
    """facet=<parameter>:<id> -> the appliedFacets body the board's own filter sends."""
    param, _, value = (site.extra.get("facet") or "").partition(":")
    return {param: [value]} if param and value else {}


def fetch(site):
    api, public = _urls(site)
    jobs = []
    for page in range(MAX_PAGES):
        data = http.post_json(f"{api}/jobs", {"appliedFacets": _facets(site), "limit": PAGE,
                                              "offset": page * PAGE, "searchText": ""})
        rows = data.get("jobPostings") or []
        for r in rows:
            path = r.get("externalPath") or ""
            ref = (r.get("bulletFields") or [path])[0]
            where = clean(r.get("locationsText"))
            published, ms, age = _dated(_age(r.get("postedOn")))
            jobs.append(blank(
                id=f"{ATS}:{site.host}:{ref}",
                collapse_key=f"{ATS}:{site.host}:{ref}",
                title=clean(r.get("title")),
                company=site.label,
                company_site=public,
                location=where,
                cities=[where] if where and not MULTI.match(where) else [],
                workplace_type=_workplace(where),
                published=published, published_millis=ms, age_days=age,
                source=ATS,
                apply_url=f"{public}{path}" if path else public,
            ))
        if len(rows) < PAGE:
            break
    return jobs


def enrich(site, jobs):
    """Description, the real posting date, pay and work model — new postings only."""
    api, public = _urls(site)
    for job in jobs:
        path = (job.get("apply_url") or "")[len(public):]
        if not path.startswith("/job/"):
            continue
        try:
            info = http.get_json(f"{api}{path}").get("jobPostingInfo") or {}
        except http.Unavailable:
            continue
        # Descriptions arrive HTML-escaped, and some tenants escape them twice — one
        # pass leaves &#xa; sitting in the middle of a salary. Unescape, then strip.
        body = info.get("jobDescription") or ""
        for _ in range(2):
            body = re.sub(r"<[^>]+>", " ", unescape(body))
        body = " ".join(body.split())
        job["requirements"] = body[:400] or None
        job["commitment"] = clean(info.get("timeType")) or job["commitment"]
        if info.get("location"):
            job["location"] = clean(info["location"])
        job["workplace_type"] = _workplace(info.get("remoteType")) or job["workplace_type"]
        published, ms, age = parse_date((info.get("startDate") or "")[:10])
        if published:
            job.update(published=published, published_millis=ms, age_days=age)
        pay = PAY.search(body)
        if pay:
            job["salary"] = parse_salary(pay.group(0))
