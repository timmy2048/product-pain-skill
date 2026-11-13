#!/usr/bin/env python3
"""Opt-in fetch of public, logged-out Amazon reviews via a third-party API.

This helper is OFF BY DEFAULT. It never signs in to Amazon, never sends
Amazon cookies, and never calls Amazon directly. It only calls a
user-supplied ScrapingBee or Apify endpoint for logged-out public content.

Warning: Automated scraping of Amazon may violate Amazon's Conditions of
Use and can lead to IP or account blocks. You enable this at your own risk.

Request formats (from public docs; do not guess other endpoints):

- ScrapingBee Amazon Product API, GET
  https://app.scrapingbee.com/api/v1/amazon/product
  Authorization: Bearer $SCRAPINGBEE_API_KEY
  query=<ASIN>, domain=com|co.uk|com.au, light_request=false
  (light requests can omit reviews). There is no documented
  /api/v1/amazon/review endpoint; reviews are taken from the product
  payload and will usually be a partial, featured-on-page subset.

- Apify official run-sync dataset endpoint, POST
  https://api.apify.com/v2/actors/{actorId}/run-sync-get-dataset-items
  Authorization: Bearer $APIFY_TOKEN
  JSON input is actor-specific. Default actor and input follow the
  public docs for webdatalabs/amazon-reviews-scraper; override with
  --actor and --apify-input.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_DIR = REPO_ROOT / "output" / "cache" / "amazon-reviews"

MARKET_DOMAINS = {
    "us": "com",
    "uk": "co.uk",
    "au": "com.au",
}
MARKET_HOSTS = {
    "us": "www.amazon.com",
    "uk": "www.amazon.co.uk",
    "au": "www.amazon.com.au",
}
ALLOWED_MARKETS = set(MARKET_DOMAINS)
DEFAULT_STARS = (2, 3)
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")

# Documented public actor; override with APIFY_AMAZON_REVIEWS_ACTOR or --actor.
DEFAULT_APIFY_ACTOR = "webdatalabs~amazon-reviews-scraper"
SCRAPINGBEE_PRODUCT_URL = "https://app.scrapingbee.com/api/v1/amazon/product"
APIFY_RUN_SYNC_URL = "https://api.apify.com/v2/actors/{actor_id}/run-sync-get-dataset-items"

PERSONAL_KEYS = {
    "author",
    "authorname",
    "author_name",
    "name",
    "username",
    "user",
    "reviewer",
    "reviewer_name",
    "reviewername",
    "profile",
    "profile_url",
    "profileurl",
    "author_url",
    "authorurl",
    "avatar",
    "avatar_url",
    "reviewer_url",
    "reviewerurl",
}

TOS_WARNING = (
    "Automated scraping of Amazon may violate Amazon's Conditions of Use "
    "and can lead to IP or account blocks. You enable this at your own risk. "
    "This script only requests logged-out public content through a third-party "
    "API and never signs in to Amazon."
)

MISSING_KEY_MESSAGE = """error: no third-party scraping API key is set. This script is opt-in and off by default.

