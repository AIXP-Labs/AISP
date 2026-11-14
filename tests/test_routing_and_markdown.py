"""Error-route, trace-consistency and rendered-Markdown regression guards."""
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.aisp_check_runtime_trace import check_trace
from tools.aisp_validate import main, validate_skill
from tools.check_doc_sync import check_protocol_structure
from tools.check_doc_sync import main as doc_main
from tools.check_markdown_links import check_links, heading_anchors


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"
STOCK = ROOT / "examples/aisp/stock_analysis_aisp"


def load_script(name):
    spec = importlib.util.spec_from_file_location("review_" + name, CREATOR / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


light = load_script("validate_aisp_skill")
simulator = load_script("simulate_aisp_flow")


class RoutingAndMarkdownTests(unittest.TestCase):
    def test_fenced_headings_do_not_create_anchors_or_consume_suffixes(self):
        for marker in ("```", "````", "~~~"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / "README.md"
                p.write_text(f"# Same\n{marker}markdown\n# Ghost\n# Same\n{marker}\n# Same\n[bad](#ghost)\n", encoding="utf-8")
                self.assertEqual(heading_anchors(p), {"same", "same-1"})
                self.assertIn("missing anchor", check_links(Path(tmp), [p.name])[0]["message"])

    def test_shorter_fence_does_not_close_a_longer_code_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("````markdown\n```\n# Ghost\n````\n# Real\n", encoding="utf-8")
            self.assertEqual(heading_anchors(p), {"real"})

    def test_fenced_and_inline_example_links_are_not_rendered_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("```markdown\n[example](absent.md)\n```\n`[inline](also-absent.md)`\n# Real\n[valid](#real)\n", encoding="utf-8")
            self.assertEqual(check_links(Path(tmp), [p.name]), [])

    def test_real_link_line_numbers_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("```\n[example](absent.md)\n```\n\n[real](missing.md)\n", encoding="utf-8")
            problems = check_links(Path(tmp), [p.name])
            self.assertEqual(len(problems), 1)
            self.assertEqual(problems[0]["line"], 5)

    def test_code_formatted_link_labels_still_validate_their_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# Real\n[`good`](#real)\n[`bad`](missing.md)\n`[example](not-a-link.md)`\n", encoding="utf-8")
            problems = check_links(Path(tmp), [p.name])
            self.assertEqual(len(problems), 1)
            self.assertEqual(problems[0]["link"], "missing.md")

    def test_missing_and_external_scan_targets_fail_before_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            external = Path(tmp) / "outside.md"
            external.write_text("# Outside", encoding="utf-8")
            for target in ("missing.md", str(external)):
                with self.subTest(target=target), patch.object(Path, "read_text") as read:
                    problems = check_links(root, [target])
                    self.assertTrue(problems)
                    read.assert_not_called()

    def test_encoded_unsafe_schemes_and_local_absolute_paths_fail(self):
        for target in ("%46ile%3A/tmp/private.txt", "JavaScript&#58;alert(1)", "C:/outside.md"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / "README.md"
                p.write_text(f"[unsafe]({target})\n", encoding="utf-8")
                self.assertTrue(check_links(Path(tmp), [p.name]))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a&b.md").write_text("# Real\n", encoding="utf-8")
            (root / "README.md").write_text("[entity](a&amp;b.md)\n", encoding="utf-8")
            self.assertEqual(check_links(root, ["README.md"]), [])

    def test_protocol_layout_must_not_exist_only_inside_a_code_fence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "protocol.md"
            text = (ROOT / "specification/AISP_Protocol.md").read_text(encoding="utf-8")
            p.write_text("````markdown\n" + text + "\n````\n", encoding="utf-8")
            self.assertTrue(check_protocol_structure(p))

    def test_doc_sync_missing_root_fails_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                code = doc_main(["--root", str(Path(tmp) / "missing")])
            self.assertEqual(code, 1)
            self.assertIn("could not complete", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())

    def test_core_and_lightweight_reject_dangling_or_malformed_on_error(self):
        for routing in (None, [], {"default": []}, {"default": "missing"}, {"default": "end_node"}):
            with self.subTest(routing=routing), tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "simple_aisp"
                skill.mkdir()
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["functions"]["start"]["on_error"] = routing
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                valid = routing == {"default": "end_node"}
                a = {r["code"] for r in validate_skill(skill)["results"]}
                b = {r["code"] for r in light.validate(str(skill))["issues"]}
                self.assertEqual("AISP_E_M1_ON_ERROR" not in a, valid)
                self.assertEqual("AISP_E_M1_ON_ERROR" not in b, valid)

    def test_lightweight_rejects_bad_roles_ambiguous_json_and_edge_shapes(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        cases = []
        doc = copy.deepcopy(seed)
        doc[0]["role"] = "user"
        cases.append((json.dumps(doc), "AISP_E_M1_ROLES"))
        cases.append((json.dumps(seed).replace('"version": "1.0.0"', '"version": "1.0.0", "version": "1.0.0"'), "AISP_E_M1_JSON"))
        for spec in (None, {"next": 1}, {"branches": []}):
            doc = copy.deepcopy(seed)
            doc[1]["content"]["aisop"]["main"]["start"] = spec
            cases.append((json.dumps(doc), "AISP_E_M1_GRAPH" if spec is None else "AISP_E_M1_EDGE_SHAPE"))
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "simple_aisp"
            skill.mkdir()
            for text, expected in cases:
                with self.subTest(expected=expected):
                    (skill / "aisp.aisop.json").write_text(text, encoding="utf-8")
                    self.assertIn(expected, {r["code"] for r in light.validate(str(skill))["issues"]})

    def test_simulator_checks_each_graph_owner_for_shared_functions(self):
        user = {"aisop": {
            "main": {"shared": {"next": ["handler"]}, "handler": {}},
            "research": {"shared": {"next": ["done"]}, "done": {}},
        }, "functions": {
            "shared": {"step1": "work", "on_error": {"default": "handler"}},
            "handler": {"step1": "handle"}, "done": {"step1": "finish"},
        }, "aisp_contract": {"non_negotiable": [{"enforced_by": "aisop.main"}]}}
        report = {"failures": [], "static": {}}
        simulator.check_static({"tools": []}, user, report)
        self.assertTrue(any("STATIC.on_error" in message and "research" in message for message in report["failures"]))

    def test_simulator_binding_requires_numeric_steps_and_actual_calls(self):
        graphs = {"main": {"start": {}}}
        for binding, text, expected in (
            ("start.step1:sys.assert", "sys.assert('true')", True),
            ("start.step1:sys.assert", "sys.assert_fake('true')", False),
            ("start.step1:sys.assert", "Mention sys.assert in prose", False),
            ("start.step_note:sys.assert", "sys.assert('true')", False),
            ("main", "sys.assert('true')", False),
        ):
            with self.subTest(binding=binding, text=text):
                functions = {"start": {"step1": text, "step_note": text}}
                self.assertEqual(simulator._resolve_enforced_by(binding, graphs, functions, []), expected)

    def test_contradictory_contract_flags_fail_trace_and_strict_tools(self):
        good = json.loads((STOCK / "evals/runtime-traces/hard-pass.json").read_text(encoding="utf-8"))
        for field, code in (("contract_read", "AISP_E_R1_CONFLICT"), ("contract_visible_to_model", "AISP_E_R3_CONFLICT")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                doc = copy.deepcopy(good)
                doc[field] = False
                p = Path(tmp) / "trace.json"
                p.write_text(json.dumps(doc), encoding="utf-8")
                result = check_trace(STOCK, p)
                self.assertFalse(result["runtime_conformant"])
                self.assertIn(code, {r["code"] for r in result["results"]})
                output = io.StringIO()
                with redirect_stdout(output):
                    status = main(["--json", "--strict-tools", "--runtime-trace", str(p), str(STOCK)])
                self.assertEqual(status, 1)
                self.assertIn("AISP_E_R6_TRACE_NOT_CONFORMANT", output.getvalue())
                del doc[field]
                p.write_text(json.dumps(doc), encoding="utf-8")
                self.assertTrue(check_trace(STOCK, p)["runtime_conformant"])
