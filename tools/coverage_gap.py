#!/usr/bin/env python3
"""Analyze j2cs rule coverage and rank semantic workstream gaps."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RULES_ROOT = ROOT / "rules"
DEFAULT_CATALOG = ROOT / "coverage" / "catalog.json"


@dataclass
class Rule:
    path: str
    id: str
    category: str
    strategy: str
    confidence: str
    helper: str | None
    tests: int


def load_rules() -> list[Rule]:
    rules: list[Rule] = []
    for path in sorted(RULES_ROOT.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rules.append(
            Rule(
                path=str(path.relative_to(ROOT)),
                id=data["id"],
                category=data["category"],
                strategy=data["strategy"],
                confidence=data["confidence"],
                helper=data.get("target", {}).get("helper"),
                tests=len(data.get("tests", [])),
            )
        )
    return rules


def load_catalog(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("workstreams"), list):
        raise ValueError("coverage catalog must contain version=1 and workstreams[]")
    return data


def helper_root(helper: str | None) -> str | None:
    return helper.split(".", 1)[0] if helper else None


def matches(rule: Rule, target: dict[str, Any]) -> bool:
    match = target.get("match", {})
    categories = set(match.get("categories", []))
    category_prefixes = tuple(match.get("category_prefixes", []))
    prefixes = tuple(match.get("id_prefixes", []))
    exact_ids = set(match.get("ids", []))
    return (
        rule.category in categories
        or (bool(category_prefixes) and rule.category.startswith(category_prefixes))
        or rule.id in exact_ids
        or (bool(prefixes) and rule.id.startswith(prefixes))
    )


def analyze(rules: list[Rule], catalog: dict[str, Any]) -> dict[str, Any]:
    category_counts = Counter(r.category for r in rules)
    strategy_counts = Counter(r.strategy for r in rules)
    confidence_counts = Counter(r.confidence for r in rules)
    helper_counts = Counter(helper_root(r.helper) for r in rules if helper_root(r.helper))

    targets: list[dict[str, Any]] = []
    for target in catalog["workstreams"]:
        matched = [r for r in rules if matches(r, target)]
        strategies = Counter(r.strategy for r in matched)
        confidences = Counter(r.confidence for r in matched)
        min_rules = int(target.get("minimum_rules", 1))
        count = len(matched)
        completeness = min(count / max(min_rules, 1), 1.0)

        required_prefixes = list(target.get("required_id_prefixes", []))
        missing_prefixes = [
            prefix
            for prefix in required_prefixes
            if not any(r.id.startswith(prefix) for r in matched)
        ]

        runtime_ratio = strategies["runtime"] / count if count else 0.0
        uncertain_ratio = (
            (confidences["low"] + confidences["medium"]) / count if count else 0.0
        )
        threshold = float(target.get("runtime_heavy_threshold", 0.75))

        if count == 0:
            status = "missing"
        elif count < min_rules or missing_prefixes:
            status = "thin"
        elif runtime_ratio >= threshold:
            status = "runtime-heavy"
        else:
            status = "covered"

        score = float(target.get("priority", 50))
        if count == 0:
            score += 60
        score += (1.0 - completeness) * 35
        score += min(len(missing_prefixes), 8) * 7
        if count >= 5 and runtime_ratio >= threshold:
            score += 18
        if count >= 5 and uncertain_ratio >= 0.30:
            score += 8
        if status == "covered":
            score -= 35

        targets.append(
            {
                "workstream": target["id"],
                "title": target.get("title", target["id"]),
                "priority": target.get("priority", 50),
                "status": status,
                "score": round(score, 2),
                "rules": count,
                "minimum_rules": min_rules,
                "completeness": round(completeness, 4),
                "strategies": dict(strategies),
                "confidences": dict(confidences),
                "runtime_ratio": round(runtime_ratio, 4),
                "uncertain_ratio": round(uncertain_ratio, 4),
                "missing_id_prefixes": missing_prefixes,
                "scope": target.get("scope", []),
                "ownership_notes": target.get("ownership_notes", []),
                "matched_rule_ids": [r.id for r in matched],
                "test_count": sum(r.tests for r in matched),
                "helper_roots": sorted(
                    {
                        root
                        for root in (helper_root(r.helper) for r in matched)
                        if root
                    }
                ),
            }
        )

    targets.sort(key=lambda x: (-x["score"], x["workstream"]))
    return {
        "summary": {
            "rule_count": len(rules),
            "category_count": len(category_counts),
            "categories": dict(sorted(category_counts.items())),
            "strategies": dict(strategy_counts),
            "confidences": dict(confidence_counts),
            "helper_roots": dict(helper_counts.most_common()),
        },
        "workstreams": targets,
    }


def issue_body(item: dict[str, Any]) -> str:
    why = [
        f"- Matching rules: **{item['rules']}** (catalog target: {item['minimum_rules']})",
        f"- Coverage status: **{item['status']}**",
        f"- Gap score: **{item['score']}**",
    ]
    if item["missing_id_prefixes"]:
        why.append(
            "- Missing semantic surfaces: "
            + ", ".join(f"`{p}*`" for p in item["missing_id_prefixes"])
        )
    if item["rules"]:
        why.append(f"- Runtime ratio: **{item['runtime_ratio']:.0%}**")

    scope = "\n".join(f"- {x}" for x in item["scope"]) or (
        "- Refine this workstream from current repository coverage."
    )
    ownership = "\n".join(f"- {x}" for x in item["ownership_notes"]) or (
        "- Reuse canonical helpers and avoid duplicate semantic ownership."
    )

    return (
        f"WORKSTREAM: {item['workstream']}\n"
        "STATUS: READY\n"
        "AUTO_GENERATED: coverage-gap-v1\n\n"
        "## Why selected\n"
        + "\n".join(why)
        + "\n\n## Scope\n"
        + scope
        + "\n\n## Ownership notes\n"
        + ownership
        + "\n\n## Completion\n"
        "Follow `prompts/worker.md`, claim via `work/issue-<ISSUE_NUMBER>`, "
        "validate, and open a PR with `Closes #<ISSUE_NUMBER>`.\n"
    )


def render_markdown(report: dict[str, Any], top: int) -> str:
    summary = report["summary"]
    lines = [
        "# j2cs Coverage Gap Report",
        "",
        f"- Rules: **{summary['rule_count']}**",
        f"- Categories: **{summary['category_count']}**",
        f"- Strategies: `{json.dumps(summary['strategies'], sort_keys=True)}`",
        "",
        "## Ranked gaps",
        "",
        "| Rank | Workstream | Status | Score | Rules / Target | Runtime | Missing surfaces |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for i, item in enumerate(report["workstreams"][:top], 1):
        missing = ", ".join(item["missing_id_prefixes"][:5])
        if len(item["missing_id_prefixes"]) > 5:
            missing += ", …"
        lines.append(
            f"| {i} | `{item['workstream']}` | {item['status']} | {item['score']:.1f} | "
            f"{item['rules']} / {item['minimum_rules']} | {item['runtime_ratio']:.0%} | "
            f"{missing or '—'} |"
        )

    lines += ["", "## Existing category counts", ""]
    for category, count in summary["categories"].items():
        lines.append(f"- `{category}`: {count}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--issues-out", type=Path)
    args = parser.parse_args()

    rules = load_rules()
    if not rules:
        raise SystemExit("No rules found.")

    report = analyze(rules, load_catalog(args.catalog))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(
            render_markdown(report, args.top), encoding="utf-8"
        )

    candidates = [
        {
            **x,
            "issue_title": f"WORKSTREAM: {x['workstream']}",
            "issue_body": issue_body(x),
        }
        for x in report["workstreams"]
        if x["status"] != "covered"
    ]
    if args.issues_out:
        args.issues_out.parent.mkdir(parents=True, exist_ok=True)
        args.issues_out.write_text(
            json.dumps(candidates[: args.top], indent=2) + "\n",
            encoding="utf-8",
        )

    print(render_markdown(report, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
