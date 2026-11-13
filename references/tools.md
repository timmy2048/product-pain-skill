# Tooling notes (free first)

Paid keyword, rank, or review suites may be cited if the user already has access. They are never required to finish a v1 run. Official APIs are optional accelerators, not prerequisites. Do not delay a run while an API application is under review.

## Demand and search

- **Google Search** plus a free overlay such as Keyword Surfer, when installed: use the figure you can see on the results page and label it as an extension estimate. Keyword Surfer only works in a browser with the extension. Build Google URLs with `hl=en` and `gl` set to the target market so you are not silently redirected to a local domain.
- **Google Trends**: `https://trends.google.com/trends/explore?q={query}&date=today%205-y&geo={market}`. Optional. Good for direction (rising, flat, fading), not for absolute volume. Worldwide vs country must be stated. The public web UI may rate-limit automated requests; `pytrends` is an unofficial scripted option if it still returns data, and those figures stay estimates. If the page is blocked, mark Trends as unverified and lean on ecommerce proxies.
- If official Keyword Planner data is not available, do not invent it. Either use another labeled estimate or mark volume as unverified and lean on ecommerce proxies.
- Third-party trend blogs and shop-sales dashboards are leads only, never evidence that gate 1 or gate 2 has passed.

## Ad library and traffic

- **Meta Ad Library**: `https://www.facebook.com/ads/library/`. Search the brand or the pain keyword. Use URLs from `scripts/build_search_urls.py` (they include `search_type` and `media_type`). Note whether ads are still active, roughly how many, and how long a creative or advertiser has been running. These are spend and expansion clues, not proof that the product is profitable. The public page is often behind a script challenge; if a fetch is blocked, open it in a browser or, when the user already has a Meta developer app and a user token with `ads_read` (identity verification is often required), use the official [Ad Library API](https://www.facebook.com/ads/library/api/). Coverage through the API can be narrower than the website. If you still cannot open it, record the gap. Do not wait on app review before continuing the other gates.
- **Similarweb free snapshot**: `https://www.similarweb.com/website/{domain}/`. Strip a leading `www.` from the domain. Capture only what the free page shows (often a traffic band or trend, sometimes a source mix). If the free view is blank or paywalled, write "traffic unknown." Automated fetches may return an empty response even when a browser or another fetch path works; try once more or record the gap. Treat Similarweb numbers as estimates and as leads, not as proof for gates 1–2.

## Trademarks and patents

Official name search is a browser step for gate 8a. Automated fetches of these pages often return an empty shell. Search each name candidate (exact and near marks, relevant classes) on the office that matches each target market in the run. A third-party site can be a lead, not a clearance. Do not call undocumented internal search endpoints.

- **United States — USPTO**: [Trademark Search](https://tmsearch.uspto.gov/). A start page also lives at `https://www.uspto.gov/trademarks/search`. There is no official API that searches by brand name. The TSDR API looks up an already-known serial or registration number; it does not replace a name search. Official bulk data is available through the USPTO Open Data Portal, but it is not required for a v1 name check.
- **United Kingdom — UK IPO**: [Search for a trade mark](https://trademarks.ipo.gov.uk/ipo-tmtext) (word search). The GOV.UK landing page is `https://www.gov.uk/search-for-trademark`.
- **Australia — IP Australia**: [Australian Trade Mark Search](https://search.ipaustralia.gov.au/trademarks/search).
- **Canada — CIPO**, when Canada is in the run: [Canadian Trademarks Database](https://ised-isde.canada.ca/cipo/trademark-search/srch/).
- **New Zealand — IPONZ**, when selected: [Search for a trade mark](https://www.iponz.govt.nz/about-ip/trade-marks/search/).
- **Ireland**, when selected: [EUIPO eSearch](https://euipo.europa.eu/eSearch/) for EU marks, plus the national office if you can open it.
- **Google Patents**: `https://patents.google.com/?q={query}`. Look for utility or design patents that would block the proposed form.

Gate 8a is not passed until the official searches you intended are actually completed in a browser. "No hits on an unofficial site" is not a clearance. Candidate brand names stay candidates. Completing the search is not a legal opinion.

Supplier pages used later in gate 8b (for example a public factory listing) are often blocked by captchas. Record the gap, use the RFQ in `templates/rfq.md`, and do not invent MOQ or ex-factory prices. Do not contact a supplier unless the user has agreed.

## URL helper

`python scripts/build_search_urls.py --keywords "example pain" --markets us,uk,au` prints these destinations as Markdown. Add `--discover` for gate-0 links, `--pain-patterns` for Reddit pain queries, `--compare` for a Trends comparison URL, and `--names` for official trademark-office start pages to open in a browser. It does not fetch or scrape the pages.
