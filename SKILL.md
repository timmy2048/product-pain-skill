---
name: product-pain
description: Use when screening a D2C product from a real category pain point, positioning a brand around that pain, reverse-evaluating a product the user already has, or rerunning the full selection workflow.
---

# Product pain skill

Collect inputs first, then run the gates in order. Stop when a gate fails. After a stop, still write the full report: sections for gates that were not run must say **Not evaluated — stopped at gate N**. Do not jump to branding, tooling, or paid tests early. The conclusion must be exactly one of: **worth a small-scale test**, **reject**, or **insufficient evidence — stop for now**. Mark unverified facts as uncertain. Never invent volumes, factory prices, MOQ, or margins, and never promise sales results. You may back-calculate a target landed or ex-factory ceiling from dated competitor shelf prices, but every percentage you use must be labelled an **assumption**, never a quote or a verified factory cost.

This skill is model-agnostic. It works with any agent that can read this file, open public web pages, and write the report. Do not bind evidence collection to one model vendor.

## Report language

Write the conclusion report in the language the user asked for. If they do not specify a language, write it in English. The skill file and playbooks stay in English. When the report is not in English, translate the body and use these official verdict translations (the facts file still stores the English canonical verdict):

- worth a small-scale test → 值得小规模测试
- reject → 淘汰
- insufficient evidence — stop for now → 证据不足先停

Use `templates/report.md` for English and `templates/report.zh.md` for Chinese. For any other language, keep the English section order and translate the body by hand. `scripts/render_report.py --lang` (or `language` in the facts file) selects the shipped template; the default is English.

## Two entry points

Use the same gates, tools, and report either way.

- **Recommend:** start from a category, audience, or pain. Mine recurring problems, infer a product form, and decide whether it is worth a small test.
- **Reverse:** start from a product or idea the user already has. Test it against the same gates and return the same report.

If the user only names a market or says "find me a product," use Recommend. If they paste a product, brand, listing, or concept, use Reverse.

## Inputs

- Category, or products and brand names to exclude or that were already tried
- Target market (if unspecified, default to English-speaking D2C markets, commonly the US, UK, and Australia). Canada, Ireland, and New Zealand may be added when the user asks; they are optional, not required defaults
- Price band or budget, if any
- Whether medical, hair-growth, or other efficacy claims are allowed as selling copy
- Report language, if any

If a key input is missing, use a reasonable default from context and state it in the report. Do not block reversible work just to ask more questions.

## Principles

