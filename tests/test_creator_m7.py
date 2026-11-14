"""Offline consumer regression; no Creator/model workflow is invoked."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CREATOR = ROOT / "examples/aisp/aisp_creator_evolution_aisp"
GATE = CREATOR / "scripts/check_generated_candidate.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def run(*args):
    return subprocess.run([sys.executable, "-B", *map(str, args)], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8", env=ENV)


class CreatorM7Tests(unittest.TestCase):
    def make_candidate(self, parent, summary=None):
        skill = parent / "regression_aisp"
        skill.mkdir()
        body = json.loads((CREATOR / "evals/candidate-seed.json").read_text(encoding="utf-8"))
        body[0]["content"]["id"] = skill.name
        if summary is not None:
            body[0]["content"]["summary"] = summary
        (skill / "aisp.aisop.json").write_text(json.dumps(body), encoding="utf-8")
        self.regenerate(skill)
        return skill

    def regenerate(self, skill):
        for tool in ("aisp_skill_md.py", "aisp_readme.py"):
            args = [skill, "--write"]
            if tool == "aisp_skill_md.py":
                args += ["--executor-version-requirement", ">=1.0.0"]
            result = run(CREATOR / "aisp_reference_tools" / tool, *args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def gate(self, skill, creator=CREATOR, explicit=True):
        args = [GATE, skill, "--creator-root", creator]
        if explicit:
            args += ["--output-path", skill.parent]
        result = run(*args)
        return result, json.loads(result.stdout)

    def test_create_edit_and_derived_description_use_authoritative_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_candidate(Path(tmp), "An inert long summary. " * 90)
            result, report = self.gate(skill)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report["pass"])
            path = skill / "aisp.aisop.json"
            body = json.loads(path.read_text(encoding="utf-8"))
            body[0]["content"]["summary"] = "A controlled manual update to an inert regression."
            path.write_text(json.dumps(body), encoding="utf-8")
            self.assertNotEqual(self.gate(skill)[0].returncode, 0)
            self.regenerate(skill)
            self.assertEqual(self.gate(skill)[0].returncode, 0)

    def test_missing_interface_cannot_use_removed_opt_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_candidate(Path(tmp))
            (skill / "SKILL.md").unlink()
            result, report = self.gate(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("AISP_E_M7_SKILL_MD_MISSING", json.dumps(report))
            self.assertIn("AISP_E_CANDIDATE_SIDECAR_MISSING_DEFAULT", json.dumps(report))
            bypass = run(GATE, skill, "--creator-root", CREATOR, "--allow-missing-sidecar")
            self.assertEqual(bypass.returncode, 2)

    def test_legacy_corrupt_and_drifted_interfaces_reject_without_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_candidate(Path(tmp))
            path = skill / "SKILL.md"
            original = path.read_text(encoding="utf-8")
            cases = [
                original.replace('bridge_mode: "agent_skills_bridge"', 'bridge_mode: "native_sidecar"'),
                original.replace('"executor_version": "soulrun --version"', '"executor_version": null'),
                original + "\nUnapproved fixed-body addition.\n",
            ]
            for text in cases:
                with self.subTest(text=text[-60:]):
                    self.assertNotEqual(text, original)
                    path.write_text(text, encoding="utf-8")
                    before = path.read_bytes()
                    result, report = self.gate(skill)
                    self.assertEqual(result.returncode, 1, report)
                    self.assertEqual(path.read_bytes(), before)

    def test_default_sibling_and_explicit_location_rules_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            creator = parent / "creator_aisp"
            shutil.copytree(CREATOR / "aisp_reference_tools", creator / "aisp_reference_tools")
            skill = self.make_candidate(parent)
            self.assertEqual(self.gate(skill, creator, explicit=False)[0].returncode, 0)
            result, report = self.gate(skill, CREATOR, explicit=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("AISP_E_CANDIDATE_LOCATION", json.dumps(report))
            self.assertEqual(self.gate(skill, CREATOR, explicit=True)[0].returncode, 0)

    def test_lightweight_validation_explicitly_does_not_check_m7(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_candidate(Path(tmp))
            (skill / "SKILL.md").unlink()
            result = run(CREATOR / "scripts/validate_aisp_skill.py", skill)
            report = json.loads(result.stdout)
            self.assertTrue(report["m1_to_m6_pass"])
            self.assertFalse(report["m7_checked"])
            self.assertIn("M7", report["coverage_note"])
            self.assertEqual(self.gate(skill)[0].returncode, 1)


if __name__ == "__main__":
    unittest.main()
