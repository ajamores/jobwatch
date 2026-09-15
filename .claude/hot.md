---
type: meta
title: "Hot — job-watch"
updated: 2026-09-11
tags:
  - meta
  - hot-cache
status: evergreen
---
# Hot — job-watch (two job watches, no LLM in extraction)

> This repo's own working-memory board — session continuity, loaded at session start via
> `/hot`. A cache, not a journal: rewritten each save. Durable knowledge lives in this repo's
> own stores; business/vault learnings go to the vault's inbox (`wiki/projects/inbox/`).

## What this repo is

Armand's own job search, as two watches. `bin/watch.sh` sweeps hiring.cafe and needs a headed
Chrome (Cloudflare); `bin/watch-sites.sh` checks 75 employers on their own boards and needs no
browser. Python 3.12 via uv; everything runs as `python -m jobwatch.<thing>` from the repo root.
Nothing uses an LLM — `docs/NOTES.md` says why.

## Current State (2026-09-11)

- **Branch `main`**, last commit `8d7f6a0`. **Today's work is entirely uncommitted**: 9 files
  modified, 7 new.
- Landed today: a census of 287 institutional employers within 200km (`docs/census.tsv`) plus
  `watchlist/fingerprint.py` to identify each one's vendor; three new adapters — `workday`,
  `ukg`, `adp`. The watchlist went 17 → **75 employers across 6 adapters**. Last full run:
  **75/75 answered, 105 postings**. `filters.txt` gained exclusions for plant engineering and
  fundraising.
- **`data/` is untouched** — every test ran `--no-state` to a scratch file. Consequence: the
  first real `bin/watch-sites.sh` run reports all ~105 as new, in one burst.
- **NEXT:** commit this. Then the Taleo Business Edition adapter — 8 employers incl. St.
  Joseph's Health System and Town of Oakville, plain server-rendered HTML at
  `tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=<ORG>&cws=<N>`. Queue ranked in
  `docs/unresolved.txt` §B.

## Recent sessions (rolling — last 2–3)

### 2026-09-11 — the census, and three adapters off the back of it

- Fingerprinted 287 employers: 114 hand-roll their careers page, 157 rent one. That data chose
  what to build. All 18 school boards are unreachable (ApplyToEducation is login-walled);
  Njoyn and iCIMS refuse plain scripts.

### 2026-09-09 — repo packaged, data quarantined

- `8d7f6a0` gave the code a package shape; `e2bdd78` added the watchlist stream.

## Where the rest of the context lives

- **This repo has no decision record, lessons file or ticket store.** Durable knowledge sits in
  `docs/NOTES.md` (mechanics and why), `docs/unresolved.txt` (every unreached employer by
  vendor, with the reason, and the ranked build queue), `docs/check-by-hand.md` (227 employers
  with links — regenerate with `python -m jobwatch.watchlist.uncovered`), `README.md`, and the
  adapter docstrings. If a decision needs a home, the honest answer is a richer commit body.
- Conversational path: `.claude/skills/jobs/SKILL.md` (`/jobs`).
- **Business/vault context** (pricing, prospects, positioning) lives in the vault — `/garden`.
