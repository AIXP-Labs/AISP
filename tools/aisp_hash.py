#!/usr/bin/env python3
"""Compute AISP package provenance hashes.

The registry-facing hashes are deterministic and zero-dependency:
- contract_sha256: canonical JSON hash of user.content.aisp_contract
- program_sha256: canonical JSON hash of the complete two-message program
- resources_sha256: canonical JSON hash of declared resource path/hash records
- package_sha256: canonical JSON hash of package content evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


REMOTE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
SKILL_ID_RE = re.compile(r"^[a-z0-9_]+_aisp$")
VALID_RESOURCE_SCOPES = {"skill", "shared"}
LEGACY_PACKAGE_HASH_FIELDS = (
    "manifest_version",
    "protocol",
    "skill_id",
    "skill_version",
    "contract_sha256",
    "resources_sha256",
    "resources",
)
PACKAGE_HASH_FIELDS = (*LEGACY_PACKAGE_HASH_FIELDS, "program_sha256")


class ResourcePathError(ValueError):
    """Raised when a declared resource path is outside the package boundary."""


def check_generated_target(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f"Generated output must be a regular non-symlink file: {path}")


def write_generated_text(path: Path, text: str) -> None:
    """Replace one projection atomically instead of truncating linked/partial files."""
    check_generated_target(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=f".{path.name}.",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def strict_json_loads(text: str) -> Any:
    """Parse one unambiguous JSON value, rejecting duplicate keys and NaN/Infinity."""
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    def reject(value: str) -> None:
        raise ValueError(f"non-JSON numeric constant: {value}")

    return json.loads(text, object_pairs_hook=unique, parse_constant=reject)


def load_skill(skill_path: Path) -> tuple[Path, list[Any]]:
    skill_dir = skill_path if skill_path.is_dir() else skill_path.parent
    skill_file = skill_dir / "aisp.aisop.json" if skill_path.is_dir() else skill_path
    if not is_inside(skill_file.resolve(), skill_dir.resolve()):
        raise ResourcePathError("Skill entry file resolves outside its folder")
    doc = strict_json_loads(skill_file.read_text(encoding="utf-8-sig"))
    if (not isinstance(doc, list) or len(doc) != 2
            or any(not isinstance(message, dict) for message in doc)
            or [message.get("role") for message in doc] != ["system", "user"]
            or any(not isinstance(message.get("content"), dict) for message in doc)
            or not isinstance(doc[1]["content"].get("aisp_contract"), dict)):
        raise ValueError("Expected a two-message AISP JSON array with system/user roles, object content and an object contract")
    return skill_dir.resolve(), doc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256_bytes(payload)


def package_hash_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    version = manifest.get("manifest_version")
    if version not in ("1.0", "1.1"):
        raise ValueError("Unsupported manifest_version")
    fields = LEGACY_PACKAGE_HASH_FIELDS if version == "1.0" else PACKAGE_HASH_FIELDS
    if version == "1.1" and not isinstance(manifest.get("program_sha256"), str):
        raise ValueError("Manifest 1.1 requires program_sha256")
    return {key: manifest.get(key) for key in fields}


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
    path = resource.get("path")
    scope = resource.get("scope", "skill")
    if not isinstance(scope, str) or scope not in VALID_RESOURCE_SCOPES:
        raise ResourcePathError(f"resource {path!r} has invalid scope {scope!r}")
    if not isinstance(path, str) or not path:
        raise ResourcePathError("resource path is empty")
    if REMOTE_RE.match(path) or WINDOWS_DRIVE_RE.match(path) or path.startswith(("\\", "/")) or Path(path).is_absolute() or has_parent_escape(path):
        raise ResourcePathError(f"resource path {path!r} is outside the allowed package boundary")

    registry = skill_dir.resolve().parent
    base = (registry / "_shared").resolve() if scope == "shared" else skill_dir.resolve()
    if scope == "shared" and not is_inside(base, registry):
        raise ResourcePathError("Shared resource root resolves outside the aisp directory")
    resolved = (base / path.replace("\\", "/")).resolve()
    if not is_inside(resolved, base):
        raise ResourcePathError(f"resource path {path!r} resolves outside {base}")
    return resolved


def compute_manifest(skill_path: Path, source: str | None = None, commit: str | None = None) -> dict[str, Any]:
    skill_dir, doc = load_skill(skill_path)
    system = doc[0].get("content", {}) if isinstance(doc, list) and doc else {}
    user = doc[1].get("content", {}) if isinstance(doc, list) and len(doc) > 1 else {}
    contract = user.get("aisp_contract", {})
    resources = contract.get("resources", []) if isinstance(contract, dict) else []
    if not isinstance(resources, list) or any(not isinstance(resource, dict) for resource in resources):
        raise ValueError("resources must be an array of objects")

    resource_records = []
    for resource in resources:
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
        "manifest_version": "1.1",
        "protocol": system.get("protocol"),
        "skill_id": system.get("id"),
        "skill_version": system.get("version"),
        "source": source,
        "commit": commit,
        "skill_path": package_skill_path(skill_dir, system),
        "contract_sha256": canonical_hash(contract),
        "program_sha256": canonical_hash(doc),
        "resources": resource_records,
        "resources_sha256": canonical_hash(resource_records),
    }
    payload["package_sha256"] = canonical_hash(package_hash_payload(payload))
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
        try:
            skill = Path(args.skill)
            directory = (skill if skill.is_dir() else skill.parent).resolve()
            program = directory / "aisp.aisop.json" if skill.is_dir() else skill.resolve()
            protected = [program, *(resolve_resource(directory, item) for item in manifest["resources"])]
            output = Path(args.out)
            for item in protected:
                if output.resolve() == item.resolve() or (output.exists() and item.exists() and output.samefile(item)):
                    raise ValueError("Manifest output must not overwrite a business-program or declared-resource input")
            write_generated_text(output, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        except (OSError, ValueError, RuntimeError) as exc:
            print(f"ERROR: cannot write manifest: {exc}", file=sys.stderr)
            return 1
    if args.json or not args.out:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
