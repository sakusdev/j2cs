#!/usr/bin/env python3

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "rule.schema.json"
RULES_ROOT = ROOT / "rules"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    failures = 0
    rule_ids: dict[str, Path] = {}
    files = sorted(RULES_ROOT.rglob("*.json"))

    if not files:
        print("No rule files found.")
        return 1

    for path in files:
        rel = path.relative_to(ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR {rel}: invalid JSON: {exc}")
            failures += 1
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        if errors:
            for error in errors:
                where = ".".join(str(p) for p in error.absolute_path) or "<root>"
                print(f"ERROR {rel}:{where}: {error.message}")
            failures += len(errors)
            continue

        rule_id = data["id"]
        if rule_id in rule_ids:
            print(f"ERROR {rel}: duplicate id '{rule_id}' also used by {rule_ids[rule_id].relative_to(ROOT)}")
            failures += 1
        else:
            rule_ids[rule_id] = path
            print(f"OK    {rel} ({rule_id})")

    print(f"\nValidated {len(files)} rule file(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
