"""Contradictory evidence and invalid links must fail without false greens."""
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import check_markdown_links as links
from tools.aisp_check_runtime_trace import check_trace, trace_shape_errors
from tools.aisp_validate import main as validate_main


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
STOCK = ROOT / "examples/aisp/stock_analysis_aisp"
spec = importlib.util.spec_from_file_location("evidence_consistency_gate", CREATOR / "scripts/check_generated_candidate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def bridge_payload():
    return {"conformant": True, "summary": {"fail": 0, "warn": 0, "info": 1}, "reports": [
        {"conformant": True, "summary": {"fail": 0, "warn": 0, "info": 1}, "results": [
            {"severity": "INFO", "passed": True, "code": "AISP_I_M7_SKILL_MD", "message": "synthetic format check"}
        ]}
    ]}


class EvidenceAndLinkConsistencyTests(unittest.TestCase):
    def bridge_check(self, raw):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("synthetic placeholder", encoding="utf-8")
            report = {"results": [], "artifacts": {}}
            with patch.object(gate, "run_process", return_value={"exit_code": 0, "stdout": raw, "stderr": ""}):
                gate.check_sidecar(root, root, report)
            return report

    def trace_check(self, trace, skill=STOCK):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps(trace), encoding="utf-8")
            return check_trace(skill, path)

    def test_invalid_link_paths_return_json_and_original_line_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Real\n[bad](bad%00.md)\n[also bad](missing.md)\n", encoding="utf-8")
            problems = links.check_links(root, ["README.md"])
            self.assertEqual([item["line"] for item in problems], [2, 3])
            self.assertIn("cannot resolve", problems[0]["message"])
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(links.main(["--root", str(root), "--json", "README.md"]), 1)
            self.assertEqual(json.loads(out.getvalue())["problem_count"], 2)

    def test_anchor_read_errors_are_problems_not_tracebacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("[anchor](other.md#real)\n", encoding="utf-8")
            (root / "other.md").write_text("# Real\n", encoding="utf-8")
            with patch.object(links, "heading_anchors", side_effect=OSError("synthetic access denial")):
                problems = links.check_links(root, ["README.md"])
            self.assertEqual(len(problems), 1)
            self.assertIn("cannot inspect target", problems[0]["message"])

    def test_drive_relative_links_are_not_mistaken_for_external_schemes(self):
        for target in ("C:private.md", "C:/private.md", "C%3Aprivate.md"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "README.md").write_text(f"[host-local]({target})\n", encoding="utf-8")
                self.assertIn("host-local drive path", links.check_links(root, ["README.md"])[0]["message"])

    def test_unresolvable_root_produces_a_machine_readable_failure(self):
        out = io.StringIO()
        with patch.object(Path, "resolve", side_effect=RuntimeError("synthetic loop")), redirect_stdout(out):
            self.assertEqual(links.main(["--json"]), 1)
        self.assertIn("cannot inspect repository", json.loads(out.getvalue())["problems"][0]["message"])

    def test_bridge_rejects_empty_truthy_or_contradictory_success_claims(self):
        cases = [None, [], True, {}, {"conformant": "true"}, {"conformant": True, "summary": {"fail": 0}, "reports": []}]
        for value in (1, False, None, "0"):
            doc = bridge_payload()
            doc["summary"]["fail"] = value
            cases.append(doc)
        for value in (None, [], {"conformant": False}):
            doc = bridge_payload()
            doc["reports"] = [value]
            cases.append(doc)
        for doc in cases:
            with self.subTest(doc=doc):
                report = self.bridge_check(json.dumps(doc))
                self.assertTrue(gate.has_failures(report))
                self.assertEqual(report["results"][0]["code"], "AISP_E_CANDIDATE_BRIDGE_VALIDATION")

    def test_bridge_rejects_failed_empty_and_malformed_nested_results(self):
        mutations = [
            ("summary", {"fail": 1}), ("summary", {"fail": False}),
            ("results", []), ("results", [None]),
            ("results", [{"severity": "FAIL", "passed": True, "code": "contradiction"}]),
            ("results", [{"severity": "INFO", "passed": "true", "code": "invalid"}]),
            ("results", [{"severity": [], "passed": True, "code": "invalid"}]),
            ("results", [{"severity": "INFO", "passed": True, "code": {}}]),
        ]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                doc = bridge_payload()
                doc["reports"][0][field] = value
                self.assertTrue(gate.has_failures(self.bridge_check(json.dumps(doc))))

    def test_bridge_preserves_valid_warnings_and_blocks_legacy_release_warnings(self):
        self.assertFalse(gate.has_failures(self.bridge_check(json.dumps(bridge_payload()))))
        for code in ("AISP_W_CUSTOM", "AISP_W_EC7_PROTOCOL"):
            doc = bridge_payload()
            doc["reports"][0]["results"].append({"severity": "WARN", "passed": False, "code": code, "message": "synthetic warning"})
            doc["reports"][0]["summary"]["warn"] = doc["summary"]["warn"] = 1
            report = self.bridge_check(json.dumps(doc))
            self.assertEqual(gate.has_failures(report), code == "AISP_W_EC7_PROTOCOL")
            if code == "AISP_W_CUSTOM":
                self.assertIn(code, {r["code"] for r in report["results"]})

    def test_candidate_json_readers_reject_ambiguity_before_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evals").mkdir()
            (root / "evals/script-behavior.json").write_text('{"scripts": [], "scripts": []}', encoding="utf-8")
            report = {"results": [], "artifacts": {}}
            self.assertIsNone(gate.load_script_evidence(root, report))
            self.assertTrue(gate.has_failures(report))
            (root / "schema.json").write_text('{"$schema": "synthetic", "type": "string", "type": "number"}', encoding="utf-8")
            user = {"aisp_contract": {"resources": [{"path": "schema.json", "kind": "schema"}]}}
            report = {"results": [], "artifacts": {}}
            gate.check_schema_resources(root, user, report)
            self.assertIn("AISP_E_CANDIDATE_SCHEMA_JSON", {r["code"] for r in report["results"]})
            (root / "evals/behavior-cases.json").write_text('{"cases": [], "extension": NaN}', encoding="utf-8")
            user["aisp_contract"]["resources"].append({"path": "evals/behavior-cases.json", "kind": "eval"})
            report = {"results": [], "artifacts": {}}
            gate.check_behavior_cases(root, {}, user, report)
            self.assertIn("AISP_E_CANDIDATE_BEHAVIOR_EVIDENCE_JSON", {r["code"] for r in report["results"]})

    def test_bridge_duplicate_keys_cannot_hide_a_failed_claim(self):
        raw = json.dumps(bridge_payload()).replace('"conformant": true', '"conformant": false, "conformant": true', 1)
        self.assertTrue(gate.has_failures(self.bridge_check(raw)))

    def test_recorded_inline_dispatch_must_honor_explicit_or_default_inline(self):
        original = json.loads((STOCK / "evals/runtime-traces/hard-pass.json").read_text(encoding="utf-8"))
        doc = json.loads((STOCK / "aisp.aisop.json").read_text(encoding="utf-8"))
        node = next(name for name, fn in doc[1]["content"]["functions"].items() if fn.get("execute_mode") == "inline")
        for omitted in (False, True):
            with tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "stock_analysis_aisp"
                skill.mkdir()
                skill_doc = copy.deepcopy(doc)
                if omitted:
                    del skill_doc[1]["content"]["functions"][node]["execute_mode"]
                (skill / "aisp.aisop.json").write_text(json.dumps(skill_doc), encoding="utf-8")
                for mode, dispatched in (("inline", "agent"), ("agent", "inline"), ("agent", "agent")):
                    with self.subTest(omitted=omitted, mode=mode, dispatched=dispatched):
                        trace = copy.deepcopy(original)
                        trace["events"].append({"type": "execute_mode_dispatch", "node": node, "mode": mode, "dispatched_as": dispatched})
                        self.assertEqual(trace_shape_errors(trace), [])
                        report = self.trace_check(trace, skill)
                        self.assertFalse(report["runtime_conformant"])
                        self.assertIn("AISP_E_R7_MODE_MISMATCH", {r["code"] for r in report["results"]})

    def test_inline_check_does_not_add_mandatory_inline_event_coverage(self):
        trace = json.loads((STOCK / "evals/runtime-traces/hard-pass.json").read_text(encoding="utf-8"))
        self.assertTrue(self.trace_check(trace)["runtime_conformant"])
        doc = json.loads((STOCK / "aisp.aisop.json").read_text(encoding="utf-8"))
        node = next(name for name, fn in doc[1]["content"]["functions"].items() if fn.get("execute_mode") == "inline")
        trace["events"].append({"type": "execute_mode_dispatch", "node": node, "mode": "inline", "dispatched_as": "inline"})
        self.assertTrue(self.trace_check(trace)["runtime_conformant"])

    def test_strict_tools_cannot_accept_trace_with_known_inline_dispatch_mismatch(self):
        trace = json.loads((STOCK / "evals/runtime-traces/hard-pass.json").read_text(encoding="utf-8"))
        doc = json.loads((STOCK / "aisp.aisop.json").read_text(encoding="utf-8"))
        node = next(name for name, fn in doc[1]["content"]["functions"].items() if fn.get("execute_mode") == "inline")
        trace["events"].append({"type": "execute_mode_dispatch", "node": node, "mode": "inline", "dispatched_as": "agent"})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps(trace), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                status = validate_main(["--json", "--strict-tools", "--runtime-trace", str(path), str(STOCK)])
            self.assertEqual(status, 1)
            self.assertIn("AISP_E_R6_TRACE_NOT_CONFORMANT", out.getvalue())


if __name__ == "__main__":
    unittest.main()
