"""Watch hiring.cafe's network traffic for a JSON search API.

Headed Chrome (clears Cloudflare), CDP Network domain enabled before navigation,
every XHR/fetch response body captured and dumped to netlog/.
"""

import asyncio
import json
import sys
from pathlib import Path

from browser_use import Browser

from chrome import executable_path

OUT = Path("netlog")


async def main():
    url = Path(sys.argv[1]).read_text().strip()
    settle = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    browser = Browser(
        executable_path=executable_path(),
        headless=False,
        user_data_dir=str(Path.home() / ".cache/browser-use-profile"),
    )
    await browser.start()
    try:
        cdp = await browser.get_or_create_cdp_session()
        client, sid = cdp.cdp_client, cdp.session_id

        requests: dict[str, dict] = {}
        finished: list[str] = []

        def on_request(ev, session_id=None):
            r = ev["request"]
            requests[ev["requestId"]] = {
                "url": r["url"],
                "method": r["method"],
                "postData": r.get("postData"),
                "resourceType": ev.get("type"),
            }

        def on_response(ev, session_id=None):
            rec = requests.setdefault(ev["requestId"], {})
            resp = ev["response"]
            rec.update(
                url=rec.get("url") or resp["url"],
                status=resp["status"],
                mimeType=resp.get("mimeType"),
                resourceType=ev.get("type") or rec.get("resourceType"),
            )

        def on_finished(ev, session_id=None):
            rec = requests.get(ev["requestId"])
            if rec:
                rec["encodedLength"] = ev.get("encodedDataLength")
            finished.append(ev["requestId"])

        client.register.Network.requestWillBeSent(on_request)
        client.register.Network.responseReceived(on_response)
        client.register.Network.loadingFinished(on_finished)

        await client.send.Network.enable(params={}, session_id=sid)
        await browser.navigate_to(url)
        print(f"navigated; settling {settle}s...", file=sys.stderr)
        await asyncio.sleep(settle)

        OUT.mkdir(exist_ok=True)
        (OUT / "requests.json").write_text(json.dumps(requests, indent=1))
        interesting = []
        for rid in finished:
            rec = requests.get(rid, {})
            rtype = (rec.get("resourceType") or "").lower()
            mime = (rec.get("mimeType") or "")
            if rtype not in ("xhr", "fetch") and "json" not in mime:
                continue
            body = None
            try:
                res = await client.send.Network.getResponseBody(
                    params={"requestId": rid}, session_id=sid
                )
                body = res.get("body")
            except Exception as e:
                rec["bodyError"] = str(e)[:200]
            rec["bodyLength"] = len(body or "")
            if body:
                (OUT / f"{rid.replace('.', '_')}.txt").write_text(body[:2_000_000])
            interesting.append({"requestId": rid, **rec})

        interesting.sort(key=lambda r: r.get("bodyLength", 0), reverse=True)
        (OUT / "index.json").write_text(json.dumps(interesting, indent=1))

        print(f"\n{len(requests)} requests total, {len(interesting)} xhr/fetch/json\n")
        for r in interesting[:25]:
            print(f"{r.get('bodyLength',0):>9}  {r.get('method','?'):<5} "
                  f"{r.get('status','?')}  {r['url'][:110]}")
    finally:
        await browser.kill()


asyncio.run(main())
