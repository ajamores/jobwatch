# hot — hiringcafe-watch

<https://github.com/ajamores/hiringcafe-watch> (private)

_Updated 2026-09-09_

## What this is

Two job watches. Neither has an LLM in the extraction path.

```
bin/watch.sh --no-mail          hiring.cafe. Wide net. Needs headed Chrome, ~1 min
bin/watch-sites.sh --no-mail    bookmarked employers, direct. No browser, 15-min safe
```

## State: both working, manual, committed

The watchlist stream landed as `e2bdd78`. The repo was then restructured into a package —
that is a separate, purely mechanical commit, so the feature diff stayed readable.

17 employers, 3 adapters, 31 jobs after filtering. Both streams re-verified after the move.

## Layout

```
jobwatch/           the code, importable
  hiringcafe/       search → scrape → parse       needs a browser
  watchlist/        check + adapters/             does not
  notify.py  export.py  chrome.py  paths.py
bin/                watch.sh, watch-sites.sh
config/             watchlist.txt, filters.txt, profile.md, searches/
data/               state + generated — gitignored, per-machine
exports/            spreadsheets — gitignored
docs/               NOTES.md, unresolved.txt
```

Everything runs as `python -m jobwatch.<thing>` from the repo root. `jobwatch/paths.py`
anchors every path to the repo, so nothing depends on the working directory any more.

**`data/` left git in the cleanup.** `seen.json` used to be tracked deliberately, for
cross-machine continuity. It now is not — it churns every run and only one machine should
ever be scheduled anyway. Consequence: a fresh clone reports the whole back catalogue on
its first run unless `data/` is copied across by hand.

Deleted in the cleanup: `run.py`, `example.py`, `score.py`, `netwatch.py`, `main.py`,
`sheets.csv`. All recoverable from history; none of them were on a live path.

## The watchlist stream

Built because an aggregator is always a crawl behind. Going direct removes that lag, and
a plain careers API is cheap enough to poll every fifteen minutes.

| File | Does |
|---|---|
| `config/watchlist.txt` | The employers. Adding one is a line, not code |
| `jobwatch/watchlist/adapters/` | One per **vendor**, not per employer — `bamboohr`, `greenhouse`, `successfactors` |
| `config/filters.txt` | Which titles and places count. Data, not code |
| `jobwatch/watchlist/check.py` | Runs it all → `data/sites_jobs.json` + `new_sites.json`, state in `seen_sites.json` |
| `bin/watch-sites.sh` | `check` then `notify` |
| `docs/unresolved.txt` | 25 bookmarked employers with no adapter yet, and why |

The whole point: your 73 bookmarks use a handful of vendors between them. Three adapters
cover 17 employers.

## The four things that matter

1. **Most of these boards publish no posting date.** Scotiabank prints one neither on the
   list nor on the posting itself; of the SuccessFactors tenants only Toronto does. So
   `check` records **first-seen** instead — `seen_sites.json` is a dict of
   `{id: timestamp}`, not a list. That is the better signal anyway: what matters is that
   it is new to Armand.
2. **Greenhouse is the best source in the project.** Real `first_published`, real salary
   bands. `boards-api.greenhouse.io/v1/boards/<token>/jobs`, no auth, no browser.
3. **`#` only starts a comment at line start or after a space.** Without that rule the
   `#` in `+ c#` was read as a comment marker, leaving a bare `c` that matched almost
   every title — that is why an early filter pass returned Court Clerk and Housekeeping.
4. **Filter tokens of 3 characters or fewer are matched whole.** `it` must not match
   "**It**em Clerk", `qa` must not match "**Qa**tar". Longer tokens still match plurals.

## In flight

- Cron still **paused** for hiring.cafe; the move to the MacBook is still open. The
  watchlist stream needs no browser, so it can be scheduled anywhere immediately. Cron
  lines now point at `bin/`.
- `notify` still needs `GMAIL_USER` + `GMAIL_APP_PASSWORD` in `.env`. **No email has
  ever actually sent**, on either stream. Dry runs only.
- `pyproject.toml` is now `job-watch`. The GitHub remote is still `hiringcafe-watch` and
  the local directory is still `browser-use`; neither was renamed.

## Next

1. **Re-check `docs/unresolved.txt` through headed Chrome.** 25 employers, 10 of them in
   the Golden Horseshoe — which is exactly where results are currently empty. Faire was in
   this group until today and turned out to be Greenhouse. Highest value.
2. **Workday adapter** — 11 more employers: RBC, BMO, CIBC, Sun Life, Best Buy, Shoppers,
   Intact, Aritzia, Home Depot, Marmon, Procor. Needs a tenant + site name per line, not
   just a hostname.
3. Set the Gmail app password and confirm one real email arrives.

## Do not

- Re-add LLM extraction. DeepSeek emits malformed JSON past ~3k chars of action
  arguments; six consecutive failures is why this is deterministic.
- Change `bin/watch.sh`'s filters casually — `data/seen.json` is keyed on the filtered
  set. Same applies to `config/filters.txt` and `data/seen_sites.json`.
- Promise that fetching a job's detail page will fill in a missing date. It was checked
  across six employers: only Region of Waterloo publishes one there.

Full detail in `docs/NOTES.md` and `README.md`. Conversational path is
`.claude/skills/jobs/SKILL.md`.
