"""jobs.json -> jobs.csv, one row per posting, for opening in Sheets or Excel.

Data only. Application tracking lives in Armand's own tracker, so this deliberately
adds no Status / Applied / Notes columns.

    python export.py [jobs.json] [--out jobs.csv]
"""

import argparse
import csv
import json
from pathlib import Path

COLUMNS = [
    ("Posted", lambda j: (j["published"] or "")[:10]),
    ("Age (days)", lambda j: j["age_days"]),
    ("Title", lambda j: j["title"]),
    ("Company", lambda j: j["company"]),
    ("Location", lambda j: j["location"]),
    ("Workplace", lambda j: j["workplace_type"]),
    ("Seniority", lambda j: j["seniority"]),
    ("Min YOE", lambda j: j["yoe"]),
    ("Salary low", lambda j: j["salary"]["min"]),
    ("Salary high", lambda j: j["salary"]["max"]),
    ("Currency", lambda j: j["salary"]["currency"]),
    ("Per", lambda j: j["salary"]["frequency"]),
    ("Salary", lambda j: j["salary"]["text"]),
    ("Category", lambda j: j["category"]),
    ("Role type", lambda j: j["role_type"]),
    ("Tech", lambda j: ", ".join(j["tech"] or [])),
    ("Requirements", lambda j: j["requirements"]),
    ("Visa sponsorship", lambda j: j["visa_sponsorship"]),
    ("Company site", lambda j: j["company_site"]),
    ("What they do", lambda j: j["tagline"]),
    ("Applicants", lambda j: j["applies"]),
    ("Views", lambda j: j["views"]),
    ("Board", lambda j: j["source"]),
    ("Apply", lambda j: j["apply_url"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs", nargs="?", default="jobs.json")
    ap.add_argument("--out", default="jobs.csv")
    args = ap.parse_args()

    jobs = json.loads(Path(args.jobs).read_text())
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in COLUMNS])
        for j in jobs:
            w.writerow([fn(j) for _, fn in COLUMNS])
    print(f"wrote {args.out}: {len(jobs)} rows, {len(COLUMNS)} columns")


main()
