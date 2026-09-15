---
name: jobs
description: Search for job postings and report what is worth applying to. Use when Armand asks to check for new jobs, search for roles in a place or discipline ("QA jobs near Hamilton", "remote dev jobs posted this week"), asks what is new since last time, or wants postings ranked against his profile. Drives the scrapers in this repo — never scrape hiring.cafe by hand.
---

# job search

Two streams. `bin/watch.sh` sweeps hiring.cafe and needs a **headed** Chrome — headless
never clears Cloudflare, so every run opens a visible browser window for ~15 seconds. That
is expected. `bin/watch-sites.sh` checks 75 employers on their own
boards, needs no browser, and is the cheap one to reach for.

Those 75 rent 6 vendors between them, which is why there are 6 adapters and not 75
scrapers. Most of them came out of `docs/census.tsv` — 287 institutional employers within
200km of Hamilton, the ones juniors never think to check. `docs/unresolved.txt` says which
are still out of reach and why.

Everything runs as a module from the repo root: `.venv/bin/python -m jobwatch.<thing>`.
Read `docs/NOTES.md` before changing anything; it records why each piece works the way it
does.

## Deciding what to run

**"anything new?" / "check for jobs"** — run the cheap one first; it needs no browser and
finishes in seconds:

```bash
bin/watch-sites.sh --no-mail    # bookmarked employers, direct
bin/watch.sh --no-mail          # hiring.cafe, wide net, ~1 min of visible Chrome
```

Each prints only what is not already in its state file. Report those; say plainly if there
are none.

**A new search** — different discipline, different place, different recency:

```bash
.venv/bin/python -m jobwatch.hiringcafe.search "qa engineer jobs near Hamilton Ontario" --radius 60
.venv/bin/python -m jobwatch.hiringcafe.scrape
.venv/bin/python -m jobwatch.hiringcafe.parse --location "Hamilton,Burlington,Toronto" --max-age 7
```

`search` prints a result count before anything is scraped. **Show that count and stop
if it looks wrong** — zero results usually means too tight a radius, and a few thousand
means the department filter did not land.

**Re-filtering results already on disk** — no browser needed, instant:

```bash
.venv/bin/python -m jobwatch.hiringcafe.parse --workplace Remote --salary-min 90000 --max-age 3
```

## The two levers

Filter at the server when you can, at parse time when you cannot.

| Want | Use |
|---|---|
| A discipline | `search --departments "Quality Assurance"` — exact, server-side |
| A city, with a travel radius | `search "… near Hamilton Ontario" --radius 60` |
| Only jobs pinned to a place | `search --strict-location` (drops Canada-wide remote) |
| A shortlist of towns | `parse --location "Toronto,Hamilton,Burlington"` |
| Remote or hybrid only | `parse --workplace Remote,Hybrid` |
| Recent only | `parse --max-age 7` |
| A salary floor | `parse --salary-min 90000` (keeps jobs with no listed band) |
| Which employers are checked directly | a line in `config/watchlist.txt` |
| Which employers exist to be checked at all | `docs/census.tsv`, then `python -m jobwatch.watchlist.fingerprint` |
| Which titles and places count on those boards | `config/filters.txt` |

Department values: Software Development, Quality Assurance, Engineering, Research and
Development (R&D), Information Technology, Data and Analytics, Product Management, Sales,
Business Development, Business Operations, Customer Service, Finance and Accounting,
Human Resources.

## Exporting a spreadsheet

```bash
.venv/bin/python -m jobwatch.export data/jobs.json --out exports/entry-level-dev.csv
.venv/bin/python -m jobwatch.export data/sites_jobs.json --out exports/watchlist.csv
```

One row per posting, opening cleanly in Sheets and Excel. Columns nothing filled in are
dropped — employer boards publish far less than hiring.cafe does — and `--keep-empty`
keeps them. Data only: he tracks applications in his own tracker, so do not add Status /
Applied / Notes columns.

Use `parse --no-state` when exporting a one-off search, or `data/seen.json` gets polluted
with a search the scheduled watch does not use.

## Reporting back

In `data/`: `jobs.json` and `sites_jobs.json` are everything that passed the filters,
newest first; `new.json` and `new_sites.json` are the subsets not seen before. Each record carries title, company, location, workplace type, seniority,
YOE, a structured salary band, tech stack, a requirements summary, and `apply_url` — the
employer's own posting, which is where he applies.

Lead with what is worth his time, not with a table of everything. `config/profile.md` holds his
background; read it and say which postings actually fit and which are a stretch. Name the
salary and the location for each — those are the two things he screens on. Link
`apply_url`, never a hiring.cafe URL.

## Traps

- **`data/seen.json` is keyed on the filtered set.** Change the filters and everything looks
  new. If he changed the search, say so rather than reporting a burst of fake news.
- **Do not hardcode `buildId`.** It changes on every hiring.cafe deploy; the scripts read
  it at runtime.
- **Do not add an LLM to extraction.** DeepSeek emits malformed JSON past ~3,000
  characters of action arguments; that failure is why this pipeline is deterministic.
  See the model findings in `docs/NOTES.md`.
- **`--keep-query` widens and dirties the results.** The fuzzy text search pulls in a gold
  mine's planning engineer. Prefer `departments`.
