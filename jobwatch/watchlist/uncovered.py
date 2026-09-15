"""What the census found and the watchlist does not cover — as something to read.

`docs/unresolved.txt` explains the vendors. This writes the other half: every employer
still out of reach, grouped by sector, closest first, each with a link to its real
careers page so it can be checked by hand.

Re-run it whenever the watchlist or the census changes, or the file goes stale:

    python -m jobwatch.watchlist.uncovered
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from html import unescape
from urllib.parse import parse_qs, unquote, urlsplit, urlunsplit

from . import parse_watchlist
from ..paths import CONFIG, DATA, ROOT

CENSUS = ROOT / "docs" / "census.tsv"
VENDORS = DATA / "census_vendors.tsv"
OUT = ROOT / "docs" / "check-by-hand.md"

# The watchlist label and the census name are normally identical, and where they differ
# it is a trailing word — "Enbridge" for "Enbridge Gas" — so matching is a prefix at a
# word boundary. Never a shared first word: that folds Halton Healthcare into Halton
# Region and Brantford Public Library into Brantford Police. Irregular ones are named.
ALIAS = {
    "procor limited": "procor marmon",
    "oakville enterprises oakville hydro": "oakville hydro",
}

SECTORS = [
    ("schoolboard", "K-12 school boards"), ("library", "Public libraries"),
    ("hospital", "Hospitals & health networks"), ("university", "Colleges & universities"),
    ("school", "Independent schools"), ("municipal", "Municipal & regional government"),
    ("police", "Police services"), ("finance", "Insurance, mutuals, credit unions, pensions"),
    ("tech", "Tech"), ("industry", "Manufacturing & industrial"),
    ("utility", "Utilities & energy"), ("transport", "Transport & infrastructure"),
    ("agency", "Crown corporations & agencies"),
    ("conservation", "Conservation authorities & attractions"), ("nonprofit", "Non-profits"),
]

WHY = {
    "applytoeducation": "ApplyToEducation — **login-walled**, no public listing",
    "njoyn": "Njoyn — bot wall, needs a browser",
    "icims": "iCIMS — refuses plain scripts (405)",
    "dayforce": "Dayforce — adapter not built",
    "taleo": "Taleo — adapter not built",
    "erecruit": "MediSolution eRecruit — adapter not built",
    "oracle-orc": "Oracle Recruiting — adapter not built",
    "cornerstone": "Cornerstone — adapter not built",
    "smartrecruiters": "SmartRecruiters — adapter not built",
    "peoplesoft": "PeopleSoft — adapter not built",
    "?custom": "no vendor — hand-built page, needs its own scraper",
    "?js": "page builds itself in the browser",
    "?blocked": "Cloudflare / WAF",
}
SUPPORTED = {"workday", "ukg", "adp", "successfactors", "bamboohr", "greenhouse"}

# Employers whose fingerprint is misleading. Left in the census, explained honestly here.
OVERRIDE = {
    "hopaports.ca": ("https://www.hopaports.ca/about-hopa/people-and-careers/",
                     "false match — the board it links to belongs to a port tenant "
                     "(BWC Terminals), not HOPA"),
    "ferrerocareers.com": (None, "fingerprint keeps mis-firing — confirmed NOT "
                                 "SuccessFactors, real vendor unknown"),
    "caasco.com": ("https://www.caasco.com/about/careers",
                   "the link found points at an SAP *staging* host; live board not identified"),
    "rhpl.ca": (None, "career17.sapsf.com is raw SAP, not a tenant career site — the tile URL 404s"),
    "brampton.ca": (None, "SuccessFactors tenant answers, but shows no job tiles on either template"),
    "kitchener.ca": (None, "SuccessFactors tenant answers, but shows no job tiles on either template"),
    "yrp.ca": (None, "SuccessFactors tenant answers, but shows no job tiles on either template"),
    "appleby.on.ca": (None, "ADP, but the site refuses a plain script (403), so its client id is unreadable"),
    "hpl.ca": ("https://hpl.ca/jobs",
               "no vendor — hand-built page, needs its own scraper"),
    "haltonhealthcare.on.ca": ("https://www.haltonhealthcare.on.ca/careers",
                               "SmartRecruiters — adapter not built"),
}

HEADER = """# The ones we could not reach — check these by hand

{total} of the {census} employers in `docs/census.tsv` are not on the watchlist. Every link goes
to the real careers page, resolved by the fingerprint pass rather than guessed at.

Closest first within each section: **A** is within 40km of Hamilton, **B** is 40-100km,
**C** is 100-200km.

Four reasons cover most of the list:

- **login-walled** — there is no public listing to read at all. Every K-12 school board.
- **hand-built page** — no vendor to adapt; each needs its own scraper. Most libraries.
- **bot wall** — answers a browser, refuses a script. Njoyn and iCIMS.
- **adapter not built** — a known vendor, simply not written yet. That is the build queue.

