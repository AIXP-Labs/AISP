#!/usr/bin/env python3
"""Check a research-result envelope from stdin; not grounding or full schema validation."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def strict_json_loads(text: str) -> Any:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    def reject(value):
        raise ValueError(f"non-JSON numeric constant: {value}")

    return json.loads(text, object_pairs_hook=unique, parse_constant=reject)


def check_result(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["research_result must be an object"]
    errors = []
    if value.get("status") not in ("complete", "incomplete"):
        errors.append("status must be complete or incomplete")
    for field in ("findings", "citations"):
        if not isinstance(value.get(field), list):
            errors.append(f"{field} must be an array")
    for finding in value.get("findings", []) if isinstance(value.get("findings"), list) else []:
        if not isinstance(finding, dict) or not isinstance(finding.get("claim"), str):
            errors.append("each finding must have a string claim")
    for citation in value.get("citations", []) if isinstance(value.get("citations"), list) else []:
        if not isinstance(citation, dict) or any(
            not isinstance(citation.get(key), str) or not citation[key] for key in ("id", "source")
        ):
            errors.append("each citation must have non-empty string id and source")
    return errors


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    try:
        errors = check_result(strict_json_loads(sys.stdin.buffer.read().decode("utf-8-sig")))
    except (ValueError, UnicodeError, RecursionError) as exc:
        errors = [f"Invalid JSON input: {exc}"]
    print(json.dumps({"valid": not errors, "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