- The main path starts from pain: find problems current products handle poorly, then infer form and brand. Sizing a large market first is only a cross-check, not a required starting point.
- Social evidence is limited to exactly three channels: Reddit, TikTok, and YouTube. Do not use Pinterest, Instagram, Facebook organic, or other social networks by default. The main ecommerce channel is Amazon US, UK, and Australia (add `.ca` only when the user asks). Other retailers are optional supplements, not defaults. Trend charts and videos alone are not enough to call a pain real.
- Reddit and YouTube show unprompted pain and how people use a product. TikTok is for content heat (hooks already running, short-form activity), not a substitute for those pain channels. Absolute search volume and ad-auction competition confirm demand size. Google Trends is optional direction, not a required gate.
- Collect transcripts, volumes, prices, and reviews from pages or dedicated tools. The model only clusters, judges, and writes the conclusion. It does not invent evidence.
- After the form and the logistics/education screen both pass, gates 5–7 may run in parallel. If one of them fails, is unverified, or (for gate 7) is incomplete, finish any of 5–7 already in progress, then stop before gate 8. Gate 8 stays after those. Gate 8b is a supplier-quote follow-up and is not required to conclude **worth a small-scale test**. Gate 9 is always last and must not run if gate 8 or any earlier gate failed or was unverified on a must-have fact. A pending 8b does not block gate 9 or that verdict.
- Prefer public pages, official APIs, or a constructed search URL that a person or browser then opens. If a page is blocked or requires login, record the gap and treat the missing fact as unverified. Never sign in to or automate an Amazon account, and never pass Amazon cookies to a script. The default Amazon review path is public "Customers say" plus featured reviews, and manual signed-in browser viewing of 2–3 star reviews on the top 3–5 competitors. Helium 10, Jungle Scout, and Sellersprite are optional accelerators only when the user already has an account. An optional, off-by-default helper (`scripts/fetch_amazon_reviews.py`) may call a user-supplied ScrapingBee or Apify key for logged-out public review text. Automated scraping of Amazon violates Amazon's Conditions of Use and can lead to IP or account blocks; the user must pass `--accept-risk` with their own key and accepts that risk. Record the review source in the report and say when coverage is partial.
- Official APIs for Reddit and the Meta Ad Library are optional accelerators when the user already has approved credentials. They are not required to finish a run, and you should not wait on API review before starting the gates. If credentials are missing, use public pages and record the gap. TikTok's Research API is limited to approved academic or non-profit researchers and is not a commercial selection tool. Amazon has no official API for 2–3-star review text. Official trademark name search has no public API at USPTO, UK IPO, or IP Australia; use each official search page in a browser after a product is picked, if a name will actually be used. Do not call undocumented internal search endpoints. Trademark search is not part of the selection verdict.
- Default to free, publicly reachable tools. Paid rank, review, or keyword suites are optional upgrades, never required dependencies for a complete run.
- Every report must list which required channels actually returned data and which failed (channel coverage), and which Amazon review source was used. Missing must-have evidence for an evaluated gate means **insufficient evidence — stop for now**, not a guessed pass.
- Shipping weight, restricted goods, return or hygiene rules, and market-education cost can kill an otherwise valid pain-plus-demand idea. Screen them early, before deep brand work.
- During selection, judge price feasibility with a competitor-price teardown: dated competitor shelf prices, then a back-calculated target landed cost and allowable ex-factory range. State every assumption percentage (marketplace fees, shipping, returns, ads, margin). Never present those percentages, or the resulting ceilings, as quotes or as verified factory costs.
- Official trademark and name clearance happen after you pick the product. They are optional in the selection report and must not affect the verdict. Gate 7 may list brief, uncleared name ideas; it must not run a trademark search.
- Third-party trend blogs, shop-sales snapshots, and traffic estimates (for example Nolyn, Trenz, or Similarweb estimates) are leads only. They must not be used as evidence that gate 1 or gate 2 has passed. Look the same claim up on a required channel before it counts.
- Every visible price used as evidence must include the date it was seen and the marketplace or page. Do not treat an editorial or press price as a live transaction price.

## Gate status and verdicts

Every evaluated gate gets exactly one status:

- **pass** — the pass rule is met with evidence you actually opened.
- **fail** — the fail rule is met.
- **unverified** — a must-have fact could not be checked (blocked page, login wall, unpaid data, or missing source).
- Gate 7 uses **complete** or **incomplete** instead of pass or fail. Incomplete is treated like unverified when choosing the verdict.
- Gate 8b uses **pending**, **complete**, or **fail** (or **not evaluated** if gate 8 did not pass). **pending** is not unverified and does not block a test verdict.
- Gates not reached are **not evaluated**.

Must-have facts are the ones named in each gate's Pass or Complete rule. Optional extras (for example Google Trends in gate 2, or brand-name candidates in gate 7) may stay unverified or omitted without failing the gate if the must-have evidence is present.

Verdict mapping:

| Outcome | Verdict |
| --- | --- |
| Any of gates 1–3, 5, or 6 **fail** | **reject** |
| Gate 4 **fail** because shipping, restrictions, returns, or education cost is clearly unworkable at a realistic price | **reject** |
| Gate 4 risk looks material but the cost cannot be verified | **insufficient evidence — stop for now** |
| Any evaluated must-have gate is **unverified**, or gate 7 is **incomplete** (a **pending** 8b does not count; a missing trademark search does not count) | **insufficient evidence — stop for now** |
| Gates 1–7 pass or are complete, and gate 8 **pass** | **worth a small-scale test**. Gate 8b may still be **pending**. Gate 9 need not have been entered. Official trademark search is not required for this verdict. |
| Gate 8 **fail** | **reject** when evidence you opened already shows a clearly closed regulatory path, a patent that would block the proposed form, or a competitor-price back-calculation that leaves no room under the stated assumptions. |
| Gate 8 **unverified** | **insufficient evidence — stop for now** (the regulatory path, a patent quick look on the core feature, or a competitor-price sketch grounded in visible dated shelf prices could not be completed). Do not invent MOQ or ex-factory cost to force a pass. Do not fail or un-verify this gate for lack of a trademark search. |
| Gate 8b later **fail** (quotes received, and verified costs cannot work) | **reject**, even if an earlier draft had said the idea was worth a test. |