The technical detail is in `docs/unresolved.txt`. This file is for reading with a browser
open. Regenerate it with `python -m jobwatch.watchlist.uncovered`.
"""


def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def read_census(path=CENSUS):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            f = line.split("\t")
            if len(f) >= 5:
                rows.append(dict(zip(("tier", "sector", "name", "city", "domain"),
                                     (x.strip() for x in f[:5]))))
    return rows


# A path segment that IS the careers section, not merely a page mentioning it.
CAREER_SEGMENT = re.compile(r"^(careers?|jobs?|employment|vacancies|work-with-us|join-us)$", re.I)
# A sign-in page is never the answer, whoever the vendor is. Nor is a script file.
DEAD_END = re.compile(r"sign-?in|log-?in|/account/|/register|/auth", re.I)
ASSET = re.compile(r"\.(js|json|css|xml)$", re.I)


def tidy(url):
    """Decode the entities the page escaped, drop tracking params and fragments."""
    bits = urlsplit(unescape(url))
    query = "&".join(p for p in bits.query.split("&") if p and not p.lower().startswith("utm_"))
    return urlunsplit((bits.scheme, bits.netloc, bits.path, query, ""))


def board(row, found):
    """The link worth clicking — never a bot wall, a sign-in, or the wrong tenant.

    For employers with no vendor the recorded URL is only the best page the fingerprint
    reached, which is often a sub-page of the careers section rather than the section:
    McMaster's immigration page, Hamilton Police's summer-jobs page. So such a link is
    cut back to its careers segment, and trusted at all only when it sits on the
    employer's own domain. Vendor URLs are left alone — their paths are opaque by design
    (`/careersection/2/jobsearch.ftl`) and truncating them would break them.
    """
    home = f"https://{row['domain']}"
    if row["domain"] in OVERRIDE:
        return OVERRIDE[row["domain"]][0] or home
    url = (found or {}).get("careers_url") or ""
    if "perfdrive.com" in url:                  # Njoyn's wall hides the real board inside itself
        url = unquote(parse_qs(urlsplit(url).query).get("ssc", [""])[0]) or url
    if "bidsandtenders" in url:                 # a false match that leads somewhere useless
        url = ""
    if not url:
        return home
    url = tidy(url)
    bits = urlsplit(url)
    if DEAD_END.search(bits.path) or ASSET.search(bits.path):
        return home
    if (found or {}).get("vendor", "?").startswith("?"):
        if not bits.netloc.lower().endswith(row["domain"].lower()):
            return home
        segs = [x for x in bits.path.split("/") if x]
        at = next((i for i, seg in enumerate(segs) if CAREER_SEGMENT.match(seg)), None)
        if at is None:
            return home
        url = urlunsplit((bits.scheme, bits.netloc, "/" + "/".join(segs[:at + 1]), "", ""))
    return url


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)

    labels = [norm(s.label) for s in
              parse_watchlist((CONFIG / "watchlist.txt").read_text())[0]]

    def watched(name):
        n = ALIAS.get(norm(name), norm(name))
        return any(n == l or n.startswith(l + " ") or l.startswith(n + " ") for l in labels)

    rows = read_census()
    found = {r["domain"]: r for r in csv.DictReader(open(VENDORS, encoding="utf-8"),
                                                    delimiter="\t")} if VENDORS.exists() else {}

    out, gap, demoted = defaultdict(list), [], []
    for row in rows:
        if watched(row["name"]):
            continue
        f = found.get(row["domain"], {})
        vendor, url = f.get("vendor", "?"), board(row, f)
        if row["domain"] in OVERRIDE:
            why = OVERRIDE[row["domain"]][1]
        elif vendor in SUPPORTED:
            why = f"**{vendor} — we support this vendor already**"
            gap.append((row, vendor, url))
        elif vendor == "?unreachable":
            why = f"did not answer — {(f.get('note') or 'no connection')[:52]}"
        else:
            why = WHY.get(vendor, f"{vendor} — adapter not built")
        out[row["sector"]].append((row, url, why))
        if url == f"https://{row['domain']}" and (f.get("careers_url") or ""):
            demoted.append(row["name"])

    def table(items, last):
        head = [f"| Employer | City | Careers page | {last} |", "|---|---|---|---|"]
        return head + [f"| {r['name']} | {r['city']} ({r['tier']}) | [open]({u}) | {w} |"
                       for r, u, w in sorted(items, key=lambda x: (x[0]["tier"], x[0]["name"]))]

    total = sum(len(v) for v in out.values())
    doc = [HEADER.format(total=total, census=len(rows))]
    if gap:
        doc += ["\n## Worth a look first — vendors we already support\n",
                "Each sits on an adapter that works today. If any matter to you, "
                "they are one line each.\n",
                *table([(r, u, v) for r, v, u in gap], "Vendor")]
    for key, title in SECTORS:
        if out.get(key):
            doc += [f"\n## {title} — {len(out[key])}\n", *table(out[key], "Why not watched")]

    Path(a.out).write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"{a.out}: {total} of {len(rows)} employers not covered")
    if demoted:
        print(f"  ({len(demoted)} links fell back to the home page — the recorded one was\n   off-site or not a careers path)")
    for key, title in SECTORS:
        if out.get(key):
            print(f"  {title:<44} {len(out[key]):>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
