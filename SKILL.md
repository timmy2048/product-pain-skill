---
name: product-pain
description: Use when screening a D2C product from a real category pain point, positioning a brand around that pain, reverse-evaluating a product the user already has, or rerunning the full selection workflow.
---

# Product pain skill

Collect inputs first, then run the gates in order. Stop when a gate fails. Do not jump to branding, tooling, or paid tests early. The conclusion must be exactly one of: **worth a small-scale test**, **reject**, or **insufficient evidence — stop for now**. Mark unverified facts as uncertain. Never invent volumes, factory prices, MOQ, or margins, and never promise sales results.

This skill is model-agnostic. It works with any agent that can read this file, open public web pages, and write the report. Do not bind evidence collection to one model vendor.

## Two entry points

Use the same gates, tools, and report either way.

- **Recommend:** start from a category, audience, or pain. Mine recurring problems, infer a product form, and decide whether it is worth a small test.
- **Reverse:** start from a product or idea the user already has. Test it against the same gates and return the same report.

If the user only names a market or says "find me a product," use Recommend. If they paste a product, brand, listing, or concept, use Reverse.

## Inputs

- Category, or products and brand names to exclude or that were already tried
- Target market (if unspecified, default to English-speaking D2C markets, commonly the US, UK, and Australia)
- Price band or budget, if any
- Whether medical, hair-growth, or other efficacy claims are allowed as selling copy

If a key input is missing, use a reasonable default from context and state it in the report. Do not block reversible work just to ask more questions.

## Principles

- The main path starts from pain: find problems current products handle poorly, then infer form and brand. Sizing a large market first is only a cross-check, not a required starting point.
- Ecommerce evidence is required. Check the channels the target market actually buys from (Amazon is the default for US/UK/AU; add other retailers or official brand sites when relevant). Trend charts and videos alone are not enough to call a pain real.
- YouTube and similar routine content show how people use a product and what they complain about. Absolute search volume and ad-auction competition confirm demand size. Google Trends is optional direction, not a required gate.
- Collect transcripts, volumes, prices, and reviews from pages or dedicated tools. The model only clusters, judges, and writes the conclusion. It does not invent evidence.
- After the form and the logistics/education screen both pass, gates 5–7 may run in parallel. Gate 8 stays after those. Gate 9 is always last and must not run if any earlier gate failed.
- Prefer public pages, official APIs, or a constructed search URL that a person or browser then opens. Do not use scrapers, credentials, or plugins that violate a site's terms of service. If a page is blocked or requires login, record the gap and treat the missing fact as unverified.
- Default to free, publicly reachable tools. Paid rank, review, or keyword suites are optional upgrades, never required dependencies for a complete run.
- Shipping weight, restricted goods, and market-education cost can kill an otherwise valid pain-plus-demand idea. Screen them early, before deep brand and trademark work.

## Tooling (free first)

Use these defaults in v1. Paid alternatives may be added in the report as optional follow-up, not as blockers.

| Need | Default (free) | How to use |
| --- | --- | --- |
| Pain in the wild | Reddit, Amazon, TikTok, YouTube public search | Follow `references/` playbooks. Build URLs with `scripts/build_search_urls.py`. |
| Demand / search | Google Search plus a free volume overlay when available (for example Keyword Surfer); Google Trends for direction | Label third-party or extension figures as estimates. Never invent official Keyword Planner volumes. |
| Reviews and competitors | Amazon public product pages, especially 2–3 star reviews | See `references/amazon.md`. Brand sites are a supplement, not a substitute. |
| Ad spend signals | Meta Ad Library | Longevity and ad count are spend/expansion clues, not proof of profit. |
| Site traffic | Similarweb free snapshot | If the free view is empty or paywalled, mark traffic as unknown. |
| Trademarks and patents | USPTO public trademark search, Google Patents | Incomplete official search means the IP gate is not passed. |

Channel playbooks: `references/reddit.md`, `references/amazon.md`, `references/tiktok.md`, `references/youtube.md`. Tool notes: `references/tools.md`.

## Gates

### 1. Define the category and mine the pain

Sources: Amazon and other ecommerce reviews, return reasons, and Q&A; Reddit threads; TikTok and YouTube comments and captions.

Pass: the same pain is mentioned repeatedly, and current products clearly leave it unsolved.

Fail: only scattered complaints, or a hot category with no concrete problem.

### 2. Confirm demand exists and is not clearly fading

Sources: keyword volume and ad-auction or competition signals when available; ecommerce rank, review velocity, and listing density as proxies; Google Trends only as a direction check.

Pass: people are already looking for a solution, and demand does not look like it has peaked and collapsed.

Fail: volume is tiny, clearly declining, or you only have relative trend lines with no magnitude and cannot backfill other demand evidence.

### 3. Infer the product form

Translate the pain into what to make, and what not to make.

Pass: the form maps to the pain, and the difference from current forms can be stated in plain language.

Fail: the form does not address the pain, or it is only a reskin of products that already exist.

### 4. Screen logistics and market-education cost

Do this before brand, trademark, and deep competitive work.

Fail or stop if the idea is clearly expensive to ship or to explain relative to a realistic retail price: heavy or bulky goods, wet wipes and other liquids, batteries or hazardous materials, or a product that requires teaching a new habit before anyone will buy it. A trending, unbranded pain is not enough if fulfillment or education would dominate cost.

If shipping or education cost cannot be verified, do not invent it. Mark the uncertainty. If the risk looks material, the allowed conclusion at this gate is **insufficient evidence — stop for now**.

### 5. Brand vacuum

Look at routine content, review roundups, and ecommerce shelves for a brand people name unprompted, and whether that brand already solves this pain.

Pass: no single dominant brand, or a dominant brand exists but its form or experience still misses this pain (partially clean).

Fail: a dominant brand has locked the category and already solved the pain. The presence of competitors alone is not a reason to reject.

### 6. Contrast competitors and name the difference

Keep using ecommerce reviews, returns, Q&A, and reputable roundups.

Pass: there is a verifiable difference in form, experience, aesthetic, price band, or use occasion — not a slogan.

### 7. Positioning, name candidates, and claim boundaries

Write the target user, aesthetic references, two or three brand-name candidates, and claims that must not be used (especially medical or efficacy claims). This gate does not clear a trademark; that belongs in gate 8. Treat name candidates as unregistered ideas only.

### 8. Compliance, IP, supply chain, and unit economics

Check trademarks, patents, and target-market rules (especially efficacy and medical-device language). Confirm MOQ, ex-factory price, certifications, and lead time from a factory or a page you can actually open, then back into retail price and margin.

If a figure cannot be verified, label it uncertain and stop here. Do not invent MOQ or cost. Pass only when the regulatory path is clear and a price and margin built from verified costs still make sense.

### 9. Small-scale test

Run creative and a landing page (or equivalent) as a small conversion test. Tooling and inventory come after the test works. Do not enter this gate if any earlier gate failed. Do not spend money on ads unless the user explicitly asks after the earlier gates have passed.

## Report

Always write a conclusion report from `templates/report.md`. You may use `scripts/render_report.py` to fill and validate it. Required sections:

- Mode (recommend or reverse) and inputs used, including defaults
- Pain statement
- Demand evidence
- Recommended or evaluated form
- Logistics and education-cost screen
- Vacuum judgment
- Competitors and difference
- Positioning and brand-name candidates
- Claim boundaries
- Compliance, IP, and cost status, with source links
- Final conclusion: exactly one of the three allowed verdicts
- Open gaps (pages blocked, login walls, unpaid data)

Every material claim needs a source link or an explicit "unverified" label.
