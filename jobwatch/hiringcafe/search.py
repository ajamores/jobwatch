"""Build a hiring.cafe search URL from plain English.

hiring.cafe has its own filter-parsing endpoint (/api/ai-search/parse-filters, Gemini
behind it) that turns "qa engineer jobs in Hamilton Ontario" into a proper filter object —
including a location with the internal id and a radius, which cannot be hand-written.
This asks it, merges in the standing defaults, and writes the search URL.

    python -m jobwatch.hiringcafe.search "qa engineer jobs in Hamilton Ontario" --radius 50
    python -m jobwatch.hiringcafe.search "software developer" --departments "Software Development"
    python -m jobwatch.hiringcafe.search --show     # what the saved search currently means
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import quote, urlparse, parse_qs

from browser_use import Browser

from ..chrome import executable_path
from ..paths import DATA

HOME = "https://hiringcafe.com/"

JS_PARSE_FILTERS = r"""
(async function(){
  try{
    const r = await fetch('/api/ai-search/parse-filters?query=' + encodeURIComponent(%s));
    if(!r.ok) return JSON.stringify({error:`HTTP ${r.status}`});
    return JSON.stringify(await r.json());
  }catch(e){ return JSON.stringify({error:e.message}); }
})()
"""

JS_COUNT = r"""
(async function(){
  try{
    const j = JSON.parse(document.getElementById('__NEXT_DATA__').textContent);
    const r = await fetch(`/_next/data/${j.buildId}/index.json?searchState=`
                          + encodeURIComponent(%s) + '&page=0',
                          {headers:{'x-nextjs-data':'1'}});
    const d = await r.json(); const p = d.pageProps || {};
    const cats = {};
    (p.ssrHits||[]).forEach(h => {
      const c = h.v5_processed_job_data?.job_category; cats[c] = (cats[c]||0)+1;
    });
    return JSON.stringify({total:p.ssrTotalCount, companies:p.ssrCompanyCount,
                           err:p.ssrError, cats});
  }catch(e){ return JSON.stringify({error:e.message}); }
})()
"""


def summarise(ss):
    def loc_str(l):
        o = l.get("options") or {}
        bits = []
        if o.get("radius"):
            bits.append(f"{o['radius']}{o.get('radius_unit', 'miles')[:2]} radius")
        bits.append("+flexible" if o.get("flexible_regions") else "strict")
        return f"{l.get('formatted_address')} [{', '.join(bits)}]"

    locs = ", ".join(loc_str(l) for l in ss.get("locations", [])) or "anywhere"
    return (
        f"  query       {ss.get('searchQuery') or '(none — departments only)'}\n"
        f"  departments {', '.join(ss.get('departments') or []) or 'any'}\n"
        f"  locations   {locs}\n"
        f"  seniority   {', '.join(ss.get('seniorityLevel') or []) or 'any'}\n"
        f"  commitment  {', '.join(ss.get('commitmentTypes') or []) or 'any'}\n"
        f"  workplace   {', '.join(ss.get('workplaceTypes') or []) or 'any'}\n"
        f"  posted      last {ss.get('dateFetchedPastNDays', '—')} days"
    )


def csv(v):
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="plain English, e.g. 'qa jobs in Hamilton'")
    ap.add_argument("--out", default=str(DATA / "search_url.txt"))
    ap.add_argument("--show", action="store_true", help="print the current --out and exit")
    ap.add_argument("--departments", help="override, comma-separated")
    ap.add_argument("--locations", help='override with "any" to drop location filtering')
    ap.add_argument("--radius", type=int, help="miles around a city (ignored for provinces)")
    ap.add_argument("--strict-location", action="store_true",
                    help="only jobs pinned to that place; drops country/continent/worldwide "
                         "remote listings that would otherwise qualify")
    ap.add_argument("--seniority", default="Entry Level,Mid Level")
    ap.add_argument("--commitment", default="Full Time")
    ap.add_argument("--workplace", help='e.g. "Remote" or "Remote,Hybrid"')
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--keep-query", action="store_true",
                    help="keep the free-text query alongside departments (fuzzier, wider)")
    args = ap.parse_args()

    if args.show:
        url = Path(args.out).read_text().strip()
        ss = json.loads(parse_qs(urlparse(url).query)["searchState"][0])
        print(f"{args.out}:\n{summarise(ss)}")
        return
    if not args.query:
        sys.exit("give a query, or --show")

    browser = Browser(
        executable_path=executable_path(),
        headless=False,
        user_data_dir=str(Path.home() / ".cache/browser-use-profile"),
    )
    await browser.start()
    try:
        await browser.navigate_to(HOME)
        await asyncio.sleep(10)  # Cloudflare
        cdp = await browser.get_or_create_cdp_session()

        async def js(expr):
            r = await cdp.cdp_client.send.Runtime.evaluate(
                params={"expression": expr, "returnByValue": True, "awaitPromise": True},
                session_id=cdp.session_id,
            )
            return json.loads(r["result"].get("value") or '{"error":"no value"}')

        parsed = await js(JS_PARSE_FILTERS % json.dumps(args.query))
        if parsed.get("error"):
            sys.exit(f"parse-filters: {parsed['error']}")
        sf = parsed.get("suggestedFilters") or {}

        ss = {
            "searchQuery": sf.get("searchQuery", args.query) if args.keep_query else "",
            "locations": sf.get("locations") or [],
            "departments": csv(args.departments) or sf.get("departments") or [],
            "seniorityLevel": csv(args.seniority) or [],
            "commitmentTypes": csv(args.commitment) or [],
            "dateFetchedPastNDays": args.days,
        }
        if args.workplace:
            ss["workplaceTypes"] = csv(args.workplace)
        if args.locations == "any":
            ss["locations"] = []
        for loc in ss["locations"]:
            # A radius around a province centroid is meaningless — Ontario's centroid is
            # 500km north of anywhere anyone works. Radius is for cities only.
            wide = any(t in ("administrative_area_level_1", "administrative_area_level_2",
                             "country", "continent") for t in loc.get("types", []))
            opts = {} if wide else dict(loc.get("options") or {})
            opts.pop("flexible_regions", None)
            if args.radius and not wide:
                opts.update(radius=args.radius, radius_unit="miles", ignore_radius=False)
            if not args.strict_location:
                # Without this, a job posted as "anywhere in Canada" does not match an
                # Ontario search. Worth 136 results instead of 102.
                opts["flexible_regions"] = ["anywhere_in_country", "anywhere_in_continent",
                                            "anywhere_in_world"]
            loc["options"] = opts
        if not ss["searchQuery"] and not ss["departments"]:
            ss["searchQuery"] = args.query  # nothing to filter on; fall back to free text

        blob = json.dumps(ss, separators=(",", ":"))
        count = await js(JS_COUNT % json.dumps(blob))

        Path(args.out).write_text(f"{HOME}?searchState={quote(blob, safe='')}\n")
        print(f"wrote {args.out}\n{summarise(ss)}")
        if count.get("error") or count.get("err"):
            print(f"  ! dry run: {count.get('error') or count.get('err')}")
        else:
            print(f"\n  {count['total']} jobs at {count['companies']} companies")
            for cat, n in sorted(count["cats"].items(), key=lambda x: -x[1]):
                print(f"    {n:>3}  {cat}")
    finally:
        await browser.kill()


if __name__ == "__main__":
    asyncio.run(main())
