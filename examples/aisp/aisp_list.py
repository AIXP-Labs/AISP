#!/usr/bin/env python3
"""aisp_list.py — discover AISP skills under this folder.

Scans <this_dir>/*_aisp/aisp.aisop.json, reads each skill's
user.content.aisp_contract, prints a human/AI-readable list, and (with --json)
writes aisp_list.json. Zero deps (stdlib). Side effect: only --json writes
aisp_list.json; --check is read-only and fails on drift. Any malformed
*_aisp package is a hard index error, not a silent skip.
  python -B aisp_list.py          # print the list
  python -B aisp_list.py --json   # also (re)generate aisp_list.json
  python -B aisp_list.py --check  # verify committed aisp_list.json
  python -B aisp_list.py --help   # print usage

Security guarantees (SE5 / ST1). This script MUST be zero-dependency (standard
library only) and human-auditable. It MUST NOT: access the network; import
third-party packages; execute skill scripts; modify any file except
aisp_list.json when --json is explicitly used; read files outside the aisp/
directory (except declared _shared metadata). The reference implementation below
meets all of these: it imports only `json` and `sys` from the stdlib, globs only
`*_aisp/aisp.aisop.json` under its own directory, and writes only
`aisp_list.json`.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = """usage: python -B aisp_list.py [--json] [--check] [--help]

Discover AISP skills under this directory.

Options:
  --json   regenerate aisp_list.json from *_aisp/aisp.aisop.json folders
  --check  verify aisp_list.json is current without writing
  --help   show this help
"""

def discover():
    skills = []
    errors = []
    for f in sorted(ROOT.glob("*_aisp/aisp.aisop.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
            sc = data[0]["content"]                  # system: id/name/summary metadata
            uc = data[1]["content"]                  # user: instruction/aisop/functions + aisp_contract
        except Exception as e:
            errors.append(f"{f}: {e}")
            continue
        if not isinstance(sc, dict):
            errors.append(f"{f}: system.content must be an object")
            continue
        if not isinstance(uc, dict):
            errors.append(f"{f}: user.content must be an object")
            continue
        c = uc.get("aisp_contract", {})              # real object field in the user message
        skill_id = sc.get("id")
        if not skill_id:
            errors.append(f"{f}: missing system.content.id")
            continue
        if not isinstance(c, dict) or not str(c.get("profile", "")).startswith("aisp.skill."):
            errors.append(f"{f}: missing aisp.skill.* profile")
            continue
        skills.append({
            "id": skill_id,
            "name": sc.get("name"),
            "summary": sc.get("summary") or sc.get("description", ""),
            "path": str(f.relative_to(ROOT.parent)).replace("\\", "/"),
            "category": c.get("discovery", {}).get("category"),
            "tags": c.get("discovery", {}).get("tags", []),
            "when_to_use": c.get("invocation", {}).get("when_to_use", []),
            "risk_level": c.get("risk_level"),
        })
    return skills, errors

def render_index(skills):
    return json.dumps({"aisp_list_version": "1.0", "skills": skills},
                      ensure_ascii=False, indent=2) + "\n"

def normalized(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").rstrip("\n")

def main():
    allowed_args = {"--json", "--check", "--help", "-h"}
    unknown_args = [arg for arg in sys.argv[1:] if arg not in allowed_args]
    if unknown_args:
        print(f"ERROR: unknown argument(s): {', '.join(unknown_args)}", file=sys.stderr)
        print(USAGE.rstrip(), file=sys.stderr)
        return 2
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE.rstrip())
        return 0
    skills, errors = discover()
    if errors:
        print("ERROR: cannot build AISP index:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    for s in skills:
        print(f"- {s['id']}: {s['summary']}  ->  {s['path']}")
    print(f"\n{len(skills)} AISP skill(s).")
    expected = render_index(skills)
    if "--check" in sys.argv:
        out = ROOT / "aisp_list.json"
        if not out.exists():
            print(f"{out} is missing; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        actual = out.read_text(encoding="utf-8-sig")
        if normalized(actual) != normalized(expected):
            print(f"{out} is stale; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        print("aisp_list.json ok")
        return 0
    if "--json" in sys.argv:
        out = ROOT / "aisp_list.json"
        out.write_text(expected, encoding="utf-8", newline="\n")
        print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
