"""SAP SuccessFactors (RMK) career sites — one adapter, twelve employers.

City of Toronto, Canada Post, Purolator and Scotiabank are unrelated organisations that
all rent the same SAP careers product, so they answer the same URL:

    https://<host><path>/tile-search-results/?q=&sortColumn=referencedate&startrow=<N>

That returns a page of job tiles, newest first. The markup is SAP's own template, so the
structural bits (`li.job-tile`, `job-id-<n>`, `data-url`, `a.jobTitle-link`) are stable
across tenants. Everything else is tenant-configured: Toronto prints a posting date and a
job stream, Scotiabank prints nothing but the title. So the tile fields are read by their
printed label, and anything absent stays None rather than being guessed at.
"""

import re
from html import unescape
from urllib.parse import unquote, urljoin

from .. import http
from ..schema import blank, clean, parse_date, parse_salary

# Tenants that print no location column still encode one in the posting slug:
#   /job/Toronto-Performance-Engineer-ON-M5H3Y2/605123817/
# Reading it is what keeps a Bogota req out of a Golden Horseshoe search.
PROVINCES = {
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador", "NS": "Nova Scotia", "NT": "Northwest Territories",
    "NU": "Nunavut", "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec",
    "SK": "Saskatchewan", "YT": "Yukon",
}
POSTAL = re.compile(r"^(?:[A-Z]\d[A-Z]|\d[A-Z]\d|\d{5})$")


def _from_slug(url):
    """(city, region) out of a posting slug. None rather than a guess when unclear."""
    m = re.search(r"/job/([^/]+)/", unquote(url or ""))
    if not m:
        return None, None
    parts = [p for p in m.group(1).split("-") if p]
    while parts and POSTAL.match(parts[-1].upper()):
        parts.pop()
    region = None
    if len(parts) > 1 and re.fullmatch(r"[A-Z]{2}", parts[-1]):
        region = PROVINCES.get(parts[-1].upper(), parts[-1].upper())
        parts.pop()
    city = parts[0].strip(" ,.") if parts and not parts[0].isupper() else None
    return city, region

ATS = "successfactors"

PATH = "/tile-search-results/?q=&sortColumn=referencedate&sortDirection=desc&startrow={row}"
MAX_ROWS = 250          # newest-first, so the tail is old news
TILE = re.compile(r'<li class="job-tile[^"]*job-id-(\d+)[^"]*"[^>]*data-url="([^"]*)"', re.I)
TITLE = re.compile(r'<a class="jobTitle-link[^"]*"[^>]*>(.*?)</a>', re.I | re.S)

# Tenants label their tile columns differently. Map what they print to what we store.
LABELS = {
    "published": ("posting date", "date posted", "posted date", "date", "start date"),
    "location":  ("location", "locations", "city", "work location", "job location",
                  "primary location"),
    "commitment": ("position type", "employment type", "job type", "schedule",
                   "employment status", "work type", "hours"),
    "category":  ("job stream", "job function", "department", "job field", "category",
                  "business unit", "job category", "division"),
    "salary":    ("salary", "compensation", "pay", "rate of pay", "hiring range",
                  "salary range"),
    "seniority": ("career level", "experience level", "seniority"),
}
LOOKUP = {name: field for field, names in LABELS.items() for name in names}


def _fragments(tile_html):
    """Tile text as a flat list of non-empty fragments: [label, value, label, value...]."""
    text = re.sub(r"<[^>]+>", "\x00", tile_html)
    return [f for f in (clean(unescape(x)) for x in text.split("\x00")) if f]


def _tiles(body):
    """Split the page into one chunk per posting, keyed by SAP's own job id."""
    starts = [(m.start(), m.group(1), m.group(2)) for m in TILE.finditer(body)]
    for i, (pos, native, url) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(body)
        yield native, url, body[pos:end]


def _page(site, base, row):
    _, body = http.get(base + PATH.format(row=row))
    jobs = []
    for native, url, tile in _tiles(body):
        titles = TITLE.findall(tile)          # SAP repeats it per breakpoint
        title = clean(unescape(re.sub(r"<[^>]+>", " ", titles[0]))) if titles else None
        job = blank(
            id=f"{ATS}:{site.host}:{native}",
            collapse_key=f"{ATS}:{site.host}:{native}",
            title=title,
            company=site.label,
            company_site=base,
            source=ATS,
            # data-url is relative to the host and already carries the career-site
            # prefix, so joining it to `base` would double it (/dofasco/dofasco/...).
            apply_url=urljoin(f"https://{site.host}", url) if url else None,
        )
        frags = _fragments(tile)
        for i, frag in enumerate(frags[:-1]):
            field = LOOKUP.get(frag.lower().rstrip(":"))
            value = frags[i + 1]
            if not field or value.lower().rstrip(":") in LOOKUP:
                continue                       # a label followed by another label
            if field == "published":
                iso, ms, age = parse_date(value)
                job["published"], job["published_millis"], job["age_days"] = iso, ms, age
            elif field == "salary":
                job["salary"] = parse_salary(value)
            elif not job[field]:
                job[field] = value
        if not job["location"] and job["apply_url"]:
            city, region = _from_slug(job["apply_url"])
            job["location"] = ", ".join(x for x in (city, region) if x) or None
            job["states"] = [region] if region else []
        if job["location"]:
            job["cities"] = [job["location"].split(",")[0].strip()]
        if job["title"]:
            jobs.append(job)
    return jobs


def fetch(site):
    """Page through newest-first until the tiles run out or MAX_ROWS is reached.

    `path=` in watchlist.txt names the career-site prefix for tenants that use one
    (Ottawa's /city-jobs, Dofasco's /dofasco). Most answer at the root too, so an empty
    first page falls back there before giving up.
    """
    prefix = (site.extra.get("path") or "").rstrip("/")
    for base in dict.fromkeys([f"https://{site.host}{prefix}", f"https://{site.host}"]):
        jobs, row, size = [], 0, None
        while row < MAX_ROWS:
            page = _page(site, base, row)
            if not page:
                break
            new = [j for j in page if j["id"] not in {x["id"] for x in jobs}]
            jobs.extend(new)
            size = size or len(page)
            if len(page) < size or not new:
                break
            row += size
        if jobs:
            return jobs
    return []
