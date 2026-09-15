"""Work out which job-board vendor each employer in the census actually rents.

The census is 287 root domains. This resolves each one to its real careers page —
follow the homepage's own careers link, follow the redirects, read where it lands —
and names the vendor from the URL it ends at.

The point is the tally at the end, not the individual rows. Employers do not build
careers pages, they rent them, so a handful of adapters covers a long list of
employers. This says which handful, in order of how many employers each unlocks.

    python -m jobwatch.watchlist.fingerprint
    python -m jobwatch.watchlist.fingerprint --sector hospital --workers 8
"""

import argparse
import csv
import html
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlsplit

from . import ADAPTERS, http
from ..paths import DATA, ROOT

CENSUS = ROOT / "docs" / "census.tsv"
OUT = DATA / "census_vendors.tsv"

# --- what a vendor looks like ---------------------------------------------------
# Matched against the final URL first, because a URL is evidence and body text is
# only a hint — half these vendors leave their name in a stray analytics script on
# pages that have nothing to do with hiring.

BY_URL = [
    ("applytoeducation", r"applytoeducation\.com|simplication\.com"),
    ("njoyn",            r"njoyn\.com"),
    ("erecruit",         r"/erecruit/"),          # Ontario hospitals, quietly everywhere
    ("workday",          r"myworkdayjobs\.com|myworkdaysite\.com|wd\d+\.myworkday"),
    ("taleo",            r"taleo\.net|/careersection/"),
    ("icims",            r"icims\.com"),
    ("successfactors",   r"successfactors\.com|/tile-search-results|jobs2web\.com"),
    ("greenhouse",       r"greenhouse\.io"),
    ("lever",            r"lever\.co/"),
    ("bamboohr",         r"bamboohr\.com"),
    ("ukg",              r"ultipro\.c|recruiting\.ukg\.|ukg\.net"),
    ("adp",              r"workforcenow\.adp\.com|recruiting\.adp\.com|myjobs\.adp\.com"),
    ("dayforce",         r"dayforcehcm\.com"),
    ("cornerstone",      r"csod\.com"),
    ("brassring",        r"brassring\.com"),
    ("oracle-orc",       r"oraclecloud\.com/hcm|/hcmUI/CandidateExperience"),
    ("peoplesoft",       r"/psp/|/psc/[^/]+/(?:EMPLOYEE|CUSTOMER)|HRS_CE"),
    ("smartrecruiters",  r"smartrecruiters\.com"),
    ("jobvite",          r"jobvite\.com"),
    ("workable",         r"workable\.com"),
    ("ashby",            r"ashbyhq\.com"),
    ("recruitee",        r"recruitee\.com|careers-page\.com"),
    ("breezy",           r"breezy\.hr"),
    ("jazzhr",           r"applytojob\.com"),
    ("paylocity",        r"recruiting\.paylocity\.com"),
    ("peopleadmin",      r"peopleadmin\.com"),
    ("silkroad",         r"silkroad\.com|openhire\."),
    ("vidcruiter",       r"vidcruiter\.com"),
    ("fitzii",           r"fitzii\.com"),
    ("eightfold",        r"eightfold\.ai"),
    ("phenom",           r"phenompeople\.com|phenom\.com"),
    ("radancy",          r"talentbrew|radancy"),
    ("avature",          r"avature\.net"),
    ("clearcompany",     r"clearcompany\.com"),
    ("applicantpro",     r"applicantpro\.com"),
    ("bullhorn",         r"bullhorn"),
    ("hrdownloads",      r"hrdownloads\.com"),
    ("indeed-hosted",    r"indeed\.com"),
    ("linkedin-hosted",  r"linkedin\.com/jobs"),
]

