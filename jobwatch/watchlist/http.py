"""One place for outbound HTTP, so every adapter behaves the same way.

Deliberately stdlib-only: these are plain public careers pages, no browser and no
Cloudflare, and that is the whole reason this path can run every fifteen minutes.
"""

import gzip
import io
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

TIMEOUT = 25
RETRIES = 2
CAP = 4_000_000  # a careers page that large is a bug, not a page


class Unavailable(Exception):
    """The site did not answer usefully. Never fatal — one bad site is not a bad run."""


def get(url, accept="text/html,application/json,*/*"):
    """Return (final_url, body). Raises Unavailable rather than killing the run."""
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": accept,
                "Accept-Language": "en-CA,en;q=0.9", "Accept-Encoding": "gzip",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read(CAP)
                if r.headers.get("Content-Encoding") == "gzip":
                    try:
                        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
                    except OSError:
                        pass
                return r.geturl(), raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (400, 401, 403, 404, 410):
                break          # a refusal will still be a refusal in two seconds
        except Exception as e:  # noqa: BLE001 — timeouts, DNS, resets, TLS
            last = f"{type(e).__name__}: {e}"
        if attempt < RETRIES:
            time.sleep(1.5 * (attempt + 1))
    raise Unavailable(f"{url} -> {last}")


def get_json(url):
    import json
    _, body = get(url, accept="application/json")
    try:
        return json.loads(body)
    except ValueError as e:
        raise Unavailable(f"{url} -> not JSON ({e})") from e


def post_json(url, payload):
    """POST a JSON body, read a JSON answer. Same contract as `get`: never fatal."""
    import json
    data = json.dumps(payload).encode()
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, data=data, method="POST", headers={
                "User-Agent": UA, "Accept": "application/json",
                "Content-Type": "application/json", "Accept-Language": "en-CA,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read(CAP).decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (400, 401, 403, 404, 410):
                break
        except ValueError as e:
            raise Unavailable(f"{url} -> not JSON ({e})") from e
        except Exception as e:  # noqa: BLE001 — timeouts, DNS, resets, TLS
            last = f"{type(e).__name__}: {e}"
        if attempt < RETRIES:
            time.sleep(1.5 * (attempt + 1))
    raise Unavailable(f"{url} -> {last}")