Do not require gate 8b to be complete, or gate 9 to have been entered, in order to conclude **worth a small-scale test**. Gate 8b stays **pending** until quotes are in hand. Gate 9 is the test plan that follows the test verdict. If you stop early, still output every report section; unreached sections must be exactly: **Not evaluated — stopped at gate N**. Older facts files may still number the desk check as **8a**; treat **8a** as the same gate as **8**.

## Channel roles, minimum evidence, and fallbacks

Required social channels (exactly these three): Reddit, TikTok, YouTube. Required ecommerce channel: Amazon US / UK / AU. Pinterest, Instagram, Facebook organic, and other social networks are not used by default. Meta Ad Library is a brand-vacuum and ad-signal tool, not a social evidence channel. Similarweb and Google Trends are optional leads only.

| Channel | What it proves | Not what it proves |
| --- | --- | --- |
| Reddit | Unprompted pain, failed products, workarounds | Demand volume or willingness to pay |
| YouTube | How people use a product and what they complain about in situ; unprompted brand names (feeds gate 5) | View counts as demand volume |
| TikTok | Content heat: hooks already running, short-form activity around the pain | A substitute for Reddit or YouTube pain evidence; profit |
| Amazon US/UK/AU | Paid demand (rank, review velocity, listing density), 2–3 star / bad-review text, and dated shelf prices | An official demand-volume number; a complete star-filtered review history from public pages alone |

Minimum evidence and fallbacks:

| Gate | Must-have evidence | Fallback | If the must-have is missing |
| --- | --- | --- | --- |
| 0 | At least one of: Amazon Movers & Shakers, TikTok Creative Center, Reddit pain-pattern posts; Google Trends optional | Use only the signals you can open | If none of the named signals open: **insufficient evidence — stop for now** |
| 1 | Recurring pain on Reddit and/or YouTube, **and** Amazon review evidence for the same pain (2–3 star text preferred) | Public "Customers say" plus featured reviews, labelled **partial**, if the 2–3 star filter is behind a login and no signed-in session or optional tool is available. TikTok comments may support pain but do not replace Reddit or YouTube | If Amazon review evidence and both social pain channels fail: **unverified** → **insufficient evidence — stop for now** |
| 2 | Amazon paid-demand proxies (rank, review velocity, listing density) showing people already look for a solution and demand is not clearly fading | Keyword volume or ad-auction figures when visible, labelled as estimates. Google Trends is optional direction only | If you have no Amazon demand proxies and no other magnitude: **unverified** → **insufficient evidence — stop for now** |
| 3 | A form that maps to the pain and a difference checkable on Amazon competitor pages | — | Fail if it is only a reskin |
| 5 | Shelf and routine-content vacuum judgment, **plus** a standalone-site check for each of the top 3–5 Amazon sellers (own site or none found; Shopify or not, if a site exists; Meta Ad Library ads; on-site reviews on that brand site) | Similarweb is optional and never proof of vacuum | If the required site/ads/on-site-review check cannot be completed: **unverified** → **insufficient evidence — stop for now** |
| 6 | A verifiable difference that addresses **repeated** complaints in the top 3–5 competitors' 2–3 star (or otherwise bad) reviews, plus dated shelf prices | Public "Customers say" plus featured reviews, labelled **partial**, if star-filtered text cannot be opened | If you cannot read those complaints at all: **unverified** → **insufficient evidence — stop for now**. Fail if the difference is only a slogan, already on a competitor page, or does not hit those repeated complaints |
| 8 | Regulatory path, patent quick look, competitor-price benchmark from dated Amazon (or other opened) shelf prices | — | Unverified if those cannot be completed |