# Same vendors, seen in the markup rather than the address bar. Weaker, so only
# consulted when the URL said nothing.
BY_BODY = [
    ("applytoeducation", r"applytoeducation|apply\s*to\s*education|simplication"),
    ("njoyn",            r"njoyn"),
    ("erecruit",         r"recentvacancies|erecruit"),
    ("workday",          r"myworkdayjobs|myworkdaysite|wd\d+\.myworkday"),
    ("taleo",            r"taleo"),
    ("icims",            r"icims"),
    ("successfactors",   r"successfactors|rmkcdn"),
    ("greenhouse",       r"greenhouse\.io|grnhse"),
    ("lever",            r"lever\.co"),
    ("bamboohr",         r"bamboohr"),
    ("ukg",              r"ultipro|\bukg\b"),
    ("adp",              r"workforcenow|adp\.com"),
    ("dayforce",         r"dayforce|ceridian"),
    ("cornerstone",      r"csod\.com|cornerstoneondemand"),
    ("oracle-orc",       r"oraclecloud"),
    ("peopleadmin",      r"peopleadmin"),
    ("smartrecruiters",  r"smartrecruiters"),
    ("vidcruiter",       r"vidcruiter"),
    ("eightfold",        r"eightfold"),
    ("phenom",           r"phenompeople"),
]

BLOCKED = re.compile(r"just a moment|cf-browser-verification|attention required|"
                     r"enable javascript|access denied|incapsula", re.I)

# --- finding the careers page ---------------------------------------------------

ANCHOR = re.compile(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.I | re.S)
TAGS = re.compile(r"<[^>]+>")

WORTH = (
    (r"apply\s*to\s*education|njoyn|myworkdayjobs|taleo|icims|greenhouse|lever\.co|"
     r"bamboohr|ultipro|workforcenow|dayforcehcm|csod\.com|brassring|oraclecloud", 40),
    (r"career", 12), (r"\bjobs?\b", 10), (r"employment", 9),
    (r"work[-\s]?(with|for|at)[-\s]?us", 7), (r"join[-\s]?(our[-\s]?team|us)", 7),
    (r"opportunit", 6), (r"hiring|recruit", 5), (r"human[-\s]?resources|\bhr\b", 2),
)
JUNK = re.compile(r"facebook|twitter|x\.com|instagram|linkedin\.com/(company|in)|"
                  r"youtube|mailto:|tel:|\.pdf$|\.jpg$|\.png$|javascript:", re.I)

GUESSES = ("/careers", "/careers/", "/jobs", "/employment", "/about/careers",
           "/en/careers.aspx", "/careers/current-opportunities", "/work-with-us")


def candidates(base, body):
    """Careers links on the homepage, best first. Scored on href and anchor text."""
    seen, scored = set(), []
    for href, text in ANCHOR.findall(body or ""):
        if JUNK.search(href):
            continue
        url = urljoin(base, href.strip())
        if not url.startswith("http") or url in seen:
            continue
        seen.add(url)
        hay = f"{url} {TAGS.sub(' ', text)}".lower()
        score = sum(w for pat, w in WORTH if re.search(pat, hay))
        if score:
            scored.append((score - len(urlsplit(url).path) / 100, url))
    scored.sort(reverse=True)
    return [u for _, u in scored[:4]]


URLISH = re.compile(r"https?://[^\s\"'<>)]+", re.I)


def identify(url, body):
    """(vendor, how, board_url). The address bar beats a link on the page, and a link
    beats a vendor's name mentioned somewhere in the markup.

    The middle rung matters most. An employer's own careers page usually links out to
    its board, and that link is the tenant URL an adapter needs — `stelco.wd3...` —
    not merely proof that a vendor is involved somewhere.
    """
    for name, pat in BY_URL:
        if re.search(pat, url, re.I):
            return name, "url", url
    head = (body or "")[:250_000]
    for link in URLISH.findall(html.unescape(head)):
        for name, pat in BY_URL:
            if not name.endswith("-hosted") and re.search(pat, link, re.I):
                return name, "link", link
    for name, pat in BY_BODY:
        if re.search(pat, head, re.I):
            return name, "markup", url
    if BLOCKED.search(head):
        return "?blocked", "challenge page", url
    if len(TAGS.sub(" ", head).split()) < 120:
        return "?js", "empty shell, built in the browser", url
    return "?custom", "no vendor fingerprint", url


