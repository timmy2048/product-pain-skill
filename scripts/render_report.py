#!/usr/bin/env python3
"""Fill templates/report.md from a JSON facts file and refuse unknown verdicts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ALLOWED_VERDICTS = {
    "worth a small-scale test",
    "reject",
    "insufficient evidence — stop for now",
}

REQUIRED_FIELDS = (
    "mode",
    "verdict",
    "rationale",
    "pain",
    "demand",
    "form",
    "logistics",
    "vacuum",
    "competitors",
    "positioning",
    "compliance",
    "test",
    "gaps",
    "sources",
)

TEMPLATE_REL = Path(__file__).resolve().parent.parent / "templates" / "report.md"


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("facts file must be a JSON object")
    return data


def as_block(value) -> str:
    if value is None:
        return "Unverified."
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return "\n".join(f"- {item}" for item in items) if items else "Unverified."
    text = str(value).strip()
    return text if text else "Unverified."


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    missing = [key for key in REQUIRED_FIELDS if key not in data]
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    mode = str(data.get("mode", "")).strip().lower()
    if mode and mode not in {"recommend", "reverse"}:
        errors.append("mode must be 'recommend' or 'reverse'")
    verdict = str(data.get("verdict", "")).strip()
    if verdict and verdict not in ALLOWED_VERDICTS:
        errors.append(
            "verdict must be exactly one of: " + " | ".join(sorted(ALLOWED_VERDICTS))
        )
    return errors


def render(data: dict) -> str:
    timezone = str(data.get("timezone") or "Asia/Shanghai")
    try:
        now = datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        timezone = "unspecified"
    date_line = data.get("date") or f"{now} ({timezone})"
    markets = data.get("markets") or "English-speaking D2C (default US, UK, AU)"
    if isinstance(markets, list):
        markets_line = ", ".join(str(m) for m in markets)
    else:
        markets_line = str(markets)
    inputs = data.get("inputs") or "See body."
    return f"""# Product pain report

- Date (timezone): {date_line}
- Mode: {data.get("mode")}
- Target markets: {markets_line}
- Inputs and defaults used: {as_block(inputs)}

## Verdict

{data.get("verdict")}

{as_block(data.get("rationale"))}

## 1. Pain statement

{as_block(data.get("pain"))}

## 2. Demand evidence

{as_block(data.get("demand"))}

## 3. Product form

{as_block(data.get("form"))}

## 4. Logistics and education cost

{as_block(data.get("logistics"))}

## 5. Brand vacuum

{as_block(data.get("vacuum"))}

## 6. Competitors and difference

{as_block(data.get("competitors"))}

## 7. Positioning and names

{as_block(data.get("positioning"))}

## 8. Compliance, IP, supply chain, unit economics

{as_block(data.get("compliance"))}

## 9. Small-scale test

{as_block(data.get("test"))}

## Open gaps

{as_block(data.get("gaps"))}

## Sources

{as_block(data.get("sources"))}
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a facts JSON file and write a conclusion report."
    )
    parser.add_argument("--input", required=True, help="Path to a JSON object of report facts.")
    parser.add_argument("--out", required=True, help="Path to write the Markdown report.")
    args = parser.parse_args(argv)

    path = Path(args.input)
    try:
        data = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: cannot read facts: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for item in errors:
            print(f"error: {item}", file=sys.stderr)
        return 2

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(data), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
