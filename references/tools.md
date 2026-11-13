# Tooling notes (free first)

Paid keyword, rank, or review suites may be cited if the user already has access. They are never required to finish a v1 run.

## Demand and search

- **Google Search** plus a free overlay such as Keyword Surfer, when installed: use the figure you can see on the results page and label it as an extension estimate.
- **Google Trends**: `https://trends.google.com/trends/explore?q={query}&geo={market}`. Optional. Good for direction (rising, flat, fading), not for absolute volume. Worldwide vs country must be stated.
- If official Keyword Planner data is not available, do not invent it. Either use another labeled estimate or mark volume as unverified and lean on ecommerce proxies.

## Ad library and traffic

- **Meta Ad Library**: `https://www.facebook.com/ads/library/`. Search the brand or the pain keyword. Note whether ads are still active, roughly how many, and how long a creative or advertiser has been running. These are spend and expansion clues, not proof that the product is profitable.
- **Similarweb free snapshot**: `https://www.similarweb.com/website/{domain}/`. Capture only what the free page shows (often a traffic band or trend, sometimes a source mix). If the free view is blank or paywalled, write "traffic unknown."

## Trademarks and patents

- **USPTO trademark search** (public): start from `https://www.uspto.gov/trademarks/search` or the current public TESS/TMsearch tool. Search exact and near marks in relevant classes. A third-party site can be a lead, not a clearance.
- **Google Patents**: `https://patents.google.com/?q={query}`. Look for utility or design patents that would block the proposed form.
- Gate 8 is not passed until the official (or equivalent national) search you intended is actually completed. "No hits on an unofficial site" is not a clearance. Candidate brand names stay candidates until then.

## URL helper

`python scripts/build_search_urls.py --keywords "example pain" --markets us,uk,au` prints these destinations as Markdown. It does not fetch or scrape the pages.