In the report, fill **Channel coverage** (which of Reddit, TikTok, YouTube, and Amazon actually returned data, and which failed) and **Review source** (`public Customers say / featured reviews`, `manual signed-in browser`, `seller tool` such as Helium 10 / Jungle Scout / Sellersprite, or `scraper`, plus whether coverage is partial). A failed must-have channel is not a silent skip.

## Tooling (free first)

Use these defaults in v1. Paid alternatives may be added in the report as optional follow-up, not as blockers.

| Need | Default (free) | How to use |
| --- | --- | --- |
| Pain in the wild | Reddit and YouTube public search; Amazon 2–3 star / bad reviews | Follow `references/` playbooks. Build URLs with `scripts/build_search_urls.py`. TikTok is for content heat, not the primary pain source. |
| Content heat | TikTok public search and, for gate 0, Creative Center if it opens | Hooks and short-form activity. Not a substitute for Reddit or YouTube pain. |
| Demand / search | Amazon US/UK/AU rank, review velocity, and listing density; Google Search plus a free volume overlay when available; Google Trends for direction | Label third-party or extension figures as estimates. Never invent official Keyword Planner volumes. |
| Reviews and competitors | Default: public "Customers say" plus featured reviews, and manual signed-in browser viewing of 2–3 star reviews on the top 3–5 competitors | See `references/amazon.md`. Record the review source and say when coverage is partial. Optional accelerators: Helium 10, Jungle Scout, or Sellersprite when the user already has an account; or `scripts/fetch_amazon_reviews.py` if the user has opted in at their own risk. Capture dated shelf prices for the gate 8 cost benchmark. |
| Brand-site and ad check (gate 5) | Each top Amazon seller's standalone site (Shopify or not), Meta Ad Library, and on-site reviews | Required for gate 5. Meta Ad Library is an ad signal, not a social evidence channel. Similarweb remains optional and is not vacuum proof. |
| Site traffic | Similarweb free snapshot | If the free view is empty or paywalled, mark traffic as unknown. Treat figures as estimates and as leads, not as gate 1–2 evidence. |
| Patents (gate 8) | Google Patents | Quick look for utility or design patents that would block the proposed form or its core feature. |
| Trademarks (after you pick the product) | Official trademark search in a browser (USPTO, UK IPO, IP Australia; add CIPO, IPONZ, or EUIPO when those markets are in the run) | Optional brand-launch checklist only. Not a selection gate, and not part of the verdict. `scripts/build_search_urls.py --names` prints the official start pages. |

Channel playbooks: `references/reddit.md`, `references/amazon.md`, `references/tiktok.md`, `references/youtube.md`. Tool notes: `references/tools.md`.

## Gates

### 0. Pick a category (recommend mode only, when none is given)

If recommend mode already has a category, audience, or pain, skip this gate and start at gate 1. If the user asked you to find a product and named no category, list 3–5 candidates from these free signals (use only the ones you can actually open):

- Amazon Movers & Shakers on the target marketplace
- Google Trends rising or breakout queries, when available
- TikTok Creative Center, if the page opens
- Reddit posts matching pain patterns such as "wish there was"

`scripts/build_search_urls.py --discover` prints these destinations. Score each candidate on season (including inverted seasons for Australia versus the US and UK), apparent pain density, and logistics risk. Pick one, write down why, and then run gates 1–9 on that pick. Third-party shop-trend articles may suggest names to look up; they are not themselves a validated signal.

This gate is **complete** when a pick and a reason are written down. If you cannot open any of the named signals, the run stops with **insufficient evidence — stop for now**.

### 1. Define the category and mine the pain

Sources: Amazon 2–3 star (or otherwise bad) review text, return reasons, and Q&A; Reddit threads; YouTube comments, titles, and transcripts. TikTok may support the same theme as content heat, but it does not replace Reddit or YouTube.

For Amazon reviews, use this default path and record which source you used: public "Customers say" plus featured reviews on the product page, **and** manual signed-in browser viewing of 2–3 star reviews on the top 3–5 competitors. If the star filter stays behind a login, keep the public snapshot, label coverage **partial**, and do not invent filtered review text. Optional accelerators, only when the user already has access or has opted in: Helium 10, Jungle Scout, Sellersprite, or `scripts/fetch_amazon_reviews.py`. Prefer 2–3 star text for unmet jobs; treat 1-star shipping-and-packaging rants as secondary.

