#!/usr/bin/env python3
"""Mocked tests for scripts/fetch_amazon_reviews.py. No live Amazon or paid API calls."""

from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_amazon_reviews as far  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_asins_and_urls(self):
        self.assertEqual(
            far.parse_asins(["B0DPDRNSXV", "https://www.amazon.co.uk/dp/B07N7KFHVH?th=1"]),
            ["B0DPDRNSXV", "B07N7KFHVH"],
        )

    def test_bad_asin(self):
        with self.assertRaises(ValueError):
            far.parse_asins(["not-an-asin"])

    def test_markets_and_stars(self):
        self.assertEqual(far.parse_markets("US,uk"), ["us", "uk"])
        self.assertEqual(far.parse_stars("2,3,3"), [2, 3])
        with self.assertRaises(ValueError):
            far.parse_markets("us,de")
        with self.assertRaises(ValueError):
            far.parse_stars("0")


class NormalizeTests(unittest.TestCase):
    def test_drops_names_and_profile_links_and_filters_stars(self):
        raw = {
            "author": "Danil",
            "author_name": "Danil",
            "profile_url": "https://www.amazon.com/gp/profile/amzn1.account.EXAMPLE",
            "rating": "2.0 out of 5 stars",
            "title": "2.0 out of 5 stars Slips forward",
            "content": "The pillow slides when I nap.",
            "timestamp": "Reviewed in the United States July 15, 2025",
            "verified_purchase": True,
            "variant": "Grey",
            "review_url": "https://www.amazon.com/gp/customer-reviews/R123",
        }
        row = far.normalize_review(
            raw,
            asin="B0EXAMPLE1",
            market="us",
            fetched_at="2026-11-14T00:00:00Z",
            default_url="https://www.amazon.com/dp/B0EXAMPLE1",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["star"], 2)
        self.assertEqual(row["title"], "Slips forward")
        self.assertEqual(row["body"], "The pillow slides when I nap.")
        self.assertTrue(row["verified"])
        self.assertEqual(row["variant"], "Grey")
        self.assertNotIn("author", row)
        self.assertNotIn("profile_url", row)
        self.assertTrue(all(key not in str(row.values()).lower() for key in ("danil", "amzn1.account")))

        five = dict(raw, rating=5, title="Great", content="Loved it")
        normalized_five = far.normalize_review(
            five,
            asin="B0EXAMPLE1",
            market="us",
            fetched_at="2026-11-14T00:00:00Z",
            default_url="https://www.amazon.com/dp/B0EXAMPLE1",
        )
        kept = far.filter_reviews([row, normalized_five], [2, 3], 10)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["star"], 2)


