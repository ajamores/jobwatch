"""Two job watches over one shape of record.

`hiringcafe` casts the wide net through an aggregator and needs a headed browser.
`watchlist` goes straight to named employers' own boards and needs no browser at
all. Both emit the record defined in `watchlist/schema.py`, so `notify` and
`export` work against either.

Neither has an LLM in the extraction path. See docs/NOTES.md for why.
"""
