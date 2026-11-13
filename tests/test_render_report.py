#!/usr/bin/env python3
"""Render-report checks for channel coverage and review source."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_report as rr  # noqa: E402

EXAMPLE = json.loads((ROOT / "examples" / "facts.example.json").read_text(encoding="utf-8"))


class RenderCoverageTests(unittest.TestCase):
    def test_example_en_and_zh_include_new_sections(self):
        en = deepcopy(EXAMPLE)
        errors = rr.validate(en)
        self.assertEqual(errors, [])
        text = rr.render(en)
        self.assertIn("## Channel coverage", text)
        self.assertIn("## Review source", text)
        self.assertIn("public Customers say and featured reviews", text)
        self.assertIn("worth a small-scale test", text)

        zh = deepcopy(EXAMPLE)
        zh["language"] = "zh"
        text_zh = rr.render(zh)
        self.assertIn("## 渠道覆盖", text_zh)
        self.assertIn("## 评论来源", text_zh)
        self.assertIn("值得小规模测试", text_zh)

    def test_missing_coverage_fields_still_validate(self):
        data = deepcopy(EXAMPLE)
        data.pop("channel_coverage")
        data.pop("review_source")
        errors = rr.validate(data)
        self.assertEqual(errors, [])
        text = rr.render(data)
        self.assertIn("Not recorded in this facts file", text)
        self.assertIn("insufficient evidence", text.lower())
        data["language"] = "zh"
        text_zh = rr.render(data)
        self.assertIn("未记录渠道覆盖", text_zh)
        self.assertIn("未记录评论来源", text_zh)

    def test_channel_alias_accepted(self):
        data = deepcopy(EXAMPLE)
        data.pop("channel_coverage")
        data["channels"] = {"amazon": "returned", "reddit": "failed"}
        data.pop("review_source")
        data["amazon_review_source"] = "manual signed-in browser; coverage partial"
        self.assertEqual(rr.validate(data), [])
        text = rr.render(data)
        self.assertIn("amazon: returned", text)
        self.assertIn("manual signed-in browser", text)

    def test_cli_writes_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.md"
            code = rr.main(
                [
                    "--input",
                    str(ROOT / "examples" / "facts.example.json"),
                    "--out",
                    str(out),
                    "--lang",
                    "en",
                ]
            )
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
