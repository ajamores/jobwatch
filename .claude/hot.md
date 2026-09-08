# hot — browser-use / hiring.cafe scraper

_Updated 2026-09-08_

## What this is

A job scraper for hiring.cafe. Started as a browser-use/LLM experiment, ended up
deterministic — no model touches the extraction path.

## State: working, manual

```
./watch.sh --no-mail      # check for new postings, print them
```

Ontario · Software Development · Entry+Mid · Full Time · 14 days → 136 jobs, 82 companies.

## The three things that matter

1. **hiring.cafe is Next.js SSR.** No XHR to intercept. Results come from
   `/_next/data/<buildId>/index.json?searchState=…&page=N`. `buildId` changes on every
   deploy — read it at runtime, never hardcode.
2. **Headed Chrome only.** Headless never clears Cloudflare, and curl gets a 403. The
   endpoint has to be called with `fetch()` from inside a page that already passed.
3. **`departments` beats `searchQuery`.** Exact, server-side, no noise. The fuzzy text
   search returns gold-mine planning engineers.

## In flight

- Cron is **paused** (crontab entry commented). Moving the schedule to the old MacBook —
  WSL cron dies when the terminal closes. Porting steps are in `NOTES.md`.
- `notify.py` needs `GMAIL_USER` + `GMAIL_APP_PASSWORD` in `.env`. Not yet set, so email
  is untested end to end. Everything else runs.

## Next

- Set the app password, confirm one real email arrives.
- Stand it up on the MacBook.
- `score.py` / `profile.md` — job-fit ranking, parked. The `jobs` skill reads `profile.md`
  conversationally instead, which may be enough.

## Do not

- Re-add LLM extraction. DeepSeek emits malformed JSON past ~3k chars of action
  arguments; six consecutive failures is why this is deterministic.
- Change `watch.sh`'s filters casually — `seen.json` is keyed on the filtered set, so it
  reports a burst of fake "new" jobs.

Full detail in `NOTES.md`. Conversational path is `.claude/skills/jobs/SKILL.md`.
