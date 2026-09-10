"""The wide net: hiring.cafe's own SSR data endpoint.

`search` builds the query URL, `scrape` walks every page of results, `parse`
flattens and filters them. Needs a headed Chrome — headless never clears
Cloudflare.
"""
