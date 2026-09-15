"""ADP Workforce Now recruitment — `workforcenow.adp.com/...recruitment.html?cid=<cid>`.

The independent schools' vendor — Upper Canada College, Branksome, Bishop Strachan — plus
Markham, the Royal Botanical Gardens, Niagara Parks, Cowan Insurance and the Vector
Institute. Every tenant lives on the one host and is told apart by its client id. The
career centre reads a public JSON feed, and the feed answers a plain GET:

    /mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid=<cid>

Real post dates, and a structured pay range wherever the employer filled one in — which,
under Ontario's pay-transparency rules, is increasingly all of them. No `enrich`.

    adp  workforcenow.adp.com  City of Markham  cid=04bf51f8-d2dd-4641-ba92-...
"""

import time

from .. import http
from ..schema import EMPTY_SALARY, blank, clean, parse_date, parse_salary
from .successfactors import PROVINCES

ATS = "adp"

FEED = "https://{host}/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions"
BOARD = "https://{host}/mascsr/default/mdf/recruitment/recruitment.html"

PAGE = 100
MAX_PAGES = 10


def _cid(site):
    cid = site.extra.get("cid")
    if not cid:
        raise http.Unavailable(f"{site}: adp needs cid=<client id> in watchlist.txt")
    return cid


def _place(loc):
    """'Markham, Ontario' from ADP's address block. Some tenants leave the city blank."""
    a = loc.get("address") or {}
    city = clean(a.get("cityName"))
    sub = a.get("countrySubdivisionLevel1") or {}
    code = sub.get("codeValue") if isinstance(sub, dict) else None
    region = PROVINCES.get(str(code or "").upper()) or clean(code)
    return ", ".join(p for p in (city, region) if p) or None


def _salary(r):
    """The structured range, when there is one. The currency is ADP's, never inferred."""
    rng = r.get("payGradeRange") or {}
    lo_rate, hi_rate = rng.get("minimumRate") or {}, rng.get("maximumRate") or {}
    lo, hi = lo_rate.get("amountValue"), hi_rate.get("amountValue")
    if lo is None and hi is None:
        return dict(EMPTY_SALARY)
    sal = parse_salary(" - ".join(str(v) for v in (lo, hi) if v is not None))
    sal["currency"] = lo_rate.get("currencyCode") or hi_rate.get("currencyCode")
    return sal


def fetch(site):
    cid = _cid(site)
    feed, board = FEED.format(host=site.host), BOARD.format(host=site.host)
    jobs = []
    for page in range(MAX_PAGES):
        data = http.get_json(f"{feed}?cid={cid}&timeStamp={int(time.time() * 1000)}"
                             f"&lang=en_CA&locale=en_CA&$top={PAGE}&$skip={page * PAGE}")
        rows = data.get("jobRequisitions") or []
        for r in rows:
            places = [p for p in (_place(loc) for loc in (r.get("requisitionLocations") or [])) if p]
            published, ms, age = parse_date((r.get("postDate") or "")[:10])
            item = r.get("itemID")
            level = r.get("workLevelCode")
            jobs.append(blank(
                id=f"{ATS}:{site.host}:{cid}:{item}",
                collapse_key=f"{ATS}:{site.host}:{cid}:{item}",
                title=clean(r.get("requisitionTitle")),
                company=site.label,
                company_site=f"{board}?cid={cid}",
                location="; ".join(places) or None,
                cities=[p.split(",")[0].strip() for p in places],
                states=[p.split(",", 1)[1].strip() for p in places if "," in p],
                commitment=clean(level.get("shortName")) if isinstance(level, dict) else None,
                salary=_salary(r),
                published=published, published_millis=ms, age_days=age,
                source=ATS,
                apply_url=f"{board}?cid={cid}&ccId=19000101_000001&jobId={item}&lang=en_CA",
            ))
        total = (data.get("meta") or {}).get("totalNumber") or 0
        if len(rows) < PAGE or (page + 1) * PAGE >= total:
            break
    return jobs
