"""Literal mode gates and stdin-only examples must fail closed on bad input."""
import importlib.util
import itertools
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import aisp_validate as validator
from tools.aisp_hash import strict_json_loads
from tools.aisp_readme import render_readme
from tools.aisp_skill_md import render_skill_md


ROOT = Path(__file__).resolve().parents[1]
STOCK = ROOT / "examples/aisp/stock_analysis_aisp"
RESEARCH = ROOT / "examples/aisp/aisp_creator_evolution_aisp/scripts/check_research_result.py"
INDICATORS = STOCK / "scripts/indicators.py"
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"
spec = importlib.util.spec_from_file_location("review_indicators", INDICATORS)
indicators = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indicators)


class ResourceUsageAndExampleInputTests(unittest.TestCase):
    def codes(self, step, path="scripts/tool.py", mode="read_only"):
        report = validator.Reporter()
        resources = {validator._normalize_rel(path): {"mode": mode}}
        validator._check_resource_usage(resources, {"node": {"step1": step}}, report, Path("aisp.aisop.json"))
        return {r.code for r in report.results}

    def run_script(self, script, raw):
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        result = subprocess.run([sys.executable, "-B", str(script)], input=raw, capture_output=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
        self.assertNotIn(b"Traceback", result.stderr)
        return result.returncode, strict_json_loads(result.stdout.decode("utf-8"))

    def test_whitespace_read_calls_cannot_read_execute_only_resources(self):
        for step in ("sys.io.read ('scripts/tool.py')", "sys.io.read\t(\n'scripts/tool.py')"):
            with self.subTest(step=step):
                self.assertIn("AISP_E_SE3_MODE_GATE", self.codes(step, mode="execute_only"))

    def test_run_forms_detect_read_only_script_execution(self):
        cases = [
            "sys.run ('python scripts/tool.py')",
            "sys.run.bg ('python scripts/tool.py')",
            '''sys.run('python "scripts/tool.py"')''',
            '''sys.run('"C:/Program Files/Python/python.exe" -B "scripts/tool.py"')''',
            '''sys.run('/usr/bin/python3 -B scripts/tool.py')''',
            r'''sys.run('python "scripts\\tool.py"')''',
        ]
        for step in cases:
            with self.subTest(step=step):
                self.assertEqual(self.codes(step), {"AISP_E_SE3_MODE_GATE"})
                self.assertEqual(self.codes(step, mode="execute_only"), set())

    def test_quoted_space_paths_and_lexical_aliases_keep_their_modes(self):
        for path in ("scripts/tool.py", "scripts/my tool.py"):
            for used in (path, path.replace("/", "/./"), path.replace("/", "//")):
                with self.subTest(path=path, used=used):
                    step = 'sys.run(' + repr('python "' + used + '"') + ')'
                    self.assertEqual(self.codes(step, path), {"AISP_E_SE3_MODE_GATE"})
        self.assertNotEqual(validator._normalize_rel(".env"), validator._normalize_rel("env"))
        self.assertNotEqual(validator._normalize_rel("/env"), validator._normalize_rel("env"))
        self.assertIn("..", validator._normalize_rel("scripts/../tool.py"))

    def test_similarly_named_calls_are_not_system_calls(self):
        for name in ("not_sys.run", "other.sys.run", "sys.run_fake"):
            self.assertEqual(validator._extract_sys_run_scripts(name + "('python scripts/tool.py')"), [])
        self.assertEqual(validator._extract_sys_run_scripts('sys.run(' + repr('python "scripts/tool.py') + ')'), [])

    def test_python_arguments_do_not_override_an_earlier_non_python_script(self):
        for command in ("bash scripts/driver.sh data/config.py", "scripts/driver.sh data/config.py"):
            with self.subTest(command=command):
                step = "sys.run(" + repr(command) + ")"
                self.assertEqual(validator._extract_sys_run_scripts(step), ["scripts/driver.sh"])
                self.assertEqual(self.codes(step, path="scripts/driver.sh"), {"AISP_E_SE3_MODE_GATE"})

    def test_python_command_module_and_help_arguments_are_not_script_operands(self):
        for command in ('python -c "print(1)" data/config.py', "python -m package data/config.py",
                        "python --help data/config.py", "python --version data/config.py"):
            with self.subTest(command=command):
                self.assertEqual(validator._extract_sys_run_scripts("sys.run(" + repr(command) + ")"), [])

    def test_combined_python_mode_and_help_flags_do_not_execute_data_arguments(self):
        for command in ('python -Bc "print(1)" data/config.py', "python -Bm package data/config.py",
                        "python -hB data/config.py", "python -BV data/config.py",
                        "python --help-env data/config.py", "python -B - data/config.py"):
            with self.subTest(command=command):
                self.assertEqual(validator._extract_sys_run_scripts("sys.run(" + repr(command) + ")"), [])

    def test_combined_python_options_still_find_the_actual_file(self):
        for command in ('python -BWignore scripts/tool.py data/config.py',
                        'python -BXutf8 scripts/tool.py',
                        'python -IBW data/filter.py scripts/tool.py',
                        'python -IBX utf8 scripts/tool.py'):
            with self.subTest(command=command):
                step = "sys.run(" + repr(command) + ")"
                self.assertEqual(validator._extract_sys_run_scripts(step), ["scripts/tool.py"])
                self.assertEqual(self.codes(step), {"AISP_E_SE3_MODE_GATE"})

    def test_python_file_boundary_and_option_values_are_not_reparsed_as_modes(self):
        cases = [
            (["python", "-IB", "scripts/tool.py", "--help", "data/config.py"], "scripts/tool.py"),
            (["python", "-W", "--help", "scripts/tool.py"], "scripts/tool.py"),
            (["python", "-X", "--help", "scripts/tool.py"], "scripts/tool.py"),
            (["python", "--", "-W", "data/config.py"], "-W"),
            (["python", "--", "-", "data/config.py"], None),
            (["python", "-IBmc", "data/config.py"], None),
        ]
        for parts, expected in cases:
            with self.subTest(parts=parts):
                self.assertEqual(validator._command_script(parts), expected)

    def test_data_arguments_of_unclassified_tools_are_not_called_executed_scripts(self):
        for command in ("cat data/config.py", "grep key data/config.py", "echo scripts/tool.py",
                        'bash -c "cat data/config.py"', "node --help data/config.py"):
            with self.subTest(command=command):
                self.assertEqual(validator._extract_sys_run_scripts("sys.run(" + repr(command) + ")"), [])
        for command, expected in (("bash scripts/tool.sh data/config.py", "scripts/tool.sh"),
                                  ("/bin/sh scripts/tool.sh data/config.py", "scripts/tool.sh"),
                                  ("./scripts/tool.sh data/config.py", "./scripts/tool.sh")):
            with self.subTest(command=command):
                self.assertEqual(validator._extract_sys_run_scripts("sys.run(" + repr(command) + ")"), [expected])

    def test_real_python_combined_c_mode_keeps_later_filename_as_data(self):
        code = "import json,sys; print(json.dumps(sys.argv))"
        proc = subprocess.run([sys.executable, "-Bc", code, "data/config.py"], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), ["-c", "data/config.py"])
        self.assertEqual(validator._command_script([sys.executable, "-Bc", code, "data/config.py"]), None)

    def test_python_option_values_do_not_steal_the_script_operand(self):
        for command in (
            'python -W "data/filter.py" -B "scripts/my tool.py" data/config.py',
            'python -X "data/option.py" "scripts/my tool.py"',
            'python --check-hash-based-pycs always "scripts/my tool.py"',
            'python -Xutf8 -Wignore "scripts/my tool.py"',
            'python -IB "scripts/my tool.py"',
            'py -3.11 -B "scripts/my tool.py"',
        ):
            with self.subTest(command=command):
                step = "sys.run(" + repr(command) + ")"
                self.assertEqual(validator._extract_sys_run_scripts(step), ["scripts/my tool.py"])
                self.assertEqual(self.codes(step, path="scripts/my tool.py"), {"AISP_E_SE3_MODE_GATE"})

    def test_python_end_of_options_and_extensionless_script_operands(self):
        for command, path in (("python -- scripts/driver.py data/argument.py", "scripts/driver.py"),
                              ("python driver data/argument.py", "driver")):
            with self.subTest(command=command):
                step = "sys.run(" + repr(command) + ")"
                self.assertEqual(validator._extract_sys_run_scripts(step), [path])
                self.assertEqual(self.codes(step, path=path), {"AISP_E_SE3_MODE_GATE"})
        for command in ("python -X", "python --"):
            self.assertEqual(validator._extract_sys_run_scripts("sys.run(" + repr(command) + ")"), [])

    def test_conflicting_normalized_alias_modes_cannot_override_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "simple_aisp"
            (skill / "scripts").mkdir(parents=True)
            (skill / "scripts/tool.py").write_text("pass", encoding="utf-8")
            for first, second in (("execute_only", "read_only"), ("read_only", "execute_only"),
                                  ("read_only", "read_and_execute")):
                with self.subTest(first=first, second=second):
                    contract = {"resources": [
                        {"id": "one", "path": "scripts/tool.py", "kind": "script", "mode": first, "requires_tools": ["shell"]},
                        {"id": "two", "path": "scripts/./tool.py", "kind": "script", "mode": second, "requires_tools": ["shell"]},
                    ]}
                    report = validator.Reporter()
                    resources = validator._check_resources(contract, {}, skill, root, report, skill / "aisp.aisop.json")
                    self.assertIn("AISP_E_SE3_MODE_GATE", {r.code for r in report.results})
                    self.assertEqual(resources["scripts/tool.py"]["mode"], first)

    def test_consistent_aliases_do_not_become_a_blanket_duplicate_ban(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "simple_aisp"
            (skill / "scripts").mkdir(parents=True)
            (skill / "scripts/tool.py").write_text("pass", encoding="utf-8")
            contract = {"resources": [
                {"id": "one", "path": "scripts/tool.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"]},
                {"id": "two", "path": "scripts//./tool.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"]},
            ]}
            report = validator.Reporter()
            resources = validator._check_resources(contract, {}, skill, root, report, skill / "aisp.aisop.json")
            self.assertEqual(report.results, [])
            self.assertEqual(len(resources), 1)

    def scoped_inventory(self, root):
        skill = root / "simple_aisp"
        (skill / "scripts").mkdir(parents=True)
        (root / "_shared/scripts").mkdir(parents=True)
        for path in (skill / "scripts/tool.py", root / "_shared/scripts/tool.py"):
            path.write_text("pass", encoding="utf-8")
        entries = [
            {"id": "local", "path": "scripts/tool.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"]},
            {"id": "shared", "path": "scripts/tool.py", "scope": "shared", "kind": "script", "mode": "read_only", "requires_tools": ["shell"]},
            {"id": "local_alias", "path": "scripts/./tool.py", "kind": "script", "mode": "read_only", "requires_tools": ["shell"]},
        ]
        return skill, entries

    def test_interleaved_scopes_cannot_hide_conflicts_in_any_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            for order in itertools.permutations(entries):
                with self.subTest(ids=[row["id"] for row in order]):
                    report = validator.Reporter()
                    validator._check_resources({"resources": list(order)}, {}, skill, root, report, skill / "aisp.aisop.json")
                    self.assertIn("AISP_E_SE3_MODE_GATE", {r.code for r in report.results})

    def test_distinct_scopes_remain_valid_but_literal_usage_is_explicitly_ambiguous(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            for order in (entries[:2], entries[1::-1]):
                with self.subTest(ids=[row["id"] for row in order]):
                    report = validator.Reporter()
                    resources = validator._check_resources({"resources": order}, {}, skill, root, report, skill / "aisp.aisop.json")
                    self.assertEqual(report.results, [])
                    validator._check_undeclared_files(resources, skill, report)
                    self.assertEqual(report.results, [])
                    validator._check_resource_usage(resources, {"node": {
                        "step1": "sys.io.read('scripts/tool.py')",
                        "step2": "sys.run('python scripts/tool.py')",
                    }}, report, skill / "aisp.aisop.json")
                    self.assertEqual([r.code for r in report.results], ["AISP_W_M5_AMBIGUOUS_USE"] * 2)
                    self.assertTrue(all(r.severity == "WARN" for r in report.results))

    def test_cross_scope_warning_cannot_downgrade_an_operation_all_modes_forbid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            modes = ("read_only", "execute_only", "read_and_execute")
            actions = (("sys.io.read('scripts/tool.py')", validator.READ_MODES),
                       ("sys.run('python scripts/tool.py')", validator.EXEC_MODES))
            for local_mode, shared_mode, (step, permitted), reverse in itertools.product(modes, modes, actions, (False, True)):
                with self.subTest(local=local_mode, shared=shared_mode, step=step, reverse=reverse):
                    rows = [dict(entries[0], mode=local_mode), dict(entries[1], mode=shared_mode)]
                    if reverse:
                        rows.reverse()
                    report = validator.Reporter()
                    resources = validator._check_resources({"resources": rows}, {}, skill, root, report, skill / "aisp.aisop.json")
                    validator._check_resource_usage(resources, {"node": {"step1": step}}, report, skill / "aisp.aisop.json")
                    denied = not ({local_mode, shared_mode} & permitted)
                    expected = "AISP_E_SE3_MODE_GATE" if denied else "AISP_W_M5_AMBIGUOUS_USE"
                    self.assertEqual([r.code for r in report.results], [expected])
                    self.assertEqual(report.results[0].severity, "FAIL" if denied else "WARN")

    def write_scoped_skill(self, root, local_mode, shared_mode, step):
        skill, entries = self.scoped_inventory(root)
        doc = json.loads(SEED.read_text(encoding="utf-8"))
        doc[1]["content"]["aisp_contract"]["resources"] = [dict(entries[0], mode=local_mode), dict(entries[1], mode=shared_mode)]
        doc[1]["content"]["functions"]["end_node"]["step1"] = step
        (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
        (skill / "SKILL.md").write_text(render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
        (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")
        return skill

    def test_core_all_denied_scopes_fail_without_ambiguity_only_success(self):
        for mode, step in (("read_only", "sys.run('python scripts/tool.py')"),
                           ("execute_only", "sys.io.read('scripts/tool.py')")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                skill = self.write_scoped_skill(Path(tmp), mode, mode, step)
                report = validator.validate_skill(skill, strict_readme=True)
                self.assertFalse(report["conformant"])
                self.assertEqual({r["code"] for r in report["results"] if r["severity"] == "FAIL"}, {"AISP_E_SE3_MODE_GATE"})
                self.assertNotIn("AISP_W_M5_AMBIGUOUS_USE", {r["code"] for r in report["results"]})

    def test_warning_exit_policy_is_distinct_from_scope_and_tools_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.write_scoped_skill(Path(tmp), "execute_only", "read_only", "sys.io.read('scripts/tool.py')")
            for flags, expected_exit in (([], 0), (["--warnings-fail"], 1), (["--strict-tools"], 0),
                                         (["--strict-readme"], 0), (["--strict-tools", "--warnings-fail"], 1)):
                with self.subTest(flags=flags):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        code = validator.main(["--json", *flags, str(skill)])
                    report = json.loads(output.getvalue())["reports"][0]
                    self.assertEqual(code, expected_exit)
                    self.assertTrue(report["conformant"])
                    self.assertEqual(report["fail_count"], 0)
                    self.assertEqual(report["warning_count"], 1)
                    warnings = [r for r in report["results"] if r["severity"] == "WARN"]
                    self.assertEqual([r["code"] for r in warnings], ["AISP_W_M5_AMBIGUOUS_USE"])
                    self.assertNotIn("_declared_modes", output.getvalue())

    def test_warning_help_describes_exit_policy_not_severity_rewriting(self):
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as stopped:
            validator.main(["--help"])
        self.assertEqual(stopped.exception.code, 0)
        text = " ".join(output.getvalue().split())
        self.assertIn("Return exit code 1 when warnings remain", text)
        self.assertIn("keep report severity and conformance unchanged", text)

    def test_missing_scoped_files_do_not_remove_declarations_from_mode_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            paths = (skill / "scripts/tool.py", root / "_shared/scripts/tool.py")
            for absent, all_denied in itertools.product(((), (0,), (1,), (0, 1)), (False, True)):
                with self.subTest(absent=absent, all_denied=all_denied):
                    for index, path in enumerate(paths):
                        path.write_text("pass", encoding="utf-8")
                        if index in absent:
                            path.unlink()
                    rows = [dict(entries[0]), dict(entries[1])]
                    if all_denied:
                        rows[1]["mode"] = "execute_only"
                    report = validator.Reporter()
                    resources = validator._check_resources({"resources": rows}, {}, skill, root, report, skill / "aisp.aisop.json")
                    self.assertEqual(len(resources["scripts/tool.py"]["_resolved_paths"]), 2)
                    validator._check_resource_usage(resources, {"node": {"step1": "sys.io.read('scripts/tool.py')"}}, report, skill / "aisp.aisop.json")
                    self.assertEqual(sum(r.code == "AISP_W_M5_MISSING_RESOURCE" for r in report.results), len(absent))
                    self.assertEqual({r.code for r in report.results if r.severity == "FAIL"},
                                     {"AISP_E_SE3_MODE_GATE"} if all_denied else set())
                    self.assertEqual(any(r.code == "AISP_W_M5_AMBIGUOUS_USE" for r in report.results), not all_denied)

    def test_user_extension_fields_cannot_replace_internal_candidate_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            rows = [dict(row, mode="read_only", _declared_modes=["read_and_execute"], _resolved_paths=[], _resolved="synthetic")
                    for row in entries[:2]]
            contract = {"resources": rows}
            before = json.dumps(contract, sort_keys=True)
            report = validator.Reporter()
            resources = validator._check_resources(contract, {}, skill, root, report, skill / "aisp.aisop.json")
            validator._check_resource_usage(resources, {"node": {"step1": "sys.run('python scripts/tool.py')"}}, report, skill / "aisp.aisop.json")
            self.assertEqual([r.code for r in report.results], ["AISP_E_SE3_MODE_GATE"])
            self.assertEqual(json.dumps(contract, sort_keys=True), before)

    def test_scoped_aliases_of_one_resolved_file_do_not_create_false_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            shared = root / "_shared"
            original = Path.resolve
            def resolve(path, *args, **kwargs):
                if path == shared or shared in path.parents:
                    return original(skill / path.relative_to(shared), *args, **kwargs)
                return original(path, *args, **kwargs)
            rows = [dict(row, mode="read_and_execute") for row in entries[:2]]
            report = validator.Reporter()
            with patch.object(Path, "resolve", resolve):
                resources = validator._check_resources({"resources": rows}, {}, skill, root, report, skill / "aisp.aisop.json")
                validator._check_resource_usage(resources, {"node": {
                    "step1": "sys.io.read('scripts/tool.py')", "step2": "sys.run('python scripts/tool.py')",
                }}, report, skill / "aisp.aisop.json")
            self.assertEqual(len(resources["scripts/tool.py"]["_resolved_paths"]), 1)
            self.assertEqual(report.results, [])

    def test_repeated_consistent_aliases_do_not_change_one_use_severity_or_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            for all_denied in (False, True):
                rows = [dict(entries[0]), dict(entries[1])]
                if all_denied:
                    rows[1]["mode"] = "execute_only"
                for count in (1, 3):
                    with self.subTest(all_denied=all_denied, count=count):
                        report = validator.Reporter()
                        resources = validator._check_resources({"resources": rows * count}, {}, skill, root, report, skill / "aisp.aisop.json")
                        validator._check_resource_usage(resources, {"node": {"step1": "sys.io.read('scripts/tool.py')"}}, report, skill / "aisp.aisop.json")
                        self.assertEqual([r.code for r in report.results],
                                         ["AISP_E_SE3_MODE_GATE" if all_denied else "AISP_W_M5_AMBIGUOUS_USE"])

    def test_multi_target_exit_code_keeps_failures_and_warnings_in_any_position(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            targets = {
                "clean": self.write_scoped_skill(root / "clean", "read_only", "read_only", "Return complete."),
                "warning": self.write_scoped_skill(root / "warning", "execute_only", "read_only", "sys.io.read('scripts/tool.py')"),
                "failure": self.write_scoped_skill(root / "failure", "read_only", "read_only", "sys.run('python scripts/tool.py')"),
                "missing": root / "missing",
            }
            orders = [("clean",), ("warning",), ("failure",), ("clean", "warning"), ("warning", "clean"),
                      ("clean", "failure"), ("failure", "warning"), ("warning", "failure"),
                      ("clean", "missing"), ("missing", "warning")]
            for labels, warnings_fail in itertools.product(orders, (False, True)):
                with self.subTest(labels=labels, warnings_fail=warnings_fail):
                    output = io.StringIO()
                    args = ["--json", *(["--warnings-fail"] if warnings_fail else []), *[str(targets[label]) for label in labels]]
                    with redirect_stdout(output):
                        code = validator.main(args)
                    reports = json.loads(output.getvalue())["reports"]
                    self.assertEqual(len(reports), len(labels))
                    self.assertEqual(code, int(any(label in {"failure", "missing"} for label in labels)
                                               or (warnings_fail and "warning" in labels)))
                    for label, report in zip(labels, reports):
                        self.assertEqual(report["conformant"], label in {"clean", "warning"})
                        self.assertEqual(report["warning_count"], int(label == "warning"))

    def test_real_cli_exit_status_matches_warning_policy_without_rewriting_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                ("clean", "read_only", "read_only", "Return complete.", ["--warnings-fail"], 0, True),
                ("warning", "execute_only", "read_only", "sys.io.read('scripts/tool.py')", ["--warnings-fail"], 1, True),
                ("failure", "read_only", "read_only", "sys.run('python scripts/tool.py')", [], 1, False),
            ]
            for name, local_mode, shared_mode, step, flags, expected_exit, conformant in cases:
                with self.subTest(name=name):
                    skill = self.write_scoped_skill(root / name, local_mode, shared_mode, step)
                    proc = subprocess.run([sys.executable, "-B", str(ROOT / "tools/aisp_validate.py"), "--json", *flags, str(skill)],
                                          capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                    self.assertEqual(proc.returncode, expected_exit, proc.stderr)
                    self.assertNotIn(b"Traceback", proc.stderr)
                    self.assertEqual(json.loads(proc.stdout)["reports"][0]["conformant"], conformant)

    def test_internal_candidate_modes_never_mutate_or_merge_contract_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill, entries = self.scoped_inventory(root)
            contract = {"resources": entries[:2]}
            before = json.dumps(contract, sort_keys=True)
            report = validator.Reporter()
            resources = validator._check_resources(contract, {}, skill, root, report, skill / "aisp.aisop.json")
            self.assertEqual(json.dumps(contract, sort_keys=True), before)
            self.assertEqual(resources["scripts/tool.py"]["_declared_modes"], {"execute_only", "read_only"})
            validator._check_resource_usage(resources, {"node": {"step1": "sys.io.read('scripts/tool.py')"}}, report, skill / "aisp.aisop.json")
            self.assertEqual([r.code for r in report.results], ["AISP_W_M5_AMBIGUOUS_USE"])

    def test_core_conflict_and_ambiguity_reports_do_not_depend_on_projection_drift(self):
        for conflict in (False, True):
            with self.subTest(conflict=conflict), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                skill, entries = self.scoped_inventory(root)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["aisp_contract"]["resources"] = entries if conflict else entries[:2]
                doc[1]["content"]["functions"]["end_node"]["step1"] = "sys.io.read('scripts/tool.py')"
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                (skill / "SKILL.md").write_text(render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
                (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")
                report = validator.validate_skill(skill, strict_readme=True)
                self.assertEqual(report["conformant"], not conflict)
                self.assertIn("AISP_W_M5_AMBIGUOUS_USE", {r["code"] for r in report["results"]})
                self.assertEqual({r["code"] for r in report["results"] if r["severity"] == "FAIL"},
                                 {"AISP_E_SE3_MODE_GATE"} if conflict else set())

    def test_core_rejects_alias_mode_conflict_with_other_projections_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "simple_aisp"
            (skill / "scripts").mkdir(parents=True)
            (skill / "scripts/tool.py").write_text("pass", encoding="utf-8")
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[1]["content"]["aisp_contract"]["resources"] = [
                {"id": "one", "path": "scripts/tool.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"]},
                {"id": "two", "path": "scripts/./tool.py", "kind": "script", "mode": "read_only", "requires_tools": ["shell"]},
            ]
            (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
            (skill / "SKILL.md").write_text(render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
            (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")
            report = validator.validate_skill(skill, strict_readme=True)
            self.assertFalse(report["conformant"])
            self.assertEqual({r["code"] for r in report["results"] if r["severity"] == "FAIL"}, {"AISP_E_SE3_MODE_GATE"})

    def test_core_validator_wires_background_literal_mode_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "simple_aisp"
            (skill / "scripts").mkdir(parents=True)
            (skill / "scripts/tool.py").write_text("raise RuntimeError('must never execute during static validation')", encoding="utf-8")
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "tool", "path": "scripts/tool.py", "mode": "read_only", "kind": "script", "requires_tools": ["shell"]}]
            doc[1]["content"]["functions"]["end_node"]["step1"] = '''sys.run.bg ('python "scripts/./tool.py"')'''
            (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
            report = validator.validate_skill(skill)
            self.assertFalse(report["conformant"])
            self.assertIn("AISP_E_SE3_MODE_GATE", {r["code"] for r in report["results"]})

    def test_research_checker_rejects_duplicate_keys_and_non_json_constants(self):
        for raw in (
            '{"status":"incomplete","status":"complete","findings":[],"citations":[]}',
            '{"status":"complete","findings":[],"citations":[],"extra":NaN}',
            '{"status":"complete","findings":[],"citations":[],"extra":Infinity}',
            '{bad',
        ):
            with self.subTest(raw=raw):
                code, result = self.run_script(RESEARCH, raw)
                self.assertEqual(code, 1)
                self.assertFalse(result["valid"])
                self.assertTrue(result["errors"])

    def test_research_checker_stays_an_envelope_check_not_grounding_proof(self):
        for status in ("incomplete", "complete"):
            value = {"status": status, "findings": [], "citations": []}
            code, result = self.run_script(RESEARCH, b"\xef\xbb\xbf" + json.dumps(value).encode("utf-8"))
            self.assertEqual(code, 0)
            self.assertTrue(result["valid"])

    def test_indicators_compute_known_population_statistics(self):
        result = indicators.compute([{"close": str(x)} for x in (1, 2, 3)])
        self.assertEqual(result, {"moving_average": 2.0, "volatility": 0.8165, "trend": "up", "first_close": 1.0, "last_close": 3.0, "samples": 3})
        self.assertEqual(indicators.compute([{"close": "3"}])["volatility"], 0.0)

    def test_volatility_does_not_use_a_prematurely_rounded_mean(self):
        result = indicators.compute([{"close": "0.000001"}, {"close": "0.000099"}])
        self.assertEqual(result["volatility"], 0.0)

    def test_invalid_price_series_are_nonzero_strict_json_errors(self):
        for raw in ("close\nNaN\n", "close\nInfinity\n", "close\n1e999\n", "close\nabc\n",
                    "close\n1\n \n", "date,close\n2026-01-01,\n", "close\n1,2\n"):
            with self.subTest(raw=raw):
                code, result = self.run_script(INDICATORS, raw)
                self.assertEqual(code, 1)
                self.assertIn("error", result)
                self.assertNotIn("moving_average", result)

    def test_empty_missing_duplicate_and_malformed_close_columns_fail(self):
        for raw in ("", "date,close\n", "date,open\n2026-01-01,10\n", "close,close\n10,20\n", 'close\n"1\n'):
            with self.subTest(raw=raw):
                code, result = self.run_script(INDICATORS, raw)
                self.assertEqual(code, 1)
                self.assertIn("error", result)

    def test_indicators_accept_utf8_bom_and_large_finite_samples(self):
        code, result = self.run_script(INDICATORS, b"\xef\xbb\xbfclose,note\n1,fixture\n3,fixture\n")
        self.assertEqual(code, 0)
        self.assertEqual(result["moving_average"], 2.0)
        self.assertEqual(result["volatility"], 1.0)
        code, result = self.run_script(INDICATORS, "close\n-1e308\n1e308\n")
        self.assertEqual(code, 0)
        self.assertEqual(result["volatility"], 1e308)
        self.assertTrue(all(math.isfinite(x) for x in result.values() if isinstance(x, float)))
        code, result = self.run_script(INDICATORS, (STOCK / "data/sample_prices.csv").read_bytes())
        self.assertEqual(code, 0)
        self.assertGreater(result["samples"], 0)

    def test_csv_lf_crlf_and_cr_newlines_remain_equivalent(self):
        expected = None
        for newline in ("\n", "\r\n", "\r"):
            for bom in (b"", b"\xef\xbb\xbf"):
                with self.subTest(newline=newline, bom=bool(bom)):
                    raw = bom + newline.join(("close", "1", "3", "")).encode("utf-8")
                    code, result = self.run_script(INDICATORS, raw)
                    self.assertEqual(code, 0)
                    if expected is None:
                        expected = result
                    self.assertEqual(result, expected)

    def test_quoted_csv_embedded_newlines_do_not_split_data_rows(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=newline):
                raw = "close,note" + newline + '1,"first' + newline + 'second"' + newline + "3,fixture" + newline
                code, result = self.run_script(INDICATORS, raw)
                self.assertEqual(code, 0)
                self.assertEqual(result["samples"], 2)
                self.assertEqual(result["moving_average"], 2.0)

    def test_csv_error_policy_is_identical_for_all_supported_line_endings(self):
        cases = [("close", "NaN", ""), ("close", "abc", ""), ("close", "", ""),
                 ("close,close", "1,3", ""), ("close", '"1', "")]
        for newline, lines, bom in itertools.product(("\n", "\r\n", "\r"), cases, (b"", b"\xef\xbb\xbf")):
            with self.subTest(newline=newline, lines=lines, bom=bool(bom)):
                code, result = self.run_script(INDICATORS, bom + newline.join(lines).encode("utf-8"))
                self.assertEqual(code, 1)
                self.assertIn("error", result)

    def test_csv_escaped_quotes_commas_and_mixed_newlines_remain_valid(self):
        raw = 'close,note\r\n1,"first ""quoted"", line\rsecond"\n3,end\r'
        code, result = self.run_script(INDICATORS, raw)
        self.assertEqual(code, 0)
        self.assertEqual(result["samples"], 2)
        self.assertEqual(result["moving_average"], 2.0)


if __name__ == "__main__":
    unittest.main()
