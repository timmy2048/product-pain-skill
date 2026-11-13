#!/usr/bin/env python3
"""Build public search URLs for a product-pain run. Does not fetch or scrape pages."""

from __future__ import annotations

import argparse
import sys
from urllib.parse import quote, quote_plus

AMAZON = {
    "us": "https://www.amazon.com/s?k={q}",
    "uk": "https://www.amazon.co.uk/s?k={q}",
    "au": "https://www.amazon.com.au/s?k={q}",
}

TRENDS_GEO = {"us": "US", "uk": "GB", "au": "AU", "ww": ""}

META_COUNTRY = {"us": "US", "uk": "GB", "au": "AU"}


def encode_query(term: str) -> str:
    return quote_plus(term.strip())


def amazon_url(market: str, term: str) -> str:
    return AMAZON[market].format(q=encode_query(term))


def reddit_urls(term: str) -> dict[str, str]:
    q = encode_query(term)
    return {
        "reddit_search": f"https://www.reddit.com/search/?q={q}",
        "google_site_reddit": f"https://www.google.com/search?q=site%3Areddit.com+{q}",
    }


def tiktok_url(term: str) -> str:
    return f"https://www.tiktok.com/search?q={encode_query(term)}"


def youtube_url(term: str) -> str:
    return f"https://www.youtube.com/results?search_query={encode_query(term)}"


def trends_url(term: str, market: str) -> str:
    q = quote(term.strip(), safe="")
    geo = TRENDS_GEO.get(market, "")
    url = f"https://trends.google.com/trends/explore?q={q}"
    if geo:
        url += f"&geo={geo}"
    return url


def meta_ad_library_url(term: str, market: str) -> str:
    country = META_COUNTRY.get(market, "US")
    q = encode_query(term)
    return (
        "https://www.facebook.com/ads/library/"
        f"?active_status=active&ad_type=all&country={country}&q={q}&sort_data[mode]=relevancy_monthly_grouped"
    )


def patents_url(term: str) -> str:
    return f"https://patents.google.com/?q={encode_query(term)}"


def uspto_trademark_url() -> str:
    return "https://www.uspto.gov/trademarks/search"


def similarweb_url(domain: str) -> str:
    host = domain.strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    return f"https://www.similarweb.com/website/{host}/"


def parse_markets(raw: str) -> list[str]:
    markets = [m.strip().lower() for m in raw.split(",") if m.strip()]
    unknown = [m for m in markets if m not in AMAZON and m != "ww"]
    if unknown:
        raise ValueError(f"Unknown market(s): {', '.join(unknown)}. Use us, uk, au, or ww.")
    if not markets:
        raise ValueError("Provide at least one market.")
    return markets


def render_markdown(keywords: list[str], markets: list[str], domains: list[str]) -> str:
    lines = ["# Search URLs", ""]
    lines.append("Open these public pages and extract what you can see. This script does not fetch them.")
    lines.append("")
    shop_markets = [m for m in markets if m in AMAZON]
    trend_markets = markets or ["ww"]

    for term in keywords:
        lines.append(f"## {term}")
        lines.append("")
        reddit = reddit_urls(term)
        lines.append(f"- Reddit search: {reddit['reddit_search']}")
        lines.append(f"- Google `site:reddit.com`: {reddit['google_site_reddit']}")
        lines.append(f"- TikTok: {tiktok_url(term)}")
        lines.append(f"- YouTube: {youtube_url(term)}")
        lines.append(f"- Google Patents: {patents_url(term)}")
        lines.append(f"- USPTO trademark search (start page): {uspto_trademark_url()}")
        for market in shop_markets:
            label = market.upper()
            lines.append(f"- Amazon {label}: {amazon_url(market, term)}")
            lines.append(f"- Meta Ad Library {label}: {meta_ad_library_url(term, market)}")
        for market in trend_markets:
            label = "worldwide" if market == "ww" else market.upper()
            lines.append(f"- Google Trends ({label}): {trends_url(term, market)}")
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
        required=True,
        help="One or more search phrases, quoted if they contain spaces.",
    )
    parser.add_argument(
        "--markets",
        default="us,uk,au",
        help="Comma-separated markets: us, uk, au, ww. Default: us,uk,au.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=[],
        help="Optional competitor or brand domains for Similarweb links.",
    )
    args = parser.parse_args(argv)
    try:
        markets = parse_markets(args.markets)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    keywords = [k.strip() for k in args.keywords if k.strip()]
    if not keywords:
        print("error: provide at least one keyword", file=sys.stderr)
        return 2
    sys.stdout.write(render_markdown(keywords, markets, args.domains))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
