# Tooling notes (free first)

Paid keyword, rank, or review suites may be cited if the user already has access. They are never required to finish a v1 run. Official APIs are optional accelerators, not prerequisites. Do not delay a run while an API application is under review.

Required social channels are only Reddit, TikTok, and YouTube. Pinterest, Instagram, Facebook organic, and other social networks are not used by default. The required ecommerce channel is Amazon US, UK, and Australia.

## Demand and search

- **Google Search** plus a free overlay such as Keyword Surfer, when installed: use the figure you can see on the results page and label it as an extension estimate. Keyword Surfer only works in a browser with the extension. Build Google URLs with `hl=en` and `gl` set to the target market so you are not silently redirected to a local domain.
- **Google Trends**: `https://trends.google.com/trends/explore?q={query}&date=today%205-y&geo={market}`. Optional. Good for direction (rising, flat, fading), not for absolute volume. Worldwide vs country must be stated. The public web UI may rate-limit automated requests; `pytrends` is an unofficial scripted option if it still returns data, and those figures stay estimates. If the page is blocked, mark Trends as unverified and lean on ecommerce proxies.
- If official Keyword Planner data is not available, do not invent it. Either use another labeled estimate or mark volume as unverified and lean on ecommerce proxies.
- Third-party trend blogs and shop-sales dashboards are leads only, never evidence that gate 1 or gate 2 has passed.

## Amazon reviews (gates 1 and 6)

Default path, no scraping: public "Customers say" plus featured reviews on the product page, and manual signed-in browser viewing of 2–3 star reviews on the top 3–5 competitors. Record the source and label coverage **partial** when you only have the public snapshot.

Optional accelerators when the user already has an account: Helium 10, Jungle Scout, or Sellersprite.

### Optional review-fetch script (off by default)

`scripts/fetch_amazon_reviews.py` is opt-in. It never signs in to Amazon and never calls Amazon directly. It only calls a user-supplied third-party key:

- ScrapingBee: `SCRAPINGBEE_API_KEY`, documented Amazon Product API `GET https://app.scrapingbee.com/api/v1/amazon/product` with `query=<ASIN>`, `domain=com|co.uk|com.au`, and `light_request=false` (light requests can omit reviews). There is no documented `/amazon/review` endpoint; results are a public product-page subset and should be treated as **partial**.
- Apify: `APIFY_TOKEN` (or `APIFY_API_TOKEN`) and `APIFY_AMAZON_REVIEWS_ACTOR` or `--actor`, official `POST https://api.apify.com/v2/actors/{actorId}/run-sync-get-dataset-items`. Default actor input follows the public docs for `webdatalabs/amazon-reviews-scraper` (`includeReviewerNames` is false); override with `--actor` and `--apify-input` if you use a different actor.

You must pass `--accept-risk`. If no key is set, the script exits with a help message. Reviewer names and profile links are dropped. Responses are cached under `output/cache/amazon-reviews/` and requests are spaced out.

**Warning:** Automated scraping of Amazon violates Amazon's Conditions of Use and can lead to IP or account blocks. The user enables this at their own risk.

## Ad library and traffic

