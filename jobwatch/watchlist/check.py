"""Check every employer in watchlist.txt directly, and report what is new.

This is the fast half of the job watch. Nothing here needs a browser, so it can run on a
short timer; hiring.cafe stays on its slow schedule as the wide net.

    python -m jobwatch.watchlist.check                      everything
    python -m jobwatch.watchlist.check --only bamboohr      one vendor
    python -m jobwatch.watchlist.check --site jobs.toronto.ca
    python -m jobwatch.watchlist.check --no-state           do not record what was seen
    python -m jobwatch.watchlist.check --reset              forget seen_sites.json first

Deliberately unlike the hiring.cafe parse, there is no age filter: a posting that has been open since
2024 is still worth seeing once. "New" means new to seen_sites.json.
"""

import argparse
import concurrent.futures as cf
import json
import sys
from datetime import datetime
from pathlib import Path

from ..paths import CONFIG, DATA
from . import ADAPTERS, parse_watchlist
from . import filters as filt
from .http import Unavailable


def check(site):
    """One employer. Returns (site, jobs, error) — a bad site never fails the run."""
    adapter = ADAPTERS[site.ats]
    try:
        jobs = adapter.fetch(site)
        # Institutional boards name buildings, not towns — "Town Hall", "Lake Erie
        # Works" — and the place filter would drop every one of them. where= in the
        # watchlist says which town the employer is actually in.
        where = site.extra.get("where")
        if where:
            for job in jobs:
                job["cities"] = [*job["cities"], where]
        return site, jobs, None
    except Unavailable as e:
        return site, [], str(e)
    except Exception as e:  # noqa: BLE001 — a markup change must not stop the others
        return site, [], f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("watchlist", nargs="?", default=str(CONFIG / "watchlist.txt"))
    ap.add_argument("--out", default=str(DATA / "sites_jobs.json"))
    ap.add_argument("--state", default=str(DATA / "seen_sites.json"))
    ap.add_argument("--new-out", default=str(DATA / "new_sites.json"))
    ap.add_argument("--no-state", action="store_true")
    ap.add_argument("--reset", action="store_true", help="forget the state file first")
    ap.add_argument("--only", help="one vendor, e.g. bamboohr")
    ap.add_argument("--site", help="one host from the watchlist")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--filters", default=str(CONFIG / "filters.txt"),
                    help="relevance rules; 'none' to keep everything")
    ap.add_argument("--suppress", default=str(DATA / "jobs.json"),
                    help="hide postings already reported by the hiring.cafe run; "
                         "'none' to disable")
    args = ap.parse_args()

    sites, problems = parse_watchlist(Path(args.watchlist).read_text())
    for p in problems:
        print(f"watchlist: {p}", file=sys.stderr)
    if args.only:
        sites = [s for s in sites if s.ats == args.only]
    if args.site:
        sites = [s for s in sites if s.host == args.site]
    if not sites:
        sys.exit("no sites selected")

    if args.reset:
        Path(args.state).unlink(missing_ok=True)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(check, sites))

    jobs, failures = [], []
    for site, found, err in results:
        if err:
            failures.append((site, err))
        print(f"  {site.ats:<15} {site.host:<30} "
              f"{'ERROR: ' + err[:44] if err else f'{len(found)} jobs'}", file=sys.stderr)
        jobs.extend(found)

    rules = filt.load(args.filters) if args.filters != "none" else filt.Filters()
    if rules:
        jobs, dropped = rules.apply(jobs)
        for why, n in sorted(dropped.items(), key=lambda x: -x[1]):
            print(f"  dropped {n:>4}  {why}", file=sys.stderr)

    # Dedupe within the run; the same posting can be listed twice on one board.
    unique, seen_ids = [], set()
    for job in jobs:
        if job["id"] in seen_ids:
            continue
        seen_ids.add(job["id"])
        unique.append(job)

    # Most of these boards never publish a posting date — Scotiabank prints one neither
    # on the list nor on the posting itself. So record when we first saw a job instead.
    # Checking every quarter of an hour makes that accurate enough to be the better
    # signal anyway: what matters is that it is new to you, not when HR pressed publish.
    state = Path(args.state)
    known = {}
    if state.exists():
        stored = json.loads(state.read_text())
        known = dict.fromkeys(stored) if isinstance(stored, list) else stored
    now = datetime.now().replace(microsecond=0).isoformat(" ")
    for job in unique:
        job["first_seen"] = known.get(job["id"]) or now

    new = unique if args.no_state else [j for j in unique if j["id"] not in known]

    # Do not report a job the hiring.cafe run has already emailed about.
    if args.suppress != "none" and Path(args.suppress).exists():
        already = {((j.get("company") or "").lower().strip(),
                    (j.get("title") or "").lower().strip())
                   for j in json.loads(Path(args.suppress).read_text())}
        before = len(new)
        new = [j for j in new
               if ((j["company"] or "").lower().strip(),
                   (j["title"] or "").lower().strip()) not in already]
        if before != len(new):
            print(f"  ({before - len(new)} already seen via hiring.cafe)", file=sys.stderr)

    # Detail costs a request per posting, so only ever pay it for the new ones.
    by_site = {}
    for job in new:
        by_site.setdefault(job["id"].split(":")[1], []).append(job)
    for site in sites:
        adapter = ADAPTERS[site.ats]
        batch = by_site.get(site.host)
        if batch and hasattr(adapter, "enrich"):
            try:
                adapter.enrich(site, batch)
            except Exception as e:  # noqa: BLE001
                print(f"  enrich {site.host}: {e}", file=sys.stderr)

    def newest_first(j):
        return (j["published"] or "", j["first_seen"] or "")

    unique.sort(key=newest_first, reverse=True)
    new.sort(key=newest_first, reverse=True)
    Path(args.out).write_text(json.dumps(unique, indent=1))
    if not args.no_state:
        known.update({j["id"]: j["first_seen"] for j in unique})
        state.write_text(json.dumps(known, indent=0, sort_keys=True))
        Path(args.new_out).write_text(json.dumps(new, indent=1))

    ok = len(sites) - len(failures)
    print(f"\n{len(unique)} jobs across {ok}/{len(sites)} employers"
          f"{'' if args.no_state else f', {len(new)} new'}")
    for j in new[:20]:
        age = f"{j['age_days']}d" if j["age_days"] is not None else "—"
        print(f"  {age:>4}  {(j['title'] or '')[:46]:<46} {(j['company'] or '')[:22]:<22} "
              f"{(j['location'] or '')[:24]:<24} {j['salary']['text'] or ''}")
    if failures:
        print(f"\n{len(failures)} employer(s) did not answer:")
        for site, err in failures:
            print(f"  {site.label} — {err[:90]}")


if __name__ == "__main__":
    main()
