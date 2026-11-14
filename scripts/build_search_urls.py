#!/usr/bin/env python3
"""Build public search URLs for a product-pain run. Does not fetch or scrape pages."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from urllib.parse import quote_plus

AMAZON = {
    "us": "https://www.amazon.com/s?k={q}",
    "uk": "https://www.amazon.co.uk/s?k={q}",
    "au": "https://www.amazon.com.au/s?k={q}",
    "ca": "https://www.amazon.ca/s?k={q}",
    "ie": "https://www.amazon.co.uk/s?k={q}",
    "nz": "https://www.amazon.com.au/s?k={q}",
}

AMAZON_NOTE = {
    "ie": "Ireland has no separate Amazon marketplace; this is amazon.co.uk.",
    "nz": "New Zealand has no separate Amazon marketplace; this is amazon.com.au.",
}

MOVERS = {
    "us": "https://www.amazon.com/gp/movers-and-shakers",
    "uk": "https://www.amazon.co.uk/gp/movers-and-shakers",
    "au": "https://www.amazon.com.au/gp/movers-and-shakers",
    "ca": "https://www.amazon.ca/gp/movers-and-shakers",
    "ie": "https://www.amazon.co.uk/gp/movers-and-shakers",
    "nz": "https://www.amazon.com.au/gp/movers-and-shakers",
}

TRENDS_GEO = {
    "us": "US",
    "uk": "GB",
    "au": "AU",
    "ca": "CA",
    "nz": "NZ",
    "ie": "IE",
    "ww": "",
}

META_COUNTRY = {
    "us": "US",
    "uk": "GB",
    "au": "AU",
    "ca": "CA",
    "nz": "NZ",
    "ie": "IE",
}

GOOGLE_GL = {
    "us": "us",
    "uk": "uk",
    "au": "au",
    "ca": "ca",
    "nz": "nz",
    "ie": "ie",
}

ALLOWED_MARKETS = set(TRENDS_GEO)

PAIN_PATTERNS = (
    "I hate",
    "wish there was",
    "why isn't there",
    "doesn't work",
    "finally switched",
    "any recs",
    "alternatives to",
    "stopped using",
)

CREATIVE_CENTER = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
)

USPTO_SEARCH = "https://tmsearch.uspto.gov/"
USPTO_START = "https://www.uspto.gov/trademarks/search"

# Official start pages only. Do not invent unofficial query endpoints.
TM_OFFICES = {
    "us": [
        ("USPTO Trademark Search", USPTO_SEARCH),
        ("USPTO trademarks start page", USPTO_START),
    ],
    "uk": [
        ("UK IPO trade mark search", "https://trademarks.ipo.gov.uk/ipo-tmtext"),
        ("GOV.UK trade mark search landing page", "https://www.gov.uk/search-for-trademark"),
    ],
    "au": [
        ("IP Australia Trade Mark Search", "https://search.ipaustralia.gov.au/trademarks/search"),
    ],
    "ca": [
        ("CIPO Canadian Trademarks Database", "https://ised-isde.canada.ca/cipo/trademark-search/srch/"),
    ],
    "nz": [
        ("IPONZ trade mark search", "https://www.iponz.govt.nz/about-ip/trade-marks/search/"),
    ],
    "ie": [
        ("EUIPO eSearch (Ireland / EU marks)", "https://euipo.europa.eu/eSearch/"),
    ],
}


def encode_query(term: str, extra_safe: str = "") -> str:
    return quote_plus(term.strip(), safe=extra_safe)


def encode_google_query(term: str) -> str:
    # Keep operator punctuation such as site: and after: readable.
    return quote_plus(term.strip(), safe=':"')


def amazon_url(market: str, term: str) -> str:
    return AMAZON[market].format(q=encode_query(term))


def google_search_url(query: str, market: str | None = None) -> str:
    url = f"https://www.google.com/search?q={encode_google_query(query)}&hl=en"
    if market and market in GOOGLE_GL:
        url += f"&gl={GOOGLE_GL[market]}"
    return url


def reddit_urls(term: str, market: str | None = None, after: str | None = None) -> dict[str, str]:
    q = encode_query(term)
    google_q = f"site:reddit.com {term.strip()}"
    if after:
        google_q += f" after:{after}"
    return {
        "reddit_search": f"https://www.reddit.com/search/?q={q}&t=year",
        "google_site_reddit": google_search_url(google_q, market),
    }


def tiktok_url(term: str) -> str:
    return f"https://www.tiktok.com/search?q={encode_query(term)}"


def youtube_url(term: str) -> str:
    return f"https://www.youtube.com/results?search_query={encode_query(term)}"


def trends_url(term: str, market: str, compare: list[str] | None = None) -> str:
    parts = [encode_query(term)] + [encode_query(t) for t in (compare or []) if t.strip()]
    url = f"https://trends.google.com/trends/explore?q={','.join(parts)}&date=today%205-y"
    geo = TRENDS_GEO.get(market, "")
    if geo:
        url += f"&geo={geo}"
    return url


def meta_ad_library_url(term: str, market: str) -> str:
    country = META_COUNTRY.get(market, "US")
    q = encode_query(term)
    return (
        "https://www.facebook.com/ads/library/"
        f"?active_status=active&ad_type=all&country={country}"
        f"&q={q}&search_type=keyword_unordered&media_type=all"
        "&sort_data%5Bmode%5D=relevancy_monthly_grouped"
    )


def patents_url(term: str, exact: bool = False) -> str:
    q = term.strip()
    if exact and " " in q:
        q = f'"{q}"'
    return f"https://patents.google.com/?q={encode_query(q)}"


def normalize_domain(domain: str) -> str:
    host = domain.strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def similarweb_url(domain: str) -> str:
    return f"https://www.similarweb.com/website/{normalize_domain(domain)}/"


def google_ads_search_url(query: str, region: str = "US") -> str:
    """Ads Transparency search URL.

    Only the `region` and `query` parameters were observed live
    (2026-11-14, Asia/Shanghai), and only `region=US` was confirmed.
    Do not invent other query-string parameters.
    """
    return (
        "https://adstransparency.google.com/search"
        f"?region={region}&query={encode_query(query)}"
    )


def parse_markets(raw: str) -> list[str]:
    markets = [m.strip().lower() for m in raw.split(",") if m.strip()]
    unknown = [m for m in markets if m not in ALLOWED_MARKETS]
    if unknown:
        raise ValueError(
            f"Unknown market(s): {', '.join(unknown)}. "
            "Use us, uk, au, ca, nz, ie, or ww."
        )
    if not markets:
        raise ValueError("Provide at least one market.")
    return markets


def year_ago_iso() -> str:
    return (date.today() - timedelta(days=365)).isoformat()


def _trends_explore(market: str) -> str:
    geo = TRENDS_GEO.get(market, "")
    url = "https://trends.google.com/trends/explore?date=today%205-y"
    if geo:
        url += f"&geo={geo}"
    return url



def trademark_section(markets: list[str], names: list[str]) -> list[str]:
    lines = [
        "## Official trademark search (after you pick the product)",
        "",
        "Open these official tools in a browser and type the names below. This script does not query them. Trademark search is a post-selection brand-launch step and does not affect the selection verdict.",
        "",
    ]
    if names:
        lines.append("Names to search (exact and near marks, relevant classes):")
        for name in names:
            lines.append(f"- {name}")
        lines.append("")
    seen: set[str] = set()
    office_markets = [m for m in markets if m in TM_OFFICES] or ["us", "uk", "au"]
    for market in office_markets:
        for label, url in TM_OFFICES[market]:
            if url in seen:
                continue
            seen.add(url)
            lines.append(f"- {label} ({market.upper()}): {url}")
    lines.append("")
    return lines


def render_markdown(
    keywords: list[str],
    markets: list[str],
    domains: list[str],
    *,
    pain_patterns: bool = False,
    compare: list[str] | None = None,
    discover: bool = False,
    names: list[str] | None = None,
) -> str:
    lines = ["# Search URLs", ""]
    lines.append(
        "Open these public pages and extract what you can see. This script does not fetch them."
    )
    lines.append("")
    shop_markets = [m for m in markets if m in AMAZON]
    trend_markets = markets or ["ww"]
    after = year_ago_iso()
    google_market = next((m for m in markets if m in GOOGLE_GL), None)

    if discover:
        # Rebuild discovery with a proper Trends homepage when there is no keyword.
        disc = [
            "## Discovery (gate 0)",
            "",
            "Use these when recommend mode has no category yet. Open only what you can reach.",
            "",
        ]
        shop = [m for m in markets if m in MOVERS] or ["us", "uk", "au"]
        seen: set[str] = set()
        for market in shop:
            url = MOVERS[market]
            if url in seen:
                continue
            seen.add(url)
            note = AMAZON_NOTE.get(market, "")
            suffix = f" ({note})" if note else ""
            disc.append(f"- Amazon Movers & Shakers ({market.upper()}): {url}{suffix}")
        disc.append(f"- TikTok Creative Center (popular hashtags): {CREATIVE_CENTER}")
        for market in trend_markets:
            label = "worldwide" if market == "ww" else market.upper()
            disc.append(f"- Google Trends explore ({label}, last 5 years): {_trends_explore(market)}")
        gm = google_market or "us"
        disc.append(
            "- Reddit pain pattern example: "
            + reddit_urls("wish there was", gm, after)["google_site_reddit"]
        )
        disc.append("")
        lines.extend(disc)

    for term in keywords:
        lines.append(f"## {term}")
        lines.append("")
        reddit = reddit_urls(term, google_market, after)
        lines.append(f"- Reddit search (past year): {reddit['reddit_search']}")
        lines.append(f"- Google `site:reddit.com` (past year, hl=en): {reddit['google_site_reddit']}")
        lines.append(f"- TikTok: {tiktok_url(term)}")
        lines.append(f"- YouTube: {youtube_url(term)}")
        lines.append(f"- Google Patents: {patents_url(term)}")
        if " " in term.strip():
            lines.append(f"- Google Patents (quoted phrase): {patents_url(term, exact=True)}")
        for market in shop_markets:
            label = market.upper()
            note = f" — {AMAZON_NOTE[market]}" if market in AMAZON_NOTE else ""
            lines.append(f"- Amazon {label}: {amazon_url(market, term)}{note}")
            lines.append(f"- Meta Ad Library {label}: {meta_ad_library_url(term, market)}")
        # Meta for ww-only or trends-only markets that have a country code but no Amazon already listed
        for market in markets:
            if market in META_COUNTRY and market not in shop_markets:
                label = market.upper()
                lines.append(f"- Meta Ad Library {label}: {meta_ad_library_url(term, market)}")
        for market in trend_markets:
            label = "worldwide" if market == "ww" else market.upper()
            lines.append(f"- Google Trends ({label}, last 5 years): {trends_url(term, market)}")
            if compare:
                lines.append(
                    f"- Google Trends comparison ({label}): {trends_url(term, market, compare)}"
                )
        lines.append("")
        if pain_patterns:
            lines.append(f"### {term} — Reddit pain patterns")
            lines.append("")
            for phrase in PAIN_PATTERNS:
                patterned = f'{term} "{phrase}"'
                patterned_urls = reddit_urls(patterned, google_market, after)
                lines.append(f"- `{phrase}` Reddit: {patterned_urls['reddit_search']}")
                lines.append(f"- `{phrase}` Google: {patterned_urls['google_site_reddit']}")
            lines.append("")

    names = [n.strip() for n in (names or []) if n.strip()]
    if names:
        lines.extend(trademark_section(markets, names))

    if keywords or domains:
        lines.extend(
            [
                "## Google Ads Transparency Center (gate 5)",
                "",
                "Open these official pages in a browser. Search the domain first; if it returns 0 results, retry the brand name, then the legal company name (for example 'X LLC', 'X Inc', 'X Ltd'), then the Amazon seller or brand name from the listing. Try the target-market region, then Anywhere. Only record \"no ads found\" after all variants return 0, and list the exact queries and URLs you tried. Only the `region` and `query` parameters were observed live, and only `region=US` was confirmed; do not invent other query-string parameters. For other regions or Anywhere, set the filter in the UI and record the URL the browser shows. This script does not fetch the pages.",
                "",
                "- Home: https://adstransparency.google.com/",
                "- Search: https://adstransparency.google.com/search",
                "",
            ]
        )
        if domains:
            lines.append(
                "Observed search URL form (`region=US` confirmed live):"
            )
            lines.append("")
            for domain in domains:
                host = normalize_domain(domain)
                if not host:
                    continue
                lines.append(f"- {host} (US): {google_ads_search_url(host, 'US')}")
            lines.append("")

    if domains:
        lines.append("## Similarweb (free snapshot)")
        lines.append("")
        for domain in domains:
            lines.append(f"- {domain}: {similarweb_url(domain)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build public Reddit, Amazon, TikTok, YouTube, Trends, Ads, and IP search URLs."
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=[],
        help="One or more search phrases, quoted if they contain spaces.",
    )
    parser.add_argument(
        "--markets",
        default="us,uk,au",
        help="Comma-separated markets: us, uk, au, ca, nz, ie, ww. Default: us,uk,au.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=[],
        help="Optional competitor or brand domains for Similarweb and Google Ads Transparency search URLs.",
    )
    parser.add_argument(
        "--pain-patterns",
        action="store_true",
        help="Also emit Reddit and Google URLs for common pain phrases combined with each keyword.",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        default=[],
        help="Optional extra terms for a Google Trends comparison URL.",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Also (or only) print gate-0 discovery links: Movers & Shakers, Creative Center, Trends.",
    )
    parser.add_argument(
        "--names",
        nargs="+",
        default=[],
        help="Brand-name candidates for official trademark-office start pages (post-selection / brand-launch checklist; does not affect the selection verdict). Emitted only when this flag is passed. The script does not search them.",
    )
    args = parser.parse_args(argv)
    try:
        markets = parse_markets(args.markets)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    keywords = [k.strip() for k in args.keywords if k.strip()]
    names = [n.strip() for n in args.names if n.strip()]
    if not keywords and not args.discover and not names:
        print("error: provide at least one keyword, or pass --discover or --names", file=sys.stderr)
        return 2
    sys.stdout.write(
        render_markdown(
            keywords,
            markets,
            args.domains,
            pain_patterns=args.pain_patterns,
            compare=args.compare,
            discover=args.discover,
            names=names,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
