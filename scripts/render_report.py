#!/usr/bin/env python3
"""Fill a language-matched report template from a JSON facts file and validate it."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATHS = {
    "en": REPO_ROOT / "templates" / "report.md",
    "zh": REPO_ROOT / "templates" / "report.zh.md",
}

CANONICAL_VERDICTS = {
    "worth a small-scale test",
    "reject",
    "insufficient evidence — stop for now",
}

VERDICT_ALIASES = {
    "worth a small-scale test": "worth a small-scale test",
    "reject": "reject",
    "insufficient evidence — stop for now": "insufficient evidence — stop for now",
    "insufficient evidence – stop for now": "insufficient evidence — stop for now",
    "insufficient evidence - stop for now": "insufficient evidence — stop for now",
    "值得小规模测试": "worth a small-scale test",
    "淘汰": "reject",
    "证据不足先停": "insufficient evidence — stop for now",
}

VERDICT_DISPLAY = {
    "en": {
        "worth a small-scale test": "worth a small-scale test",
        "reject": "reject",
        "insufficient evidence — stop for now": "insufficient evidence — stop for now",
    },
    "zh": {
        "worth a small-scale test": "值得小规模测试",
        "reject": "淘汰",
        "insufficient evidence — stop for now": "证据不足先停",
    },
}

MODE_DISPLAY = {
    "en": {"recommend": "recommend", "reverse": "reverse"},
    "zh": {"recommend": "推荐选品", "reverse": "反推评估"},
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
    "desk",
    "suppliers",
    "test",
    "gaps",
    "sources",
    "inputs",
    "markets",
)

SECTION_KEYS = (
    "gate0",
    "pain",
    "demand",
    "form",
    "logistics",
    "vacuum",
    "competitors",
    "positioning",
    "desk",
    "suppliers",
    "test",
    "gaps",
    "sources",
)

GATE_NUMBERS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "8b", "9")
LEGACY_GATE_ALIASES = {"8a": "8"}
STATUSES_COMMON = {"pass", "fail", "unverified", "not_evaluated"}
STATUSES_GATE7 = {"complete", "incomplete", "not_evaluated"}
STATUSES_GATE0 = {"complete", "incomplete", "not_evaluated", "skipped"}
STATUSES_GATE8B = {"pending", "complete", "fail", "not_evaluated", "not_sent"}
STATUSES_GATE9 = {"pass", "fail", "unverified", "not_evaluated", "entered", "not_entered"}

NOT_EVALUATED_PREFIX = "Not evaluated — stopped at gate"


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("facts file must be a JSON object")
    return data


def normalize_verdict(value: object) -> str:
    text = " ".join(str(value or "").strip().split())
    if text in VERDICT_ALIASES:
        return VERDICT_ALIASES[text]
    collapsed = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )
    for raw, canonical in VERDICT_ALIASES.items():
        if raw.replace("–", "-").replace("—", "-").replace("−", "-") == collapsed:
            return canonical
    return text


def as_inline(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [as_inline(item) for item in value if as_inline(item)]
        return "; ".join(parts)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            rendered = as_inline(item)
            if rendered:
                parts.append(f"{_label(key)}: {rendered}")
        return "; ".join(parts)
    return str(value).strip()


def _label(key: str) -> str:
    return str(key).replace("_", " ")


def as_block(value) -> str:
    if value is None:
        return "Unverified."
    if isinstance(value, list):
        items = [item for item in value if as_inline(item) or isinstance(item, (list, dict))]
        if not items:
            return "Unverified."
        lines: list[str] = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f"- {as_inline(item)}")
            elif isinstance(item, list):
                lines.append(f"- {as_inline(item)}")
            else:
                lines.append(f"- {str(item).strip()}")
        return "\n".join(lines)
    if isinstance(value, dict):
        if not value:
            return "Unverified."
        if set(value.keys()) <= {"status", "stopped_at", "note"} and value.get("status") in {
            "not_evaluated",
            "skipped",
            "not_entered",
        }:
            note = str(value.get("note") or "").strip()
            if note:
                return note
            stopped = value.get("stopped_at")
            if stopped is not None:
                return f"{NOT_EVALUATED_PREFIX} {stopped}"
            if value.get("status") == "skipped":
                return "Skipped — a category, audience, or pain was already given."
            if value.get("status") == "not_entered":
                return "Not entered."
            return f"{NOT_EVALUATED_PREFIX} ?"
        lines = []
        for key, item in value.items():
            if isinstance(item, list):
                rendered = as_block(item)
                if "\n" in rendered:
                    lines.append(f"- {_label(key)}:")
                    for row in rendered.splitlines():
                        lines.append(f"  {row}")
                else:
                    lines.append(f"- {_label(key)}: {rendered.removeprefix('- ')}")
            elif isinstance(item, dict):
                lines.append(f"- {_label(key)}:")
                for row in as_block(item).splitlines():
                    lines.append(f"  {row}")
            else:
                text = str(item).strip() if item is not None else ""
                lines.append(f"- {_label(key)}: {text if text else 'Unverified.'}")
        return "\n".join(lines) if lines else "Unverified."
    text = str(value).strip()
    return text if text else "Unverified."


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not any(not is_blank(item) for item in value)
    if isinstance(value, dict):
        return not any(not is_blank(item) for item in value.values())
    return False


def nested_get(data: dict, *keys: str):
    for key in keys:
        if key in data and not is_blank(data[key]):
            return data[key]
    positioning = data.get("positioning")
    if isinstance(positioning, dict):
        for key in keys:
            if key in positioning and not is_blank(positioning[key]):
                return positioning[key]
    return None


def normalize_gate_key(number: object) -> str:
    key = str(number).strip().lower()
    return LEGACY_GATE_ALIASES.get(key, key)


def alias_keys(number: str) -> list[str]:
    number = normalize_gate_key(number)
    keys = [number]
    for alias, canonical in LEGACY_GATE_ALIASES.items():
        if canonical == number and alias not in keys:
            keys.append(alias)
    return keys


def lookup_raw(gates: dict, number: str):
    for key in alias_keys(number):
        if key in gates:
            return gates[key]
        if key.isdigit() and int(key) in gates:
            return gates[int(key)]
    return None


def lookup_status(gates: dict, number: str) -> str:
    raw = lookup_raw(gates, number)
    if raw is None:
        return ""
    if isinstance(raw, dict):
        return str(raw.get("status") or "").strip().lower()
    return str(raw or "").strip().lower()


def allowed_statuses(number: str) -> set[str]:
    number = normalize_gate_key(number)
    if number == "0":
        return STATUSES_GATE0
    if number == "7":
        return STATUSES_GATE7
    if number == "8b":
        return STATUSES_GATE8B
    if number == "9":
        return STATUSES_GATE9
    return STATUSES_COMMON


def section_is_not_evaluated(value) -> bool:
    text = as_block(value)
    return text.startswith("Not evaluated") or text.startswith("未评估")


def _status_text(raw) -> str:
    if isinstance(raw, dict):
        return str(raw.get("status") or "").strip().lower()
    return str(raw or "").strip().lower()


def normalize_facts(data: dict) -> dict:
    """Accept older field names: compliance, 8a, shelf_price_sketch, desk.trademark_search."""
    if "desk" not in data and "compliance" in data:
        data["desk"] = data["compliance"]
    gates = data.get("gates")
    if isinstance(gates, dict):
        if "8" not in gates and "8a" in gates:
            gates["8"] = gates["8a"]
    desk = data.get("desk")
    if isinstance(desk, dict):
        sketch = desk.get("shelf_price_sketch")
        if is_blank(desk.get("competitor_price_benchmark")) and not is_blank(sketch):
            desk["competitor_price_benchmark"] = sketch
            desk.pop("shelf_price_sketch", None)
        elif not is_blank(desk.get("competitor_price_benchmark")) and desk.get(
            "competitor_price_benchmark"
        ) == sketch:
            desk.pop("shelf_price_sketch", None)
        trademark = desk.pop("trademark_search", None)
        if not is_blank(trademark):
            launch = data.get("brand_launch")
            if is_blank(launch):
                data["brand_launch"] = {
                    "trademark_search": trademark,
                    "note": (
                        "Moved from desk notes. Official trademark search is "
                        "optional, happens after a product is picked, and does "
                        "not affect the selection verdict."
                    ),
                }
            elif isinstance(launch, dict) and is_blank(launch.get("trademark_search")):
                launch["trademark_search"] = trademark
            elif isinstance(launch, str):
                data["brand_launch"] = {
                    "note": launch,
                    "trademark_search": trademark,
                }
    return data


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    normalize_facts(data)
    missing = [key for key in REQUIRED_FIELDS if key not in data]
    if missing:
        errors.append("missing fields: " + ", ".join(missing))

    language = str(data.get("language") or "en").strip().lower()
    if language not in TEMPLATE_PATHS:
        errors.append(
            "language must be 'en' or 'zh' for the shipped templates; "
            "write other languages from the English template by hand"
        )

    mode = str(data.get("mode") or "").strip().lower()
    if not mode:
        errors.append("mode must be 'recommend' or 'reverse' (empty is not allowed)")
    elif mode not in {"recommend", "reverse"}:
        errors.append("mode must be 'recommend' or 'reverse'")

    raw_verdict = str(data.get("verdict") or "").strip()
    verdict = normalize_verdict(raw_verdict)
    if not raw_verdict:
        errors.append(
            "verdict must be exactly one of: "
            + " | ".join(sorted(CANONICAL_VERDICTS))
            + " (empty is not allowed)"
        )
    elif verdict not in CANONICAL_VERDICTS:
        errors.append(
            "verdict must be exactly one of: "
            + " | ".join(sorted(CANONICAL_VERDICTS))
            + f" (got {raw_verdict!r})"
        )

    for key in ("inputs", "markets", "rationale"):
        if key in data and is_blank(data.get(key)):
            errors.append(f"{key} must not be empty")

    # claims and aesthetic reference are required unless gate 7 was not reached
    gates = data.get("gates")
    gate7 = ""
    if isinstance(gates, dict):
        gate7 = lookup_status(gates, "7")
        unknown_keys = [
            str(k) for k in gates
            if normalize_gate_key(k) not in GATE_NUMBERS
        ]
        if unknown_keys:
            errors.append("unknown gate keys: " + ", ".join(unknown_keys))
        if "8" in gates and "8a" in gates:
            left, right = _status_text(gates["8"]), _status_text(gates["8a"])
            if left and right and left != right:
                errors.append(
                    "gates.8 and legacy gates.8a disagree "
                    f"({left!r} vs {right!r}); use a single status for the desk check"
                )
        for number in gates:
            status = lookup_status(gates, str(number))
            if not status:
                errors.append(f"gates.{number} is missing a status")
            elif status not in allowed_statuses(str(number)):
                allowed = ", ".join(sorted(allowed_statuses(str(number))))
                errors.append(f"gates.{number} status must be one of: {allowed} (got {status!r})")
    elif gates is not None:
        errors.append("gates must be an object keyed by gate number")

    needs_positioning_details = gate7 not in {"not_evaluated", "skipped"}
    if needs_positioning_details:
        if is_blank(nested_get(data, "aesthetic_reference", "cross_category_aesthetic_reference")):
            errors.append("aesthetic_reference is required unless gate 7 is not_evaluated")
        if is_blank(nested_get(data, "claims", "claim_boundaries")):
            errors.append("claims (claim boundaries) are required unless gate 7 is not_evaluated")

    if isinstance(gates, dict) and verdict in CANONICAL_VERDICTS:
        statuses = {n: lookup_status(gates, n) for n in GATE_NUMBERS if lookup_status(gates, n)}
        reject_fails = any(
            statuses.get(n) == "fail" for n in ("1", "2", "3", "5", "6")
        ) or statuses.get("4") == "fail" or statuses.get("8") == "fail" or statuses.get("8b") == "fail"
        must_have_unverified = [
            n for n in GATE_NUMBERS
            if n != "8b" and statuses.get(n) == "unverified"
        ]
        has_unverified = bool(must_have_unverified) or statuses.get("7") == "incomplete" or statuses.get("0") == "incomplete"
        early_pass = all(statuses.get(n) == "pass" for n in ("1", "2", "3", "4", "5", "6", "8"))
        gate7_complete = statuses.get("7") == "complete"
        gate8b = statuses.get("8b")
        if verdict == "worth a small-scale test":
            if not (early_pass and gate7_complete):
                errors.append(
                    "verdict 'worth a small-scale test' requires gates 1–7 to pass "
                    "(gate 7 complete) and gate 8 to pass; gate 8b may be pending "
                    "and gate 9 may be not entered; trademark search is optional "
                    "and must not affect this verdict"
                )
            elif gate8b not in {"pending", "not_sent", "complete"}:
                errors.append(
                    "verdict 'worth a small-scale test' requires gate 8b to be "
                    "pending, not_sent, or complete (attach the RFQ; do not treat "
                    "a pending quote as unverified)"
                )
        elif verdict == "reject":
            if not reject_fails:
                errors.append(
                    "verdict 'reject' requires at least one fail among gates 1–6, 8, or 8b"
                )
        elif verdict == "insufficient evidence — stop for now":
            if reject_fails:
                errors.append(
                    "a reject-level fail is present; verdict must be 'reject', "
                    "not 'insufficient evidence — stop for now'"
                )
            elif not has_unverified:
                if early_pass and gate7_complete:
                    errors.append(
                        "gates 1–7 and 8 all passed, so the verdict cannot be "
                        "'insufficient evidence — stop for now' (gate 8b may stay pending; "
                        "a missing trademark search does not count as insufficient evidence)"
                    )
                elif not statuses:
                    errors.append(
                        "verdict 'insufficient evidence — stop for now' needs a gates object "
                        "with at least one unverified or incomplete must-have gate"
                    )

        stopper = None
        for n in ("0", "1", "2", "3", "4"):
            st = statuses.get(n)
            if st in {"fail", "unverified", "incomplete"}:
                stopper = n
                break
        if stopper is None:
            for n in ("5", "6", "7"):
                st = statuses.get(n)
                if st in {"fail", "unverified", "incomplete"}:
                    stopper = n
                    break
        if stopper is None and statuses.get("8") in {"fail", "unverified"}:
            stopper = "8"
        if stopper is not None:
            if stopper in {"5", "6", "7"}:
                blocked = ("8", "8b", "9")
            elif stopper == "8":
                blocked = ("8b", "9")
            else:
                blocked = ("5", "6", "7", "8", "8b", "9")
            for n in blocked:
                st = statuses.get(n)
                if st and st not in {"not_evaluated", "not_entered"}:
                    errors.append(
                        f"gates.{n} must be not_evaluated (or not_entered) because the run "
                        f"stopped at gate {stopper}"
                    )

    return errors


def format_date(data: dict) -> str:
    if data.get("date"):
        return str(data["date"])
    timezone = str(data.get("timezone") or "Asia/Shanghai")
    try:
        now = datetime.now(ZoneInfo(timezone))
        return f"{now.strftime('%Y-%m-%d %H:%M %z')} ({timezone})"
    except Exception:
        now = datetime.now().astimezone()
        return f"{now.strftime('%Y-%m-%d %H:%M %z')} (local)"


def gate_status_block(data: dict, language: str) -> str:
    gates = data.get("gates")
    if not isinstance(gates, dict) or not gates:
        return "Unverified." if language == "en" else "未核实。"
    labels = {
        "en": {n: f"Gate {n}" for n in GATE_NUMBERS},
        "zh": {n: f"第 {n} 关" for n in GATE_NUMBERS},
    }[language]
    status_zh = {
        "pass": "通过",
        "fail": "未通过",
        "unverified": "未核实",
        "complete": "已完成",
        "incomplete": "未完成",
        "not_evaluated": "未评估",
        "skipped": "跳过",
        "entered": "已进入",
        "not_entered": "未进入",
        "pending": "待询价",
        "not_sent": "未发出",
    }
    lines = []
    for n in GATE_NUMBERS:
        status = lookup_status(gates, n)
        if not status:
            continue
        shown = status if language == "en" else status_zh.get(status, status)
        raw = lookup_raw(gates, n)
        extra = ""
        if isinstance(raw, dict) and raw.get("note"):
            extra = f" — {raw['note']}"
        lines.append(f"- {labels[n]}: {shown}{extra}")
    return "\n".join(lines) if lines else ("Unverified." if language == "en" else "未核实。")


def default_gate0(data: dict, language: str) -> str:
    if not is_blank(data.get("gate0")):
        return as_block(data.get("gate0"))
    gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}
    status = lookup_status(gates, "0") if gates else "skipped"
    if status in {"skipped", ""}:
        return (
            "Skipped — a category, audience, or pain was already given."
            if language == "en"
            else "已跳过——用户已给出赛道、人群或痛点。"
        )
    return as_block({"status": status, "note": data.get("gate0")})


def default_channel_coverage(data: dict, language: str) -> str:
    value = data.get("channel_coverage")
    if is_blank(value) and isinstance(data.get("channels"), (dict, list, str)):
        value = data.get("channels")
    if not is_blank(value):
        return as_block(value)
    if language == "zh":
        return (
            "此份事实文件未记录渠道覆盖。正式报告须写明 Reddit、TikTok、YouTube "
            "和 Amazon 美/英/澳哪些实际拿到了数据、哪些失败。"
            "缺必须证据时应改为「证据不足先停」，不要把未核过的关卡写成通过。"
        )
    return (
        "Not recorded in this facts file. For a real run, list which of Reddit, "
        "TikTok, YouTube, and Amazon US/UK/AU actually returned data and which "
        "failed. Missing must-have evidence means insufficient evidence — stop "
        "for now, not a guessed pass."
    )


def default_review_source(data: dict, language: str) -> str:
    value = data.get("review_source")
    if is_blank(value) and not is_blank(data.get("amazon_review_source")):
        value = data.get("amazon_review_source")
    if not is_blank(value):
        return as_block(value)
    if language == "zh":
        return (
            "此份事实文件未记录评论来源。正式报告须写明用的是公开 “Customers say” "
            "与精选评论、登录后的浏览器 2–3 星筛选、卖家工具（Helium 10 / Jungle Scout / "
            "Sellersprite），还是用户自愿启用的抓取脚本，以及覆盖是否不完整。"
        )
    return (
        "Not recorded in this facts file. For a real run, state which Amazon "
        "review source was used (public Customers say / featured reviews, "
        "manual signed-in browser, a seller tool such as Helium 10, Jungle "
        "Scout, or Sellersprite, or an opt-in scraper) and whether coverage "
        "is partial."
    )


def default_brand_launch(data: dict, language: str) -> str:
    if not is_blank(data.get("brand_launch")):
        return as_block(data.get("brand_launch"))
    if language == "zh":
        return (
            "可选，不影响选品结论。品选定之后，如需启用某个品牌名，再在目标市场的"
            "官方商标库检索（美国 USPTO、英国 UK IPO、澳大利亚 IP Australia；"
            "如包含加拿大、新西兰或爱尔兰/欧盟，再查 CIPO、IPONZ 或 EUIPO）。"
            "检索完成也不等于法律意见。在此之前，候选名都是未检索的想法。"
        )
    return (
        "Optional, and not part of the selection verdict. After you pick a product, "
        "search any name you actually want to use on the official trademark offices "
        "for your markets (USPTO, UK IPO, IP Australia, and CIPO, IPONZ, or EUIPO "
        "when those markets are in the run). Completing a search is not a legal "
        "opinion. Candidate names stay uncleared until then."
    )


def render(data: dict) -> str:
    normalize_facts(data)
    language = str(data.get("language") or "en").strip().lower() or "en"
    template_path = TEMPLATE_PATHS.get(language, TEMPLATE_PATHS["en"])
    template = template_path.read_text(encoding="utf-8")
    verdict = normalize_verdict(data.get("verdict"))
    display_verdict = VERDICT_DISPLAY.get(language, VERDICT_DISPLAY["en"]).get(verdict, verdict)
    mode = str(data.get("mode") or "").strip().lower()
    display_mode = MODE_DISPLAY.get(language, MODE_DISPLAY["en"]).get(mode, mode)
    markets = as_inline(data.get("markets"))
    inputs = as_inline(data.get("inputs"))
    replacements = {
        "date": format_date(data),
        "language": language,
        "mode": display_mode,
        "markets": markets,
        "inputs": inputs,
        "verdict": display_verdict,
        "rationale": as_block(data.get("rationale")),
        "gate0": default_gate0(data, language),
        "pain": as_block(data.get("pain")),
        "demand": as_block(data.get("demand")),
        "form": as_block(data.get("form")),
        "logistics": as_block(data.get("logistics")),
        "vacuum": as_block(data.get("vacuum")),
        "competitors": as_block(data.get("competitors")),
        "positioning": as_block(data.get("positioning")),
        "desk": as_block(data.get("desk")),
        "suppliers": as_block(data.get("suppliers")),
        "brand_launch": default_brand_launch(data, language),
        "test": as_block(data.get("test")),
        "gate_status": gate_status_block(data, language),
        "channel_coverage": default_channel_coverage(data, language),
        "review_source": default_review_source(data, language),
        "gaps": as_block(data.get("gaps")),
        "sources": as_block(data.get("sources")),
    }
    out = template
    for key, value in replacements.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = [part for part in out.split("{{")[1:] if "}}" in part]
    if leftover:
        names = ", ".join(part.split("}}", 1)[0] for part in leftover)
        raise ValueError(f"unfilled template placeholders: {names}")
    return out if out.endswith("\n") else out + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a facts JSON file and write a conclusion report."
    )
    parser.add_argument("--input", required=True, help="Path to a JSON object of report facts.")
    parser.add_argument("--out", required=True, help="Path to write the Markdown report.")
    parser.add_argument(
        "--lang",
        default=None,
        help="Report language: en or zh. Overrides facts.language. Default: English.",
    )
    args = parser.parse_args(argv)

    path = Path(args.input)
    try:
        data = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: cannot read facts: {exc}", file=sys.stderr)
        return 2

    normalize_facts(data)
    if args.lang:
        data["language"] = args.lang.strip().lower()
    else:
        data.setdefault("language", "en")

    errors = validate(data)
    if errors:
        for item in errors:
            print(f"error: {item}", file=sys.stderr)
        return 2

    try:
        text = render(data)
    except (OSError, ValueError) as exc:
        print(f"error: cannot render report: {exc}", file=sys.stderr)
        return 2

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