- **Meta Ad Library**: `https://www.facebook.com/ads/library/`. Search the brand or the pain keyword. Use URLs from `scripts/build_search_urls.py` (they include `search_type` and `media_type`). Note whether ads are still active, roughly how many, and how long a creative or advertiser has been running. These are spend and expansion clues for the gate 5 standalone-site check, not proof that the product is profitable, and not a social evidence channel. The public page is often behind a script challenge; if a fetch is blocked, open it in a browser or, when the user already has a Meta developer app and a user token with `ads_read` (identity verification is often required), use the official [Ad Library API](https://www.facebook.com/ads/library/api/). Coverage through the API can be narrower than the website. If you still cannot open it, record the gap. Do not wait on app review before continuing the other gates.
- **Google Ads Transparency Center**: official start page `https://adstransparency.google.com/` and search page `https://adstransparency.google.com/search`. Required for gate 5, complementary to Meta Ad Library. Open the official pages in a browser and search by advertiser name or website, then filter by region and date when the UI allows it. Record whether ads are present, copy themes, and whether a visible landing is a brand site or Amazon. This does not prove pain or paid demand and cannot replace Reddit, YouTube, or Amazon reviews. Do not use a paid Google Ads account or spend money. Do not call undocumented internal APIs. If the page times out or is blocked, mark it unverified; do not invent ads. See `references/google-ads.md`. List coverage in the report.
- **Similarweb free snapshot**: `https://www.similarweb.com/website/{domain}/`. Strip a leading `www.` from the domain. Capture only what the free page shows (often a traffic band or trend, sometimes a source mix). If the free view is blank or paywalled, write "traffic unknown." Automated fetches may return an empty response even when a browser or another fetch path works; try once more or record the gap. Treat Similarweb numbers as estimates and as leads, not as proof for gates 1–2.

## Patents (gate 8)

- **Google Patents**: `https://patents.google.com/?q={query}`. Look for utility or design patents that would block the proposed form or its core feature. This quick look is part of the gate 8 desk check. A blocking patent can fail gate 8.

## Competitor-price cost benchmark (gate 8)

Use dated shelf prices you actually opened on competitor listings (price, marketplace or page, and date seen). Back-calculate a target landed cost and an allowable ex-factory range with clearly stated assumption percentages for marketplace fees, shipping or fulfillment, returns, ads, and margin. Label every percentage and every resulting ceiling as an assumption, never as a quote or a verified factory cost. Do not invent MOQ or an ex-factory price to fill the sketch. If you cannot ground the sketch in visible dated prices, mark gate 8 unverified.

## Trademarks (after you pick the product)

Official name search is a browser step for the post-selection brand-launch checklist. It is not part of gate 8, and it must not affect the selection verdict. Automated fetches of these pages often return an empty shell. Search each name you actually want to use (exact and near marks, relevant classes) on the office that matches each target market in the run. A third-party site can be a lead, not a clearance. Do not call undocumented internal search endpoints. `scripts/build_search_urls.py --names` prints the official start pages; the script does not add them unless `--names` is passed.

- **United States — USPTO**: [Trademark Search](https://tmsearch.uspto.gov/). A start page also lives at `https://www.uspto.gov/trademarks/search`. There is no official API that searches by brand name. The TSDR API looks up an already-known serial or registration number; it does not replace a name search. Official bulk data is available through the USPTO Open Data Portal, but it is not required for a v1 name check.
- **United Kingdom — UK IPO**: [Search for a trade mark](https://trademarks.ipo.gov.uk/ipo-tmtext) (word search). The GOV.UK landing page is `https://www.gov.uk/search-for-trademark`.
- **Australia — IP Australia**: [Australian Trade Mark Search](https://search.ipaustralia.gov.au/trademarks/search).
- **Canada — CIPO**, when Canada is in the run: [Canadian Trademarks Database](https://ised-isde.canada.ca/cipo/trademark-search/srch/).
- **New Zealand — IPONZ**, when selected: [Search for a trade mark](https://www.iponz.govt.nz/about-ip/trade-marks/search/).
- **Ireland**, when selected: [EUIPO eSearch](https://euipo.europa.eu/eSearch/) for EU marks, plus the national office if you can open it.

"No hits on an unofficial site" is not a clearance. Candidate brand names stay uncleared ideas until this search is done. Completing the search is not a legal opinion. Leaving this checklist unstarted during selection is fine.

Supplier pages used later in gate 8b (for example a public factory listing) are often blocked by captchas. Record the gap, use the RFQ in `templates/rfq.md` (built around the competitor-price benchmark), and do not invent MOQ or ex-factory prices. Do not contact a supplier unless the user has agreed.

## URL helper

`python scripts/build_search_urls.py --keywords "example pain" --markets us,uk,au` prints these destinations as Markdown. Add `--discover` for gate-0 links, `--pain-patterns` for Reddit pain queries, `--compare` for a Trends comparison URL, and `--names` for official trademark-office start pages to open in a browser after a product is picked. Trademark URLs are emitted only when `--names` is passed. It does not fetch or scrape the pages.

The optional review helper is `python scripts/fetch_amazon_reviews.py --help`. It does nothing until a key is set and `--accept-risk` is passed.
