# browser-use + hiring.cafe — working notes

Last updated: 2026-09-08

## Setup

- `browser-use` 0.13.10, Python 3.12 via uv, venv in `.venv`. Local project renamed
  `browser-use-lab` in `pyproject.toml` — a project named `browser-use` cannot depend on
  the package `browser-use`.
- Browser: system `/usr/bin/google-chrome`. No Playwright — browser-use 0.13 drives
  Chrome over CDP directly.
- LLM: DeepSeek. Key in `.env` (gitignored), copied from `~/.config/mg-deepseek/key.env`.
- Models: `deepseek-v4-pro` (default), `deepseek-v4-flash`, `deepseek-v4-flash-vision-exp`.

## Model findings

- **Use `-pro`, not `-flash`.** Flash emitted malformed action arguments (invented a
  `new_tab` field the schema rejects), then hallucinated a DNS failure to explain itself.
- **`-flash-vision-exp` genuinely works.** Verified two ways: raw API on a solid-red test
  image, and end to end through browser-use. The DeepSeek serializer
  (`browser_use/llm/deepseek/serializer.py`) forwards `image_url` parts intact.
- **Reasoning tokens eat the budget.** `max_tokens: 50` returned an empty string with
  `reasoning_tokens: 50`. Set `max_tokens` in the thousands or you get blank replies.
- **The hard ceiling: DeepSeek emits malformed JSON once an action argument passes roughly
  3,000 characters.** Both pro and the flash fallback failed six consecutive times trying
  to `write_file` a batch of ~10 job records. This is why extraction is deterministic and
  not LLM-driven. Short outputs are fine — scoring one posting per call would be reliable.
- Long URLs in the prompt also break it: given an 887-char URL, the model insisted it was
  truncated and refused to navigate. Fixed with `--url`, which navigates via
  `initial_actions` before the LLM ever runs.

## Cloudflare

hiring.cafe sits behind Cloudflare Turnstile ("Verify you are human").

- `curl` → 403. Headless Chrome → challenge loops forever, never resolves.
- **Headed Chrome passes it immediately.** That is the whole fix; no stealth patching
  involved. Run with `--headful` (WSLg provides the display).
- browser-use detects this and nudges toward its paid cloud browser. Not needed.

## hiring.cafe mechanics

**Filter state is fully encoded in the URL** as `?searchState=<url-encoded JSON>`. Set
filters by building the URL, not by clicking. Keys discovered by driving the UI once:

| Filter | Key |
|---|---|
| Query | `searchQuery: "software developer"` |
| Location | `locations: [{...}]` — Ontario object incl. `id: "AxY1yZQBoEtHp_8UErDW"` |
| Seniority | `seniorityLevel: ["Entry Level","Mid Level"]` |
| Job type | `commitmentTypes: ["Full Time"]` |
| Date posted | `dateFetchedPastNDays: 14` |

Leave `workplace_types: []` inside the location object to keep onsite + hybrid + remote.
Setting it to `["Remote"]` filters to remote only.

Date Posted options: All time, 24 hours, 3 days, 1 week, 2 weeks, 3 weeks, 1 month,
2/3/4/5/6 months, 1/2/3 years, Custom range.

**Do not click job cards** — that opens a sign-in modal. Everything needed is already
printed on the card: age badge, title, location, salary band, work-model badge,
commitment badge, company + blurb, YOE badge, tech-stack line, and a `Job Posting` link
whose href is a real shareable URL (`/job/<slug>-<id>`).

**DOM:** cards are the children of `div.grid.grid-cols-1`. Card `innerText` is
newline-separated and regular:

```
4d / Software Developer / Toronto, Ontario, Canada / $101k-$118k/yr / Remote /
Full Time / Company: blurb / 2+ YOE<requirements> / <comma-separated tech stack>
```

**40 cards load per page and the grid does NOT infinite-scroll.** Scrolling loads nothing
more. The current filtered search reports 182 jobs, so 142 are unreached — pagination is
still unsolved.

## Pipeline

