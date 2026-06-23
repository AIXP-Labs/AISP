#!/usr/bin/env python3
"""Compute AISP package provenance hashes.

The registry-facing hashes are deterministic and zero-dependency:
- contract_sha256: canonical JSON hash of user.content.aisp_contract
- resources_sha256: canonical JSON hash of declared resource path/hash records
- package_sha256: canonical JSON hash of package content evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REMOTE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
SKILL_ID_RE = re.compile(r"^[a-z0-9_]+_aisp$")
VALID_RESOURCE_SCOPES = {"skill", "shared"}
PACKAGE_HASH_FIELDS = (
    "manifest_version",
    "protocol",
    "skill_id",
    "skill_version",
    "contract_sha256",
    "resources_sha256",
    "resources",
)


class ResourcePathError(ValueError):
    """Raised when a declared resource path is outside the package boundary."""


def load_skill(skill_path: Path) -> tuple[Path, list[Any]]:
    skill_dir = skill_path if skill_path.is_dir() else skill_path.parent
    skill_file = skill_dir / "aisp.aisop.json" if skill_path.is_dir() else skill_path
    return skill_dir.resolve(), json.loads(skill_file.read_text(encoding="utf-8-sig"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def package_skill_path(skill_dir: Path, system: dict[str, Any]) -> str:
    """Return a portable package-internal skill folder label, never a host path."""
    skill_id = system.get("id")
    candidate = skill_id.strip() if isinstance(skill_id, str) and skill_id.strip() else skill_dir.name
    if not SKILL_ID_RE.fullmatch(candidate):
        raise ResourcePathError(f"skill_path {candidate!r} is not a portable AISP skill id")
    return candidate


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def has_parent_escape(path: str) -> bool:
    return any(part == ".." for part in path.replace("\\", "/").split("/"))


def resolve_resource(skill_dir: Path, resource: dict[str, Any]) -> Path:
    path = str(resource.get("path", ""))
    scope = resource.get("scope", "skill")
    if scope not in VALID_RESOURCE_SCOPES:
        raise ResourcePathError(f"resource {path!r} has invalid scope {scope!r}")
    if not path:
        raise ResourcePathError("resource path is empty")
    if REMOTE_RE.match(path) or WINDOWS_DRIVE_RE.match(path) or Path(path).is_absolute() or has_parent_escape(path):
        raise ResourcePathError(f"resource path {path!r} is outside the allowed package boundary")

    base = (skill_dir.parent / "_shared").resolve() if scope == "shared" else skill_dir.resolve()
    resolved = (base / path).resolve()
    if not is_inside(resolved, base):
        raise ResourcePathError(f"resource path {path!r} resolves outside {base}")
    return resolved


def compute_manifest(skill_path: Path, source: str | None = None, commit: str | None = None) -> dict[str, Any]:
    skill_dir, doc = load_skill(skill_path)
    system = doc[0].get("content", {}) if isinstance(doc, list) and doc else {}
    user = doc[1].get("content", {}) if isinstance(doc, list) and len(doc) > 1 else {}
    contract = user.get("aisp_contract", {})
    resources = contract.get("resources", []) if isinstance(contract, dict) else []

    resource_records = []
    for resource in resources if isinstance(resources, list) else []:
        if not isinstance(resource, dict):
            continue
        resolved = resolve_resource(skill_dir, resource)
        record = {
            "id": resource.get("id"),
            "path": resource.get("path"),
            "scope": resource.get("scope", "skill"),
            "mode": resource.get("mode"),
            "kind": resource.get("kind"),
            "exists": resolved.is_file(),
            "sha256": sha256_bytes(resolved.read_bytes()) if resolved.is_file() else None,
        }
        resource_records.append(record)

    payload = {
        "manifest_version": "1.0",
        "protocol": system.get("protocol"),
        "skill_id": system.get("id"),
        "skill_version": system.get("version"),
        "source": source,
        "commit": commit,
        "skill_path": package_skill_path(skill_dir, system),
        "contract_sha256": canonical_hash(contract),
        "resources": resource_records,
        "resources_sha256": canonical_hash(resource_records),
    }
    payload["package_sha256"] = canonical_hash({key: payload.get(key) for key in PACKAGE_HASH_FIELDS})
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute AISP registry/provenance hashes.")
    parser.add_argument("skill", help="Skill folder or aisp.aisop.json path.")
    parser.add_argument("--source", help="Optional source repository or registry URL.")
    parser.add_argument("--commit", help="Optional source commit.")
    parser.add_argument("--out", help="Optional path to write the manifest JSON.")
    parser.add_argument("--json", action="store_true", help="Print full JSON manifest.")
    args = parser.parse_args(argv)

    try:
        manifest = compute_manifest(Path(args.skill), args.source, args.commit)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json or not args.out:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
