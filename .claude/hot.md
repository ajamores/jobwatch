# hot — hiringcafe-watch

<https://github.com/ajamores/hiringcafe-watch> (private)

_Updated 2026-09-09_

## What this is

Two job watches. Neither has an LLM in the extraction path.

```
./watch.sh --no-mail          hiring.cafe. Wide net. Needs headed Chrome, ~1 min
./watch_sites.sh --no-mail    bookmarked employers, direct. No browser, 15-min safe
```

## State: both working, manual, uncommitted

The watchlist stream is new as of 2026-09-09 and **nothing is committed yet**.

17 employers, 3 adapters, 31 jobs after filtering. hiring.cafe path untouched and still works.

## The watchlist stream

Built because an aggregator is always a crawl behind. Going direct removes that lag, and
a plain careers API is cheap enough to poll every fifteen minutes.

| File | Does |
|---|---|
| `watchlist.txt` | The employers. Adding one is a line, not code |
| `sources/` | One adapter per **vendor**, not per employer — `bamboohr`, `greenhouse`, `successfactors` |
| `filters.txt` | Which titles and places count. Data, not code |
| `sites.py` | Runs it all → `sites_jobs.json` + `new_sites.json`, state in `seen_sites.json` |
| `watch_sites.sh` | `sites.py` then `notify.py` |
| `unresolved.txt` | 25 bookmarked employers with no adapter yet, and why |

The whole point: your 73 bookmarks use a handful of vendors between them. Three adapters
cover 17 employers.

## The four things that matter

1. **Most of these boards publish no posting date.** Scotiabank prints one neither on the
   list nor on the posting itself; of the SuccessFactors tenants only Toronto does. So
   `sites.py` records **first-seen** instead — `seen_sites.json` is now a dict of
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

- **Nothing committed.** Working tree has `sources/`, `sites.py`, `watch_sites.sh`,
  `watchlist.txt`, `filters.txt`, `unresolved.txt`, plus edits to `notify.py`,
  `export.py`, `profile.md`, `README.md`, `.gitignore`.
- Cron still **paused** for hiring.cafe; the move to the MacBook is still open. The
  watchlist stream needs no browser, so it can be scheduled anywhere immediately.
- `notify.py` still needs `GMAIL_USER` + `GMAIL_APP_PASSWORD` in `.env`. **No email has
  ever actually sent**, on either stream. Dry runs only.

## Next

1. **Re-check `unresolved.txt` through headed Chrome.** 25 employers, 10 of them in the
   Golden Horseshoe — which is exactly where results are currently empty. Faire was in
   this group until today and turned out to be Greenhouse. Highest value.
2. **Workday adapter** — 11 more employers: RBC, BMO, CIBC, Sun Life, Best Buy, Shoppers,
   Intact, Aritzia, Home Depot, Marmon, Procor. Needs a tenant + site name per line, not
   just a hostname.
3. Set the Gmail app password and confirm one real email arrives.

## Do not

- Re-add LLM extraction. DeepSeek emits malformed JSON past ~3k chars of action
  arguments; six consecutive failures is why this is deterministic.
- Change `watch.sh`'s filters casually — `seen.json` is keyed on the filtered set. Same
  now applies to `filters.txt` and `seen_sites.json`.
- Promise that fetching a job's detail page will fill in a missing date. It was checked
  across six employers: only Region of Waterloo publishes one there.

Full detail in `NOTES.md` and `README.md`. Conversational path is
`.claude/skills/jobs/SKILL.md`.
