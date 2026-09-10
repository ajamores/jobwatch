"""One module per job-board vendor, not one per employer.

Employers rent their careers pages rather than build them, so a handful of
adapters covers the whole watchlist. Each exposes:

    ATS                  the name used in watchlist.txt
    fetch(site)          -> [job, ...]   cheap; runs on every check
    enrich(site, jobs)   -> None         optional; detail pages, new postings only
"""
