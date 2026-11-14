"""Input integrity, safe hash output and folder-derived discovery evidence."""
import copy
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import aisp_hash, aisp_validate
from tools.aisp_check_runtime_trace import check_trace
from tools.aisp_readme import render_readme
from tools.aisp_skill_md import render_skill_md


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


gate = module(CREATOR / "scripts/check_generated_candidate.py", "integrity_gate")
light = module(CREATOR / "scripts/validate_aisp_skill.py", "integrity_light")


class InputIntegrityAndIndexTests(unittest.TestCase):
    def make_skill(self, parent):
        skill = Path(parent) / "simple_aisp"
        skill.mkdir()
        (skill / "aisp.aisop.json").write_bytes(SEED.read_bytes())
        (skill / "SKILL.md").write_text(render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
        (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")
        return skill

    def discovery(self, root):
        value = module(ROOT / "examples/aisp/aisp_list.py", "integrity_discovery")
        value.ROOT = root
        return value

    def project_document(self, skill, doc):
        (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
        (skill / "SKILL.md").write_text(render_skill_md(skill, executor_version_requirement=">=1.0.1"), encoding="utf-8")
        (skill / "README.md").write_text(render_readme(skill), encoding="utf-8")

    def test_optional_known_metadata_types_cannot_be_washed_by_current_projections(self):
        cases = []
        for field in ("summary", "description", "license", "system_prompt"):
            cases.extend((0, field, value) for value in (None, True, 3, [], {"value": "text"}))
        cases.extend((0, "license", value) for value in (False, 0, {}))
        cases.extend((0, "params", value) for value in (None, True, 3, [], "text"))
        cases.extend((1, "user_input", value) for value in (None, True, 3, [], {}))
        for index, field, value in cases:
            with self.subTest(index=index, field=field, value=value), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[index]["content"][field] = value
                self.project_document(skill, doc)
                report = aisp_validate.validate_skill(skill, strict_readme=True)
                self.assertFalse(report["conformant"])
                self.assertEqual({r["code"] for r in report["results"] if r["severity"] == "FAIL"}, {"AISP_E_M1_FIELD"})
                local = light.validate(str(skill))
                self.assertFalse(local["m1_to_m6_pass"])
                self.assertIn("AISP_E_M1_FIELD", {r["code"] for r in local["issues"]})
                if field == "license":
                    self.assertNotIn("AISP_W_M1_LICENSE", {r["code"] for r in report["results"]})
                    self.assertNotIn("AISP_W_M1_LICENSE", {r["code"] for r in local["issues"]})
                    for flags in ([], ["--warnings-fail"]):
                        out = io.StringIO()
                        with redirect_stdout(out):
                            code = aisp_validate.main(["--json", "--strict-readme", *flags, str(skill)])
                        cli_report = json.loads(out.getvalue())["reports"][0]
                        self.assertEqual(code, 1)
                        self.assertFalse(cli_report["conformant"])
                        self.assertEqual(cli_report["warning_count"], 0)

    def test_optional_metadata_can_be_omitted_without_adding_new_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            for field in ("summary", "description", "system_prompt", "params"):
                doc[0]["content"].pop(field, None)
            doc[1]["content"].pop("user_input", None)
            self.project_document(skill, doc)
            self.assertTrue(aisp_validate.validate_skill(skill, strict_readme=True)["conformant"])
            self.assertTrue(light.validate(str(skill))["m1_to_m6_pass"])

            doc[0]["content"]["params"] = {}
            self.project_document(skill, doc)
            self.assertTrue(aisp_validate.validate_skill(skill, strict_readme=True)["conformant"])
            self.assertTrue(light.validate(str(skill))["m1_to_m6_pass"])

    def test_empty_optional_text_and_open_world_parameters_remain_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[0]["content"].update({"summary": "", "description": "", "system_prompt": "",
                                      "params": {"request": {"type": "string", "default": ""},
                                                 "license": {}, "system_prompt": [], "user_input": False,
                                                 "tools": {"vendor_options": []}},
                                      "vendor_extension": {"nested": [None, True, "allowed"]}})
            doc[1]["content"].update({"user_input": "", "tools": {"display_only": True},
                                      "vendor_extension": {"allowed": True}})
            self.project_document(skill, doc)
            self.assertTrue(aisp_validate.validate_skill(skill, strict_readme=True)["conformant"])
            self.assertTrue(light.validate(str(skill))["m1_to_m6_pass"])

    def test_license_omission_still_warns_instead_of_becoming_a_required_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            doc[0]["content"].pop("license", None)
            self.project_document(skill, doc)
            report = aisp_validate.validate_skill(skill, strict_readme=True)
            self.assertTrue(report["conformant"])
            self.assertIn("AISP_W_M1_LICENSE", {r["code"] for r in report["results"]})
            local = light.validate(str(skill))
            self.assertTrue(local["m1_to_m6_pass"])
            self.assertIn("AISP_W_M1_LICENSE", {r["code"] for r in local["issues"]})

    def test_lightweight_required_text_fields_match_core_type_checks(self):
        for field in ("name", "version"):
            for value in (True, 3, ["text"], {"value": "text"}, "   "):
                with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as tmp:
                    skill = self.make_skill(tmp)
                    doc = json.loads(SEED.read_text(encoding="utf-8"))
                    doc[0]["content"][field] = value
                    self.project_document(skill, doc)
                    self.assertIn("AISP_E_M1_FIELD", {r["code"] for r in aisp_validate.validate_skill(skill)["results"]})
                    self.assertIn("AISP_E_M1_FIELD", {r["code"] for r in light.validate(str(skill))["issues"]})

    def test_blank_license_stays_advisory_with_warning_exit_policy(self):
        for value in ("", " ", "\t\r\n", "\u00a0"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[0]["content"]["license"] = value
                self.project_document(skill, doc)
                for flags, expected in (([], 0), (["--warnings-fail"], 1)):
                    out = io.StringIO()
                    with redirect_stdout(out):
                        code = aisp_validate.main(["--json", "--strict-readme", *flags, str(skill)])
                    report = json.loads(out.getvalue())["reports"][0]
                    self.assertEqual(code, expected)
                    self.assertTrue(report["conformant"])
                    self.assertEqual({r["code"] for r in report["results"] if r["severity"] != "INFO"}, {"AISP_W_M1_LICENSE"})
                local = light.validate(str(skill))
                self.assertTrue(local["m1_to_m6_pass"])
                self.assertEqual({r["code"] for r in local["issues"]}, {"AISP_W_M1_LICENSE"})

    def test_field_reference_and_proto_keep_existing_optionality_and_profile_form(self):
        text = (ROOT / "docs/reference/aisp-fields.md").read_text(encoding="utf-8")
        for field, location in (("summary", "system.content"), ("description", "system.content"), ("user_input", "user.content")):
            self.assertIn(f"| `{field}` | {location} | string | MAY |", text)
        self.assertIn("| `on_error` | object | MAY |", text)
        self.assertIn("array of non-empty strings", text)
        self.assertNotIn("or structured tool objects", text)
        self.assertNotIn('MUST start with "aisp.skill."', (ROOT / "specification/aisp.proto").read_text(encoding="utf-8"))
        self.assertIn("aisp.skill.v<major>", (ROOT / "specification/aisp.proto").read_text(encoding="utf-8"))

    def test_tools_declaration_types_match_core_without_making_tools_required(self):
        cases = [(None, False), (False, False), (3, False), ("shell", False), ({}, False),
                 ({"shell": True}, False), ([{"name": "shell"}], False), ([None], False),
                 ([False], False), ([3], False), ([[]], False), ([""], False), ([" "], False),
                 (["\u00a0"], False), (["shell", {}], False), ([], True),
                 (["filesystem", "shell"], True), (["vendor.custom"], True), (["shell", "shell"], True)]
        for value, valid in cases:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[0]["content"]["tools"] = value
                self.project_document(skill, doc)
                core = aisp_validate.validate_skill(skill, strict_readme=True)
                local = light.validate(str(skill))
                self.assertEqual(core["conformant"], valid)
                self.assertEqual(local["m1_to_m6_pass"], valid)
                self.assertEqual({r["code"] for r in core["results"] if r["severity"] != "INFO"}, set() if valid else {"AISP_E_M1_FIELD"})
                self.assertEqual({r["code"] for r in local["issues"]}, set() if valid else {"AISP_E_M1_FIELD"})
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            doc = json.loads(SEED.read_text(encoding="utf-8"))
            del doc[0]["content"]["tools"]
            self.project_document(skill, doc)
            self.assertTrue(aisp_validate.validate_skill(skill, strict_readme=True)["conformant"])
            self.assertTrue(light.validate(str(skill))["m1_to_m6_pass"])

    def test_nonblank_license_strings_do_not_create_presence_warnings(self):
        for value in ("Apache-2.0", "MIT", "LicenseRef-Custom", " \tMIT\r\n"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[0]["content"]["license"] = value
                self.project_document(skill, doc)
                core = aisp_validate.validate_skill(skill, strict_readme=True)
                local = light.validate(str(skill))
                self.assertTrue(core["conformant"])
                self.assertEqual(core["warning_count"], 0)
                self.assertTrue(local["m1_to_m6_pass"])
                self.assertEqual(local["issues"], [])

    def test_tools_bound_redlines_require_a_nonempty_allowlist_in_both_validators(self):
        for mode in ("omitted", "empty", "null", "object", "declared"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["aisp_contract"]["non_negotiable"][0]["enforced_by"] = "tools"
                if mode == "omitted":
                    del doc[0]["content"]["tools"]
                else:
                    doc[0]["content"]["tools"] = {"empty": [], "null": None, "object": {},
                                                  "declared": ["filesystem"]}[mode]
                self.project_document(skill, doc)
                core = aisp_validate.validate_skill(skill, strict_readme=True)
                local = light.validate(str(skill))
                valid = mode == "declared"
                self.assertEqual(core["conformant"], valid)
                self.assertEqual(local["m1_to_m6_pass"], valid)
                if valid:
                    self.assertEqual({r["code"] for r in core["results"] if r["severity"] != "INFO"},
                                     {"AISP_W_R6_TOOLS_CONDITIONAL"})
                    self.assertEqual(local["issues"], [])
                    strict = aisp_validate.validate_skill(skill, strict_readme=True, strict_tools=True)
                    self.assertFalse(strict["conformant"])
                    self.assertIn("AISP_E_R6_TOOLS_NOT_HARD", {r["code"] for r in strict["results"]})
                else:
                    expected = {"AISP_E_M4_TOOLS"}
                    if mode in ("null", "object"):
                        expected.add("AISP_E_M1_FIELD")
                    self.assertEqual({r["code"] for r in core["results"] if r["severity"] != "INFO"}, expected)
                    self.assertEqual({r["code"] for r in local["issues"]}, expected)

    def test_release_privacy_scan_is_generic_and_cannot_silently_skip_read_errors(self):
        text = (ROOT / "scripts/release_check.ps1").read_text(encoding="utf-8")
        body = text.split("function Assert-NoPrivatePathLeak", 1)[1].split("function Assert-NoForbiddenAiapFiles", 1)[0]
        self.assertNotIn('Label = "local username"', body)
        self.assertIn("-ErrorAction Stop", body)
        self.assertIn('throw "Privacy scan could not read', body)
        self.assertIn('if ($null -eq $text) { $text = "" }', body)
        self.assertNotRegex(body, r"catch\s*\{\s*return")

    def test_release_privacy_scan_actual_files_without_running_wrapper(self):
        shells = [path for path in (shutil.which("pwsh"), shutil.which("powershell")) if path]
        if not shells:
            self.skipTest("PowerShell is unavailable; static privacy guards still run")
        # Load only the named function AST, never the Git-bearing wrapper.
        script = r'''
$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($env:AISP_PRIVACY_SCRIPT, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'PowerShell syntax errors' }
$definition = $ast.Find({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Assert-NoPrivatePathLeak' }, $true)
if ($null -eq $definition) { throw 'Privacy function missing' }
. ([scriptblock]::Create($definition.Extent.Text))
$rootPath = $env:AISP_PRIVACY_FIXTURE
$file = Join-Path $rootPath '[literal].txt'
$utf8 = [Text.UTF8Encoding]::new($false)
foreach ($text in @('', 'runner root user', "`r`n")) {
  [IO.File]::WriteAllText($file, $text, $utf8)
  Assert-NoPrivatePathLeak
}
$markers = @(
  ('c:' + [char]92 + 'uSeRs' + [char]92 + 'synthetic'),
  ('C:' + [char]47 + 'Users' + [char]47 + 'synthetic'),
  ('D:' + [char]92 + 'synthetic'),
  ('d:' + [char]47 + 'synthetic'),
  ('BEGIN ' + 'PRIVATE KEY'),
  ('BEGIN ' + 'RSA ' + 'PRIVATE KEY'),
  ('BEGIN ' + 'EC ' + 'PRIVATE KEY'),
  ('BEGIN ' + 'DSA ' + 'PRIVATE KEY'),
  ('BEGIN ' + 'OPENSSH ' + 'PRIVATE KEY')
)
foreach ($encoding in @($utf8, [Text.UTF8Encoding]::new($true), [Text.Encoding]::Unicode)) {
  foreach ($marker in $markers) {
    [IO.File]::WriteAllText($file, $marker, $encoding)
    $blocked = $false
    try { Assert-NoPrivatePathLeak } catch { $blocked = $_.Exception.Message.StartsWith('Potential private path/key leak found:') }
    if (-not $blocked) { throw 'Marker was not rejected' }
  }
}
[IO.File]::WriteAllText($file, 'clean but locked', $utf8)
$handle = [IO.File]::Open($file, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
try {
  $blocked = $false
  try { Assert-NoPrivatePathLeak } catch { $blocked = $_.Exception.Message.StartsWith('Privacy scan could not read ') }
  if (-not $blocked) { throw 'Unreadable file was not rejected' }
} finally { $handle.Dispose() }
[IO.File]::WriteAllText($file, '', $utf8)
$ignored = Join-Path $rootPath '.git'
[IO.Directory]::CreateDirectory($ignored) | Out-Null
[IO.File]::WriteAllText((Join-Path $ignored 'fixture.txt'), $markers[0], $utf8)
Assert-NoPrivatePathLeak
[IO.File]::WriteAllText($file, ($markers[0] + ('x' * (5MB - 1 - $markers[0].Length))), $utf8)
$blocked = $false
try { Assert-NoPrivatePathLeak } catch { $blocked = $_.Exception.Message.StartsWith('Potential private path/key leak found:') }
if (-not $blocked) { throw 'File below the size limit was not scanned' }
[IO.File]::WriteAllText($file, ($markers[0] + ('x' * (5MB - $markers[0].Length))), $utf8)
Assert-NoPrivatePathLeak
Write-Output 'PRIVACY_FIXTURES_PASS'
'''
        for shell in dict.fromkeys(shells):
            with self.subTest(shell=Path(shell).name), tempfile.TemporaryDirectory(prefix="aisp-privacy-test-") as tmp:
                fixture = Path(tmp) / "scan root [literal]"
                fixture.mkdir()
                env = dict(os.environ, AISP_PRIVACY_SCRIPT=str(ROOT / "scripts/release_check.ps1"),
                           AISP_PRIVACY_FIXTURE=str(fixture))
                proc = subprocess.run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                                      env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("PRIVACY_FIXTURES_PASS", proc.stdout)

    def test_json_null_and_other_non_program_values_never_pass_strict_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            for value in (None, True, False, 0, "", {}, []):
                with self.subTest(value=value):
                    (skill / "aisp.aisop.json").write_text(json.dumps(value), encoding="utf-8")
                    out = io.StringIO()
                    with redirect_stdout(out):
                        code = aisp_validate.main(["--json", "--strict-readme", "--strict-tools", str(skill)])
                    report = json.loads(out.getvalue())["reports"][0]
                    self.assertEqual(code, 1)
                    self.assertFalse(report["conformant"])
                    self.assertIn("AISP_E_M1_SHAPE", {r["code"] for r in report["results"]})

    def test_parse_errors_remain_distinct_from_json_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            (skill / "aisp.aisop.json").write_text("{bad", encoding="utf-8")
            codes = {r["code"] for r in aisp_validate.validate_skill(skill)["results"]}
            self.assertEqual(codes, {"AISP_E_M1_JSON"})

    def test_reserved_flow_and_optional_metadata_types_are_checked(self):
        cases = [("flow_format", "unknown"), ("flow_format", []), ("summary", {}), ("description", None)]
        for field, value in cases:
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as tmp:
                skill = self.make_skill(tmp)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[0]["content"][field] = value
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                codes = {r["code"] for r in aisp_validate.validate_skill(skill)["results"]}
                self.assertIn("AISP_E_M1_FIELD", codes)
                if field == "flow_format":
                    self.assertIn("AISP_E_M1_FIELD", {r["code"] for r in light.validate(str(skill))["issues"]})

    def test_discovery_metadata_types_match_the_contract_schema(self):
        for field, value in (("category", []), ("tags", {}), ("tags", [1])):
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                skill = self.make_skill(root)
                doc = json.loads(SEED.read_text(encoding="utf-8"))
                doc[1]["content"]["aisp_contract"]["discovery"][field] = value
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                self.assertIn("AISP_E_M3_CONTRACT", {r["code"] for r in aisp_validate.validate_skill(skill)["results"]})
                self.assertTrue(self.discovery(root).discover()[1])

    def test_discovery_rejects_ambiguous_or_non_json_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self.make_skill(root)
            seed = SEED.read_text(encoding="utf-8")
            duplicate = seed.replace('"version": "1.0.0"', '"version": "1.0.0", "version": "1.0.0"')
            for raw in (duplicate, seed.replace('"system_prompt": ""', '"system_prompt": NaN')):
                (skill / "aisp.aisop.json").write_text(raw, encoding="utf-8")
                self.assertTrue(self.discovery(root).discover()[1])

    def test_ec2_checks_routing_metadata_not_only_ids_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            self.make_skill(root)
            (root / "README.md").write_text("Directory", encoding="utf-8")
            (root / "aisp_list.py").write_bytes((ROOT / "examples/aisp/aisp_list.py").read_bytes())
            rows, errors = self.discovery(root).discover()
            self.assertEqual(errors, [])
            index = {"aisp_list_version": "1.0", "skills": rows}
            for field, stale in (("name", "stale name"), ("summary", "stale"), ("category", "stale"),
                                 ("tags", ["stale"]), ("when_to_use", ["stale"]), ("risk_level", "critical")):
                with self.subTest(field=field):
                    payload = copy.deepcopy(index)
                    payload["skills"][0][field] = stale
                    (root / "aisp_list.json").write_text(json.dumps(payload), encoding="utf-8")
                    report = aisp_validate.validate_aisp_dir(root)
                    self.assertTrue(report["conformant"], report)
                    self.assertTrue(any(r["code"] == "AISP_W_EC2_INDEX_DRIFT" and field in r["message"] for r in report["results"]))
            (root / "aisp_list.json").write_text(json.dumps(index), encoding="utf-8")
            self.assertFalse(any(r["code"] == "AISP_W_EC2_INDEX_DRIFT" for r in aisp_validate.validate_aisp_dir(root)["results"]))

    def test_hash_output_cannot_overwrite_program_or_declared_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            program = skill / "aisp.aisop.json"
            doc = json.loads(program.read_text(encoding="utf-8"))
            doc[1]["content"]["aisp_contract"]["resources"] = [
                {"id": "data", "path": "data.txt", "kind": "data", "mode": "read_only"},
                {"id": "missing", "path": "missing.txt", "kind": "data", "mode": "read_only"},
            ]
            program.write_text(json.dumps(doc), encoding="utf-8")
            (skill / "data.txt").write_text("unchanged", encoding="utf-8")
            before = program.read_bytes()
            for output in (program, skill / "data.txt", skill / "missing.txt"):
                with self.subTest(output=output.name), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(aisp_hash.main([str(skill), "--out", str(output)]), 1)
            self.assertEqual(program.read_bytes(), before)
            self.assertEqual((skill / "data.txt").read_text(encoding="utf-8"), "unchanged")
            self.assertFalse((skill / "missing.txt").exists())

    def test_hash_output_rejects_hardlink_alias_of_program(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            program = skill / "aisp.aisop.json"
            output = Path(tmp) / "alias.json"
            try:
                output.hardlink_to(program)
            except OSError as exc:
                self.skipTest(f"hardlink unavailable (OS error {exc.errno})")
            before = program.read_bytes()
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(aisp_hash.main([str(skill), "--out", str(output)]), 1)
            self.assertEqual(program.read_bytes(), before)
            self.assertEqual(output.read_bytes(), before)

    def test_external_manifest_is_atomic_utf8_and_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            before = (skill / "aisp.aisop.json").read_bytes()
            output = Path(tmp) / "manifest.json"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(aisp_hash.main([str(skill), "--out", str(output)]), 0)
            raw = output.read_bytes()
            self.assertNotIn(b"\r\n", raw)
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(json.loads(raw)["manifest_version"], "1.1")
            self.assertEqual((skill / "aisp.aisop.json").read_bytes(), before)
            self.assertFalse(list(Path(tmp).glob(".*.tmp")))

    def test_entry_confinement_precedes_byte_reads_in_all_loaders(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(tmp)
            program = skill / "aisp.aisop.json"
            original = Path.resolve
            def resolve(path, *args, **kwargs):
                return Path(tmp) / "outside.json" if path == program else original(path, *args, **kwargs)
            with patch.object(Path, "resolve", resolve), patch.object(Path, "read_text") as read:
                self.assertFalse(aisp_validate.validate_skill(skill)["conformant"])
                with self.assertRaises(ValueError):
                    aisp_hash.load_skill(skill)
                self.assertFalse(check_trace(skill, Path(tmp) / "trace.json")["runtime_conformant"])
                self.assertTrue(self.discovery(Path(tmp)).discover()[1])
                read.assert_not_called()

    def test_candidate_reference_payload_cannot_claim_pass_with_failed_results(self):
        cases = [
            {"conformant": True, "fail_count": 1, "results": [{"severity": "FAIL", "passed": False}]},
            {"conformant": True, "fail_count": 0, "results": [{"severity": "FAIL", "passed": False}]},
            {"conformant": True, "fail_count": 0, "results": []},
        ]
        for entry in cases:
            with self.subTest(entry=entry):
                report = {"results": [], "artifacts": {}}
                proc = {"exit_code": 0, "stdout": json.dumps({"reports": [entry]}), "stderr": ""}
                with patch.object(gate, "run_process", return_value=proc):
                    gate.check_reference_tools(CREATOR, CREATOR, report)
                self.assertTrue(gate.has_failures(report))

    def test_index_write_refuses_hardlinks_but_readonly_check_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            root.mkdir()
            self.make_skill(root)
            discovery = self.discovery(root)
            rows, errors = discovery.discover()
            self.assertEqual(errors, [])
            outside = Path(tmp) / "outside.json"
            before = discovery.render_index(rows).encode("utf-8")
            outside.write_bytes(before)
            try:
                (root / "aisp_list.json").hardlink_to(outside)
            except OSError as exc:
                self.skipTest(f"hardlink unavailable (OS error {exc.errno})")
            with patch("sys.argv", ["aisp_list.py", "--json"]), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(discovery.main(), 1)
            self.assertEqual(outside.read_bytes(), before)
            with patch("sys.argv", ["aisp_list.py", "--check"]), redirect_stdout(io.StringIO()):
                self.assertEqual(discovery.main(), 0)

    def test_specification_discovery_snippets_match_the_canonical_script(self):
        expected = (ROOT / "examples/aisp/aisp_list.py").read_text(encoding="utf-8-sig").rstrip("\n")
        for name, marker in (("AISP_Protocol.md", "## Appendix C:"), ("AISP_Protocol_cn.md", "## \u9644\u5f55 C\uff1a")):
            text = (ROOT / "specification" / name).read_text(encoding="utf-8-sig")
            block = text.split(marker, 1)[1].split("```python\n", 1)[1].split("\n```", 1)[0]
            self.assertEqual(block, expected, name)
