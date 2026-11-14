"""Candidate replay is executable engineering evidence, not a safety sandbox."""
import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import check_doc_sync
from tools.aisp_validate import _normalize_rel, validate_skill


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
SPEC = importlib.util.spec_from_file_location("candidate_boundary_gate", CREATOR / "scripts/check_generated_candidate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def report():
    return {"results": [], "artifacts": {}}


def evidence(root, cases, entries=None):
    (root / "evals").mkdir(exist_ok=True)
    entries = entries if entries is not None else [{"path": "task.py", "cases": cases}]
    (root / "evals/script-behavior.json").write_text(json.dumps({"scripts": entries}), encoding="utf-8")
    return {"aisp_contract": {"resources": [
        {"path": "task.py", "kind": "script", "mode": "execute_only"},
        {"path": "evals/script-behavior.json", "kind": "eval", "mode": "read_only"},
    ]}}


def good_cases():
    return [{"name": kind, "kind": kind, "argv": ["python", "-B", "task.py"], "expected_exit": 0}
            for kind in ("positive", "boundary", "failure")]


class CandidateBoundaryTests(unittest.TestCase):
    def test_runtime_caches_fail_both_package_residue_checks(self):
        spec = importlib.util.spec_from_file_location("privacy_cache_simulator", CREATOR / "scripts/simulate_aisp_flow.py")
        simulator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(simulator)
        for folder, forbidden in ((".soulrun_cache", True), (".execution_cache", True),
                                  (".evolution_snapshot", True), (".version_history", True),
                                  ("__pycache__", True), ("evals/runtime-traces", False),
                                  ("data", False), ("aisp_reports", False)):
            with self.subTest(folder=folder), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / "nested" / folder
                path.mkdir(parents=True)
                (path / "fixture.json").write_text("{}", encoding="utf-8")
                result = report()
                gate.check_cache(root, result)
                self.assertEqual(gate.has_failures(result), forbidden)
                if forbidden:
                    self.assertEqual({item["code"] for item in result["results"]}, {"AISP_E_CANDIDATE_CACHE_RESIDUE"})
                simulation = {"static": {}, "failures": []}
                simulator.check_no_cache_residue(root, simulation)
                self.assertEqual(bool(simulation["failures"]), forbidden)
                self.assertEqual(simulation["static"]["cache_residue_dirs"], int(forbidden))

    def test_dotfiles_do_not_alias_visible_files_or_absolute_paths(self):
        self.assertNotEqual(_normalize_rel(".env"), _normalize_rel("env"))
        self.assertEqual(_normalize_rel("././.env"), ".env")
        self.assertNotEqual(_normalize_rel("/env"), _normalize_rel("env"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "simple_aisp"
            root.mkdir()
            doc = json.loads((ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json").read_text(encoding="utf-8"))
            resources = [
                {"id": "visible", "path": "env", "kind": "data", "mode": "execute_only"},
                {"id": "hidden", "path": ".env", "kind": "data", "mode": "read_only"},
            ]
            doc[1]["content"]["aisp_contract"]["resources"] = resources
            for name in ("env", ".env"):
                (root / name).write_text("fixture", encoding="utf-8")
            for name, forbidden in (("env", True), (".env", False)):
                doc[1]["content"]["functions"]["start"]["step1"] = f"sys.io.read('{name}')"
                (root / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                codes = {r["code"] for r in validate_skill(root)["results"]}
                self.assertEqual("AISP_E_SE3_MODE_GATE" in codes, forbidden)

    def test_snapshot_malformed_manifests_return_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            (snapshot / "README.md").write_text("Snapshot", encoding="utf-8")
            for raw in ("[]", "null", "{bad", '{"files":[],"files":[]}'):
                with self.subTest(raw=raw), patch.object(check_doc_sync, "SNAPSHOT_DIRS", [Path("snapshot")]):
                    (snapshot / "MANIFEST.sha256.json").write_text(raw, encoding="utf-8")
                    self.assertTrue(check_doc_sync.check_snapshot_metadata(root))
                    self.assertTrue(check_doc_sync.check_snapshot_manifest_integrity(root))

    def test_snapshot_escape_is_rejected_before_reading_file_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            for path in ("../outside.txt", "..\\outside.txt", "/outside.txt", "C:/outside.txt"):
                manifest = {"files": [{"path": path, "bytes": 7, "sha256": hashlib.sha256(b"outside").hexdigest()}]}
                (snapshot / "MANIFEST.sha256.json").write_text(json.dumps(manifest), encoding="utf-8")
                with self.subTest(path=path), patch.object(check_doc_sync, "SNAPSHOT_DIRS", [Path("snapshot")]), patch.object(Path, "read_bytes") as read:
                    self.assertTrue(check_doc_sync.check_snapshot_manifest_integrity(root))
                    read.assert_not_called()

    def test_static_failures_skip_candidate_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = io.StringIO()
            fail = lambda a, b, r: gate.add(r, "FAIL", "test_static_failure", "controlled failure")
            with patch.object(gate, "load_skill", return_value=({"id": root.name}, {"aisp_contract": {}})), \
                    patch.object(gate, "check_reference_tools", side_effect=fail), \
                    patch.object(gate, "check_sidecar"), patch.object(gate, "check_schema_resources"), \
                    patch.object(gate, "check_behavior_cases"), patch.object(gate, "check_cache"), \
                    patch.object(gate, "check_script_behavior") as replay, redirect_stdout(output):
                code = gate.main([str(root), "--creator-root", str(root), "--output-path", str(root.parent)])
            self.assertEqual(code, 1)
            replay.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())["artifacts"]["script_cases_skipped"], "static preflight failed")

    def test_behavior_requires_expectations_and_declared_inputs_even_with_no_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evals").mkdir()
            cases = [{"name": k, "kind": k, "input_params": {"undeclared": 1}, "expected_behavior": []}
                     for k in ("positive", "boundary", "failure")]
            (root / "evals/behavior-cases.json").write_text(json.dumps({"cases": cases}), encoding="utf-8")
            user = {"aisp_contract": {"resources": [{"path": "evals/behavior-cases.json"}]}}
            r = report()
            gate.check_behavior_cases(root, {"params": {}}, user, r)
            codes = {item["code"] for item in r["results"]}
            self.assertIn("AISP_E_CANDIDATE_BEHAVIOR_CASE_EXPECTED", codes)
            self.assertIn("AISP_E_CANDIDATE_BEHAVIOR_CASE_PARAM", codes)
            cases[0]["kind"] = []
            (root / "evals/behavior-cases.json").write_text(json.dumps({"cases": cases}), encoding="utf-8")
            gate.check_behavior_cases(root, {"params": {}}, user, report())

    def test_all_script_evidence_preflights_before_any_execution(self):
        bad_cases = [None, {"kind": []}, {**good_cases()[0], "argv": "task.py"},
                     {**good_cases()[0], "expected_exit": True},
                     {**good_cases()[0], "timeout_seconds": False},
                     {**good_cases()[0], "expect_stdout_contains": "text"}]
        for bad in bad_cases:
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                user = evidence(root, [*good_cases(), bad])
                r = report()
                with patch.object(gate, "run_process") as run:
                    gate.check_script_behavior(root, user, r)
                run.assert_not_called()
                self.assertTrue(gate.has_failures(r))

    def test_duplicate_script_entries_fail_without_running(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = {"path": "task.py", "cases": good_cases()}
            user = evidence(root, [], [entry, copy.deepcopy(entry)])
            r = report()
            with patch.object(gate, "run_process") as run:
                gate.check_script_behavior(root, user, r)
            run.assert_not_called()
            self.assertTrue(gate.has_failures(r))

    def test_unexpected_script_failure_stops_remaining_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user = evidence(root, good_cases())
            r = report()
            with patch.object(gate, "run_process", return_value={"exit_code": 9, "stdout": "", "stderr": ""}) as run:
                gate.check_script_behavior(root, user, r)
            self.assertEqual(run.call_count, 1)
            self.assertTrue(gate.has_failures(r))

    def test_reference_warnings_remain_visible_in_candidate_summary(self):
        for code in ("AISP_W_R6_TOOLS_CONDITIONAL", "AISP_W_M5_AMBIGUOUS_USE"):
            with self.subTest(code=code):
                payload = {"reports": [{"conformant": True, "fail_count": 0, "warning_count": 1, "results": [
                    {"severity": "WARN", "passed": False, "code": code, "message": "not independently proved"}]}]}
                r = report()
                proc = {"exit_code": 0, "stdout": json.dumps(payload), "stderr": ""}
                with patch.object(gate, "run_process", return_value=proc):
                    gate.check_reference_tools(CREATOR, CREATOR, r)
                self.assertIn(code, {item["code"] for item in r["results"]})
                self.assertFalse(gate.has_failures(r))

    def test_shared_schema_resources_follow_declared_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "simple_aisp"
            skill.mkdir()
            shared = root / "_shared"
            shared.mkdir()
            (shared / "schema.json").write_text(json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}), encoding="utf-8")
            user = {"aisp_contract": {"resources": [{"path": "schema.json", "kind": "schema", "scope": "shared"}]}}
            r = report()
            gate.check_schema_resources(skill, user, r)
            self.assertFalse(gate.has_failures(r), r)

    def test_subprocess_unicode_is_utf8_without_global_environment_changes(self):
        text = "Unicode: \u7814\u7a76"
        result = gate.run_process([sys.executable, "-B", "-c", "import sys; print(sys.stdin.read(), end='')"], ROOT, stdin=text)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"], text)
