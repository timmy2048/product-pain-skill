# Google Ads Transparency Center playbook

Google Ads Transparency Center is a required **gate 5** check, complementary to Meta Ad Library. It is a free public channel for seeing whether competitors advertise on Google (search, display, YouTube, and other Google surfaces that the Center shows), what the visible ad copy says, and whether a visible landing destination looks like a brand site or Amazon.

It does **not** prove pain or paid demand. It cannot replace Reddit or YouTube for pain, or Amazon reviews and shelf proxies for demand. Do not treat it as a social evidence channel. A top-selling Amazon brand with no Google ads is only a supplementary brand-vacuum signal.

## Official URLs

- Home: `https://adstransparency.google.com/`
- Search: `https://adstransparency.google.com/search`
- Observed search form (2026-11-14, Asia/Shanghai): `https://adstransparency.google.com/search?region=US&query=...`

Only the `region` and `query` parameters were observed live, and only `region=US` was confirmed. Do not invent other query-string parameters. For a region other than US, or for **Anywhere**, set the filter in the UI and record the exact URL the browser shows.

Open these official pages in a browser. Do not call undocumented internal search endpoints. Official help states that you search by **advertiser name or website** and may filter by serving region and date: [About advertiser verification / Ads transparency](https://support.google.com/My-Ad-Center-Help/answer/12155361).

Do not sign in to a paid Google Ads account and do not spend money. A 2026-11-14 Asia/Shanghai live test opened the public pages without a paid ads account. The browser already had a Google session; signed-out behavior was not separately verified. If a sign-in wall or script challenge appears, record the gap.

## How to search

1. Open the official start or search page, or the observed search URL.
2. For each of the top 3–5 Amazon sellers, run queries in this order. If a query returns 0 results, go to the next variant. Do not stop at the first empty result:
   1. The domain (including a brand site from the gate 5 checklist).
   2. The brand name.
   3. The legal company name (for example `X LLC`, `X Inc`, or `X Ltd`).
   4. The Amazon seller or brand name as shown on the listing.
3. For each variant, set the serving region to the target market (US, UK, or AU), then retry with **Anywhere**. Note any date range the UI applies.
4. To check a category, look up the known competitor advertisers and domains in that category. The official tool does not document a keyword-bid search. If category language appears in visible ad copy, record it as a copy theme, not as proof of the keywords they buy.
5. Only record **no ads found** after every name and domain variant has returned 0 results in both the target-market region and Anywhere. List the exact queries you tried, each with its URL in the observed form (or the URL the browser showed). A timeout or empty shell is **unverified**, not “no ads found.”

A domain query can return 0 results even when the advertiser exists. In the 2026-11-14 Asia/Shanghai live test, `chomperlabs.com` returned nothing in the US, but the brand name `Chomper Labs` found **Chomper Labs LLC** (verified, 13 ads).

## What to record

For each advertiser you find, write down:

- Advertiser name as shown
- Verified status
- Ad count
- Formats (text, image, or whatever the page shows)
- Last-shown dates (detail pages show last-shown dates, not first-shown dates)
- Example ad text, verbatim
- Advertiser page URL

If visible ad text points to `amazon.com`, record that the brand buys Google traffic to its Amazon listing.

For lookups that return 0 after every variant, record **no ads found** and list the exact queries and URLs. In the same live test, Retainer Brite returned 0 results for domain and name, in the US and Anywhere.

Do not invent ad counts, spend, targeting, or keywords. Absence of results for one query is not proof that no ads exist.

## How to read a finding

A top-selling Amazon brand with no Google ads after all variants (as with Retainer Brite above) is a supplementary brand-vacuum signal only. It is never proof of pain or demand.

## Coverage and failures

List Google Ads Transparency Center in the report's **Channel coverage** section (returned or failed), alongside Meta Ad Library. If the page times out, is blocked, or returns an empty shell, mark this part of gate 5 **unverified**. Do not invent ads or copy to fill the gap.
