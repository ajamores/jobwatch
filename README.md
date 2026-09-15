# job watch

Two streams, both reporting only what is new, neither with an LLM anywhere near the
extraction — every field comes out of structured JSON or a vendor's own template.

```bash
bin/watch.sh --no-mail          # the wide net: hiring.cafe. Needs Chrome, takes a minute
bin/watch-sites.sh --no-mail    # the fast one: your bookmarked employers, no browser
```

| | `watch.sh` | `watch-sites.sh` |
|---|---|---|
| Source | hiring.cafe, an aggregator | employers' own careers pages |
| Needs a browser | yes — headed Chrome, Cloudflare | no |
| Realistic cadence | a few times a day | every 15 minutes |
| Coverage | wide, everyone | only who you list |
| Freshness | behind hiring.cafe's own crawl | first-hand |
| State | `data/seen.json` | `data/seen_sites.json` |

The second exists because an aggregator is always at least one crawl behind. Going
straight to the employer removes that lag, and a request to a plain careers API costs so
little that it can run on a short timer.

## Layout

```
jobwatch/           the code, importable as a package
  hiringcafe/       search → scrape → parse
  watchlist/        check + fingerprint + one adapter per job-board vendor
  notify.py  export.py  chrome.py  paths.py
bin/                the two scheduled entry points
config/             watchlist.txt, filters.txt, profile.md, searches/
data/               state and generated output — disposable, gitignored
exports/            spreadsheets — gitignored
docs/               NOTES.md, unresolved.txt, census.tsv
```

Everything runs as a module from the repo root: `python -m jobwatch.watchlist.check`.
Nothing resolves a path relative to the working directory, so cron and the shell are
equally safe.

**`data/` is not in git.** It churns on every run and it is per-machine. Clone this
somewhere new and the first run will report the entire back catalogue as new — copy
`data/` across by hand, or accept one noisy run.

## Setup

```bash
uv sync
```

Needs a real Chrome. Headless never clears Cloudflare, so every run of the hiring.cafe
stream opens a visible browser window for about fifteen seconds — that is expected, not a
bug. Chrome is located automatically; set `CHROME_PATH` in `.env` if it lives somewhere
unusual. The watchlist stream needs no browser at all.

For email digests, add to `.env`:

```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

That is a Google [app password](https://myaccount.google.com/apppasswords), not your
account password, and the account needs 2FA. Skip it and use `--no-mail`.

## The watchlist

`config/watchlist.txt` is the list of employers checked directly. Adding one is a line,
not code:

```
ats             host                          label                     extras
bamboohr        cityofhamilton.bamboohr.com   City of Hamilton
successfactors  jobs.toronto.ca               City of Toronto           path=/jobsatcity
workday         milton.wd10.myworkdayjobs.com Town of Milton            site=TownOfMilton,where=Milton
ukg             recruiting.ultipro.ca         Meridian Credit Union     tenant=MER5001MCUL,board=6c1f133f-...
adp             workforcenow.adp.com          City of Markham           cid=04bf51f8-...,where=Markham
```

The trick is that employers do not build careers pages, they rent them. The 75
employers here use 6 vendors between them, so there are 6 adapters in
`jobwatch/watchlist/adapters/` rather than 75 scrapers. That ratio is the whole
design, and it is why adding an employer is usually a line rather than a day.

Extras ride at the end of the line, comma-separated:

| Extra | Vendor | What it is |
|---|---|---|
| `path=` | SuccessFactors | the career-site prefix, for tenants that use one |
| `site=` | Workday | the board's own path segment |
| `tenant=` | Workday | only for tenants on the shared `myworkdaysite.com` host |
| `facet=<param>:<id>` | Workday | narrows a global board server-side — Magna is 1,428 postings worldwide and 203 in Canada |
| `tenant=`, `board=` | UKG | several tenants share the one host |
| `cid=` | ADP | every tenant is on the one host, told apart by client id |
| `where=` | any | the employer's town, for boards that print a building — "Town Hall", "Lake Erie Works" — instead of a place. The `@` filter would otherwise drop every one of them |

Unlike the hiring.cafe run there is **no age filter** — these employers are worth checking
whether a posting went up today or in 2024. "New" means new to `data/seen_sites.json`.

Relevance filtering happens instead in `config/filters.txt`, because an employer board is
unfiltered: Canada Post alone lists 260 postings and almost all of them are letter
carriers.

```
+ developer      keep a posting only if its title matches one of these
- help desk      drop it whatever else matches
@ hamilton       an acceptable place; unknown locations are kept
```

`docs/unresolved.txt` lists every employer with no adapter yet and why — vendor by
vendor, with the reason each one resists.

## The census

`docs/census.tsv` is 287 institutional and overlooked employers within about 200km of
Hamilton: hospitals, school boards, universities, libraries, municipalities, police
services, utilities, farm mutuals, credit unions, conservation authorities. The premise is
that none of them compete for juniors on LinkedIn. They post once, on their own board, and
wait.

`jobwatch.watchlist.fingerprint` resolves each one to its real careers page and names the
vendor, so the build order is decided by the data rather than by guesswork:

```bash
python -m jobwatch.watchlist.fingerprint                      # all of them
python -m jobwatch.watchlist.fingerprint --sector hospital    # one sector
python -m jobwatch.watchlist.fingerprint --recheck-markup     # re-probe the weak matches
```

It follows the employer's own careers link two hops, then reads the vendor off the URL it
lands on — or failing that off a board link in the markup, which is the tenant URL an
adapter actually needs. Results land in `data/census_vendors.tsv`.

The answer on 2026-09-11: 114 of the 287 hand-roll their careers page, and 157 rent one.
Workday leads with 24, then ApplyToEducation with 18 — login-walled, which puts every
public school board out of reach — SuccessFactors 15, Dayforce and ADP 11 each, UKG and
Taleo 10. That is what chose `workday`, `ukg` and `adp` as the adapters to write.

## Changing the search

```bash
python -m jobwatch.hiringcafe.search "qa engineer jobs near Hamilton Ontario" --radius 60
python -m jobwatch.hiringcafe.search --show          # explain the current search
```

`search` prints a result count before anything is scraped. Filter further at parse time
without touching the browser:

```bash
python -m jobwatch.hiringcafe.parse --location "Toronto,Hamilton" --workplace Remote --max-age 7
```

## Pipeline

| Module | Does |
|---|---|
| `hiringcafe.search` | Plain English → `data/search_url.txt`, via hiring.cafe's own filter parser |
| `hiringcafe.scrape` | Every page of results → `data/jobs_raw.json` |
| `hiringcafe.parse` | Flatten, filter, dedupe → `jobs.json` + `new.json`, tracked in `seen.json` |
| `watchlist.check` | Every employer in `watchlist.txt` → `sites_jobs.json` + `new_sites.json`, tracked in `seen_sites.json` |
| `watchlist.fingerprint` | Every employer in `docs/census.tsv` → which vendor each one rents |
| `watchlist.adapters` | One module per job-board vendor — `adp`, `bamboohr`, `greenhouse`, `successfactors`, `ukg`, `workday` |
| `notify` | Emails what is new. Sends nothing when nothing is new |
| `export` | Any of those JSON files → a CSV that opens cleanly in Sheets |
| `bin/watch.sh` | scrape → parse → notify. Cron-safe |
| `bin/watch-sites.sh` | check → notify. No browser, safe on a short timer |

## Scheduling

```
0 8,11,14,17,20,23 * * * /path/to/browser-use/bin/watch.sh
*/15 * * * *             /path/to/browser-use/bin/watch-sites.sh
```

Three things that will bite you. `seen.json` is keyed on the filtered set, so changing the
filters in `watch.sh` makes the next run report a burst of jobs that are not new — and the
same is true of `filters.txt` and `seen_sites.json`. A sleeping machine runs no cron jobs.
And on a large board like Scotiabank's, postings shift across page boundaries between
requests, so one occasionally surfaces a run late; state only ever accumulates, so nothing
is reported twice.

## Why it works the way it does

`docs/NOTES.md` — the SSR endpoint, the Cloudflare constraint, why `departments` beats the
text search, and why there is no LLM anywhere near the extraction.