Set one of:
  SCRAPINGBEE_API_KEY     Uses the documented ScrapingBee Amazon Product API
                          (GET https://app.scrapingbee.com/api/v1/amazon/product).
  APIFY_TOKEN             Uses the official Apify run-sync dataset endpoint
  (or APIFY_API_TOKEN)    (POST https://api.apify.com/v2/actors/{actorId}/run-sync-get-dataset-items).
                          Also set APIFY_AMAZON_REVIEWS_ACTOR or pass --actor
                          (username~actor-name). The default actor is
                          webdatalabs~amazon-reviews-scraper; override it if you
                          use a different actor, and pass --apify-input when the
                          input schema differs.

You must also pass --accept-risk.

Do not log in to Amazon or pass Amazon cookies. Only logged-out public content is requested.

Warning: Automated scraping of Amazon may violate Amazon's Conditions of Use
and can lead to IP or account blocks. You enable this at your own risk.

Default evidence path (no key needed): public "Customers say" plus featured
reviews on the product page, and manual signed-in browser viewing of 2-3 star
reviews on the top 3-5 competitors. Helium 10, Jungle Scout, and Sellersprite
are optional accelerators when you already have an account.
"""

REVIEW_COLUMNS = (
    "asin",
    "marketplace",
    "star",
    "title",
    "body",
    "date",
    "verified",
    "variant",
    "source_url",
    "fetched_at",
)


class FetchError(RuntimeError):
    """A documented API call failed."""


# --- parsing helpers ---------------------------------------------------------


def parse_markets(raw: str) -> list[str]:
    markets = [m.strip().lower() for m in raw.split(",") if m.strip()]
    unknown = [m for m in markets if m not in ALLOWED_MARKETS]
    if unknown:
        raise ValueError(
            f"Unknown market(s): {', '.join(unknown)}. Use us, uk, or au."
        )
    if not markets:
        raise ValueError("Provide at least one market: us, uk, or au.")
    return markets


def parse_stars(raw: str) -> list[int]:
    stars: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            value = int(part)
        except ValueError as exc:
            raise ValueError(f"Stars must be integers 1-5, got {part!r}") from exc
        if value < 1 or value > 5:
            raise ValueError(f"Stars must be integers 1-5, got {part!r}")
        if value not in stars:
            stars.append(value)
    if not stars:
        raise ValueError("Provide at least one star rating.")
    return stars


def parse_asins(values: list[str]) -> list[str]:
    asins: list[str] = []
    for raw in values:
        for part in re.split(r"[,\s]+", raw.strip()):
            if not part:
                continue
            asin = extract_asin(part)
            if not asin:
                raise ValueError(
                    f"Not a valid 10-character ASIN or Amazon product URL: {part!r}"
                )
            if asin not in asins:
                asins.append(asin)
    if not asins:
        raise ValueError("Provide at least one ASIN or Amazon product URL.")
    return asins


def extract_asin(text: str) -> str | None:
    text = text.strip()
    upper = text.upper()
    if ASIN_RE.match(upper):
        return upper
    match = re.search(r"(?:/dp/|/gp/product/|/product/)([A-Z0-9]{10})", text, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"\b([A-Z0-9]{10})\b", upper)
    if match:
        return match.group(1)
    return None


def product_url(asin: str, market: str) -> str:
    return f"https://{MARKET_HOSTS[market]}/dp/{asin}"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- personal-data stripping and review normalization ------------------------


def _key_fold(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def drop_personal_fields(item: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in item.items():
        folded = _key_fold(str(key))
        if folded in PERSONAL_KEYS or folded.endswith("profileurl") or folded.endswith("authorurl"):
            continue
        if isinstance(value, str) and re.search(r"/profile/|amazon\.[^/]+/gp/profile", value, re.I):
            continue
        cleaned[key] = value
    return cleaned


def first_present(item: dict[str, Any], *keys: str) -> Any:
    folded_map = {_key_fold(str(k)): v for k, v in item.items()}
    for key in keys:
        value = folded_map.get(_key_fold(key))
        if value is not None and value != "":
            return value
    return None


def parse_star(value: Any) -> int | None:
    if value is None or value is False:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = int(value)
        return number if 1 <= number <= 5 else None
    text = str(value).strip()
    match = re.search(r"([1-5])(?:\.0+)?", text)
    if match:
        return int(match.group(1))
    return None


def parse_verified(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "yes", "verified", "verified purchase", "1"}:
        return True
    if text in {"false", "no", "0", "unverified"}:
        return False
    return None


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return ""
    return str(value).strip()


def normalize_review(
    raw: dict[str, Any],
    *,
    asin: str,
    market: str,
    fetched_at: str,
    default_url: str,
) -> dict[str, Any] | None:
    item = drop_personal_fields(raw if isinstance(raw, dict) else {})
    star = parse_star(
        first_present(item, "star", "stars", "rating", "star_rating", "starRating")
    )
    title = as_text(first_present(item, "title", "review_title", "reviewTitle", "headline"))
    body = as_text(
        first_present(
            item,
            "body",
            "content",
            "text",
            "review",
            "review_text",
            "reviewText",
            "body_text",
        )
    )
    # ScrapingBee product-page titles sometimes prepend "5.0 out of 5 stars ".
    title = re.sub(r"^[1-5](?:\.0)? out of 5 stars\s*", "", title, flags=re.I).strip()
    if star is None and not title and not body:
        return None
    date = as_text(
        first_present(
            item, "date", "timestamp", "reviewed_at", "review_date", "date_utc", "published_date"
        )
    )
    verified = parse_verified(
        first_present(
            item,
            "verified",
            "verified_purchase",
            "is_verified",
            "verifiedPurchase",
            "isVerified",
        )
    )
    variant = as_text(
        first_present(
            item, "variant", "variation", "product_variation", "color_size", "format"
        )
    )
    if isinstance(first_present(item, "variant", "variation", "dimensions"), dict):
        variant = as_text(
            variant
            or ", ".join(
                f"{k}: {v}"
                for k, v in (first_present(item, "variant", "variation", "dimensions") or {}).items()
            )
        )
    source = as_text(
        first_present(item, "source_url", "review_url", "url", "link", "reviewUrl")
    ) or default_url
    return {
        "asin": as_text(first_present(item, "asin")) or asin,
        "marketplace": market,
        "star": star,
        "title": title,
        "body": body,
        "date": date,
        "verified": verified,
        "variant": variant,
        "source_url": source,
        "fetched_at": fetched_at,
    }


def filter_reviews(rows: list[dict[str, Any]], stars: list[int], limit: int | None) -> list[dict[str, Any]]:
    wanted = set(stars)
    out = [row for row in rows if row.get("star") in wanted]
    if limit is not None and limit >= 0:
        out = out[:limit]
    return out


# --- HTTP --------------------------------------------------------------------

Opener = Callable[[str, str, dict[str, str], bytes | None, int], tuple[int, bytes, str]]


def default_opener(
    url: str, method: str, headers: dict[str, str], body: bytes | None, timeout: int
) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), response.geturl()
    except urllib.error.HTTPError as exc:
        payload = exc.read() if exc.fp else b""
        return exc.code, payload, url


def http_json(
    opener: Opener,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: Any = None,
    timeout: int = 60,
) -> Any:
    if params:
        query = urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None and v != ""}
        )
        url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
    body = None
    req_headers = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req_headers.setdefault("Accept", "application/json")
    status, payload, final_url = opener(url, method, req_headers, body, timeout)
    if status >= 400:
        snippet = payload[:400].decode("utf-8", errors="replace")
        raise FetchError(f"HTTP {status} from {redact_url(final_url)}: {snippet}")
    if not payload:
        return None
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise FetchError(
            f"Non-JSON response from {redact_url(final_url)}: {payload[:200]!r}"
        ) from exc


def redact_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    for key in list(query):
        if key.lower() in {"api_key", "token", "key", "apikey"}:
            query[key] = ["***"]
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query, doseq=True),
            parsed.fragment,
        )
    )


# --- providers ---------------------------------------------------------------


def scrapingbee_request(asin: str, market: str, api_key: str) -> dict[str, Any]:
    return {
        "method": "GET",
        "url": SCRAPINGBEE_PRODUCT_URL,
        "headers": {"Authorization": f"Bearer {api_key}"},
        "params": {
            "query": asin,
            "domain": MARKET_DOMAINS[market],
            "light_request": "false",
        },
        "timeout": 60,
    }


def reviews_from_scrapingbee_payload(
    payload: Any, *, asin: str, market: str, fetched_at: str
) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    raw_reviews = payload.get("reviews") or []
    if isinstance(raw_reviews, dict):
        raw_reviews = raw_reviews.get("items") or raw_reviews.get("results") or []
    if not isinstance(raw_reviews, list):
        return []
    url = as_text(payload.get("url")) or product_url(asin, market)
    rows: list[dict[str, Any]] = []
    for item in raw_reviews:
        if not isinstance(item, dict):
            continue
        row = normalize_review(
            item, asin=asin, market=market, fetched_at=fetched_at, default_url=url
        )
        if row:
            rows.append(row)
    return rows


def apify_actor_id(raw: str) -> str:
    text = raw.strip()
    text = text.replace("/", "~")
    if not text:
        raise ValueError("Apify actor id is empty.")
    return text


def apify_request(
    asins: list[str],
    market: str,
    stars: list[int],
    *,
    token: str,
    actor: str,
    max_reviews: int,
    extra_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actor_id = apify_actor_id(actor)
    urls = [{"url": product_url(asin, market)} for asin in asins]
    payload: dict[str, Any] = {
        "productUrls": urls,
        "maxReviewsPerProduct": max_reviews,
        "starRatings": [str(s) for s in stars],
        "verifiedOnly": False,
        "includeReviewerNames": False,
    }
    if extra_input:
        payload.update(extra_input)
    return {
        "method": "POST",
        "url": APIFY_RUN_SYNC_URL.format(actor_id=urllib.parse.quote(actor_id, safe="~")),
        "headers": {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        "json_body": payload,
        "timeout": 310,
    }


def reviews_from_apify_items(
    payload: Any, *, default_asin: str, market: str, fetched_at: str
) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("data") or payload.get("reviews") or []
    elif isinstance(payload, list):
        items = payload
    else:
        items = []
    rows: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        # Some actors wrap a product with a nested reviews list.
        nested = item.get("reviews")
        sources = nested if isinstance(nested, list) else [item]
        asin = extract_asin(str(first_present(item, "asin", "productAsin", "product_id") or "")) or default_asin
        url = as_text(first_present(item, "url", "productUrl", "product_url")) or product_url(asin, market)
        for raw in sources:
            if not isinstance(raw, dict):
                continue
            row = normalize_review(
                raw, asin=asin, market=market, fetched_at=fetched_at, default_url=url
            )
            if row:
                rows.append(row)
    return rows


# --- cache -------------------------------------------------------------------


def cache_key(provider: str, market: str, asin: str, stars: list[int], max_reviews: int) -> str:
    material = "|".join([provider, market, asin, ",".join(str(s) for s in stars), str(max_reviews)])
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"{provider}_{market}_{asin}_{digest}.json"


def cache_path(cache_dir: Path, **kwargs: Any) -> Path:
    return cache_dir / cache_key(**kwargs)


def load_cache(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def save_cache(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --- orchestration -----------------------------------------------------------


def env_get(*names: str) -> str:
    for name in names:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return ""


def resolve_provider(explicit: str | None) -> tuple[str, str]:
    scrapingbee = env_get("SCRAPINGBEE_API_KEY")
    apify = env_get("APIFY_TOKEN", "APIFY_API_TOKEN")
    wanted = (explicit or env_get("AMAZON_REVIEWS_PROVIDER") or "").strip().lower()
    if wanted in {"auto", ""}:
        if scrapingbee and apify:
            raise ValueError(
                "Both SCRAPINGBEE_API_KEY and APIFY_TOKEN are set. "
                "Pass --provider scrapingbee or --provider apify."
            )
        if scrapingbee:
            return "scrapingbee", scrapingbee
        if apify:
            return "apify", apify
        raise ValueError("missing-key")
    if wanted == "scrapingbee":
        if not scrapingbee:
            raise ValueError("missing-key")
        return "scrapingbee", scrapingbee
    if wanted == "apify":
        if not apify:
            raise ValueError("missing-key")
        return "apify", apify
    raise ValueError("Provider must be scrapingbee, apify, or auto.")


def fetch_scrapingbee(
    asins: list[str],
    market: str,
    stars: list[int],
    *,
    api_key: str,
    max_reviews: int,
    delay: float,
    cache_dir: Path,
    force: bool,
    opener: Opener,
    sleeper: Callable[[float], None],
) -> tuple[list[dict[str, Any]], list[str], int]:
    fetched_at = utc_now()
    rows: list[dict[str, Any]] = []
    notes: list[str] = []
    failures = 0
    for index, asin in enumerate(asins):
        path = cache_path(
            cache_dir,
            provider="scrapingbee",
            market=market,
            asin=asin,
            stars=stars,
            max_reviews=max_reviews,
        )
        cached = None if force else load_cache(path)
        if cached and isinstance(cached.get("reviews"), list):
            rows.extend(cached["reviews"])
            notes.append(f"{asin} ({market}): cache hit")
            continue
        if index and delay > 0:
            sleeper(delay)
        request = scrapingbee_request(asin, market, api_key)
        try:
            payload = http_json(opener, **request)
        except FetchError as exc:
            failures += 1
            notes.append(f"{asin} ({market}): fetch failed — {exc}")
            continue
        batch = filter_reviews(
            reviews_from_scrapingbee_payload(
                payload, asin=asin, market=market, fetched_at=fetched_at
            ),
            stars,
            max_reviews,
        )
        save_cache(
            path,
            {
                "asin": asin,
                "marketplace": market,
                "provider": "scrapingbee",
                "fetched_at": fetched_at,
                "reviews": batch,
            },
        )
        if not batch:
            notes.append(
                f"{asin} ({market}): no {stars} star reviews in the public product-page subset"
            )
        rows.extend(batch)
    notes.append(
        "ScrapingBee Amazon Product API returns a public product-page review subset, "
        "not a full star-filtered history. Coverage is partial."
    )
    return rows, notes, failures


def fetch_apify(
    asins: list[str],
    market: str,
    stars: list[int],
    *,
    token: str,
    actor: str,
    max_reviews: int,
    extra_input: dict[str, Any] | None,
    cache_dir: Path,
    force: bool,
    opener: Opener,
) -> tuple[list[dict[str, Any]], list[str], int]:
    fetched_at = utc_now()
    notes: list[str] = []
    if not force:
        cached_rows: list[dict[str, Any]] = []
        all_hit = True
        for asin in asins:
            path = cache_path(
                cache_dir,
                provider="apify",
                market=market,
                asin=asin,
                stars=stars,
                max_reviews=max_reviews,
            )
            cached = load_cache(path)
            if cached and isinstance(cached.get("reviews"), list):
                cached_rows.extend(cached["reviews"])
                notes.append(f"{asin} ({market}): cache hit")
            else:
                all_hit = False
                break
        if all_hit:
            return cached_rows, notes, 0

    request = apify_request(
        asins,
        market,
        stars,
        token=token,
        actor=actor,
        max_reviews=max_reviews,
        extra_input=extra_input,
    )
    payload = http_json(opener, **{k: v for k, v in request.items()})
    rows = filter_reviews(
        reviews_from_apify_items(
            payload, default_asin=asins[0], market=market, fetched_at=fetched_at
        ),
        stars,
        None,
    )
    by_asin: dict[str, list[dict[str, Any]]] = {asin: [] for asin in asins}
    for row in rows:
        by_asin.setdefault(row["asin"], []).append(row)
    limited: list[dict[str, Any]] = []
    for asin in asins:
        batch = by_asin.get(asin, [])[:max_reviews]
        if not batch:
            notes.append(f"{asin} ({market}): no {stars} star reviews returned")
        limited.extend(batch)
        save_cache(
            cache_path(
                cache_dir,
                provider="apify",
                market=market,
                asin=asin,
                stars=stars,
                max_reviews=max_reviews,
            ),
            {
                "asin": asin,
                "marketplace": market,
                "provider": "apify",
                "fetched_at": fetched_at,
                "reviews": batch,
            },
        )
    notes.append(
        "Apify results are treated as a logged-out public snapshot. Coverage is "
        "partial unless you can show otherwise. Reviewer names were requested off "
        "and stripped if present."
    )
    return limited, notes, 0


def build_result(
    *,
    provider: str,
    markets: list[str],
    asins: list[str],
    stars: list[int],
    reviews: list[dict[str, Any]],
    notes: list[str],
) -> dict[str, Any]:
    return {
        "fetched_at": utc_now(),
        "provider": provider,
        "markets": markets,
        "asins": asins,
        "stars": stars,
        "coverage": "partial",
        "warning": TOS_WARNING,
        "notes": notes,
        "review_count": len(reviews),
        "reviews": reviews,
    }


def write_output(path: Path, result: dict[str, Any], fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(REVIEW_COLUMNS))
        writer.writeheader()
        for row in result["reviews"]:
            writer.writerow({key: row.get(key) if row.get(key) is not None else "" for key in REVIEW_COLUMNS})


def load_apify_input(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("{"):
        data = json.loads(text)
    else:
        data = json.loads(Path(text).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--apify-input must be a JSON object or a path to one.")
    return data


# --- CLI ---------------------------------------------------------------------


def main(
    argv: list[str] | None = None,
    *,
    opener: Opener | None = None,
    sleeper: Callable[[float], None] | None = None,
    environ: dict[str, str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Opt-in helper: pull public, logged-out Amazon reviews through "
            "ScrapingBee or Apify. Off by default. Does not sign in to Amazon. "
            "Automated scraping may violate Amazon's Conditions of Use."
        )
    )
    parser.add_argument(
        "--asins",
        nargs="+",
        required=True,
        help="One or more ASINs or Amazon product URLs.",
    )
    parser.add_argument(
        "--markets",
        default="us",
        help="Comma-separated markets: us, uk, au. Default: us.",
    )
    parser.add_argument(
        "--stars",
        default="2,3",
        help="Comma-separated star ratings to keep. Default: 2,3.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output path. Format follows --format (json or csv).",
    )
    parser.add_argument(
        "--format",
        choices=("json", "csv"),
        default="json",
        help="Output format. Default: json.",
    )
    parser.add_argument(
        "--provider",
        choices=("auto", "scrapingbee", "apify"),
        default="auto",
        help="Which third-party API to use. Default: auto (the one key that is set).",
    )
    parser.add_argument(
        "--actor",
        default=None,
        help="Apify actor id (username~name). Defaults to APIFY_AMAZON_REVIEWS_ACTOR "
        f"or {DEFAULT_APIFY_ACTOR}.",
    )
    parser.add_argument(
        "--apify-input",
        default=None,
        help="Extra JSON object, or path to one, merged into the Apify actor input.",
    )
    parser.add_argument(
        "--max-reviews",
        type=int,
        default=50,
        help="Maximum reviews to keep per ASIN after star filtering. Default: 50.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between ScrapingBee ASIN requests. Default: 2.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Directory for cached responses. Default: output/cache/amazon-reviews.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cache and fetch again.",
    )
    parser.add_argument(
        "--accept-risk",
        action="store_true",
        help="Required confirmation that you accept the Amazon Conditions of Use risk.",
    )
    args = parser.parse_args(argv)

    if environ is not None:
        old_env = os.environ.copy()
        os.environ.clear()
        os.environ.update(environ)
    else:
        old_env = None

    try:
        if not args.accept_risk:
            print(
                "error: pass --accept-risk to opt in. Automated scraping of Amazon "
                "may violate Amazon's Conditions of Use and can lead to IP or "
                "account blocks. You enable this at your own risk.",
                file=sys.stderr,
            )
            return 2
        try:
            asins = parse_asins(args.asins)
            markets = parse_markets(args.markets)
            stars = parse_stars(args.stars)
            extra_input = load_apify_input(args.apify_input)
            provider, secret = resolve_provider(args.provider)
        except ValueError as exc:
            if str(exc) == "missing-key":
                print(MISSING_KEY_MESSAGE, file=sys.stderr)
                return 2
            print(f"error: {exc}", file=sys.stderr)
            return 2

        if args.max_reviews < 1:
            print("error: --max-reviews must be at least 1", file=sys.stderr)
            return 2

        client = opener or default_opener
        pause = sleeper or time.sleep
        cache_dir = Path(args.cache_dir)
        reviews: list[dict[str, Any]] = []
        notes: list[str] = []
        failures = 0
        attempted = 0
        try:
            if provider == "scrapingbee":
                for market in markets:
                    attempted += len(asins)
                    batch, batch_notes, failed = fetch_scrapingbee(
                        asins,
                        market,
                        stars,
                        api_key=secret,
                        max_reviews=args.max_reviews,
                        delay=args.delay,
                        cache_dir=cache_dir,
                        force=args.force,
                        opener=client,
                        sleeper=pause,
                    )
                    reviews.extend(batch)
                    notes.extend(batch_notes)
                    failures += failed
            else:
                actor = args.actor or env_get("APIFY_AMAZON_REVIEWS_ACTOR") or DEFAULT_APIFY_ACTOR
                for market in markets:
                    attempted += len(asins)
                    batch, batch_notes, failed = fetch_apify(
                        asins,
                        market,
                        stars,
                        token=secret,
                        actor=actor,
                        max_reviews=args.max_reviews,
                        extra_input=extra_input,
                        cache_dir=cache_dir,
                        force=args.force,
                        opener=client,
                    )
                    reviews.extend(batch)
                    notes.extend(batch_notes)
                    failures += failed
        except FetchError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        result = build_result(
            provider=provider,
            markets=markets,
            asins=asins,
            stars=stars,
            reviews=reviews,
            notes=notes,
        )
        output = Path(args.out)
        write_output(output, result, args.format)
        print(
            f"wrote {output} ({result['review_count']} reviews, coverage={result['coverage']})",
            file=sys.stderr,
        )
        print(TOS_WARNING, file=sys.stderr)
        if attempted and failures == attempted:
            for note in notes:
                if "fetch failed" in note:
                    print(f"error: {note}", file=sys.stderr)
            print("error: every request failed; see notes in the output file.", file=sys.stderr)
            return 2
        return 0
    finally:
        if old_env is not None:
            os.environ.clear()
            os.environ.update(old_env)


if __name__ == "__main__":
    raise SystemExit(main())
