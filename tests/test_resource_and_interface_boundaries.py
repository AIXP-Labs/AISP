"""Filesystem boundaries must survive shared roots, discovery and interface scans."""
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import aisp_hash, aisp_readme, aisp_skill_md, aisp_validate
from tools import aisp_validate_agent_skill_bridge as bridge


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


light = load_module(CREATOR / "scripts/validate_aisp_skill.py", "resource_boundary_light")
gate = load_module(CREATOR / "scripts/check_generated_candidate.py", "resource_boundary_gate")
simulator = load_module(CREATOR / "scripts/simulate_aisp_flow.py", "resource_boundary_simulator")


class ResourceAndInterfaceBoundaryTests(unittest.TestCase):
    def make_skill(self, root):
        skill = root / "simple_aisp"
        skill.mkdir()
        (skill / "aisp.aisop.json").write_bytes(SEED.read_bytes())
        (skill / "SKILL.md").write_text(aisp_skill_md.render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
        (skill / "README.md").write_text(aisp_readme.render_readme(skill), encoding="utf-8")
        return skill

    def redirected_resolve(self, source, destination):
        original = Path.resolve

        def resolve(path, *args, **kwargs):
            if path == source or source in path.parents:
                return original(destination / path.relative_to(source), *args, **kwargs)
            return original(path, *args, **kwargs)
        return resolve

    def test_shared_root_escape_is_rejected_before_reading_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            skill = self.make_skill(root)
            outside = Path(tmp) / "outside"
            outside.mkdir()
            resource = {"id": "schema", "path": "schema.json", "scope": "shared", "kind": "schema", "mode": "read_only"}
            user = {"aisp_contract": {"resources": [resource]}}
            report = {"results": [], "artifacts": {}}
            with patch.object(Path, "resolve", self.redirected_resolve(root / "_shared", outside)), \
                 patch.object(Path, "read_bytes", side_effect=AssertionError("unexpected resource read")), \
                 patch.object(Path, "read_text", side_effect=AssertionError("unexpected schema read")):
                with self.assertRaises(aisp_hash.ResourcePathError):
                    aisp_hash.resolve_resource(skill, resource)
                reporter = aisp_validate.Reporter()
                resources = aisp_validate._check_resources(user["aisp_contract"], {}, skill, root, reporter, skill / "aisp.aisop.json")
                self.assertEqual(resources, {})
                self.assertIn("AISP_E_SE1_PATH", {r.code for r in reporter.results})
                gate.check_schema_resources(skill, user, report)
                self.assertTrue(gate.has_failures(report))

    def test_shared_root_alias_within_registry_is_still_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self.make_skill(root)
            shared = root / "shared_assets"
            shared.mkdir()
            (shared / "data.txt").write_text("synthetic", encoding="utf-8")
            resource = {"id": "data", "path": "data.txt", "scope": "shared", "kind": "data", "mode": "read_only"}
            with patch.object(Path, "resolve", self.redirected_resolve(root / "_shared", shared)):
                self.assertEqual(aisp_hash.resolve_resource(skill, resource), shared / "data.txt")
                reporter = aisp_validate.Reporter()
                resources = aisp_validate._check_resources({"resources": [resource]}, {}, skill, root, reporter, skill / "aisp.aisop.json")
                self.assertEqual(len(resources), 1)
                self.assertFalse(reporter.results)

    def test_invalid_filesystem_resource_returns_clean_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "bad", "path": "data\0.json", "kind": "data", "mode": "read_only"}]
            (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
            report = aisp_validate.validate_skill(skill)
            self.assertFalse(report["conformant"])
            self.assertIn("AISP_E_SE1_PATH", {r["code"] for r in report["results"]})
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(aisp_validate.main(["--json", str(skill)]), 1)
            self.assertFalse(json.loads(out.getvalue())["reports"][0]["conformant"])

    def test_unreadable_or_non_file_discovery_scripts_fail_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("registry", encoding="utf-8")
            script = root / "aisp_list.py"
            for raw in (b"\xff\xfe", b"if :", b"\x00"):
                with self.subTest(raw=raw):
                    script.write_bytes(raw)
                    report = aisp_validate.validate_aisp_dir(root)
                    self.assertFalse(report["conformant"])
                    self.assertIn("AISP_E_SE5_SCRIPT", {r["code"] for r in report["results"]})
            script.unlink()
            script.mkdir()
            self.assertFalse(aisp_validate.validate_aisp_dir(root)["conformant"])

    def test_external_discovery_script_is_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            script = root / "aisp_list.py"
            script.write_text("pass", encoding="utf-8")
            outside = Path(tmp) / "outside.py"
            with patch.object(Path, "resolve", self.redirected_resolve(script, outside)), \
                 patch.object(Path, "read_text", side_effect=AssertionError("external script read")):
                reporter = aisp_validate.Reporter()
                aisp_validate._check_discovery_script(script, reporter)
                self.assertEqual([r.code for r in reporter.results], ["AISP_E_SE5_SCRIPT"])

    def test_linked_index_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = root / "aisp_list.json"
            index.write_text('{"skills": []}', encoding="utf-8")
            original = Path.is_symlink
            with patch.object(Path, "is_symlink", lambda path: path == index or original(path)), \
                 patch.object(Path, "read_text", side_effect=AssertionError("linked index read")):
                reporter = aisp_validate.Reporter()
                aisp_validate._check_index(root, [], reporter)
                self.assertEqual([r.code for r in reporter.results], ["AISP_E_EC2_INDEX"])

    def test_bridge_keeps_link_identity_for_direct_and_scanned_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self.make_skill(root)
            interface = skill / "SKILL.md"
            original = Path.is_symlink
            with patch.object(Path, "resolve", self.redirected_resolve(interface, root / "external.md")), \
                 patch.object(Path, "is_symlink", lambda path: path == interface or original(path)):
                for target in (interface, skill, root):
                    with self.subTest(target=target):
                        self.assertIn(interface, bridge.iter_bridge_files(target))
                with patch.object(Path, "read_text", side_effect=AssertionError("linked interface read")):
                    report = bridge.validate_bridge(interface)
                self.assertFalse(report["conformant"])
                self.assertEqual(report["results"][0]["code"], "AISP_E_M7_SKILL_MD_INPUT")

    def test_bridge_does_not_ignore_invalid_target_among_valid_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self.make_skill(root)
            out = io.StringIO()
            with redirect_stdout(out):
                code = bridge.main(["--json", str(skill), str(root / "missing")])
            report = json.loads(out.getvalue())
            self.assertEqual(code, 1)
            self.assertFalse(report["conformant"])
            self.assertEqual(len(report["reports"]), 2)

    def test_batch_generators_refuse_escaping_folder_before_writes_or_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            skill = self.make_skill(root)
            for tool in (aisp_readme, aisp_skill_md, bridge):
                with self.subTest(tool=tool.__name__), \
                     patch.object(Path, "resolve", self.redirected_resolve(skill, Path(tmp) / "external_aisp")):
                    if tool is bridge:
                        with self.assertRaises(ValueError):
                            tool.iter_bridge_files(root)
                    else:
                        with patch.object(tool, "write_lf") as write, redirect_stderr(io.StringIO()):
                            self.assertEqual(tool.main([str(root), "--write-all"]), 1)
                            write.assert_not_called()

    def test_bridge_invalid_program_path_returns_failure_not_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('  aisp_program: "aisp.aisop.json"', '  aisp_program: "data\\u0000.json"'), encoding="utf-8")
            report = bridge.validate_bridge(path)
            self.assertFalse(report["conformant"])
            self.assertIn("AISP_E_EC7_PROGRAM_PATH", {r["code"] for r in report["results"]})

    def test_projection_discovery_errors_are_clean_and_never_resolve_versions(self):
        for tool in (aisp_readme, aisp_skill_md):
            with self.subTest(tool=tool.__name__), \
                 patch.object(tool, "iter_skill_dirs", side_effect=OSError("synthetic discovery denial")), \
                 patch.object(aisp_skill_md, "_latest_soulrun_requirement") as resolve, \
                 redirect_stderr(io.StringIO()):
                self.assertEqual(tool.main([str(ROOT / "examples"), "--write-all"]), 1)
                resolve.assert_not_called()

    def test_core_cli_returns_json_when_filesystem_inspection_fails(self):
        out = io.StringIO()
        with patch.object(aisp_validate, "validate_skill", side_effect=OSError("synthetic unreadable target")), redirect_stdout(out):
            self.assertEqual(aisp_validate.main(["--json", str(SEED)]), 1)
        report = json.loads(out.getvalue())["reports"][0]
        self.assertFalse(report["conformant"])
        self.assertEqual(report["results"][0]["code"], "AISP_E_INPUT")

    def test_lightweight_non_string_bindings_fail_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            for value in (1, True, ["sys.assert"], {"mechanism": "sys.assert"}):
                with self.subTest(value=value):
                    doc = json.loads(SEED.read_text(encoding="utf-8"))
                    doc[1]["content"]["aisp_contract"]["non_negotiable"][0]["enforced_by"] = value
                    (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                    report = light.validate(str(skill))
                    self.assertFalse(report["m1_to_m6_pass"])
                    self.assertIn("AISP_E_M4_GRAMMAR", {r["code"] for r in report["issues"]})

    def test_lightweight_entry_and_shared_root_escape_fail_safety_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            skill = self.make_skill(root)
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "data", "path": "data.json", "scope": "shared", "kind": "data", "mode": "read_only"}]
            (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
            original = os.path.realpath
            for source in (str(root / "_shared"), str(skill / "aisp.aisop.json")):
                def redirect(path, *args, **kwargs):
                    if os.path.normcase(str(path)) == os.path.normcase(source):
                        return original(str(Path(tmp) / "outside"), *args, **kwargs)
                    return original(path, *args, **kwargs)
                with self.subTest(source=source), patch.object(light.os.path, "realpath", redirect):
                    report = light.validate(str(skill))
                    self.assertFalse(report["m1_to_m6_pass"])
                    self.assertFalse(report["safety_pass"])
                    self.assertIn("AISP_E_SE1_PATH", {r["code"] for r in report["issues"]})

    def test_candidate_and_simulator_entry_confinement_precedes_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self.make_skill(root)
            entry = skill / "aisp.aisop.json"
            report = {"results": [], "artifacts": {}}
            with patch.object(Path, "resolve", self.redirected_resolve(entry, root / "external.json")), \
                 patch.object(Path, "read_text", side_effect=AssertionError("external entry read")):
                self.assertEqual(gate.load_skill(skill, report), ({}, {}))
                self.assertTrue(gate.has_failures(report))
                with self.assertRaises(ValueError):
                    simulator.load_skill(skill)


if __name__ == "__main__":
    unittest.main()
