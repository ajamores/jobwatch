# hiring.cafe job watch

Scrapes [hiring.cafe](https://hiringcafe.com) for job postings, filters them, and reports
what is new. No LLM in the extraction path — every field comes out of structured JSON.

```bash
./watch.sh --no-mail          # check for new postings, print them
./watch.sh                    # same, but email the new ones
```

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

## Scheduling

```
0 8,11,14,17,20,23 * * * /path/to/browser-use/watch.sh
```

Two things that will bite you. `seen.json` is keyed on the filtered set, so changing the
filters in `watch.sh` makes the next run report a burst of jobs that are not new. And a
sleeping machine runs no cron jobs.

## Why it works the way it does

`NOTES.md` — the SSR endpoint, the Cloudflare constraint, why `departments` beats the text
search, and why there is no LLM anywhere near the extraction.