| File | Does |
|---|---|
| `run.py` | browser-use agent runner. `--task-file`, `--url` (deterministic pre-nav), `--vision`, `--headful`, `--steps`, `--profile`. Has a fallback LLM and `llm_timeout=180`. |
| `chrome.py` | Finds Chrome. `CHROME_PATH` wins, else the first known location that exists (macOS app bundle, then the Linux paths). |
| `watch.sh` | One whole check: scrape → parse → notify. `--no-mail` prints instead of emailing, `--reset` forgets `seen.json`. Portable — skips the display exports on macOS, resolves its own directory. |
| `search.py` | Builds `search_url.txt` from plain English via hiring.cafe's own `/api/ai-search/parse-filters`. `--show` explains the current one. |
| `scrape.py` | No agent. Headed Chrome clears Cloudflare, then `fetch()`es `/_next/data/<buildId>/index.json?searchState=…&page=N` from inside the page until `ssrIsLastPage`. Writes every raw hit to `jobs_raw.json`. |
| `parse.py` | `jobs_raw.json` → `jobs.json`. Field selection from structured JSON — no string parsing left. Dedupes on `collapse_key`, drops expired, filters to `--category "Software Development"` (`--category all` to keep everything), sorts newest first. Diffs against `seen.json` and writes the unseen ones to `new.json`. |
| `score.py` | **Out of scope.** Job-fit scoring against a personal profile. Ignore unless you want it back. |
| `netwatch.py` | CDP network recorder. Enables `Network` before navigation, dumps every xhr/fetch body to `netlog/`. Used for the API check. |
| `example.py` | Minimal browser-use hello-world. |

**Run order: `search.py "…"` (only when the search changes) → `scrape.py` → `parse.py`.**

