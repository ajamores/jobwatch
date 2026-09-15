# jobwatch

Watches for new job postings around Hamilton, Ontario, from two sources: hiring.cafe, an
aggregator, and the careers pages of 75 employers checked directly. Each run reports only
what it has not seen before. No LLM touches the extraction. Every field comes from
structured JSON or from a vendor's own page template.

```bash
bin/watch.sh --no-mail          # the wide net: hiring.cafe. Needs Chrome, takes a minute
bin/watch-sites.sh --no-mail    # the fast one: your bookmarked employers, no browser
```

| | `watch.sh` | `watch-sites.sh` |
|---|---|---|
| Source | hiring.cafe, an aggregator | employers' own careers pages |
| Needs a browser | yes, a headed Chrome to get past Cloudflare | no |
| Realistic cadence | a few times a day | every 15 minutes |
| Coverage | wide | only the employers you list |
| Freshness | as current as hiring.cafe's last crawl | first-hand |
| State | `data/seen.json` | `data/seen_sites.json` |

An aggregator is always at least one crawl behind, which is why the second stream exists.
Asking the employer directly removes the lag, and a request to a plain careers API is cheap
enough to run on a short timer.

## Layout

```
jobwatch/           the code, importable as a package
  hiringcafe/       search → scrape → parse
  watchlist/        check + fingerprint + one adapter per job-board vendor
  notify.py  export.py  chrome.py  paths.py
bin/                the two scheduled entry points
config/             watchlist.txt, filters.txt, profile.example.md, searches/
data/               state and generated output — disposable, gitignored
exports/            spreadsheets — gitignored
docs/               NOTES.md, unresolved.txt, census.tsv
```

Everything runs as a module from the repo root, for example
`python -m jobwatch.watchlist.check`. No path is resolved relative to the working directory,
so the scripts behave the same under cron as in a shell.

`data/` is not in git, because it changes on every run and belongs to one machine. On a
fresh clone the first run reports the whole back catalogue as new. Copy `data/` across by
hand or accept one noisy run.

## Setup

```bash
uv sync
```

The hiring.cafe stream needs a real Chrome. Headless Chrome never clears Cloudflare, so each
run opens a visible browser window for about fifteen seconds, which is expected. Chrome is
found automatically; set `CHROME_PATH` in `.env` if yours is somewhere unusual. The
watchlist stream needs no browser.

For email digests, add to `.env`:

```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

That is a Google [app password](https://myaccount.google.com/apppasswords), not your
account password, and the account needs 2FA. Without it, run with `--no-mail`.

No script reads a candidate profile. The Claude Code skill in `.claude/skills/jobs/` does,
to judge which postings fit, so copy `config/profile.example.md` to `config/profile.md` if
you use it.

## The watchlist

`config/watchlist.txt` lists the employers checked directly. Adding one takes a line of
text:

```
ats             host                          label                     extras
bamboohr        cityofhamilton.bamboohr.com   City of Hamilton
successfactors  jobs.toronto.ca               City of Toronto           path=/jobsatcity
workday         milton.wd10.myworkdayjobs.com Town of Milton            site=TownOfMilton,where=Milton
ukg             recruiting.ultipro.ca         Meridian Credit Union     tenant=MER5001MCUL,board=6c1f133f-...
adp             workforcenow.adp.com          City of Markham           cid=04bf51f8-...,where=Markham
```

Most employers rent their careers page from a vendor. The 75 employers here use 6 vendors
between them, so `jobwatch/watchlist/adapters/` holds 6 adapters, and adding an employer on
a vendor that already has one is usually a single line.

Extras go at the end of the line, separated by commas:

| Extra | Vendor | What it is |
|---|---|---|
| `path=` | SuccessFactors | the career-site prefix, for tenants that use one |
| `site=` | Workday | the board's own path segment |
| `tenant=` | Workday | only for tenants on the shared `myworkdaysite.com` host |
| `facet=<param>:<id>` | Workday | narrows a global board on the server. Magna has 1,428 postings worldwide and 203 in Canada |
| `tenant=`, `board=` | UKG | several tenants share the one host |
| `cid=` | ADP | every tenant is on the one host, told apart by client id |
| `where=` | any | the employer's town, for boards that list a building ("Town Hall", "Lake Erie Works") where a place should be. Without it the `@` filter would drop all of them |

The hiring.cafe run has an age filter and this one does not, because these employers are
worth checking whether a posting went up today or in 2024. A posting counts as new when it
is not already in `data/seen_sites.json`.

Relevance is handled in `config/filters.txt` instead, since an employer board lists
everything. Canada Post alone has 260 postings, and almost all of them are for letter
carriers.

```
+ developer      keep a posting only if its title matches one of these
- help desk      drop it whatever else matches
@ hamilton       an acceptable place; unknown locations are kept
```

`docs/unresolved.txt` lists every employer that has no adapter yet, grouped by vendor, with
the reason each one is still out of reach.

## The census

`docs/census.tsv` lists 287 institutional and often overlooked employers within about 200km
of Hamilton: hospitals, school boards, universities, libraries, municipalities, police
services, utilities, farm mutuals, credit unions and conservation authorities. None of them
compete for juniors on LinkedIn. They post once, on their own board, and wait.

`jobwatch.watchlist.fingerprint` finds each employer's real careers page and names the
vendor behind it. Those counts set the order in which adapters get built.

```bash
python -m jobwatch.watchlist.fingerprint                      # all of them
python -m jobwatch.watchlist.fingerprint --sector hospital    # one sector
python -m jobwatch.watchlist.fingerprint --recheck-markup     # re-probe the weak matches
```

It follows the employer's own careers link up to two hops and reads the vendor from the URL
it lands on. If that fails, it looks for a board link in the markup, which is also the
tenant URL an adapter needs. Results go to `data/census_vendors.tsv`.

On 2026-09-11, 114 of the 287 had built their own careers page and 157 rented one. Workday
led with 24. ApplyToEducation came next with 18, and because it sits behind a login, every
public school board is out of reach. SuccessFactors had 15, Dayforce and ADP 11 each, and
UKG and Taleo 10. Those numbers are why `workday`, `ukg` and `adp` were the adapters
written next.

## Changing the search

```bash
python -m jobwatch.hiringcafe.search "qa engineer jobs near Hamilton Ontario" --radius 60
python -m jobwatch.hiringcafe.search --show          # explain the current search
```

`search` prints a result count before anything is scraped. You can narrow the results
further at parse time without opening the browser:

```bash
python -m jobwatch.hiringcafe.parse --location "Toronto,Hamilton" --workplace Remote --max-age 7
```

## Pipeline

| Module | Does |
|---|---|
| `hiringcafe.search` | Turns a plain-English query into `data/search_url.txt`, using hiring.cafe's own filter parser |
| `hiringcafe.scrape` | Fetches every page of results into `data/jobs_raw.json` |
| `hiringcafe.parse` | Flattens, filters and dedupes into `jobs.json` and `new.json`, tracked in `seen.json` |
| `watchlist.check` | Checks every employer in `watchlist.txt`, writing `sites_jobs.json` and `new_sites.json`, tracked in `seen_sites.json` |
| `watchlist.fingerprint` | Names the vendor behind each employer in `docs/census.tsv` |
| `watchlist.adapters` | One module per job-board vendor: `adp`, `bamboohr`, `greenhouse`, `successfactors`, `ukg`, `workday` |
| `notify` | Emails what is new, and sends nothing when nothing is |
| `export` | Converts any of those JSON files to a CSV that opens cleanly in Sheets |
| `bin/watch.sh` | Runs scrape, parse and notify. Safe under cron |
| `bin/watch-sites.sh` | Runs check and notify. Needs no browser, so it is safe on a short timer |

## Scheduling

```
0 8,11,14,17,20,23 * * * /path/to/jobwatch/bin/watch.sh
*/15 * * * *             /path/to/jobwatch/bin/watch-sites.sh
```

`seen.json` is keyed on the filtered set, so changing the filters in `watch.sh` makes the
next run report a burst of postings that are not actually new. `filters.txt` and
`seen_sites.json` behave the same way. Cron does nothing while the machine sleeps. On a
large board such as Scotiabank's, postings shift across page boundaries between requests,
so one occasionally shows up a run late. State only ever accumulates, so nothing is
reported twice.

## Why it works the way it does

`docs/NOTES.md` covers the SSR endpoint, the Cloudflare constraint, why `departments` beats
the text search, and why no LLM is used for extraction.
