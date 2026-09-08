---
name: jobs
description: Search hiring.cafe for job postings and report what is worth applying to. Use when Armand asks to check for new jobs, search for roles in a place or discipline ("QA jobs near Hamilton", "remote dev jobs posted this week"), asks what is new since last time, or wants postings ranked against his profile. Drives the scrapers in this repo — never scrape hiring.cafe by hand.
---

# hiring.cafe job search

Three scripts, run in order. All of them need a **headed** Chrome — headless never clears
Cloudflare. Every run opens a visible browser window for ~15 seconds. That is expected.

Read `NOTES.md` before changing anything; it records why each piece works the way it does.

## Deciding what to run

**"anything new?" / "check for jobs"** — the search has not changed, so skip `search.py`:

```bash
./watch.sh --no-mail
```

Prints only postings not already in `seen.json`. Report those; say plainly if there are none.

**A new search** — different discipline, different place, different recency:

```bash
.venv/bin/python search.py "qa engineer jobs near Hamilton Ontario" --radius 60
.venv/bin/python scrape.py
.venv/bin/python parse.py --location "Hamilton,Burlington,Toronto" --max-age 7
```

`search.py` prints a result count before anything is scraped. **Show that count and stop
if it looks wrong** — zero results usually means too tight a radius, and a few thousand
means the department filter did not land.

**Re-filtering results already on disk** — no browser needed, instant:

```bash
.venv/bin/python parse.py --workplace Remote --salary-min 90000 --max-age 3
```

## The two levers

Filter at the server when you can, in `parse.py` when you cannot.

| Want | Use |
|---|---|
| A discipline | `search.py --departments "Quality Assurance"` — exact, server-side |
| A city, with a travel radius | `search.py "… near Hamilton Ontario" --radius 60` |
| Only jobs pinned to a place | `search.py --strict-location` (drops Canada-wide remote) |
| A shortlist of towns | `parse.py --location "Toronto,Hamilton,Burlington"` |
| Remote or hybrid only | `parse.py --workplace Remote,Hybrid` |
| Recent only | `parse.py --max-age 7` |
| A salary floor | `parse.py --salary-min 90000` (keeps jobs with no listed band) |

Department values: Software Development, Quality Assurance, Engineering, Research and
Development (R&D), Information Technology, Data and Analytics, Product Management, Sales,
Business Development, Business Operations, Customer Service, Finance and Accounting,
Human Resources.

## Exporting a spreadsheet

```bash
.venv/bin/python export.py jobs.json --out entry_level_dev_jobs.csv
```

27 columns, one row per posting, opening cleanly in Sheets and Excel. The last three —
Status, Applied on, Notes — are his to fill in, and a re-export carries them across on
apply URL rather than wiping them. Never pass `--clobber` unless he asks; it discards
that tracking.

Use `parse.py --no-state` when exporting a one-off search, or `seen.json` gets polluted
with a search the scheduled watch does not use.

## Reporting back

`jobs.json` is everything that passed the filters, newest first. `new.json` is the subset
not seen before. Each record carries title, company, location, workplace type, seniority,
YOE, a structured salary band, tech stack, a requirements summary, and `apply_url` — the
employer's own posting, which is where he applies.

Lead with what is worth his time, not with a table of everything. `profile.md` holds his
background; read it and say which postings actually fit and which are a stretch. Name the
salary and the location for each — those are the two things he screens on. Link
`apply_url`, never a hiring.cafe URL.

## Traps

- **`seen.json` is keyed on the filtered set.** Change the filters and everything looks
  new. If he changed the search, say so rather than reporting a burst of fake news.
- **Do not hardcode `buildId`.** It changes on every hiring.cafe deploy; the scripts read
  it at runtime.
- **Do not add an LLM to extraction.** DeepSeek emits malformed JSON past ~3,000
  characters of action arguments; that failure is why this pipeline is deterministic.
  See the model findings in `NOTES.md`.
- **`--keep-query` widens and dirties the results.** The fuzzy text search pulls in a gold
  mine's planning engineer. Prefer `departments`.