class FakeOpener:
    def __init__(self, responses: list[tuple[int, bytes]]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def __call__(self, url, method, headers, body, timeout):
        self.calls.append(
            {"url": url, "method": method, "headers": headers, "body": body, "timeout": timeout}
        )
        if not self.responses:
            raise AssertionError(f"Unexpected HTTP call to {url}")
        status, payload = self.responses.pop(0)
        return status, payload, url


class CliTests(unittest.TestCase):
    def test_missing_key_exits_helpfully(self):
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            code = far.main(
                [
                    "--asins",
                    "B0DPDRNSXV",
                    "--out",
                    "/tmp/unused.json",
                    "--accept-risk",
                ],
                environ={},
            )
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        text = buf.getvalue()
        self.assertIn("SCRAPINGBEE_API_KEY", text)
        self.assertIn("APIFY_TOKEN", text)
        self.assertIn("Conditions of Use", text)
        self.assertIn("opt-in", text)

    def test_requires_accept_risk_even_with_key(self):
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            code = far.main(
                ["--asins", "B0DPDRNSXV", "--out", "/tmp/unused.json"],
                environ={"SCRAPINGBEE_API_KEY": "secret"},
            )
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("--accept-risk", buf.getvalue())
        self.assertIn("Conditions of Use", buf.getvalue())

    def test_scrapingbee_mocked_request_and_output(self):
        payload = {
            "asin": "B0DPDRNSXV",
            "url": "https://www.amazon.com/dp/B0DPDRNSXV",
            "reviews": [
                {
                    "author": "Should Be Dropped",
                    "rating": 2,
                    "title": "Chin strap failed",
                    "content": "It still slips forward.",
                    "timestamp": "Reviewed in the United States 12 November 2026",
                    "verified_purchase": "yes",
                },
                {
                    "rating": 5,
                    "title": "Perfect",
                    "content": "Love it",
                },
            ],
        }
        opener = FakeOpener([(200, json.dumps(payload).encode("utf-8"))])
        delays: list[float] = []
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "reviews.json"
            code = far.main(
                [
                    "--asins",
                    "B0DPDRNSXV",
                    "--markets",
                    "us",
                    "--out",
                    str(out),
                    "--accept-risk",
                    "--provider",
                    "scrapingbee",
                    "--cache-dir",
                    str(Path(tmp) / "cache"),
                    "--delay",
                    "0",
                ],
                opener=opener,
                sleeper=delays.append,
                environ={"SCRAPINGBEE_API_KEY": "test-key"},
            )
            self.assertEqual(code, 0)
            self.assertEqual(len(opener.calls), 1)
            call = opener.calls[0]
            self.assertEqual(call["method"], "GET")
            self.assertIn("api/v1/amazon/product", call["url"])
            self.assertIn("query=B0DPDRNSXV", call["url"])
            self.assertIn("domain=com", call["url"])
            self.assertIn("light_request=false", call["url"])
            self.assertNotIn("test-key", call["url"])
            self.assertEqual(call["headers"]["Authorization"], "Bearer test-key")
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["provider"], "scrapingbee")
            self.assertEqual(data["coverage"], "partial")
            self.assertEqual(data["review_count"], 1)
            self.assertEqual(data["reviews"][0]["star"], 2)
            self.assertEqual(data["reviews"][0]["body"], "It still slips forward.")
            self.assertNotIn("Should Be Dropped", json.dumps(data))
            self.assertIn("Conditions of Use", data["warning"])

            # Second run should hit cache and not call the network again.
            code = far.main(
                [
                    "--asins",
                    "B0DPDRNSXV",
                    "--markets",
                    "us",
                    "--out",
                    str(Path(tmp) / "reviews2.json"),
                    "--accept-risk",
                    "--provider",
                    "scrapingbee",
                    "--cache-dir",
                    str(Path(tmp) / "cache"),
                ],
                opener=opener,
                sleeper=delays.append,
                environ={"SCRAPINGBEE_API_KEY": "test-key"},
            )
            self.assertEqual(code, 0)
            self.assertEqual(len(opener.calls), 1)

    def test_apify_mocked_request_and_csv(self):
        items = [
            {
                "asin": "B07N7KFHVH",
                "rating": 3,
                "title": "OK but noisy",
                "text": "The zipper rattles.",
                "date": "2026-01-02",
                "authorName": "Jane Doe",
                "verified": False,
            }
        ]
        opener = FakeOpener([(201, json.dumps(items).encode("utf-8"))])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "reviews.csv"
            code = far.main(
                [
                    "--asins",
                    "B07N7KFHVH",
                    "--markets",
                    "uk",
                    "--out",
                    str(out),
                    "--format",
                    "csv",
                    "--accept-risk",
                    "--provider",
                    "apify",
                    "--cache-dir",
                    str(Path(tmp) / "cache"),
                ],
                opener=opener,
                environ={"APIFY_TOKEN": "apify-secret"},
            )
            self.assertEqual(code, 0)
            self.assertEqual(len(opener.calls), 1)
            call = opener.calls[0]
            self.assertEqual(call["method"], "POST")
            self.assertIn(
                "api.apify.com/v2/actors/webdatalabs~amazon-reviews-scraper/run-sync-get-dataset-items",
                call["url"],
            )
            self.assertNotIn("apify-secret", call["url"])
            self.assertEqual(call["headers"]["Authorization"], "Bearer apify-secret")
            body = json.loads(call["body"].decode("utf-8"))
            self.assertEqual(body["includeReviewerNames"], False)
            self.assertEqual(body["starRatings"], ["2", "3"])
            self.assertEqual(body["productUrls"], [{"url": "https://www.amazon.co.uk/dp/B07N7KFHVH"}])
            with out.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["star"], "3")
            self.assertEqual(rows[0]["body"], "The zipper rattles.")
            self.assertEqual(rows[0]["marketplace"], "uk")
            self.assertNotIn("Jane Doe", out.read_text(encoding="utf-8"))

    def test_both_keys_require_explicit_provider(self):
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            code = far.main(
                ["--asins", "B0DPDRNSXV", "--out", "/tmp/x.json", "--accept-risk"],
                environ={"SCRAPINGBEE_API_KEY": "a", "APIFY_TOKEN": "b"},
            )
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("--provider", buf.getvalue())

    def test_http_error_is_reported_without_live_call(self):
        opener = FakeOpener([(401, b'{"error":"nope"}')])
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            with tempfile.TemporaryDirectory() as tmp:
                code = far.main(
                    [
                        "--asins",
                        "B0DPDRNSXV",
                        "--out",
                        str(Path(tmp) / "x.json"),
                        "--accept-risk",
                        "--cache-dir",
                        str(Path(tmp) / "cache"),
                    ],
                    opener=opener,
                    environ={"SCRAPINGBEE_API_KEY": "bad-key"},
                )
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("HTTP 401", buf.getvalue())
        self.assertNotIn("bad-key", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
