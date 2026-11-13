# Amazon playbook

Amazon is a required evidence source for US, UK, and AU runs. It is used to mine pain, map competitors, and read visible prices. It is not, by itself, a demand-volume number.

## Where to search

Use the marketplace that matches the target market:

- US: `https://www.amazon.com/s?k={query}`
- UK: `https://www.amazon.co.uk/s?k={query}`
- AU: `https://www.amazon.com.au/s?k={query}`

`scripts/build_search_urls.py` emits these URLs. Open official product pages, the review summary, Q&A, and visible bestsellers rank when it is shown. Brand sites are a supplement if the product is sold mainly off Amazon.

Record the delivery country you actually browsed. A catalog filtered to another country is not a substitute for the target market.

## Which reviews to mine

Prefer **2–3 star** reviews for unmet jobs and fixable product gaps.

- 5-star reviews are weak for finding a new USP; they mostly confirm what already works.
- 1-star reviews are often shipping, packaging, or "arrived broken" complaints. Use them only when they describe the product itself (fit, durability, design), not as the main pain source.

Also read "customers say" style summaries, Q&A, and, when visible, return-reason hints. Quote only text you actually opened. Do not invent review counts or star breakdowns.

## Competitor notes

For each relevant listing, capture: title, URL, visible price (and the date and marketplace), rating and review count if shown, and whether claims such as certifications appear without a verifiable number.

If a price is only in an editorial article, or the buy box is missing, say so. Do not treat a press price as a live transaction price.

## Access

Use public pages. If a review page redirects to sign-in, or a product will not ship to the browsed location, write that limitation into the report and do not fill the gap with guesses. Do not use scrapers or paid review-export tools as a required step.
