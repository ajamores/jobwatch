"""UKG Pro Recruiting, formerly UltiPro — `recruiting.ultipro.ca/<tenant>/JobBoard/<board>`.

The credit unions' vendor: Meridian, Alterna, Kindred and Tandia all rent it, as do
Dejero and Sandvine in Waterloo and a handful of health employers. The board page fills
itself from one JSON endpoint, and that endpoint answers a plain POST:

    POST /<tenant>/JobBoard/<board>/JobBoardView/LoadSearchResults

Every hit already carries a real posted timestamp, a requisition number, a full-time
flag and a structured address — more than most boards give up on a detail page — so
there is no `enrich`.

Tenants share hosts, so the watchlist names the tenant and the board explicitly:

    ukg  recruiting.ultipro.ca  Meridian Credit Union  tenant=MER5001MCUL,board=6c1f133f-...
"""

import re

from .. import http
from ..schema import EMPTY_SALARY, blank, clean, parse_date, parse_salary
from .successfactors import PROVINCES
from .workday import PAY

ATS = "ukg"

PAGE = 50
MAX_PAGES = 20

REMOTE = re.compile(r"\bremote\b", re.I)
HYBRID = re.compile(r"\bhybrid\b", re.I)
TAGS = re.compile(r"<[^>]+>")


def _search(skip):
    """The board's own request shape, newest first."""
    return {"opportunitySearch": {
                "Top": PAGE, "Skip": skip, "QueryString": "",
                "OrderBy": [{"Value": "postedDateDesc", "PropertyName": "PostedDate",
                             "Ascending": False}],
                "Filters": [{"t": "TermsSearchFilterDto", "fieldName": n, "extra": None,
                             "values": []} for n in (4, 5, 6)]},
            "matchCriteria": {"PreferredJobs": [], "Educations": [],
                              "LicenseAndCertifications": [], "Skills": [],
                              "hasNoLicenses": False, "SkippedSkills": []}}


def _board(site):
    tenant, board = site.extra.get("tenant"), site.extra.get("board")
    if not (tenant and board):
        raise http.Unavailable(f"{site}: ukg needs tenant=<code>,board=<guid> in watchlist.txt")
    return tenant, f"https://{site.host}/{tenant}/JobBoard/{board}"


def _place(loc):
    """'Elmira, Ontario' out of UKG's address block, or its own label as a fallback."""
    a = loc.get("Address") or {}
    city = clean(a.get("City"))
    state = a.get("State")
    code = state.get("Code") if isinstance(state, dict) else state
    name = state.get("Name") if isinstance(state, dict) else None
    region = PROVINCES.get(str(code or "").upper()) or clean(name) or clean(code)
    return ", ".join(p for p in (city, region) if p) or clean(loc.get("LocalizedDescription"))


def fetch(site):
    tenant, base = _board(site)
    jobs = []
    for page in range(MAX_PAGES):
        data = http.post_json(f"{base}/JobBoardView/LoadSearchResults", _search(page * PAGE))
        rows = data.get("opportunities") or []
        for r in rows:
            places = [p for p in (_place(loc) for loc in (r.get("Locations") or [])) if p]
            where = "; ".join(places) or None
            title = clean(r.get("Title"))
            brief = clean(TAGS.sub(" ", r.get("BriefDescription") or ""))
            published, ms, age = parse_date((r.get("PostedDate") or "")[:10])
            # Remote-ness is read from the place and the title only. Descriptions say
            # "remote monitoring" and "remote sites" far too often to be trusted.
            hint = f"{where or ''} {title or ''}"
            pay = PAY.search(brief or "")
            jobs.append(blank(
                id=f"{ATS}:{site.host}:{tenant}:{r.get('Id')}",
                collapse_key=f"{ATS}:{site.host}:{tenant}:{r.get('Id')}",
                title=title,
                company=site.label,
                company_site=base,
                location=where,
                cities=[p.split(",")[0].strip() for p in places],
                states=[p.split(",", 1)[1].strip() for p in places if "," in p],
                workplace_type=("Remote" if REMOTE.search(hint)
                                else "Hybrid" if HYBRID.search(hint) else None),
                commitment={True: "Full time", False: "Part time"}.get(r.get("FullTime")),
                category=clean(r.get("JobCategoryName")),
                requirements=(brief or "")[:400] or None,
                salary=parse_salary(pay.group(0)) if pay else dict(EMPTY_SALARY),
                published=published, published_millis=ms, age_days=age,
                source=ATS,
                apply_url=f"{base}/OpportunityDetail?opportunityId={r.get('Id')}",
            ))
        total = data.get("totalCount") or 0
        if len(rows) < PAGE or (page + 1) * PAGE >= total:
            break
    return jobs
