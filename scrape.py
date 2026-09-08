"""hiring.cafe scraper — pulls every page of a filtered search as structured JSON.

hiring.cafe is a Next.js SSR app: results are not fetched by an XHR the client can be
watched for, they are embedded in __NEXT_DATA__. Next.js also serves those same props at
/_next/data/<buildId>/index.json?searchState=<...>&page=<N>, which is the endpoint used
here.

Cloudflare 403s that endpoint for curl, so it is called with fetch() from inside a headed
Chrome page that has already cleared the challenge.

    python scrape.py [search_url.txt] [--out jobs_raw.json] [--max-pages N]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from browser_use import Browser

from chrome import executable_path


JS_BUILD_ID = "JSON.parse(document.getElementById('__NEXT_DATA__').textContent).buildId"

JS_FETCH_PAGE = r"""
(async function(){
  const url = %s;
  try{
    const r = await fetch(url, {headers:{'x-nextjs-data':'1'}});
    if(!r.ok) return JSON.stringify({error:`HTTP ${r.status}`});
    const d = await r.json();
    const p = d.pageProps || {};
    return JSON.stringify({
      page: p.ssrPage, total: p.ssrTotalCount, pageSize: p.ssrPageSize,
      isLast: p.ssrIsLastPage, ssrError: p.ssrError, hits: p.ssrHits || [],
    });
  }catch(e){ return JSON.stringify({error: e.message}); }
})()
"""


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url_file", nargs="?", default="search_url.txt")
    ap.add_argument("--out", default="jobs_raw.json")
    ap.add_argument("--max-pages", type=int, default=25)
    ap.add_argument("--headful", action="store_true", default=True)
    args = ap.parse_args()

    url = Path(args.url_file).read_text().strip()
    search_state = parse_qs(urlparse(url).query).get("searchState", [""])[0]
    if not search_state:
        sys.exit(f"no searchState in {args.url_file}")

    browser = Browser(
        executable_path=executable_path(),
        headless=False,
        user_data_dir=str(Path.home() / ".cache/browser-use-profile"),
    )
    await browser.start()
    try:
        await browser.navigate_to(url)
        await asyncio.sleep(10)  # Cloudflare challenge + hydration
        cdp = await browser.get_or_create_cdp_session()

        async def js(expr):
            r = await cdp.cdp_client.send.Runtime.evaluate(
                params={"expression": expr, "returnByValue": True, "awaitPromise": True},
                session_id=cdp.session_id,
            )
            if "exceptionDetails" in r:
                raise RuntimeError(r["exceptionDetails"].get("text", "JS error"))
            return r["result"].get("value")

        build_id = await js(JS_BUILD_ID)
        if not build_id:
            sys.exit("no __NEXT_DATA__ — page did not hydrate (Cloudflare?)")
        print(f"buildId {build_id}", file=sys.stderr)

        hits, total, page = [], None, 0
        while page < args.max_pages:
            endpoint = (
                f"/_next/data/{build_id}/index.json"
                f"?searchState={search_state}&page={page}"
            )
            data = json.loads(await js(JS_FETCH_PAGE % json.dumps(endpoint)))
            if data.get("error") or data.get("ssrError"):
                print(f"page {page}: {data.get('error') or data['ssrError']}", file=sys.stderr)
                break
            total = data["total"]
            hits.extend(data["hits"])
            print(
                f"page {page}: {len(data['hits'])} hits "
                f"({len(hits)} collected, site reports {total} jobs)",
                file=sys.stderr,
            )
            if data.get("isLast") or not data["hits"]:
                break
            page += 1
            await asyncio.sleep(1)

        payload = {"searchState": search_state, "total": total, "pages": page + 1,
                   "hits": hits}
        Path(args.out).write_text(json.dumps(payload, indent=1))
        print(f"wrote {args.out}: {len(hits)} hits across {page + 1} pages "
              f"(site reports {total})")
    finally:
        await browser.kill()


asyncio.run(main())