Headed is not optional. Headless Chrome never clears the challenge, so `__NEXT_DATA__`
never appears and the run dies at `buildId`. Retested 2026-09-08 against the endpoint —
same result. `user_data_dir` is ignored by browser-use 0.13 (it logs "Created new profile
in temp directory"), so every run clears Cloudflare from scratch; there is no warm profile
to lean on.

**Neither script uses an LLM.** No API key, no DeepSeek, no tokens — verified by running both
with `DEEPSEEK_API_KEY` unset. `run.py`, `example.py`, `score.py` and `profile.md` are the
LLM-driven experiments and are not needed to scrape.

## Results (2026-09-08, API pipeline)

**179 raw hits over 4 pages → 131 after dedupe → 89 in Software Development.** Was 40
cards and 31 kept. `cards.json` / `parsed.json` / `results.json` are the old DOM-scraping
outputs, kept only for comparison.

Category spread across the 131: Software Development 89, Engineering 12, R&D 8, Sales 5,
QA 3, then singles. The `searchQuery` is fuzzy semantic matching, so a gold mine's Short
Range Planning Engineer and a wastewater graduate programme both survive it — hence the
`job_category` filter in `parse.py`.

Of the 89: 53 Mid Level / 36 Entry Level, 36 Remote / 29 Hybrid / 24 Onsite, 64 with a
salary band.

## Results (2026-09-08, old DOM run)

40 seen, 7 excluded, 2 duplicates, **31 kept** in `results.json`. Top fits: TD Bank Group
and Sun Life (both Associate-level, banking/insurance, salary on target), Autodesk
(Java/Spring Boot bullseye), Dayforce (explicit Java role), Euna Solutions (Oakville).

Excluded: IBM (Markham), March Networks / Caivan / QNX (Ottawa), Point Digital / Clutch /
Qualcomm (Senior titles).

Judgment calls worth revisiting: Perplexity survived the rules at 4+ YOE but is staff-level
in practice ($220–405k), scored 2. TD lists "Toronto or London" — unclear whether that is
Ontario or the UK. Nature Fresh Farms is the right sector but onsite in Leamington.

## Building a search

`/api/ai-search/parse-filters?query=<plain English>` is hiring.cafe's own natural-language
filter parser (Gemini 2.5 Flash behind it). It returns a `suggestedFilters` object with a
proper `locations[]` entry — including the internal `id` and geometry, which cannot be
hand-written. `search.py` asks it, merges the standing defaults, and writes the URL.

```
python search.py "software developer jobs in Ontario Canada"
python search.py "qa engineer jobs near Hamilton Ontario" --radius 60 --out searches_qa_hamilton.txt
python search.py --show
```

**`departments` is a real searchState key and it is exact.** Ontario + `departments:
["Quality Assurance"]` returns 46 hits, every one of them Quality Assurance. The fuzzy
`searchQuery` returns 61 of 63 on-target plus a gold mine's Short Range Planning Engineer.
`search.py` therefore drops the free text and filters on departments alone — pass
`--keep-query` to put the text back for a wider, fuzzier net.

Department values seen so far: Software Development, Quality Assurance, Engineering,
Research and Development (R&D), Information Technology, Data and Analytics, Product
Management, Sales, Business Development, Business Operations, Customer Service, Finance
and Accounting, Human Resources, Education services, Environment Health and Safety,
Skilled Trades - Maintenance and Repair.

**Location options — `flexible_regions`, not `radius`.**

| Option | Effect |
|---|---|
| `flexible_regions: [anywhere_in_country, anywhere_in_continent, anywhere_in_world]` | **Worth 136 results vs 102.** Admits postings listed as "anywhere in Canada" or worldwide-remote. On by default; `--strict-location` drops it. |
| `radius` / `radius_unit` | Only meaningful for a `locality`. Hamilton at 50mi → 90 jobs, at 10mi → 0. |
| `radius` on a province | Meaningless — Ontario's centroid is ~500km north of anywhere anyone works. `search.py` strips it for `administrative_area_level_*` and `country`. |

parse-filters returns `radius: 50` on provinces regardless. That is what silently costs 34
results if left alone.

## Filtering the results

`parse.py` narrows client-side, after the server has filtered:
`--location "Toronto,Hamilton"` (matches formatted location, cities, states, countries),
`--workplace Remote,Hybrid`, `--max-age 7`, `--salary-min 90000`, `--category "…"`.

**Dedupe runs after the date sort**, so the newest copy of a repost survives.
`collapse_key` alone is not enough — the same role syndicated to two boards gets two
collapse keys, which is how Citi appeared three times and Sun Life twice. Company+title is
the fallback key.

`seen.json` records what has already been reported, so a scheduled run only surfaces what
is new. It is keyed on the filtered set — **change the filters and the next run reports a
burst of "new" jobs that are not actually new.** Keep the cron's flags fixed.

## Automation

```
watch.sh  →  scrape.py  →  parse.py <fixed filters>  →  notify.py
```

**Currently manual.** Run `./watch.sh --no-mail` to check by hand.

The crontab entry exists but is **paused as of 2026-09-08** — the schedule is moving to
the old MacBook, which can stay awake without WSL being open:

```
#PAUSED 0 8,11,14,17,20,23 * * * /home/you/hiringcafe-watch/watch.sh
```

Cron hands a script almost no environment, so on Linux/WSL `watch.sh` exports `DISPLAY`,
`WAYLAND_DISPLAY` and `XDG_RUNTIME_DIR` explicitly — without them Chrome cannot reach
WSLg and the run dies. It skips all three on macOS, where they are meaningless.

**Why the schedule is leaving WSL:** cron only fires while WSL is running. Close the
terminal for the day and it stops silently, with no error to notice.

### Moving it to the MacBook

1. Clone the repo, `uv sync`.
2. Chrome is found automatically at `/Applications/Google Chrome.app/...`; set
   `CHROME_PATH` in `.env` only if it lives somewhere else.
3. Copy `.env` across (it is gitignored, so it will not come with the clone).
4. Copy `seen.json` too, or the first run emails the entire back catalogue.
5. `crontab -e`, same line with the new path.
6. macOS sleeps. `caffeinate`, or Settings → Battery → Prevent automatic sleeping, or the
   runs simply will not happen.

`notify.py` emails the contents of `new.json` as an HTML digest — title, company,
location, salary band, workplace type, seniority, YOE, tech stack, and a direct link to
the employer's own apply page (not hiring.cafe's). It sends nothing when nothing is new.

Credentials go in `.env`:

```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=<16 chars from myaccount.google.com/apppasswords>
```

That is a Google **app password**, not the account password, and it needs 2FA enabled on
the account. `notify.py --dry-run` prints the digest without sending.

## Claude Code

`.claude/skills/jobs/SKILL.md` is the conversational path — "QA jobs near Hamilton",
"anything new?" It drives these same scripts and reads results against `profile.md`; it
does not reimplement any of the scraping.