Pass: the same pain is mentioned repeatedly on Reddit and/or YouTube, Amazon review evidence supports that it is still unsolved, and current products clearly leave it unsolved.

Fail: only scattered complaints, or a hot category with no concrete problem.

If you cannot get Amazon review evidence (even the public "Customers say" fallback) and cannot get recurring pain from Reddit or YouTube, mark this gate **unverified**.

### 2. Confirm demand exists and is not clearly fading

Sources: keyword volume and ad-auction or competition signals when available; ecommerce rank, review velocity, and listing density as proxies; Google Trends only as a direction check.

Pass: people are already looking for a solution, and demand does not look like it has peaked and collapsed.

Fail: volume is tiny, clearly declining, or you only have relative trend lines with no magnitude and cannot backfill other demand evidence.

For Australia, treat seasons as inverted relative to the US and UK. A US or UK autumn or winter peak does not by itself show Australian demand in the same calendar months. Say whether you are looking at Australia's in-season or off-season window.

### 3. Infer the product form

Translate the pain into what to make, and what not to make.

Pass: the form maps to the pain, and the difference from current forms can be stated in plain language. A real difference is something a buyer or a factory can check on a competitor page: construction, a sizing system, materials, or the occasion it is made for.

Fail: the form does not address the pain, or it is only a reskin of products that already exist. A new slogan, a colorway, or a claim already printed on competing listings is a reskin. If every named difference is already visible on a current product page, this gate fails.

### 4. Screen logistics and market-education cost

Do this before brand work and deep competitive work.

Fail or stop if the idea is clearly expensive to ship or to explain relative to a realistic retail price: heavy or bulky goods, wet wipes and other liquids, batteries or hazardous materials, or a product that requires teaching a new habit before anyone will buy it. A trending, unbranded pain is not enough if fulfillment or education would dominate cost.

For apparel, footwear, and intimates, also screen return rate and hygiene rules. Many of these goods are non-returnable once worn, or have a return rate that can erase margin. If that risk is material and you cannot verify it, mark it unverified. If it is clearly unworkable at a realistic price, fail this gate.

If shipping, returns, or education cost cannot be verified, do not invent it. Mark the uncertainty. If the risk looks material, the allowed conclusion at this gate is **insufficient evidence — stop for now**.

### 5. Brand vacuum

Look at routine content (especially YouTube), review roundups, and Amazon shelves for a brand people name unprompted, and whether that brand already solves this pain.

For each of the top 3–5 Amazon sellers, also complete this required standalone-site check:

- Does the seller have its own brand site, or only an Amazon listing? Record the URL or write "none found."
- If a site exists, is it Shopify or another stack, if you can tell? If you cannot tell, say so.
- Does the brand appear in Meta Ad Library (active ads, rough count, and how long a creative or advertiser has been running, when visible)?
- Does that brand site have on-site reviews (not only Amazon reviews)?

Pass: the checklist above is completed for those top sellers, and either no single dominant brand exists, or a dominant brand exists but its form or experience still misses this pain (partially clean).

Fail: a dominant brand has locked the category and already solved the pain. The presence of competitors alone is not a reason to reject.

If the required standalone-site, ads, or on-site-review check cannot be completed, mark this gate **unverified**. Similarweb snapshots are optional leads, not a substitute for the checklist.

### 6. Contrast competitors and name the difference

Keep using Amazon reviews, returns, Q&A, and reputable roundups. The named difference must hit **repeated** complaints in the top 3–5 competitors' 2–3 star (or otherwise bad) reviews — not a slogan that ignores those complaints. Use the same default review path as gate 1, and record the review source and whether coverage is partial. Record dated competitor shelf prices and marketplaces; gate 8 will use them for the cost benchmark.

Pass: there is a verifiable difference in form, experience, aesthetic, price band, or use occasion — not a slogan — and that difference addresses repeated complaints in those competitors' bad reviews. The difference must be checkable on competitor pages (construction, sizing system, materials, or occasion), not only claimed in copy.

