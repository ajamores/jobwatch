"""jobs_raw.json -> jobs.json: flatten hiring.cafe's SSR records to the fields that matter.

Pure field selection from structured JSON — nothing is parsed out of prose, so nothing
here can invent a value or go stale when the markup changes.

Also tracks which postings have been seen before (seen.json), so a scheduled run can
report only what is new.

    python -m jobwatch.hiringcafe.parse [--location "Toronto,Hamilton"] [--workplace Remote]
                                        [--max-age 7] [--salary-min 90000]
"""

import argparse
import json
import time
from pathlib import Path

from ..paths import DATA

DAY_MS = 86_400_000


def money(v5):
    """Compensation as a single readable band, whatever frequency it was listed at."""
    for freq, lo, hi, unit in (
        ("Yearly", "yearly_min_compensation", "yearly_max_compensation", "yr"),
        ("Hourly", "hourly_min_compensation", "hourly_max_compensation", "hr"),
        ("Monthly", "monthly_min_compensation", "monthly_max_compensation", "mo"),
        ("Weekly", "weekly_min_compensation", "weekly_max_compensation", "wk"),
    ):
        a, b = v5.get(lo), v5.get(hi)
        if a or b:
            cur = v5.get("listed_compensation_currency") or ""
            fmt = lambda n: f"{int(n):,}" if n else "?"
            return {
                "min": a, "max": b, "currency": cur, "frequency": freq,
                "text": f"{fmt(a)}-{fmt(b)} {cur}/{unit}".strip(),
                "transparent": bool(v5.get("is_compensation_transparent")),
            }
    return {"min": None, "max": None, "currency": None, "frequency": None,
            "text": None, "transparent": False}


def keeps(job, args):
    """Client-side narrowing, applied after the server has done its filtering."""
    if args.location:
        hay = " ".join(str(job.get(k) or "") for k in
                       ("location", "cities", "states", "countries")).lower()
        if not any(t.strip().lower() in hay for t in args.location.split(",") if t.strip()):
            return False
    if args.workplace:
        want = {t.strip().lower() for t in args.workplace.split(",") if t.strip()}
        if (job["workplace_type"] or "").lower() not in want:
            return False
    if args.max_age is not None and (job["age_days"] is None or job["age_days"] > args.max_age):
        return False
    if args.salary_min and job["salary"]["frequency"] == "Yearly":
        top = job["salary"]["max"] or job["salary"]["min"]
        if top and top < args.salary_min:
            return False
    return True


def flatten(hit):
    v5 = hit.get("v5_processed_job_data") or {}
    ji = hit.get("job_information") or {}
    org = hit.get("attributed_org") or {}
    published = v5.get("estimated_publish_date_millis")
    return {
        "id": hit.get("id"),
        "collapse_key": hit.get("collapse_key"),
        "title": ji.get("title") or ji.get("job_title_raw") or v5.get("core_job_title"),
        "company": v5.get("company_name") or org.get("name"),
        "company_site": v5.get("company_website"),
        "tagline": v5.get("company_tagline"),
        "location": v5.get("formatted_workplace_location"),
        "cities": v5.get("workplace_cities") or [],
        "states": v5.get("workplace_states") or [],
        "countries": v5.get("workplace_countries") or [],
        "workplace_type": v5.get("workplace_type"),
        "commitment": v5.get("commitment"),
        "seniority": v5.get("seniority_level"),
        "yoe": v5.get("min_industry_and_role_yoe"),
        "salary": money(v5),
        "category": v5.get("job_category"),
        "role_type": v5.get("role_type"),
        "tech": v5.get("technical_tools") or [],
        "requirements": v5.get("requirements_summary"),
        "visa_sponsorship": v5.get("visa_sponsorship"),
        "published": v5.get("estimated_publish_date"),
        "published_millis": published,
        "age_days": round((time.time() * 1000 - published) / DAY_MS) if published else None,
        "expired": hit.get("is_expired"),
        "source": hit.get("source"),
        "applies": ji.get("num_applies"),
        "views": ji.get("num_views"),
        "apply_url": hit.get("apply_url"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", nargs="?", default=str(DATA / "jobs_raw.json"))
    ap.add_argument("--out", default=str(DATA / "jobs.json"))
    ap.add_argument("--state", default=str(DATA / "seen.json"))
    ap.add_argument("--no-state", action="store_true")
    ap.add_argument("--new-out", default=str(DATA / "new.json"))
    ap.add_argument("--category", default="all",
                    help='job_category to keep; default "all" because search.py already '
                         'filters server-side via departments')
    ap.add_argument("--location", help="comma-separated; keep jobs mentioning any of them "
                                       'e.g. "Toronto,Hamilton,Burlington"')
    ap.add_argument("--workplace", help='comma-separated: Remote, Hybrid, Onsite')
    ap.add_argument("--max-age", type=int, help="drop postings older than N days")
    ap.add_argument("--salary-min", type=int, help="drop yearly bands whose max is below this "
                                                   "(jobs with no listed salary are kept)")
    args = ap.parse_args()

    raw = json.loads(Path(args.raw).read_text())
    candidates = []
    for hit in raw["hits"]:
        job = flatten(hit)
        if job["expired"]:
            continue
        if args.category != "all" and job["category"] != args.category:
            continue
        if not keeps(job, args):
            continue
        candidates.append(job)

    # Dedupe after sorting so the newest copy of a repost is the one kept. collapse_key
    # alone misses the same role syndicated to two boards, so fall back to company+title.
    candidates.sort(key=lambda j: j["published_millis"] or 0, reverse=True)
    jobs, seen_keys, seen_pairs = [], set(), set()
    for job in candidates:
        key = job["collapse_key"] or job["id"]
        pair = ((job["company"] or "").strip().lower(),
                (job["title"] or "").strip().lower())
        if key in seen_keys or (all(pair) and pair in seen_pairs):
            continue
        seen_keys.add(key)
        seen_pairs.add(pair)
        jobs.append(job)
    Path(args.out).write_text(json.dumps(jobs, indent=1))

    new = jobs
    if not args.no_state:
        state_path = Path(args.state)
        known = set(json.loads(state_path.read_text())) if state_path.exists() else set()
        new = [j for j in jobs if (j["collapse_key"] or j["id"]) not in known]
        state_path.write_text(json.dumps(sorted(known | seen_keys), indent=0))
        Path(args.new_out).write_text(json.dumps(new, indent=1))

    label = "jobs" if args.category == "all" else f"{args.category} jobs"
    print(f"{len(raw['hits'])} hits -> {len(jobs)} {label} (site reports {raw.get('total')})"
          f"{'' if args.no_state else f', {len(new)} new'}")
    for j in (new or jobs)[:15]:
        print(f"  {str(j['age_days']) + 'd':>4}  {(j['title'] or '')[:44]:<44} "
              f"{(j['company'] or '')[:22]:<22} {(j['location'] or '')[:26]:<26} "
              f"{j['salary']['text'] or ''}")


if __name__ == "__main__":
    main()
