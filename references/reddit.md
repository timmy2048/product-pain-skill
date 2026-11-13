# Reddit playbook

Reddit is one of the three required social channels. Use it to hear unprompted complaints and workarounds (gate 1 pain), not to count demand. Pinterest, Instagram, and other social networks are not used by default.

## Where to search

Construct URLs with `scripts/build_search_urls.py`, or build them yourself:

- Reddit search (past year): `https://www.reddit.com/search/?q={query}&t=year`
- Google site search (past year, English UI): `https://www.google.com/search?q=site%3Areddit.com+{query}+after:{YYYY-MM-DD}&hl=en&gl={market}`

Pass `--pain-patterns` to emit the query patterns below combined with your keyword.

Helpful query patterns (combine with the category, not as slogans):

- `"I hate"`, `"wish there was"`, `"why isn't there"`, `"doesn't work"`, `"finally switched"`
- `"any recs"`, `"alternatives to"`, `"stopped using"`

Prefer posts and comments in the last 12–24 months. Note the subreddit, date, and a link for each theme you keep.

If Reddit search, old Reddit, or a direct thread fetch is blocked, times out, or returns an error, fall back to Google `site:reddit.com` (or another web search) and then open the thread you found. A cached or rendered copy is allowed only when you label it as cached and still try to open the live thread. A blocked Reddit homepage is not a reason to invent comments.

## What counts

- The same pain appearing in more than one community or thread
- People describing a failed product, a hack, or a job they still cannot get done
- Language you can later reuse as positioning, not as a slogan invented by the model

## What to ignore or downgrade

- A single viral rant with no corroboration
- Brand-war threads with no specific product failure
- Requests that are clearly jokes or one-off edge cases

## Access

Stay on public search and public threads. Do not scrape behind a login, and do not use unofficial APIs.

The official [Reddit Data API](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki) is an optional accelerator when the user already has approved OAuth credentials. Access is no longer fully self-serve: an application has to be approved, free use is rate-limited (on the order of 100 queries per minute), and commercial use may need a separate contract. Do not wait on that review before running the skill. If credentials are present, you may search posts and comments through the official API; if they are not, use public pages, record the gap, and continue.
