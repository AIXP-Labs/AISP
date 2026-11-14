"""Offline version-policy and migration checks, not real-host certification."""
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import aisp_skill_md as tool


ROOT = Path(__file__).resolve().parents[1]


class ExecutorVersionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.skill = Path(self.temp.name) / "simple_aisp"
        self.skill.mkdir()
        shutil.copy2(ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json", self.skill)

    def run_tool(self, *args):
        stream = io.StringIO()
        with redirect_stdout(stream), redirect_stderr(stream):
            result = tool.main([str(self.skill), *args])
        return result, stream.getvalue()

    def write(self, requirement=">=1.0.0"):
        result, output = self.run_tool("--write", "--executor-version-requirement", requirement)
        self.assertEqual(result, 0, output)
        return tool._executor_input(self.skill)[0]

    def test_default_is_resolved_once_and_frozen_without_runtime_lookup(self):
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=1.0.10") as resolver:
            self.assertEqual(self.run_tool("--write")[0], 0)
            resolver.assert_called_once()
        values, _ = tool._executor_input(self.skill)
        self.assertEqual(values[tool.VERSION_POLICY_KEY], {"requirement": ">=1.0.10", "source": "latest_stable"})
        self.assertEqual(values["executor_install"], 'python -m pip install --upgrade "soulrun>=1.0.10"')
        before = (self.skill / "SKILL.md").read_bytes()
        with patch.object(tool.urllib.request, "urlopen", side_effect=AssertionError("checks/regeneration must be offline")):
            for action in ("--check", "--print", "--write"):
                self.assertEqual(self.run_tool(action)[0], 0)
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), before)

    def test_explicit_floor_and_exact_pin_override_default_and_refresh(self):
        for requirement in (">=1.0.0", "==1.0.0"):
            with self.subTest(requirement=requirement):
                with patch.object(tool, "_latest_soulrun_requirement", side_effect=AssertionError("explicit wins")):
                    values = self.write(requirement)
                    self.assertEqual(self.run_tool("--write", "--refresh-executor-version")[0], 0)
                    self.assertEqual(tool._executor_input(self.skill)[0], values)
                self.assertEqual(values[tool.VERSION_POLICY_KEY]["source"], "explicit")
                expected = ('python -m pip install "soulrun==1.0.0"' if requirement.startswith("==")
                            else 'python -m pip install --upgrade "soulrun>=1.0.0"')
                self.assertEqual(values["executor_install"], expected)

    def test_only_explicit_refresh_changes_a_default_managed_bound(self):
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=1.0.1"):
            self.assertEqual(self.run_tool("--write")[0], 0)
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=1.0.2") as resolver:
            self.assertEqual(self.run_tool("--write", "--refresh-executor-version")[0], 0)
            resolver.assert_called_once()
        values, _ = tool._executor_input(self.skill)
        self.assertEqual(values[tool.VERSION_POLICY_KEY]["requirement"], ">=1.0.2")
        self.assertIn("soulrun>=1.0.2", values["executor_install"])
        with patch.object(tool, "_latest_soulrun_requirement", side_effect=AssertionError("argument wins")):
            self.assertEqual(self.run_tool("--write", "--refresh-executor-version", "--executor-version-requirement", "==1.0.0")[0], 0)

    def test_mismatched_managed_install_is_updated_with_explicit_or_refreshed_policy(self):
        for previous, requirement, install in (
            ("==1.0.0", "==1.0.0", 'python -m pip install --upgrade "soulrun>=1.0.1"'),
            (">=1.0.1", ">=1.0.0", 'python -m pip install "soulrun==0.9.0"'),
        ):
            with self.subTest(requirement=requirement):
                values = {**tool.EXECUTOR_DEFAULTS, "executor_install": install,
                          tool.VERSION_POLICY_KEY: {"requirement": previous, "source": "explicit"}}
                (self.skill / "SKILL.md").write_text(tool._render_interface(self.skill, values), encoding="utf-8")
                with patch.object(tool, "_latest_soulrun_requirement", side_effect=AssertionError("explicit wins")):
                    selected = self.write(requirement)
                self.assertEqual(selected["executor_install"], tool._soulrun_install(requirement))
        values[tool.VERSION_POLICY_KEY] = {"requirement": ">=1.0.1", "source": "latest_stable"}
        selected = tool._select_values(values, refresh=True, resolver=lambda: ">=1.0.10")
        self.assertEqual(selected["executor_install"], tool._soulrun_install(">=1.0.10"))

    def test_custom_install_commands_are_never_rewritten_as_managed_commands(self):
        for install in ('custom-install "soulrun==1.0.0"',
                        'python -m pip install --index-url https://example.invalid "soulrun>=1.0.0"',
                        'python -m pip install "soulrun>=1.0.0"',
                        'python -m pip install --upgrade "soulrun>=1.0.0" && echo custom'):
            with self.subTest(install=install):
                values = {**tool.EXECUTOR_DEFAULTS, "executor_install": install}
                selected = tool._select_values(values, requirement="==1.0.0")
                self.assertEqual(selected["executor_install"], install)
        values = {**tool.EXECUTOR_DEFAULTS, "executor": "another-executor"}
        self.assertEqual(tool._select_values(values, requirement="==1.0.0")["executor_install"],
                         tool.EXECUTOR_DEFAULTS["executor_install"])

    def test_version_policy_is_small_strict_and_not_a_shell_expression(self):
        for requirement in ("latest", ">=latest", "1.0.0", "=1.0.0", ">1.0.0", ">=1.0", ">=01.0.0", ">=1.0.0;echo injected", ">=1.0.0,<2.0.0", None, 1):
            with self.subTest(requirement=requirement), self.assertRaises(tool.SkillInterfaceError):
                tool._policy({"requirement": requirement, "source": "explicit"})
        for value in ({"requirement": ">=1.0.0"}, {"requirement": ">=1.0.0", "source": "invented"},
                      {"requirement": "==1.0.0", "source": "latest_stable"}, "not an object"):
            with self.subTest(value=value), self.assertRaises(tool.SkillInterfaceError):
                tool._policy(value)

    def test_other_executors_keep_commands_and_never_fall_back_to_soulrun(self):
        values = {key: "demorun " + key for key in tool.EXECUTOR_DEFAULTS}
        with patch.object(tool, "_latest_soulrun_requirement", side_effect=AssertionError("no vendor fallback")):
            explicit = tool._select_values(values, requirement="==2.4.0")
            for key in tool.EXECUTOR_DEFAULTS:
                self.assertEqual(explicit[key], values[key])
            self.assertEqual(tool._select_values(explicit, refresh=True), explicit)
            with self.assertRaises(tool.SkillInterfaceError):
                tool._select_values(values)
        (self.skill / "SKILL.md").write_text(tool._render_interface(self.skill, explicit), encoding="utf-8")
        self.assertEqual(tool.validate_skill_md(self.skill), [])

    def test_previous_callability_bootstrap_requires_controlled_migration(self):
        path = self.skill / "SKILL.md"
        old = tool._render_interface(self.skill, dict(tool.EXECUTOR_DEFAULTS), callability_legacy=True)
        path.write_text(old, encoding="utf-8")
        before = path.read_bytes()
        with patch.object(tool.urllib.request, "urlopen", side_effect=AssertionError("legacy check must not resolve")):
            self.assertIn("LEGACY", json.dumps(tool.validate_skill_md(self.skill)))
        self.assertEqual(path.read_bytes(), before)
        self.write("==1.0.0")
        self.assertEqual(tool.validate_skill_md(self.skill), [])
        path.write_text(old.replace("Do what printed says", "Do something else"), encoding="utf-8")
        damaged = path.read_bytes()
        self.assertNotEqual(self.run_tool("--write", "--executor-version-requirement", ">=1.0.0")[0], 0)
        self.assertEqual(path.read_bytes(), damaged)

    def test_missing_policy_in_new_body_is_not_mistaken_for_old_migration(self):
        self.write()
        path = self.skill / "SKILL.md"
        values, _ = tool._executor_input(self.skill)
        text = path.read_text(encoding="utf-8")
        block = text.split("```json\n", 1)[1].split("\n```", 1)[0]
        program = json.loads(block)
        del program[0]["content"]["params"][tool.VERSION_POLICY_KEY]
        path.write_text(text.replace(block, json.dumps(program, indent=2)), encoding="utf-8")
        before = path.read_bytes()
        self.assertNotEqual(self.run_tool("--write")[0], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_previous_policy_body_migrates_offline_without_changing_frozen_values(self):
        path = self.skill / "SKILL.md"
        for source, requirement in (("explicit", "==1.0.0"), ("latest_stable", ">=1.0.1")):
            values = {**tool.EXECUTOR_DEFAULTS, "executor_install": tool._soulrun_install(requirement),
                      tool.VERSION_POLICY_KEY: {"requirement": requirement, "source": source}}
            old = tool._render_interface(self.skill, values, version_policy_legacy=True)
            path.write_text(old, encoding="utf-8")
            before = path.read_bytes()
            with patch.object(tool.urllib.request, "urlopen", side_effect=AssertionError("no refresh on migration")):
                self.assertIn("LEGACY", json.dumps(tool.validate_skill_md(self.skill)))
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.run_tool("--write")[0], 0)
                self.assertEqual(tool._executor_input(self.skill)[0], values)
                self.assertEqual(tool.validate_skill_md(self.skill), [])
            for damaged in (old.replace("do not reinstall to conceal it", "reinstall immediately"),
                            old.replace('"source": "' + source + '"', '"source": "unknown"')):
                path.write_text(damaged, encoding="utf-8")
                before = path.read_bytes()
                self.assertNotEqual(self.run_tool("--write")[0], 0)
                self.assertEqual(path.read_bytes(), before)

    def test_latest_selection_is_numeric_and_excludes_pre_dev_and_yanked(self):
        data = {"info": {"name": "SoulRun"}, "releases": {"1.0.9": [{"yanked": False}], "1.0.10": [{"yanked": False}],
                             "2.0.0rc1": [{"yanked": False}], "2.0.0.dev1": [{"yanked": False}],
                             "3.0.0": [{"yanked": True}], "4.0.0": []}}
        response = io.BytesIO(json.dumps(data).encode())
        with patch.object(tool.urllib.request, "urlopen", return_value=response):
            self.assertEqual(tool._latest_soulrun_requirement(), ">=1.0.10")
        self.assertGreater(tool._release("1.0.10"), tool._release("1.0.9"))

    def test_latest_metadata_must_identify_the_default_adapter_project(self):
        for info in (None, [], {}, {"name": 1}, {"name": "unrelated-project"}, {"name": "soulrun "}):
            with self.subTest(info=info):
                data = {"info": info, "releases": {"9.0.0": [{"yanked": False}]}}
                with patch.object(tool.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(data).encode())):
                    with self.assertRaises(tool.SkillInterfaceError) as error:
                        tool._latest_soulrun_requirement()
                self.assertIn("RESOLUTION", error.exception.code)
                self.assertIn("identify the SoulRun project", str(error.exception))

    def test_resolution_failure_never_writes_or_falls_back_to_old_floor(self):
        with patch.object(tool.urllib.request, "urlopen", side_effect=OSError("controlled offline failure")):
            code, output = self.run_tool("--write")
        self.assertEqual(code, 1)
        self.assertIn("RESOLUTION", output)
        self.assertFalse((self.skill / "SKILL.md").exists())
        self.write()
        # An unsupported published stable form must fail, not silently select an older one.
        data = {"info": {"name": "soulrun"}, "releases": {"1.0.0": [{"yanked": False}], "1.0.1.post1": [{"yanked": False}]}}
        with patch.object(tool.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(data).encode())):
            with self.assertRaises(tool.SkillInterfaceError):
                tool._latest_soulrun_requirement()

    def test_failed_refresh_keeps_existing_default_bytes_without_fallback(self):
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=1.0.1"):
            self.assertEqual(self.run_tool("--write")[0], 0)
        before = (self.skill / "SKILL.md").read_bytes()
        with patch.object(tool.urllib.request, "urlopen", side_effect=OSError("controlled offline refresh")):
            code, output = self.run_tool("--write", "--refresh-executor-version")
        self.assertEqual(code, 1)
        self.assertIn("RESOLUTION", output)
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), before)

    def test_batch_resolves_once_and_validates_all_inputs_before_network_or_write(self):
        other = Path(self.temp.name) / "z_second_aisp"
        other.mkdir()
        doc = json.loads((self.skill / "aisp.aisop.json").read_text(encoding="utf-8"))
        doc[0]["content"]["id"] = other.name
        (other / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
        output = io.StringIO()
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=2.0.0") as resolver, redirect_stdout(output):
            self.assertEqual(tool.main([self.temp.name, "--write-all"]), 0)
            resolver.assert_called_once()
        for skill in (self.skill, other):
            self.assertEqual(tool._executor_input(skill)[0][tool.VERSION_POLICY_KEY]["requirement"], ">=2.0.0")
        (self.skill / "SKILL.md").unlink()
        (other / "SKILL.md").write_text("unknown handwritten file", encoding="utf-8")
        with patch.object(tool, "_latest_soulrun_requirement", side_effect=AssertionError("preflight first")), redirect_stderr(output):
            self.assertEqual(tool.main([self.temp.name, "--write-all"]), 1)
        self.assertFalse((self.skill / "SKILL.md").exists())
        self.assertEqual((other / "SKILL.md").read_text(encoding="utf-8"), "unknown handwritten file")

    def test_numeric_floor_and_pin_matrix_is_not_lexical(self):
        # Arithmetic oracle for the declared host algorithm, not a real-runtime claim.
        for requirement, installed, expected in [
            (">=1.0.0", "0.9.0", False), (">=1.0.0", "1.0.0", True),
            (">=1.0.0", "1.0.1", True), ("==1.0.0", "0.9.0", False),
            ("==1.0.0", "1.0.0", True), ("==1.0.0", "1.0.1", False),
            (">=1.0.9", "1.0.10", True),
        ]:
            policy = tool._policy({"requirement": requirement, "source": "explicit"})
            operator, bound = tool.REQUIREMENT_RE.fullmatch(policy["requirement"]).groups()
            actual = tool._release(installed)
            self.assertEqual(actual >= tool._release(bound) if operator == ">=" else actual == tool._release(bound), expected)

    def test_check_options_and_duplicate_policy_keys_never_trigger_resolution(self):
        self.write()
        with patch.object(tool.urllib.request, "urlopen", side_effect=AssertionError("read-only")):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                tool.main([str(self.skill), "--check", "--refresh-executor-version"])
            self.assertEqual(error.exception.code, 2)
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace('"requirement": ">=1.0.0",', '"requirement": ">=1.0.0", "requirement": "==9.0.0",')
        path.write_text(text, encoding="utf-8")
        before = path.read_bytes()
        self.assertNotEqual(self.run_tool("--write")[0], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_runtime_bootstrap_checks_before_run_and_after_install_without_index_lookup(self):
        program = json.loads(tool.BOOTSTRAP_JSON)[1]["content"]
        functions = program["functions"]
        self.assertTrue(functions["check"]["step2"].startswith("sys.assert"))
        self.assertTrue(functions["install"]["step3"].startswith("sys.assert"))
        self.assertTrue(functions["prepare_install"]["step2"].startswith("sys.assert"))
        self.assertTrue(functions["ask"]["step1"].startswith("sys.io.confirm"))
        self.assertEqual(functions["check"]["on_error"]["assertion_error"], "unavailable")
        self.assertEqual(functions["install"]["on_error"]["assertion_error"], "unavailable")
        self.assertIn("Do not query a package index", functions["check"]["step3"])
        self.assertIn("downgrade", functions["prepare_install"]["step1"])
        self.assertIn("business confirmation", functions["run"]["constraints"][0])
        self.assertIn("missing executor module behind an available launcher", functions["probe_error"]["step1"])
        self.assertIn("missing unrelated dependency/helper", functions["probe_error"]["step1"])
        self.assertEqual(program["aisp_contract"]["non_negotiable"][2]["enforced_by"], "ask.step1:sys.io.confirm")


if __name__ == "__main__":
    unittest.main()