def probe(row, depth=2, budget=8):
    """One employer: homepage -> careers link -> vendor.

    Two hops, not one. Plenty of employers put a hand-written careers page on their
    own CMS and link out from there to the board that actually holds the postings —
    stopping at the first page would file all of those as `?custom` and lose them.
    """
    domain = row["domain"]
    out = dict(row, vendor="?unreachable", careers_url="", note="")
    home = body = None
    for host in (domain, f"www.{domain}"):
        try:
            home, body = http.get(f"https://{host}/")
            break
        except http.Unavailable as e:
            out["note"] = str(e).split(" -> ")[-1]
    if home is None:
        return out

    seen = {home}
    queue = [(u, 1) for u in (candidates(home, body)
                              or [urljoin(home, g) for g in GUESSES[:4]])]
    fetched = 0
    while queue and fetched < budget:
        url, hop = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            final, page = http.get(url)
        except http.Unavailable:
            continue
        fetched += 1
        vendor, how, board = identify(final, page)
        if not vendor.startswith("?"):
            return dict(out, vendor=vendor, careers_url=board, note=how)
        # Best guess so far, in case nothing better turns up.
        if out["vendor"] in ("?unreachable", "?js") or out["vendor"] == "?custom" == vendor:
            out.update(vendor=vendor, careers_url=board, note=how)
        if hop < depth:
            queue += [(u, hop + 1) for u in candidates(final, page)[:3] if u not in seen]

    if out["vendor"] == "?unreachable":
        vendor, how, board = identify(home, body)
        out.update(vendor=vendor, careers_url=board, note=how)
    return out


# --- the run --------------------------------------------------------------------

def read_census(path=CENSUS):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 5:
            continue
        rows.append(dict(zip(("tier", "sector", "name", "city", "domain"),
                             (x.strip() for x in f[:5]))))
    return rows


def read_vendors(path):
    """Whatever the last pass concluded, so a re-run can skip the settled rows."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sector", help="only this sector")
    ap.add_argument("--tier", help="only this tier (A, B, C)")
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--only-unresolved", action="store_true",
                    help="re-probe only the rows the last pass filed as ?something")
    ap.add_argument("--recheck-markup", action="store_true",
                    help="re-probe rows whose only evidence was a vendor name in the markup")
    a = ap.parse_args(argv)

    rows = read_census()
    if a.sector:
        rows = [r for r in rows if r["sector"] == a.sector]
    if a.tier:
        rows = [r for r in rows if r["tier"] == a.tier.upper()]
    # A re-run merges with the last pass rather than replacing it: only the rows that
    # need another look are probed, and everything settled is carried forward.
    redo = None
    if a.only_unresolved:
        redo = lambda r: r["vendor"].startswith("?")          # noqa: E731
    if a.recheck_markup:
        redo = lambda r: r.get("note") == "markup"            # noqa: E731
    settled = []
    if redo:
        live = {r["domain"] for r in read_census()}
        prior = {r["domain"]: r for r in read_vendors(OUT) if r["domain"] in live}
        settled = [r for r in prior.values() if not redo(r)]
        rows = [r for r in rows if r["domain"] not in prior or redo(prior[r["domain"]])]
    # A census is a one-off survey, not the 15-minute watch. A host that has not
    # answered in 12 seconds is recorded as unreachable and looked at by hand,
    # rather than retried into an 80-second stall per dead domain.
    http.TIMEOUT, http.RETRIES = 12, 0
    print(f"fingerprinting {len(rows)} employers, {a.workers} at a time", file=sys.stderr)

    done = list(settled)
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(probe, r) for r in rows]
        for i, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            done.append(res)
            print(f"  {i:>3}/{len(rows)}  {res['vendor']:<18} {res['name']}",
                  file=sys.stderr, flush=True)

    cols = ("tier", "sector", "name", "city", "domain", "vendor", "careers_url", "note")
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t", extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(done, key=lambda r: (r["vendor"], r["sector"], r["name"])))

    tally = {}
    for r in done:
        tally[r["vendor"]] = tally.get(r["vendor"], 0) + 1
    print(f"\n{len(done)} employers -> {a.out}\n")
    print(f"{'vendor':<20}{'employers':>10}   {'adapter?':<10}")
    have = set(ADAPTERS)
    for vendor, n in sorted(tally.items(), key=lambda kv: -kv[1]):
        mark = "have it" if vendor in have else ("—" if vendor.startswith("?") else "TO BUILD")
        print(f"{vendor:<20}{n:>10}   {mark:<10}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
