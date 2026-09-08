"""jobs.json -> jobs.csv, one row per posting, for opening in Sheets or Excel.

The last three columns — Status, Applied on, Notes — are yours to fill in. Re-exporting
carries whatever you typed in them across to the new file, matched on the apply URL, so
a refresh does not wipe your tracking. Pass --clobber to start clean.

    python export.py [jobs.json] [--out jobs.csv]
"""

import argparse
import csv
import json
from pathlib import Path

TRACKED = ("Status", "Applied on", "Notes")  # yours; never overwritten by a re-export

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
    # Left blank for you to fill in as you work the list.
    ("Status", lambda j: ""),
    ("Applied on", lambda j: ""),
    ("Notes", lambda j: ""),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs", nargs="?", default="jobs.json")
    ap.add_argument("--out", default="jobs.csv")
    ap.add_argument("--clobber", action="store_true",
                    help="discard any Status / Applied on / Notes already in the file")
    args = ap.parse_args()

    jobs = json.loads(Path(args.jobs).read_text())
    out = Path(args.out)

    kept = {}
    if out.exists() and not args.clobber:
        with open(out, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                marks = {c: (row.get(c) or "").strip() for c in TRACKED}
                if any(marks.values()):
                    kept[row.get("Apply")] = marks

    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in COLUMNS])
        for j in jobs:
            row = {name: fn(j) for name, fn in COLUMNS}
            row.update(kept.get(j["apply_url"], {}))
            w.writerow([row[name] for name, _ in COLUMNS])

    carried = sum(1 for j in jobs if j["apply_url"] in kept)
    orphans = len(kept) - carried
    print(f"wrote {out}: {len(jobs)} rows, {len(COLUMNS)} columns"
          + (f", carried {carried} annotated" if carried else "")
          + (f", {orphans} annotated row(s) no longer in the results" if orphans else ""))


main()
