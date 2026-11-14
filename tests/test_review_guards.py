"""Regression guards for evidence shape, projection writes and protocol layout."""
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import aisp_readme, aisp_skill_md
from tools.aisp_hash import write_generated_text
from tools.aisp_validate import main, tool_capabilities_shape_errors, validate_skill
from tools.check_doc_sync import check_protocol_structure


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"
CAPABILITIES = ROOT / "tests/fixtures/tool_capabilities/hard_tools.json"
LIGHT = ROOT / "examples/aisp/aisp_creator_evolution_aisp/scripts/validate_aisp_skill.py"


def capability_cases():
    good = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    yield "valid", good, True
    for field in ("tool_capabilities_version", "tools"):
        bad = copy.deepcopy(good)
        del bad[field]
        yield "missing " + field, bad, False
    for field, value in (("tool_capabilities_version", "99.0"), ("tools", []),
                         ("provenance", None), ("provenance", {"source": ""})):
        bad = copy.deepcopy(good)
        bad[field] = value
        yield field + repr(value), bad, False
    for spec in (None, {}, {"enforcement": "hard"}, {"risk_level": "low"},
                 {"enforcement": [], "risk_level": "low"},
                 {"enforcement": "hard", "risk_level": []},
                 {"enforcement": "hard", "risk_level": "low", "capabilities": [1]},
                 {"enforcement": "hard", "risk_level": "low", "forbidden_capabilities": {}}):
        bad = copy.deepcopy(good)
        bad["tools"]["filesystem"] = spec
        yield repr(spec), bad, False
    extra = copy.deepcopy(good)
    extra["vendor_extension"] = {"open_world": True}
    yield "open extensions", extra, True


