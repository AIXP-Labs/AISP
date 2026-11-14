"""Bounded v1 trace validation, including differential schema checks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.aisp_check_runtime_trace import check_trace, trace_shape_errors
from tools.aisp_validate import main as validate_main
from contextlib import redirect_stdout
from io import StringIO


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "examples/aisp/stock_analysis_aisp"
TRACE = SKILL / "evals/runtime-traces/hard-pass.json"


def mutated_traces():
    good = json.loads(TRACE.read_text(encoding="utf-8-sig"))
    yield "valid", good, True
    for field, value in (("runtime", 1), ("runtime", ""), ("skill_id", "wrong"),
                         ("contract_read", "false"), ("contract_visible_to_model", 1),
                         ("tool_enforcement", []), ("events", {}), ("events", [None])):
        bad = copy.deepcopy(good)
        bad[field] = value
        yield field + repr(value), bad, False
    for field in ("runtime", "skill_id", "events"):
        bad = copy.deepcopy(good)
        del bad[field]
        yield "missing " + field, bad, False
    for event in ({}, {"type": 1}, {"type": "sys_call", "bypassed": 1},
                  {"type": "tool_enforcement", "tools": [1]},
                  {"type": "tool_enforcement", "enforcement": {}},
                  {"type": "execute_mode_dispatch", "node": "analyze", "mode": "invalid", "dispatched_as": "agent"},
                  {"type": "execute_mode_dispatch", "node": [], "mode": "agent", "dispatched_as": "agent"},
                  {"type": "execute_mode_dispatch", "node": "analyze", "mode": "agent"}):
        bad = copy.deepcopy(good)
        bad["events"].append(event)
        yield repr(event), bad, False
    extra = copy.deepcopy(good)
    extra["vendor_metadata"] = {"anything": [1, True, None]}
    extra["events"].append({"type": "vendor_event", "extension": "allowed"})
    yield "open extensions", extra, True


class TraceValidationTests(unittest.TestCase):
    def check(self, doc):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            return check_trace(SKILL, path)

    def test_invalid_shapes_fail_without_exceptions(self):
        for label, doc, valid in mutated_traces():
            with self.subTest(label=label):
                self.assertEqual(not trace_shape_errors(doc), valid)
                if not valid:
                    report = self.check(doc)
                    self.assertFalse(report["runtime_conformant"])
                    self.assertIn("AISP_E_TRACE_SHAPE", {x["code"] for x in report["results"]})

    def test_shape_validation_agrees_with_published_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is a development dependency")
        schema = json.loads((ROOT / "schemas/runtime-trace-v1.schema.json").read_text(encoding="utf-8-sig"))
        validator = jsonschema.Draft202012Validator(schema)
        for label, doc, valid in mutated_traces():
            with self.subTest(label=label):
                self.assertEqual(validator.is_valid(doc), valid)
                self.assertEqual(not trace_shape_errors(doc), valid)

    def test_later_dispatch_cannot_hide_an_inline_claim(self):
        for mode, dispatched in (("agent", "inline"), ("inline", "agent")):
            doc = json.loads(TRACE.read_text(encoding="utf-8-sig"))
            doc["events"].insert(0, {"type": "execute_mode_dispatch", "node": "analyze", "mode": mode, "dispatched_as": dispatched})
            report = self.check(doc)
            self.assertIn("AISP_E_R7_COLLAPSED_INLINE", {x["code"] for x in report["results"]})

    def test_conflicting_tool_events_fail(self):
        doc = json.loads(TRACE.read_text(encoding="utf-8-sig"))
        doc["events"].append({"type": "tool_enforcement", "enforcement": "advisory"})
        report = self.check(doc)
        self.assertIn("AISP_E_R6_CONFLICT", {x["code"] for x in report["results"]})

    def test_duplicate_and_non_json_input_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            for raw in ('{"runtime":"first","runtime":"second"}', '{"extra":NaN}'):
                path.write_text(raw, encoding="utf-8")
                report = check_trace(SKILL, path)
                self.assertIn("AISP_E_INPUT", {x["code"] for x in report["results"]})

    def test_static_validator_rejects_truthy_non_boolean_claims(self):
        doc = json.loads(TRACE.read_text(encoding="utf-8-sig"))
        doc["contract_read"] = "false"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            out = StringIO()
            with redirect_stdout(out):
                code = validate_main([str(SKILL), "--json", "--strict-tools", "--runtime-trace", str(path)])
            self.assertEqual(code, 1)
            self.assertIn("AISP_E_INPUT", out.getvalue())
