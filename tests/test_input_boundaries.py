"""Malformed metadata must fail cleanly and discovery must stay confined."""
import ast
import copy
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

from tools.aisp_validate import validate_skill, validate_aisp_dir
from tools.aisp_hash import compute_manifest


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "tests/fixtures/valid/simple_aisp/aisp.aisop.json"


class InputBoundaryTests(unittest.TestCase):
    def test_packaging_explicitly_contains_tools_and_no_runtime_dependencies(self):
        config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["tool"]["setuptools"]["packages"], ["tools"])
        self.assertEqual(config["build-system"]["build-backend"], "setuptools.build_meta")
        self.assertEqual(config["project"]["license"], "Apache-2.0")
        self.assertFalse(config["project"].get("dependencies"))
        self.assertFalse(config["tool"]["setuptools"]["include-package-data"])
        requires = config["build-system"]["requires"]
        self.assertEqual(len(requires), 1)
        match = re.fullmatch(r"setuptools>=([0-9]+)\.([0-9]+)\.([0-9]+)", requires[0])
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (84, 1, 0))
        self.assertTrue((ROOT / "MANIFEST.in").is_file())

    def test_archives_reject_private_files_from_stale_source_lists(self):
        def unavailable(reason):
            if os.environ.get("AISP_REQUIRE_ARCHIVE_TEST") == "1":
                self.fail(reason)
            self.skipTest(reason)

        try:
            installed = importlib.metadata.version("setuptools")
        except importlib.metadata.PackageNotFoundError:
            unavailable("archive regression requires the declared build backend in an isolated environment")
        match = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.post[0-9]+)?", installed)
        requirement = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["build-system"]["requires"][0]
        minimum = tuple(map(int, requirement.split(">=", 1)[1].split(".")))
        if not match or tuple(map(int, match.groups())) < minimum:
            unavailable("archive regression requires setuptools >= the declared build floor; global environment unchanged")
        private = [".env", ".env.production", ".pypirc", ".netrc", "_netrc", "keys/id_rsa", "keys/id_ed25519",
                   "tools/cache.private.pem", "keys/key.p12", "keys/key.pfx", "logs/trace.log", "note.bak", "note.orig"]
        pruned_dirs = (".git", ".secrets", ".ssh", ".soulrun_cache", ".execution_cache",
                       ".evolution_snapshot", ".version_history", "__pycache__", ".pytest_cache",
                       ".mypy_cache", ".ruff_cache", ".venv", "build", "dist")
        for folder in pruned_dirs:
            private.extend(prefix + folder + "/private.json" for prefix in ("", "tools/", "tools/vendor/"))
            private.extend(prefix + folder + "/.env.example" for prefix in ("", "tools/vendor/"))
        public = [".env.example", "public/.env.example", "evals/runtime-traces/hard-pass.json", "aisp_reports/review.json",
                  "tools/vendor/.soulrun_cache_notes/keep.json", "public/dist-info/keep.json",
                  "public/id_rsa.pub", "public/certificate.pem", "public/build", "public/dist"]
        for folder in pruned_dirs:
            public.extend(prefix + folder + "_notes/keep.json" for prefix in ("public/near/", "tools/vendor/public/"))
        marker = b"AISP_SYNTHETIC_PRIVATE_ARCHIVE_CANARY"
        code = r'''
from pathlib import Path
import json
import subprocess
import sys
original = subprocess.Popen
def no_git(args, *a, **k):
    first = args[0] if isinstance(args, (list, tuple)) else args.split()[0]
    if Path(str(first).strip('"')).stem.lower() == 'git':
        raise RuntimeError('Git invocation is prohibited in archive regression')
    return original(args, *a, **k)
subprocess.Popen = no_git
from setuptools import build_meta
destination = sys.argv[1]
stale = Path('aisp_protocol_tools.egg-info/SOURCES.txt').read_text(encoding='utf-8').splitlines()
assert stale == json.loads(sys.argv[3]), 'Each build must receive the complete original stale list'
getattr(build_meta, sys.argv[2])(destination)
'''
        with tempfile.TemporaryDirectory(prefix="aisp-archive-regression-") as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            for name in ("pyproject.toml", "README.md", "LICENSE", "NOTICE", "MANIFEST.in"):
                shutil.copy2(ROOT / name, source / name)
            shutil.copytree(ROOT / "tools", source / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            for relative in private + public:
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(marker if relative in private else b"PUBLIC_PLACEHOLDER")
            egg = source / "aisp_protocol_tools.egg-info"
            egg.mkdir()
            output = Path(tmp) / "dist"
            output.mkdir()
            for hook in ("build_sdist", "build_wheel"):
                # Each format must filter the stale list itself, not inherit a cleaned list.
                (egg / "SOURCES.txt").write_text("\n".join(private + public) + "\n", encoding="utf-8")
                proc = subprocess.run([sys.executable, "-B", "-c", code, str(output), hook, json.dumps(private + public)], cwd=source,
                                      env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"),
                                      capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
                self.assertEqual(proc.returncode, 0, hook + "\n" + proc.stdout + proc.stderr)
            wheel, = output.glob("*.whl")
            sdist, = output.glob("*.tar.gz")
            with zipfile.ZipFile(wheel) as archive:
                modules = {"tools/" + p.name for p in (ROOT / "tools").glob("*.py")}
                self.assertEqual({name for name in archive.namelist() if name.startswith("tools/") and name.endswith(".py")}, modules)
                for name in modules:
                    self.assertEqual(archive.read(name), (ROOT / name).read_bytes(), name)
                for name in ("LICENSE", "NOTICE"):
                    matches = [item for item in archive.namelist() if item.endswith(".dist-info/licenses/" + name)]
                    self.assertEqual(len(matches), 1, name)
                    self.assertEqual(archive.read(matches[0]), (ROOT / name).read_bytes(), name)
                for name in archive.namelist():
                    self.assertNotIn(name, private)
                    self.assertNotIn(name, public)
                    self.assertNotIn(marker, archive.read(name), name)
                    self.assertNotIn(b"PUBLIC_PLACEHOLDER", archive.read(name), name)
            with tarfile.open(sdist, "r:gz") as archive:
                members = {m.name.split("/", 1)[1]: m for m in archive.getmembers() if m.isfile()}
                names = set(members)
                required = modules | {"pyproject.toml", "README.md", "LICENSE", "NOTICE", "MANIFEST.in"}
                self.assertFalse(set(private) & names)
                self.assertTrue(set(public).issubset(names))
                self.assertTrue(required.issubset(names))
                for name in required:
                    self.assertEqual(archive.extractfile(members[name]).read(), (ROOT / name).read_bytes(), name)
                for name in public:
                    self.assertEqual(archive.extractfile(members[name]).read(), b"PUBLIC_PLACEHOLDER", name)
                for member in archive.getmembers():
                    if member.isfile():
                        self.assertNotIn(marker, archive.extractfile(member).read(), member.name)

    def test_ci_archive_profile_cannot_silently_skip_missing_or_old_backend(self):
        for missing in (False, True):
            for required in ("", "1"):
                with self.subTest(missing=missing, required=required):
                    case = self.__class__("test_archives_reject_private_files_from_stale_source_lists")
                    result = unittest.TestResult()
                    kwargs = {"side_effect": importlib.metadata.PackageNotFoundError("setuptools")} if missing else {"return_value": "82.0.1"}
                    with patch.dict(os.environ, {"AISP_REQUIRE_ARCHIVE_TEST": required}), \
                            patch.object(importlib.metadata, "version", **kwargs):
                        case.run(result)
                    self.assertEqual(result.errors, [])
                    self.assertEqual(len(result.failures), int(required == "1"))
                    self.assertEqual(len(result.skipped), int(required != "1"))

    def test_release_archive_profile_and_cleanup_on_success_or_failure(self):
        shells = list(dict.fromkeys(path for path in (shutil.which("pwsh"), shutil.which("powershell")) if path))
        if not shells:
            self.skipTest("PowerShell unavailable; wrapper configuration still receives static checks")
        # Exercise the real unit gate with a child-local Python stub, never the Git-bearing body.
        script = r'''
$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($env:AISP_RELEASE_SCRIPT, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'PowerShell parse failure' }
$guard = $ast.Find({ param($n) $n -is [System.Management.Automation.Language.TryStatementAst] -and $n.Finally -and $n.Finally.Extent.Text.Contains('$oldArchiveRequirement') }, $true)
$checked = $ast.Find({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Invoke-Checked' }, $true)
if (-not $guard -or -not $checked) { throw 'Required wrapper blocks missing' }
$unit = $guard.Body.Find({
  param($n)
  $n -is [System.Management.Automation.Language.CommandAst] -and
  $n.GetCommandName() -eq 'Invoke-Checked' -and $n.CommandElements.Count -ge 3 -and
  $n.CommandElements[1] -is [System.Management.Automation.Language.StringConstantExpressionAst] -and
  [string]::Equals($n.CommandElements[1].Value, 'unit tests', [StringComparison]::OrdinalIgnoreCase)
}, $true)
if (-not $unit) { throw 'Unit-test gate missing' }
if ($unit.Parent -isnot [System.Management.Automation.Language.PipelineAst] -or $unit.Parent.Parent -ne $guard.Body) { throw 'Unit-test gate must be unconditional' }
$gateCommands = @($unit.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true))
if ($gateCommands.Count -ne 2 -or @($gateCommands | Where-Object { $_.GetCommandName() -notin @('Invoke-Checked', 'python') }).Count) { throw 'Unapproved unit-gate command' }
$gate = [scriptblock]::Create($unit.Extent.Text)
$setup = @()
foreach ($left in @('$oldPythonDontWriteBytecode', '$oldArchiveRequirement', '$env:PYTHONDONTWRITEBYTECODE', '$env:AISP_REQUIRE_ARCHIVE_TEST')) {
  $nodes = @($ast.EndBlock.Statements | Where-Object { $_ -is [System.Management.Automation.Language.AssignmentStatementAst] -and $_.Left.Extent.Text -eq $left })
  if ($nodes.Count -ne 1 -or $nodes[0].Extent.StartOffset -ge $guard.Extent.StartOffset) { throw 'Required setup must precede the guarded checks' }
  $setup += $nodes[0]
}
$setup = @($setup | Sort-Object { $_.Extent.StartOffset })
$cleanup = ($guard.Finally.Statements | ForEach-Object { $_.Extent.Text }) -join "`n"
$commands = @($guard.Finally.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true))
foreach ($command in $commands) {
  if ($command.GetCommandName() -eq 'Pop-Location') { continue }
  if ($command.GetCommandName() -ne 'Remove-Item' -or $command.CommandElements.Count -lt 2 -or $command.CommandElements[1] -isnot [System.Management.Automation.Language.StringConstantExpressionAst]) { throw 'Unapproved cleanup command' }
  $path = $command.CommandElements[1].Value
  if (-not [string]::Equals($path, 'Env:AISP_REQUIRE_ARCHIVE_TEST', [StringComparison]::OrdinalIgnoreCase) -and
      -not [string]::Equals($path, 'Env:PYTHONDONTWRITEBYTECODE', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unapproved cleanup command' }
}
. ([scriptblock]::Create($checked.Extent.Text))
function python {
  $expected = @('-B', '-m', 'unittest', 'discover', '-s', 'tests')
  if ($args.Count -ne $expected.Count) { throw 'Unexpected unit-test command arguments' }
  for ($index = 0; $index -lt $expected.Count; $index++) {
    if ($args[$index] -isnot [string] -or -not [string]::Equals($args[$index], $expected[$index], [StringComparison]::Ordinal)) { throw 'Unexpected unit-test command arguments' }
  }
  & $env:AISP_TEST_PYTHON -B -c "import os,sys; assert os.environ.get('AISP_REQUIRE_ARCHIVE_TEST')=='1'; assert os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'; sys.exit(int(sys.argv[1]))" $script:expectedUnitExit
  $global:LASTEXITCODE = $LASTEXITCODE
}
$unicodeState = 'caller-' + [char]0x200b + 'original'
$decomposedState = 'Caller-E' + [char]0x0301 + '-' + [char]0x4e2d
$composedState = 'Caller-' + [char]0x00c9 + '-' + [char]0x4e2d
foreach ($states in @(@('absent', 'absent'), @('empty', 'empty'), @('0', 'caller-original'), @('caller-original', '0'), @('absent', '0'), @('0', 'absent'), @('empty', 'caller-original'), @($unicodeState, '0'), @('0', $unicodeState), @($decomposedState, $composedState), @($composedState, $decomposedState))) {
  foreach ($exitCode in @(0, 1, 7)) {
    $before = @{}
    $names = @('AISP_REQUIRE_ARCHIVE_TEST', 'PYTHONDONTWRITEBYTECODE')
    for ($index = 0; $index -lt $names.Count; $index++) {
      $name = $names[$index]
      $state = $states[$index]
      if ($state -eq 'absent') { Remove-Item ('Env:' + $name) -ErrorAction SilentlyContinue }
      elseif ($state -eq 'empty') { [Environment]::SetEnvironmentVariable($name, '', 'Process') }
      else { [Environment]::SetEnvironmentVariable($name, $state, 'Process') }
      $before[$name] = @((Test-Path ('Env:' + $name)), [Environment]::GetEnvironmentVariable($name, 'Process'))
    }
    foreach ($statement in $setup) { . ([scriptblock]::Create($statement.Extent.Text)) }
    $failed = $false
    $location = (Get-Location).Path
    Push-Location $env:AISP_RELEASE_ROOT
    $script:expectedUnitExit = $exitCode
    try {
      . $gate
    } catch {
      if ($exitCode -eq 0 -or $_.Exception.Message -ne "unit tests failed with exit code $exitCode") { throw }
      $failed = $true
    } finally {
      . ([scriptblock]::Create($cleanup))
    }
    if ($failed -ne ($exitCode -ne 0)) { throw 'Native failure was lost' }
    if ((Get-Location).Path -cne $location) { throw 'Caller location not restored' }
    foreach ($name in $before.Keys) {
      if ((Test-Path ('Env:' + $name)) -ne $before[$name][0] -or -not [string]::Equals([Environment]::GetEnvironmentVariable($name, 'Process'), $before[$name][1], [StringComparison]::Ordinal)) { throw ('Caller state not restored: ' + $name) }
    }
  }
}
Write-Output 'RELEASE_PROFILE_BOUNDARIES_PASS'
exit 0
'''
        for shell in shells:
            with self.subTest(shell=Path(shell).name), tempfile.TemporaryDirectory(prefix="aisp-release-context-") as tmp:
                env = dict(os.environ, AISP_RELEASE_SCRIPT=str(ROOT / "scripts/release_check.ps1"),
                           AISP_RELEASE_ROOT=str(ROOT), AISP_TEST_PYTHON=sys.executable)
                proc = subprocess.run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                                      cwd=tmp, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("RELEASE_PROFILE_BOUNDARIES_PASS", proc.stdout)

    def test_reference_script_imports_remain_stdlib_or_local(self):
        tools = list((ROOT / "tools").glob("*.py"))
        local = {path.stem for path in tools} | {"tools"}
        paths = tools + list((ROOT / "examples/aisp").glob("*/scripts/*.py")) + [ROOT / "examples/aisp/aisp_list.py"]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
                for node in ast.walk(tree):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [alias.name.split(".")[0] for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        names = [node.module.split(".")[0]]
                    for name in names:
                        self.assertIn(name, sys.stdlib_module_names | local)

    def test_ignore_policy_covers_private_outputs_without_blanket_source_ignores(self):
        rules = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#")]
        expected = {".env", ".env.*", "!.env.example", ".pypirc", ".netrc", "_netrc", ".ssh/",
                    ".secrets/", ".soulrun_cache/", ".execution_cache/", ".evolution_snapshot/",
                    ".version_history/", "*.log", "*.bak", ".coverage.*"}
        self.assertTrue(expected.issubset(rules))
        self.assertLess(rules.index(".env.*"), rules.index("!.env.example"))
        self.assertFalse({"*.json", "*.md", "examples/", "schemas/", "aisp_reports/"} & set(rules))
        release = (ROOT / "scripts/release_check.ps1").read_text(encoding="utf-8")
        self.assertIn('".soulrun_cache"', release.split("function Assert-NoForbiddenResidue", 1)[1].split("function Assert-NoPrivatePathLeak", 1)[0])

    def test_ci_uses_readonly_permissions_and_immutable_action_references(self):
        text = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read\n")
        references = re.findall(r"(?m)^      - uses: (actions/[^@\s]+)@([^\s]+)", text)
        self.assertEqual({name for name, _ in references}, {"actions/checkout", "actions/setup-python"})
        self.assertEqual(len(references), 2)
        for _, revision in references:
            self.assertRegex(revision, r"^[0-9a-f]{40}$")
        self.assertIn("persist-credentials: false", text)
        self.assertIn('run: python -m pip install --quiet "jsonschema>=4"', text)
        self.assertIn('"setuptools>=84.1.0"', text)
        self.assertIn("AISP_REQUIRE_ARCHIVE_TEST: '1'", text)
        release = (ROOT / "scripts/release_check.ps1").read_text(encoding="utf-8")
        self.assertIn('$env:AISP_REQUIRE_ARCHIVE_TEST = "1"', release)
        self.assertIn('$env:AISP_REQUIRE_ARCHIVE_TEST = $oldArchiveRequirement', release)
        for forbidden in ("write-all", "contents: write", "persist-credentials: true", "pull_request_target:"):
            self.assertNotIn(forbidden, text)

    def test_bad_contract_types_and_message_roles_return_fail(self):
        seed = json.loads(SEED.read_text(encoding="utf-8-sig"))
        cases = []
        for field, value in (("resources", None), ("resources", {})):
            doc = copy.deepcopy(seed)
            doc[1]["content"]["aisp_contract"][field] = value
            cases.append(doc)
        for tools in ({}, [None], [[]]):
            doc = copy.deepcopy(seed)
            doc[0]["content"]["tools"] = tools
            cases.append(doc)
        for field in ("risk_level", "discovery"):
            doc = copy.deepcopy(seed)
            doc[1]["content"]["aisp_contract"][field] = []
            cases.append(doc)
        for field in ("mode", "scope", "path"):
            doc = copy.deepcopy(seed)
            doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "bad", "path": "data.txt", "kind": "data", "mode": "read_only", field: []}]
            cases.append(doc)
        doc = copy.deepcopy(seed)
        doc[0]["role"] = "user"
        cases.append(doc)
        doc = copy.deepcopy(seed)
        doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "bad", "path": "data.txt", "kind": "data", "mode": []}]
        doc[1]["content"]["functions"]["start"] = {"step1": "sys.io.read('data.txt')", "execute_mode": "inline"}
        cases.append(doc)
        for doc in cases:
            with self.subTest(doc=doc), tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "simple_aisp"
                skill.mkdir()
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                self.assertFalse(validate_skill(skill)["conformant"])

    def test_windows_style_resource_escapes_are_rejected_on_every_platform(self):
        for path in ("../outside.txt", "..\\outside.txt", "C:\\outside.txt", "C:relative.txt", "\\rooted.txt"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "simple_aisp"
                skill.mkdir()
                doc = json.loads(SEED.read_text(encoding="utf-8-sig"))
                doc[1]["content"]["aisp_contract"]["resources"] = [{"id": "bad", "path": path, "kind": "data", "mode": "read_only"}]
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                self.assertIn("AISP_E_M5_PATH_ESCAPE", {r["code"] for r in validate_skill(skill)["results"]})
                with self.assertRaises(ValueError):
                    compute_manifest(skill)

    def test_fake_sys_prefix_is_not_a_binding(self):
        doc = json.loads(SEED.read_text(encoding="utf-8-sig"))
        doc[1]["content"]["aisp_contract"]["non_negotiable"] = [{"rule": "Check", "enforced_by": "start.step1:sys.assert"}]
        doc[1]["content"]["functions"]["start"] = {"step1": "sys.assert_fake('true')", "execute_mode": "inline"}
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "simple_aisp"
            skill.mkdir()
            (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
            self.assertIn("AISP_E_M4_NO_MECHANISM", {x["code"] for x in validate_skill(skill)["results"]})

    def test_hash_rejects_invalid_message_and_resource_shapes(self):
        seed = json.loads(SEED.read_text(encoding="utf-8-sig"))
        for resources in ({}, [None], [{"path": [], "scope": "skill"}]):
            with self.subTest(resources=resources), tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "simple_aisp"
                skill.mkdir()
                doc = copy.deepcopy(seed)
                doc[1]["content"]["aisp_contract"]["resources"] = resources
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                with self.assertRaises(ValueError):
                    compute_manifest(skill)

    def discovery(self, root):
        spec = importlib.util.spec_from_file_location("isolated_aisp_list", ROOT / "examples/aisp/aisp_list.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.ROOT = root
        return module

    def test_discovery_rejects_malformed_metadata_and_empty_packages(self):
        for field in ("discovery", "invocation"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                skill = root / "simple_aisp"
                skill.mkdir()
                doc = json.loads(SEED.read_text(encoding="utf-8-sig"))
                doc[1]["content"]["aisp_contract"][field] = []
                (skill / "aisp.aisop.json").write_text(json.dumps(doc), encoding="utf-8")
                found, errors = self.discovery(root).discover()
                self.assertFalse(found)
                self.assertTrue(errors)
                (skill / "aisp.aisop.json").unlink()
                self.assertTrue(self.discovery(root).discover()[1])

    def test_discovery_rejects_an_external_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "aisp"
            root.mkdir()
            target = parent / "simple_aisp"
            target.mkdir()
            (target / "aisp.aisop.json").write_bytes(SEED.read_bytes())
            try:
                (root / "simple_aisp").symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable (OS error {getattr(exc, 'winerror', exc.errno)})")
            found, errors = self.discovery(root).discover()
            self.assertFalse(found)
            self.assertTrue(errors)

    def test_directory_index_shapes_and_missing_program_fail_cleanly(self):
        cases = [None, {}, [{"id": []}], [{"id": "simple_aisp"}] * 2]
        for entries in cases:
            with self.subTest(entries=entries), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "README.md").write_text("Directory", encoding="utf-8")
                (root / "aisp_list.json").write_text(json.dumps({"skills": entries}), encoding="utf-8")
                report = validate_aisp_dir(root)
                self.assertFalse(report["conformant"])
                self.assertIn("AISP_E_EC2_INDEX", {r["code"] for r in report["results"]})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Directory", encoding="utf-8")
            (root / "empty_aisp").mkdir()
            self.assertFalse(validate_aisp_dir(root)["conformant"])

    def test_discovery_checks_confinement_before_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "aisp"
            skill = root / "simple_aisp"
            skill.mkdir(parents=True)
            f = skill / "aisp.aisop.json"
            f.write_bytes(SEED.read_bytes())
            module = self.discovery(root)
            original = Path.resolve

            def resolve(path, *args, **kwargs):
                return root.parent / "outside.json" if path == f else original(path, *args, **kwargs)

            with patch.object(Path, "resolve", resolve), patch.object(Path, "read_text") as read:
                found, errors = module.discover()
            read.assert_not_called()
            self.assertFalse(found)
            self.assertTrue(errors)