class ReviewGuardTests(unittest.TestCase):
    def make_skill(self, parent, doc=None):
        skill = Path(parent) / "simple_aisp"
        skill.mkdir()
        doc = doc or json.loads(SEED.read_text(encoding="utf-8"))
        (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
        return skill

    def test_capability_shape_matches_the_published_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is a development dependency")
        schema = json.loads((ROOT / "schemas/tool-capabilities-v1.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for label, doc, expected in capability_cases():
            with self.subTest(label=label):
                self.assertEqual(validator.is_valid(doc), expected)
                self.assertEqual(not tool_capabilities_shape_errors(doc), expected)

    def test_bad_capability_artifacts_fail_before_evidence_consumption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capabilities.json"
            for label, doc, valid in capability_cases():
                if valid:
                    continue
                with self.subTest(label=label):
                    path.write_text(json.dumps(doc), encoding="utf-8")
                    output = io.StringIO()
                    with redirect_stdout(output):
                        code = main(["--json", "--strict-tools", "--tool-capabilities", str(path),
                                     str(ROOT / "examples/aisp/stock_analysis_aisp")])
                    self.assertEqual(code, 1)
                    self.assertIn("AISP_E_INPUT", output.getvalue())
                    self.assertNotIn("AISP_I_R6_TOOLS_HARD", output.getvalue())

    def test_explicit_bad_execute_modes_are_not_missing_defaults(self):
        for value in (None, [], {}, False, 1):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["functions"]["start"]["execute_mode"] = value
                skill = self.make_skill(tmp, doc)
                codes = {r["code"] for r in validate_skill(skill)["results"]}
                self.assertIn("AISP_E_M1_EXECUTE_MODE", codes)
                self.assertNotIn("AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE", codes)
                proc = subprocess.run([sys.executable, "-B", str(LIGHT), str(skill)],
                                      capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("AISP_E_M1_EXECUTE_MODE", {r["code"] for r in json.loads(proc.stdout)["issues"]})

    def test_supplied_empty_capability_map_is_not_overridden_by_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "capabilities.json"
            p.write_text(json.dumps({"tool_capabilities_version": "1.0", "tools": {}}), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--json", "--strict-tools", "--tool-capabilities", str(p),
                             "--runtime-trace", str(ROOT / "examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json"),
                             str(ROOT / "examples/aisp/stock_analysis_aisp")])
            self.assertEqual(code, 1)
            self.assertIn("AISP_E_R6_TOOLS_NOT_HARD", output.getvalue())
            self.assertNotIn("AISP_I_R6_TOOLS_HARD", output.getvalue())

    def test_lightweight_profile_and_binding_checks_do_not_use_loose_prefixes(self):
        for profile, call, expected in (("aisp.skill.anything", "sys.assert('true')", "AISP_E_M3_PROFILE"),
                                        ("aisp.skill.v1", "sys.assert_fake('true')", "AISP_E_M4_NO_MECHANISM")):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                contract = doc[1]["content"]["aisp_contract"]
                contract["profile"] = profile
                contract["non_negotiable"] = [{"rule": "Check", "enforced_by": "start.step1:sys.assert"}]
                doc[1]["content"]["functions"]["start"]["step1"] = call
                skill = self.make_skill(tmp, doc)
                proc = subprocess.run([sys.executable, "-B", str(LIGHT), str(skill)],
                                      capture_output=True, text=True, encoding="utf-8")
                report = json.loads(proc.stdout)
                self.assertFalse(report["m1_to_m6_pass"])
                self.assertIn(expected, {r["code"] for r in report["issues"]})

    def test_jsonflow_malformed_fields_cannot_be_silent_terminals(self):
        for spec in (None, [], {"next": 1}, {"next": [None]}, {"next": "end_node"},
                     {"branches": []}, {"branches": {"yes": []}}, {"error": []}):
            with self.subTest(spec=spec), tempfile.TemporaryDirectory() as tmp:
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["aisop"]["main"]["start"] = spec
                codes = {r["code"] for r in validate_skill(self.make_skill(tmp, doc))["results"]}
                self.assertTrue(codes & {"AISP_E_M1_GRAPH", "AISP_E_M1_EDGE_SHAPE"})

    def test_projection_writes_do_not_modify_external_hardlinks(self):
        for module, filename in ((aisp_readme, "README.md"), (aisp_skill_md, "SKILL.md")):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                external = Path(tmp) / "outside.txt"
                external.write_text("original", encoding="utf-8")
                directory = Path(tmp) / "skill"
                directory.mkdir()
                target = directory / filename
                try:
                    target.hardlink_to(external)
                except OSError as exc:
                    self.skipTest(f"hardlink unavailable (OS error {exc.errno})")
                module.write_lf(target, "new projection\r\n")
                self.assertEqual(external.read_text(encoding="utf-8"), "original")
                self.assertEqual(target.read_bytes(), b"new projection\n")

    def test_symbolic_output_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "README.md"
            path.write_text("original", encoding="utf-8")
            with patch.object(Path, "is_symlink", return_value=True), self.assertRaises(ValueError):
                write_generated_text(path, "replacement")
            self.assertEqual(path.read_text(encoding="utf-8"), "original")

    def test_failed_atomic_replace_preserves_file_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "README.md"
            path.write_text("original", encoding="utf-8")
            with patch.object(Path, "replace", side_effect=OSError("controlled failure")), self.assertRaises(OSError):
                write_generated_text(path, "replacement")
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_readme_batch_preflights_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.make_skill(tmp)
            before = first / "README.md"
            before.write_text("original", encoding="utf-8")
            other = Path(tmp) / "z_invalid_aisp"
            other.mkdir()
            (other / "aisp.aisop.json").write_text("{bad JSON", encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = aisp_readme.main([tmp, "--write-all"])
            self.assertEqual(code, 1)
            self.assertEqual(before.read_text(encoding="utf-8"), "original")

    def test_generators_share_strict_business_input_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[0]["role"] = "user"
            skill = self.make_skill(tmp, doc)
            for module in (aisp_readme, aisp_skill_md):
                with self.subTest(module=module.__name__), self.assertRaises(ValueError):
                    module.load_skill(skill)

    def test_protocol_structure_guard_rejects_duplicate_or_missing_rules(self):
        for name in ("AISP_Protocol.md", "AISP_Protocol_cn.md"):
            path = ROOT / "specification" / name
            self.assertEqual(check_protocol_structure(path), [])
            good = path.read_text(encoding="utf-8")
            for bad in (good + good, good.replace(r"^aisp\.skill\.v[0-9]+$", "aisp.skill."),
                        good.replace("## 4. ", "## 9. ", 1)):
                with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                    p = Path(tmp) / name
                    p.write_text(bad, encoding="utf-8")
                    self.assertTrue(check_protocol_structure(p))
