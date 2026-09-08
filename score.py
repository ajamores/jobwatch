"""Apply Armand's hard exclusions and score fit. Judgments are explicit, not inferred at runtime."""

import json
from pathlib import Path

EXCLUDE = {
    3:  "Hybrid in Markham - named in hard exclusions.",
    8:  "Titled Senior Software Engineer.",
    15: "Titled Senior Software Engineer.",
    24: "Titled Software Engineer, Senior.",
    17: "Hybrid in Ottawa - east of Toronto.",
    37: "Onsite in Ottawa - east of Toronto.",
    38: "Onsite in Ottawa - east of Toronto.",
}

SCORES = {
    0:  (8, "Fidelity is fintech and fully remote at $101-118k, though the stack leans Python/AWS/AI over his Java core."),
    1:  (9, "Java, Spring Boot, TypeScript, MySQL and AWS is almost exactly his stack, Toronto hybrid, 2+ YOE."),
    2:  (9, "Explicitly a Java role at a payroll/HCM company, Toronto onsite, 2+ YOE - close to his co-op work."),
    4:  (4, "Space tech asking 4+ YOE, and the Toronto/Adelaide split suggests the real team is offshore."),
    5:  (7, "Toronto hybrid at $80-120k with no stated YOE floor, restaurant SaaS - reachable but not his sector."),
    6:  (8, "Remote in Canada, only 1+ YOE and $65-115k straddles his target band."),
    7:  (7, "Fintech and remote in Canada, but SWE II at $128-188k implies a bar above a new grad."),
    9:  (3, "Right sector (agri-manufacturing) but onsite in Leamington, roughly 3.5 hours from Hamilton."),
    10: (7, "Mississauga hybrid is in-region, medical-device manufacturing, 2+ YOE at $91-101k."),
    11: (7, "Backend, remote in Canada, and $70-80k sits squarely in his target band."),
    12: (6, "Toronto hybrid but 3+ YOE and the posting says little about the stack."),
    13: (9, "TD is banking, the role is explicitly Associate level, and $60-84k matches his target exactly."),
    14: (6, "Remote with Toronto listed, fintech-adjacent, but 3+ YOE."),
    16: (6, "Remote in Canada, edtech, 3+ YOE - a stretch but not out of reach."),
    18: (7, "Kitchener is in his region and 2+ YOE fits; Google's bar makes it a long shot rather than a poor fit."),
    19: (6, "Toronto onsite at $100-150k with no YOE floor stated, but an unknown early-stage company."),
    20: (7, "Mississauga hybrid, student-loan fintech, 3+ YOE - a Microsoft/.NET team rather than his Java core."),
    21: (8, "Oakville hybrid is his exact commute, govtech, $94-118k - only the 3+ YOE is a stretch."),
    22: (3, "AI research evaluation billed hourly, closer to contract work than the full-time developer role he wants."),
    23: (4, "Toronto onsite and no YOE floor, but embedded C/C++ is off his stack."),
    25: (9, "Sun Life is insurance/fintech, Associate level, 1+ YOE, Toronto/Waterloo hybrid at $54-89k."),
    27: (6, "Amazon Toronto onsite at 3+ YOE - strong name, level slightly above him."),
    28: (6, "Explicitly All Levels and remote from Toronto, but an unproven AI startup."),
    29: (8, "Manulife is insurance/fintech, Toronto hybrid, full-stack, 2+ YOE at $86-136k."),
    30: (6, "Remote across North America, 3+ YOE, security tooling."),
    31: (5, "Remote and Canada-eligible but 3+ YOE and a very broad multi-continent hiring pool."),
    32: (6, "Remote in Canada with no YOE floor stated, though 'Agentic AI' implies ML depth he lacks."),
    34: (6, "Remote in Canada at 2+ YOE, security domain is new to him."),
    35: (5, "Fully remote and a strong brand, but Supabase hires senior OSS contributors."),
    36: (8, "Explicitly a New Grad posting at $90-92k, Toronto onsite - the level is exactly right."),
    39: (2, "Toronto is listed and it says 4+ YOE, but $220-405k marks this as a staff-level hire in practice."),
}

recs = json.load(open("parsed.json"))
kept, excluded, seen_keys = [], 0, set()
dupes = 0

for i, r in enumerate(recs):
    if i in EXCLUDE:
        excluded += 1
        continue
    key = (r["title"], r["company"], r["location"], r["salary"])
    if key in seen_keys:
        dupes += 1
        continue
    seen_keys.add(key)
    score, reason = SCORES[i]
    kept.append({
        "title": r["title"], "company": r["company"], "location": r["location"],
        "work_model": r["work_model"], "salary": r["salary"], "posted": r["posted"],
        "years_required": r["years_required"], "tech_stack": r["tech_stack"],
        "url": r["url"], "fit_score": score, "fit_reason": reason,
    })

AGE = {"h": 1, "d": 24, "w": 168, "mo": 720}
def hours(p):
    num = "".join(c for c in p if c.isdigit())
    unit = "".join(c for c in p if c.isalpha())
    return int(num or 0) * AGE.get(unit, 1)

kept.sort(key=lambda r: (hours(r["posted"]), -r["fit_score"]))

summary = {
    "filters_skipped": [],
    "total_seen": len(recs),
    "total_excluded": excluded,
    "duplicates_removed": dupes,
}
Path("results.json").write_text(json.dumps(kept + [summary], indent=1))
print(f"kept {len(kept)} | excluded {excluded} | duplicates {dupes} | seen {len(recs)}")
