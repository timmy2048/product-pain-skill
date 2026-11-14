#!/usr/bin/env python3
"""URL-helper checks for Google Ads Transparency search URLs."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_search_urls as urls  # noqa: E402


class GoogleAdsUrlTests(unittest.TestCase):
    def test_search_url_uses_only_observed_params(self):
        url = urls.google_ads_search_url("Chomper Labs", "US")
        self.assertEqual(
            url,
            "https://adstransparency.google.com/search?region=US&query=Chomper+Labs",
        )
        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "adstransparency.google.com")
        self.assertEqual(parsed.path, "/search")
        self.assertEqual(parse_qs(parsed.query), {"region": ["US"], "query": ["Chomper Labs"]})

    def test_render_includes_start_pages_and_fallback_rule(self):
        text = urls.render_markdown(["retainer cleaner"], ["us"], [])
        self.assertIn("## Google Ads Transparency Center (gate 5)", text)
        self.assertIn("- Home: https://adstransparency.google.com/", text)
        self.assertIn("- Search: https://adstransparency.google.com/search", text)
        self.assertIn("Search the domain first", text)
        self.assertIn("no ads found", text)
        self.assertIn("region=US", text)
        self.assertNotIn("adstransparency.google.com/search?region=US&query=", text)

    def test_render_emits_observed_search_urls_for_domains(self):
        text = urls.render_markdown(
            ["retainer cleaner"],
            ["us", "uk", "au"],
            ["https://www.chomperlabs.com/fizzies"],
        )
        expected = (
            "- chomperlabs.com (US): "
            "https://adstransparency.google.com/search?region=US&query=chomperlabs.com"
        )
        self.assertIn(expected, text)
        # Do not invent region codes for UK/AU or Anywhere.
        self.assertNotIn("region=UK", text)
        self.assertNotIn("region=GB", text)
        self.assertNotIn("region=AU", text)
        self.assertNotIn("region=anywhere", text)
        self.assertIn("https://www.similarweb.com/website/chomperlabs.com/", text)

    def test_normalize_domain_strips_scheme_and_www(self):
        self.assertEqual(urls.normalize_domain("https://www.ChomperLabs.com/path"), "chomperlabs.com")
        self.assertEqual(urls.normalize_domain("chomperlabs.com"), "chomperlabs.com")


if __name__ == "__main__":
    unittest.main()