Fail: the only difference is a claim or a slogan, every claimed difference is already on a competitor page, or the proposed difference does not address those repeated bad-review complaints.

If you cannot read those competitors' bad-review complaints at all (no signed-in 2–3 star text, no seller-tool export, no opted-in scraper, and no public "Customers say" or featured-review snapshot), mark this gate **unverified**.

### 7. Positioning and claim boundaries

Write the target user, aesthetic references, and claims that must not be used (especially medical or efficacy claims). Brand-name candidates are optional and should stay brief if included. If you list names, label them **uncleared ideas**. Do not run an official trademark search at this gate; name clearance belongs in the post-selection checklist, after a product is picked.

For aesthetic references, do not copy the look of established competitors in the same category. Borrow from a brand the target audience already loves in a *different* category — for example a pet product taking cues from Aesop or Muji, or a sports accessory taking cues from Rhode or Glossier. Name the reference brand and why this audience already likes it. The goal is a look that stands apart on the same shelf, not a reskin of a category incumbent.

Complete: the write-up includes a target user, a cross-category aesthetic reference with a reason, and claim boundaries. Names are not required for a complete status.

Incomplete: the target user, the aesthetic reference and reason, or the claim boundaries are missing. Missing names do not make this gate incomplete.

### 8. Desk check: regulatory path, patents, and competitor-price cost benchmark

Do this after gates 5–7. In the report and facts file this gate is numbered **8**. Older files may still use **8a**; treat that as the same gate. Official trademark search is not part of this gate and must not affect its status or the verdict.

State the regulatory path for the target markets, especially efficacy and medical-device language.

Search Google Patents for utility or design patents that would block the proposed form or its core feature. A blocking patent can kill the product form, so keep this quick look in the selection desk check.

Then build a competitor-price cost benchmark (a price-based teardown):

1. Start from dated competitor shelf prices you actually opened (price, marketplace or page, and date seen).
2. Back-calculate a target landed cost and an allowable ex-factory cost range.
3. State every assumption percentage you use — typically marketplace fees, shipping or fulfillment, returns, ads, and target margin. If you also assume inbound freight or duties, say so.
4. Show the arithmetic so a reader can see how the shelf price became the cost ceiling.
5. Label every percentage and every resulting ceiling as an **assumption**, never as a quote or a verified factory cost.

You may use clearly labelled starting percentages when you do not yet have better ones, as long as you say they are assumptions and you show the numbers you used. Do not invent MOQ, an ex-factory quote, or a margin presented as fact.

Illustrative shape only (replace every figure with the assumptions you are actually using): if a competitor is $40 on Amazon US on a stated date, and you assume marketplace fees 15%, fulfillment 10%, returns 5%, ads 20%, and a 25% margin target, then 75% of retail is spoken for and $10 is the implied landed-cost ceiling before inbound freight and duties. Those percentages and the $10 ceiling are assumptions, not quotes.

Pass: the regulatory path is stated, a patent quick look on the core feature was actually done, and a back-calculation from visible dated shelf prices still leaves room under the stated assumptions.

Fail: evidence you opened already shows a clearly closed regulatory path, a patent that would block the proposed form, or a competitor-price back-calculation that leaves no room under the stated assumptions.

If the regulatory path, the patent quick look, or a sketch grounded in visible dated shelf prices cannot be completed, mark gate 8 **unverified**. Do not mark this gate unverified or failed because a trademark search was not done.

### 8b. Supplier quotes

This step is not required to conclude **worth a small-scale test**. After gate 8 passes, attach a filled request-for-quote from `templates/rfq.md` (or `templates/rfq.zh.md` when the report is in Chinese) and set this gate to **pending**.

Build the RFQ around the competitor-price benchmark from gate 8. Tell the factory the target specification in terms of a named competitor and that competitor's dated shelf price, and give a target ex-factory ceiling from the back-calculation — for example: "target spec like competitor X at $Y (marketplace, date); target ex-factory below $Z (assumption-based ceiling, not a quote)."

Do not contact a factory or supplier unless the user has explicitly agreed to that outreach. If they have not, leave the RFQ in the report and do not send it. Until quotes are in hand, the report must say **pending 8b**. A pending RFQ does not block the test verdict.

