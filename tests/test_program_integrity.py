"""Program-body integrity, legacy manifests and supported example assertions."""
import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.aisp_hash import canonical_hash, compute_manifest, package_hash_payload, strict_json_loads
from tools.aisp_readme import check_readme, render_readme


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"
HELPER = CREATOR / "scripts/check_research_result.py"


class ProgramIntegrityTests(unittest.TestCase):
    def test_body_changes_affect_manifest_and_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "simple_aisp"
            skill.mkdir()
            program = skill / "aisp.aisop.json"
            program.write_bytes(SEED.read_bytes())
            before = compute_manifest(skill)
            (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")
            doc = json.loads(program.read_text(encoding="utf-8"))
            node = next(iter(doc[1]["content"]["functions"].values()))
            node["step1"] = "A controlled change to the business behavior."
            program.write_text(json.dumps(doc), encoding="utf-8")
            after = compute_manifest(skill)
            self.assertEqual(before["contract_sha256"], after["contract_sha256"])
            self.assertEqual(before["resources_sha256"], after["resources_sha256"])
            self.assertNotEqual(before["program_sha256"], after["program_sha256"])
            self.assertNotEqual(before["package_sha256"], after["package_sha256"])
            self.assertFalse(check_readme(skill)[0])
            program.write_text(json.dumps(doc, sort_keys=True, indent=4), encoding="utf-8")
            self.assertEqual(after["program_sha256"], compute_manifest(skill)["program_sha256"])

    def test_legacy_and_program_bound_manifest_shapes(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is a development dependency")
        schema = json.loads((ROOT / "schemas/registry-manifest-v1.schema.json").read_text(encoding="utf-8"))
        manifest = compute_manifest(SEED)
        self.assertEqual(manifest["manifest_version"], "1.1")
        jsonschema.validate(manifest, schema)
        legacy = copy.deepcopy(manifest)
        legacy["manifest_version"] = "1.0"
        del legacy["program_sha256"]
        legacy["package_sha256"] = canonical_hash(package_hash_payload(legacy))
        jsonschema.validate(legacy, schema)
        bad = copy.deepcopy(manifest)
        del bad["program_sha256"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)
        with self.assertRaises(ValueError):
            package_hash_payload(bad)

    def test_strict_json_does_not_accept_ambiguous_data(self):
        for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_json_loads(raw)

    def test_example_assertions_avoid_unsupported_python_forms(self):
        count = 0
        for path in (ROOT / "examples/aisp").glob("*_aisp/aisp.aisop.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            for name, function in doc[1]["content"]["functions"].items():
                for value in function.values():
                    if isinstance(value, str) and value.startswith("sys.assert("):
                        # `assert` is an AISOP call name, not a Python attribute.
                        call = ast.parse("check" + value[len("sys.assert"):], mode="eval").body
                        expression = ast.literal_eval(call.args[0])
                        with self.subTest(skill=path.parent.name, node=name):
                            self.assertNotRegex(expression, r"\.get\(|\.lower\(|\bisinstance\(|\band\b|\bor\b|\bin\s*\(|\bTrue\b")
                        count += 1
        self.assertGreaterEqual(count, 7)

    def test_research_envelope_helper_is_utf8_and_fail_closed(self):
        cases = [
            ({"status": "incomplete", "findings": [], "citations": []}, True),
            ({"status": "complete", "findings": [{"claim": "A Unicode claim: \u7814\u7a76"}], "citations": [{"id": "c1", "source": "fixture"}]}, True),
            ({"status": "complete", "findings": {}, "citations": []}, False),
            ({"status": "made-up", "findings": [], "citations": []}, False),
            (None, False),
        ]
        for value, valid in cases:
            with self.subTest(value=value):
                result = subprocess.run([sys.executable, "-B", str(HELPER)],
                                        input=json.dumps(value, ensure_ascii=False).encode("utf-8"),
                                        capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual(result.returncode, 0 if valid else 1)
                self.assertEqual(json.loads(result.stdout)["valid"], valid)
