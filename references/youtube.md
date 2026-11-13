# YouTube playbook

Use YouTube to see how people actually use a product, what they complain about in situ, and whether a dominant brand is already named in everyday speech.

## Where to search

- Search: `https://www.youtube.com/results?search_query={query}`
- URLs from `scripts/build_search_urls.py`

Include how-to, review, "I tried," haul, and complaint videos. Read public titles, descriptions, comments, and, when a public transcript is available, the transcript. The model should not invent captions. Any capable transcript or comment tool is fine; do not bind this step to one vendor.

Some comment or transcript tools charge credits (for example, a comment pull may cost more than a search or a single transcript). If a tool is out of credits, say so, and either fall back to the official [YouTube Data API v3](https://developers.google.com/youtube/v3) when the user has an API key, or read the public watch page and any comments you can actually see. Do not invent comment text to fill the gap.

## What counts

- Recurring use problems (fit, time, mess, durability, confusing setup)
- Comments that describe a job the featured product still fails
- Whether viewers already have a default brand they recommend unprompted (feeds gate 5)

## What not to treat as proof

- View counts or a single viral review as demand volume
- Sponsor reads as independent evidence of quality
- Medical or efficacy claims in titles; copy those into claim-boundary notes, do not repeat them as facts

## Access

Public watch and search pages only. If comments are disabled or a transcript is missing, say so and rely on title, description, and any comments you could actually read.
