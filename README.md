# job watch

Two streams, both reporting only what is new, neither with an LLM anywhere near the
extraction — every field comes out of structured JSON or a vendor's own template.

```bash
./watch.sh --no-mail          # the wide net: hiring.cafe. Needs Chrome, takes a minute
./watch_sites.sh --no-mail    # the fast one: your bookmarked employers, no browser
```

| | `watch.sh` | `watch_sites.sh` |
|---|---|---|
| Source | hiring.cafe, an aggregator | employers' own careers pages |
| Needs a browser | yes — headed Chrome, Cloudflare | no |
| Realistic cadence | a few times a day | every 15 minutes |
| Coverage | wide, everyone | only who you list |
| Freshness | behind hiring.cafe's own crawl | first-hand |
| State | `seen.json` | `seen_sites.json` |

The second exists because an aggregator is always at least one crawl behind. Going
straight to the employer removes that lag, and a request to a plain careers API costs so
little that it can run on a short timer.

## Setup

```bash
uv sync
```

Needs a real Chrome. Headless never clears Cloudflare, so every run opens a visible
browser window for about fifteen seconds — that is expected, not a bug. Chrome is located
automatically; set `CHROME_PATH` in `.env` if it lives somewhere unusual.

For email digests, add to `.env`:

```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

That is a Google [app password](https://myaccount.google.com/apppasswords), not your
account password, and the account needs 2FA. Skip it and use `--no-mail`.

## The watchlist

`watchlist.txt` is the list of employers checked directly. Adding one is a line, not code:

```
ats             host                          label
bamboohr        cityofhamilton.bamboohr.com   City of Hamilton
successfactors  jobs.toronto.ca               City of Toronto           path=/jobsatcity
```

The trick is that employers do not build careers pages, they rent them. Sixteen of the
bookmarked employers here use two vendors between them, so there are two adapters in
`sources/` rather than sixteen scrapers. `path=` names the career-site prefix for tenants
that use one; most answer at the root as well.

Unlike the hiring.cafe run there is **no age filter** — these employers are worth checking
whether a posting went up today or in 2024. "New" means new to `seen_sites.json`.

Relevance filtering happens instead in `filters.txt`, because an employer board is
unfiltered: Canada Post alone lists 260 postings and almost all of them are letter
carriers.

```
+ developer      keep a posting only if its title matches one of these
- help desk      drop it whatever else matches
@ hamilton       an acceptable place; unknown locations are kept
```

## Changing the search

```bash
python search.py "qa engineer jobs near Hamilton Ontario" --radius 60
python search.py --show                    # explain the current search
```

`search.py` prints a result count before anything is scraped. Filter further at parse
time without touching the browser:

```bash
python parse.py --location "Toronto,Hamilton" --workplace Remote --max-age 7
```

## Pipeline

| Script | Does |
|---|---|
| `search.py` | Plain English → `search_url.txt`, via hiring.cafe's own filter parser |
| `scrape.py` | Every page of results → `jobs_raw.json` |
| `parse.py` | Flatten, filter, dedupe → `jobs.json` + `new.json`, tracked in `seen.json` |
| `notify.py` | Emails `new.json`. Sends nothing when nothing is new |
| `watch.sh` | All four, in order. Cron-safe |
| `sources/` | One adapter per job-board vendor — `bamboohr`, `successfactors` |
| `sites.py` | Every employer in `watchlist.txt` → `sites_jobs.json` + `new_sites.json`, tracked in `seen_sites.json` |
| `watch_sites.sh` | `sites.py` then `notify.py`. No browser, safe on a short timer |

## Scheduling

```
0 8,11,14,17,20,23 * * * /path/to/browser-use/watch.sh
*/15 * * * *        /path/to/browser-use/watch_sites.sh
```

Three things that will bite you. `seen.json` is keyed on the filtered set, so changing the
filters in `watch.sh` makes the next run report a burst of jobs that are not new — and the
same is true of `filters.txt` and `seen_sites.json`. A sleeping machine runs no cron jobs.
And on a large board like Scotiabank's, postings shift across page boundaries between
requests, so one occasionally surfaces a run late; state only ever accumulates, so nothing
is reported twice.

## Why it works the way it does

`NOTES.md` — the SSR endpoint, the Cloudflare constraint, why `departments` beats the text
search, and why there is no LLM anywhere near the extraction.
