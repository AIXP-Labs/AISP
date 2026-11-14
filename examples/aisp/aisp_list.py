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
meets all of these: it imports only standard-library modules, scans only
`*_aisp` folders under its own directory, and writes only
`aisp_list.json`.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = """usage: python -B aisp_list.py [--json] [--check] [--help]

Discover AISP skills under this directory.

Options:
  --json   regenerate aisp_list.json from *_aisp/aisp.aisop.json folders
  --check  verify aisp_list.json is current without writing
  --help   show this help
"""

def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


def discover():
    skills = []
    errors = []
    for skill_dir in sorted(ROOT.glob("*_aisp")):
        if not skill_dir.is_dir() and not skill_dir.is_symlink():
            continue
        f = skill_dir / "aisp.aisop.json"
        try:
            resolved = f.resolve()
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.is_relative_to(skill_dir.resolve()):
                raise ValueError("skill entry escapes the discovery directory or its skill folder")
            data = json.loads(f.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
            if (not isinstance(data, list) or len(data) != 2
                    or any(not isinstance(message, dict) for message in data)
                    or [message.get("role") for message in data] != ["system", "user"]):
                raise ValueError("skill must have exactly system/user messages")
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
        if not isinstance(sc.get("name"), str) or not sc["name"].strip() or any(
            key in sc and not isinstance(sc[key], str) for key in ("summary", "description")
        ):
            errors.append(f"{f}: name/summary/description metadata has an invalid type")
            continue
        c = uc.get("aisp_contract", {})              # real object field in the user message
        skill_id = sc.get("id")
        if not isinstance(skill_id, str) or skill_id != skill_dir.name or not re.fullmatch(r"[a-z0-9_]+_aisp", skill_id):
            errors.append(f"{f}: system.content.id must match the _aisp folder name")
            continue
        if not isinstance(c, dict) or not isinstance(c.get("profile"), str) or not re.fullmatch(r"aisp\.skill\.v[0-9]+", c["profile"]):
            errors.append(f"{f}: missing versioned aisp.skill.v<major> profile")
            continue
        discovery = c.get("discovery", {})
        invocation = c.get("invocation")
        if not isinstance(discovery, dict) or not isinstance(invocation, dict):
            errors.append(f"{f}: discovery and invocation must be objects")
            continue
        if "risk_level" in c and c["risk_level"] not in ("low", "medium", "high", "critical"):
            errors.append(f"{f}: risk_level has an invalid value")
            continue
        if any(not isinstance(invocation.get(k), list) or not invocation[k]
               or any(not isinstance(v, str) for v in invocation[k])
               for k in ("when_to_use", "when_not_to_use")):
            errors.append(f"{f}: invocation lists must be non-empty string arrays")
            continue
        if ("category" in discovery and not isinstance(discovery["category"], str)) or (
            "tags" in discovery and (not isinstance(discovery["tags"], list)
                                     or any(not isinstance(tag, str) for tag in discovery["tags"]))
        ):
            errors.append(f"{f}: category/tags metadata has an invalid type")
            continue
        skills.append({
            "id": skill_id,
            "name": sc.get("name"),
            "summary": sc.get("summary") or sc.get("description", ""),
            "path": str(f.relative_to(ROOT.parent)).replace("\\", "/"),
            "category": discovery.get("category"),
            "tags": discovery.get("tags", []),
            "when_to_use": invocation["when_to_use"],
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
    out = ROOT / "aisp_list.json"
    if ("--check" in sys.argv or "--json" in sys.argv) and out.is_symlink():
        print("ERROR: aisp_list.json must not be a symbolic link", file=sys.stderr)
        return 1
    if "--check" in sys.argv:
        if not out.exists():
            print(f"{out} is missing; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        try:
            actual = out.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            print(f"ERROR: cannot read aisp_list.json: {exc}", file=sys.stderr)
            return 1
        if normalized(actual) != normalized(expected):
            print(f"{out} is stale; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        print("aisp_list.json ok")
        return 0
    if "--json" in sys.argv:
        try:
            if out.exists() and out.stat().st_nlink > 1:
                print("ERROR: refusing to overwrite a hardlinked aisp_list.json", file=sys.stderr)
                return 1
            out.write_text(expected, encoding="utf-8", newline="\n")
        except OSError as exc:
            print(f"ERROR: cannot write aisp_list.json: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
