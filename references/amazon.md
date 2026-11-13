# Amazon playbook

Amazon US, UK, and Australia is the required ecommerce channel. It is used to mine pain (especially 2–3 star review text), confirm paid demand, map competitors, and read dated shelf prices. It is not, by itself, a demand-volume number. Canada may use `amazon.ca` when the user asks. Ireland and New Zealand have no separate Amazon marketplace; use the UK and Australia catalogs respectively and say so in the report.

## Warning about automated scraping

Automated scraping of Amazon, including 2–3 star review text, **violates Amazon's Conditions of Use** and can lead to IP or account blocks. The default path in this skill does **not** scrape: use the public "Customers say" summary and featured reviews, plus manual signed-in browser viewing of star-filtered reviews.

An optional, off-by-default helper, `scripts/fetch_amazon_reviews.py`, can call a **user-supplied** ScrapingBee or Apify key for logged-out public content only. It never signs in to Amazon and never uses Amazon cookies. It is opt-in (`--accept-risk` plus an API key). **You enable it at your own risk.** If no key is set, the script exits with a help message and does nothing.

In every report, record the review source you actually used (`public Customers say / featured reviews`, `manual signed-in browser`, `seller tool`, or `scraper`) and say when coverage is partial.

## Where to search

Use the marketplace that matches the target market:

- US: `https://www.amazon.com/s?k={query}`
- UK: `https://www.amazon.co.uk/s?k={query}`
- AU: `https://www.amazon.com.au/s?k={query}`
- CA (optional): `https://www.amazon.ca/s?k={query}`

`scripts/build_search_urls.py` emits these URLs. Open official product pages, the review summary, Q&A, and visible bestsellers rank when it is shown.

For recommend mode with no category, open Movers & Shakers on the same marketplace (`/gp/movers-and-shakers`, also emitted by `--discover`). That page is a discovery lead, not proof of demand.

Record the delivery country you actually browsed. A catalog filtered to another country is not a substitute for the target market. Automated fetches may return a bot page, an empty body, or an error; if that happens, open the page in a browser or record the gap. Do not invent listing counts or prices.

## Which reviews to mine

2–3 star review text is required evidence for **gate 1** (pain) and **gate 6** (the named difference must hit repeated complaints in the top 3–5 competitors' bad reviews).

- 5-star reviews are weak for finding a new USP; they mostly confirm what already works.
- 1-star reviews are often shipping, packaging, or "arrived broken" complaints. Use them only when they describe the product itself (fit, durability, design), not as the main pain source.

Default route, in this order:

1. Public **"Customers say"** aspect summary and any **featured reviews** already visible on the logged-out product page.
2. Manual **signed-in browser** viewing of the top 3–5 competitors, filtered to 2–3 stars. Quote only what you then see.

The 2–3-star filter on Amazon usually requires a signed-in browser. That is by design. There is no official API that returns 2–3-star review text (Amazon's Creators API, when someone qualifies, still does not).

Optional accelerators, only when the user already has access, or has explicitly opted in:

- Paid seller tools on the user's own account: **Helium 10**, **Jungle Scout**, or **Sellersprite**.
- `scripts/fetch_amazon_reviews.py`, if the user supplied a ScrapingBee or Apify key and passed `--accept-risk`. That output is a public, logged-out snapshot and should be labelled **partial** unless you can show otherwise. Reviewer names and profile links are stripped.

When the star filter is behind a login and no optional tool was used, keep the public "Customers say" plus featured reviews and label coverage **partial**. Treat aspect counts as a public snapshot, not as a substitute for reading the filtered reviews. Do not invent review counts, star breakdowns, or 2–3 star quotes you did not open.

Also read Q&A and, when visible, return-reason hints. Quote only text you actually opened.

## Competitor notes

For each relevant listing, capture: title, URL, visible price (and the date and marketplace), rating and review count if shown, and whether claims such as certifications appear without a verifiable number.

If a price is only in an editorial article, or the buy box is missing, say so. Do not treat a press price as a live transaction price.

For **gate 5**, do not stop at the Amazon listing. For each of the top 3–5 sellers, check whether the brand has a standalone site (Shopify or otherwise), whether it is running Meta Ad Library ads, and whether that site has on-site reviews.

## Access

Use public pages first, then a manual signed-in browser for star-filtered reviews if the user can sign in. If a review page redirects to sign-in, or a product will not ship to the browsed location, write that limitation into the report and do not fill the gap with guesses. Do not automate an Amazon login.