When the user has agreed and quotes arrive, record verified MOQ, ex-factory price, certifications, lead time, and a margin built from those figures, and mark 8b **complete**. If those verified costs cannot work, 8b **fail** and the verdict becomes **reject**. If quotes never arrive, the test verdict may still stand, with 8b left pending and the missing factory costs labelled unverified.

### 9. Small-scale test

Run creative and a landing page (or equivalent) as a small conversion test. Tooling and inventory come after the test works. Do not enter this gate if gate 8 or any earlier gate failed or was unverified on a must-have fact. A pending 8b does not block this gate. Do not spend money on ads unless the user explicitly asks after the earlier gates have passed.

When a testable offer is ready, cold-start with organic short-form videos that try pain hooks. Watch completion, not just views. Once a video clearly reaches high completion, and only if the user has asked to spend, put the first ad budget toward people who watched about 95% or more of that video, so the first seed customers are converted at the lowest measurable cost. Do not start with broad prospecting.

## After you pick the product (brand-launch checklist)

This section is optional. It is not a selection gate and must not change the verdict.

Once a product has been picked — usually after **worth a small-scale test**, or when the user has already chosen a product to take forward — clear any brand name you actually want to use:

- Search each name (exact and near marks, in relevant classes) on the official office for every target market in the run:
  - United States: [USPTO Trademark Search](https://tmsearch.uspto.gov/)
  - United Kingdom: [UK IPO trade mark search](https://trademarks.ipo.gov.uk/ipo-tmtext)
  - Australia: [IP Australia Trade Mark Search](https://search.ipaustralia.gov.au/trademarks/search)
  - Canada, when that market is in the run: [CIPO Canadian Trademarks Database](https://ised-isde.canada.ca/cipo/trademark-search/srch/)
  - New Zealand, when selected: [IPONZ trade mark search](https://www.iponz.govt.nz/about-ip/trade-marks/search/)
  - Ireland, when selected: [EUIPO eSearch](https://euipo.europa.eu/eSearch/), plus the national office if you can open it
- `scripts/build_search_urls.py --names` prints these official start pages. Open them in a browser. Do not call undocumented internal search endpoints.
- A third-party trademark site can be a lead, not a clearance. "No hits on an unofficial site" is not a clearance.
- Candidate names stay uncleared ideas until this search is done. Completing the search is not a legal opinion.

You may leave this section blank or marked "not started" during selection. A missing trademark search never makes the verdict **insufficient evidence — stop for now** or **reject**.

## Report

Always write a conclusion report from the language-matched template (`templates/report.md` or `templates/report.zh.md`). You may use `scripts/render_report.py` to fill and validate it. Required sections:

- Mode (recommend or reverse) and inputs used, including defaults
- Report language
- Category pick (gate 0), or a note that it was skipped
- Pain statement
- Demand evidence
- Recommended or evaluated form
- Logistics and education-cost screen, including apparel return or hygiene risk when relevant
- Vacuum judgment, including the required standalone-site, Shopify, Meta Ad Library, and on-site-review check for the top Amazon sellers
- Competitors and difference, including how the difference hits repeated 2–3 star complaints, and dated shelf prices used later in gate 8
- Channel coverage: which of Reddit, TikTok, YouTube, and Amazon returned data, and which failed
- Review source: `public Customers say / featured reviews`, `manual signed-in browser`, `seller tool`, or `scraper`, and whether coverage is partial
- Positioning, claim boundaries, and the cross-category aesthetic reference; brand-name candidates only if offered, labelled uncleared
- Gate 8 desk check: regulatory path, a patent quick look on the core feature, and a competitor-price cost benchmark with stated assumption percentages and source links
- Gate 8b supplier quotes: a filled RFQ built around the competitor benchmark, sent only with the user's OK, and the status **pending 8b** until quotes arrive
- After you pick the product: optional official trademark and name-clearance checklist; omit or leave unstarted during selection; this never affects the verdict
- Per-gate status (pass, fail, unverified, complete, incomplete, pending, or not evaluated)
- Final conclusion: exactly one of the three allowed verdicts
- Open gaps (pages blocked, login walls, unpaid data)

Every material claim needs a source link or an explicit "unverified" label.
