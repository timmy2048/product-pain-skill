# Amazon playbook

Amazon is a required evidence source for US, UK, and Australia runs. It is used to mine pain, map competitors, and read visible prices. It is not, by itself, a demand-volume number. Canada may use `amazon.ca` when the user asks. Ireland and New Zealand have no separate Amazon marketplace; use the UK and Australia catalogs respectively and say so in the report.

## Where to search

Use the marketplace that matches the target market:

- US: `https://www.amazon.com/s?k={query}`
- UK: `https://www.amazon.co.uk/s?k={query}`
- AU: `https://www.amazon.com.au/s?k={query}`
- CA (optional): `https://www.amazon.ca/s?k={query}`

`scripts/build_search_urls.py` emits these URLs. Open official product pages, the review summary, Q&A, and visible bestsellers rank when it is shown. Brand sites are a supplement if the product is sold mainly off Amazon.

For recommend mode with no category, open Movers & Shakers on the same marketplace (`/gp/movers-and-shakers`, also emitted by `--discover`). That page is a discovery lead, not proof of demand.

Record the delivery country you actually browsed. A catalog filtered to another country is not a substitute for the target market. Automated fetches may return a bot page, an empty body, or an error; if that happens, open the page in a browser or record the gap. Do not invent listing counts or prices.

## Which reviews to mine

Prefer **2–3 star** reviews for unmet jobs and fixable product gaps.

- 5-star reviews are weak for finding a new USP; they mostly confirm what already works.
- 1-star reviews are often shipping, packaging, or "arrived broken" complaints. Use them only when they describe the product itself (fit, durability, design), not as the main pain source.

The 2–3-star filter on Amazon usually requires a signed-in browser. That is by design. There is no official API that returns 2–3-star review text (Amazon's Creators API, when someone qualifies, still does not). Do not use review scrapers or paid export tools as a required step.

When the star filter is behind a login, the public fallback is the "Customers say" aspect summary plus any review quotes already visible on the public product page. Treat those aspect counts as a public snapshot, not as a substitute for reading the filtered reviews. If the user can sign in, open the 2–3-star filter in the browser and quote only what you then see.

Also read Q&A and, when visible, return-reason hints. Quote only text you actually opened. Do not invent review counts or star breakdowns.

## Competitor notes

For each relevant listing, capture: title, URL, visible price (and the date and marketplace), rating and review count if shown, and whether claims such as certifications appear without a verifiable number.

If a price is only in an editorial article, or the buy box is missing, say so. Do not treat a press price as a live transaction price.

## Access

Use public pages. If a review page redirects to sign-in, or a product will not ship to the browsed location, write that limitation into the report and do not fill the gap with guesses. Paid review suites such as Helium 10 or Keepa are optional only when the user already has access; they are never required.