The split is deliberate: `watch.sh` is the scheduled path and stays a plain shell script,
because a cron run at 3am should not need a model in the loop. The skill is for sitting
down to apply, where the work is judgment rather than fetching.

## Known gaps

1. ~~**Pagination — 40 of ~186.**~~ Solved — see the API check below.
2. ~~**Query is baked into `search_url.txt`.**~~ Solved — `search.py` builds it.
3. **Headed only.** Every scheduled run opens a visible Chrome window for ~15s.
4. `ssrTotalCount` overstates slightly (136 reported, 126 hits returned). Not chased.

## API check (2026-09-08) — answered: yes, and it solves pagination

There is no XHR search call to intercept. hiring.cafe is **Next.js SSR**: the full result
set is embedded in the page's `__NEXT_DATA__` script tag, not fetched by the client.
`netwatch.py` logged all 110 requests on a filtered load — the only same-origin fetches
were `api/getCountry`, `api/ai-search/parse-filters`, and an empty `_next/data` ping. No
service worker, no websocket.

**`props.pageProps` of `__NEXT_DATA__`:**

| Key | Value on the Ontario search |
|---|---|
| `ssrHits` | 63 full job records (array) |
| `ssrTotalCount` | 189 |
| `ssrCompanyCount` | 122 |
| `ssrPage` | 0 |
| `ssrPageSize` | 40 |
| `ssrIsLastPage` | false |
| `initialSearchState` | the searchState object, echoed back |

`ssrHits` exceeds `ssrPageSize` because hits carry dedup siblings (`collapse_key`,
`strict_dedup_cluster_id`, `liberal_dedup_cluster`); 40 collapsed cards render.

**The endpoint.** Next.js exposes the same props as JSON at

```
/_next/data/<buildId>/index.json?searchState=<url-encoded JSON>&page=<N>
```

- `buildId` is `__NEXT_DATA__.buildId` — currently `oCtIMybESKe9L9iLl1vJ4`, changes every
  deploy, so read it at runtime, never hardcode.
- **`page` is a top-level query param, not a searchState key.** Verified: `&page=1` and
  `&page=2` return `ssrPage` 1 and 2 with disjoint ids. Putting `page` / `currentPage` /
  `pageNumber` / `from` inside searchState is silently ignored — still page 0.
- Header `x-nextjs-data: 1` sent; unclear whether it is required.

**Pagination gap is closed.** 189 results ÷ 40 per page = 5 calls, loop until
`ssrIsLastPage`.

**Cloudflare still applies.** `curl` against the endpoint returns 403 "Just a moment..."
with or without a browser UA. The endpoint must be called with `fetch()` from inside the
already-cleared headed Chrome page — same origin, cookies present, works first try.

**The records are far richer than the cards.** Each hit has `job_information`,
`apply_url`, `_geoloc`, `enriched_company_data`, `attributed_org_card`, and a
`v5_processed_job_data` block of ~90 fields — structured salary (yearly/monthly/weekly/
hourly min+max, currency, frequency, `is_compensation_transparent`), `seniority_level`,
`min_industry_and_role_yoe`, `workplace_type`, `workplace_cities/states/countries`,
`technical_tools`, `requirements_summary`, `job_category`, `role_type`, degree
requirements, `visa_sponsorship`, benefits flags, `estimated_publish_date_millis`.

**Verdict: finish this scraper, drop Firecrawl.** Firecrawl was only ever worth it to fix
fragile text parsing — this removes the parsing entirely. `parse.py` becomes field
selection from JSON instead of regex over `innerText`.

**Done:** `scrape.py` and `parse.py` now run on this endpoint.

Pages do not return `ssrPageSize` hits — 63, 57, 48, 11 for this search — because hits
carry dedup siblings. 179 hits collapse to 131 cards against a reported `ssrTotalCount`
of 189; the ES total counts something slightly different. Not worth chasing.

## Current search

Ontario · Software Development · Entry + Mid · Full Time · last 14 days · flexible regions.
136 jobs at 82 companies as of 2026-09-08.

`search_url.txt` holds it; `searches_qa_hamilton.txt` is a second saved search (QA within
60mi of Hamilton). Neither needs to be hand-edited any more — `search.py` writes them, and
`search.py --show` explains whichever one you point it at.

```
python search.py --show
python search.py --show --out searches_qa_hamilton.txt
```
