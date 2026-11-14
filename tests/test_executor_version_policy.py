"""Offline version-policy and old-interface rejection checks, not real-host certification."""
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


# Fixed pre-revision interfaces: rejection samples, not supported generators.
CALLABILITY_INTERFACE = r'''---
name: "simple"
description: "AISP-backed bridge for Minimal valid AISP skill for validator tests. Use when test a valid AISP skill. Do not use when no test requested."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "agent_skills_bridge"
---

# AISP Skill (run with an executor)

<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_skill_md.py -->

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "run_with_executor_aisp",
      "name": "Run this AISP skill with an executor",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "This SKILL.md is a thin bridge, not the source of truth: the executor set in params (SoulRun by default), an AISP/AISOP runtime, runs the same-folder aisp.aisop.json. Without an executor this skill does not run.",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "params": {
        "executor": "soulrun",
        "executor_version": "soulrun --version",
        "executor_command": "soulrun --aisp \"<the folder of this SKILL.md>\" --soulrun-cache-dir \"<your working folder>/.soulrun_cache\" --user-message-file \"<a file holding the user message>\" --host-tool \"agent=<true if you can start a sub-agent, otherwise false>\"",
        "executor_install": "python -m pip install --upgrade soulrun",
        "executor_help": "soulrun"
      },
      "system_prompt": "For help, run {executor_help}."
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": {
          "mode": "auto_or_manual",
          "when_to_use": [
            "the request matches the Use when part of this skill's description"
          ],
          "when_not_to_use": [
            "the request matches the Do not use when part of this skill's description"
          ]
        },
        "non_negotiable": [
          {
            "rule": "Run every request this skill is used for in this conversation through aisop.main the same way, a repeated one too; do not answer it yourself.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Run this skill only through the executor; never execute or continue aisp.aisop.json yourself. Reading it through the executor's commands, or reviewing it when the user asks, is not running it.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Install the executor only after the user agrees.",
            "enforced_by": "ask.step1:sys.io.confirm"
          }
        ],
        "risk_level": "medium"
      },
      "aisop": {
        "main": "graph TD\n    check[Check that the executor is installed] --> run[Run this skill with the executor]\n    check -.-> ask{Ask the user to install the executor}\n    ask -->|install| install[Install the executor]\n    ask -->|do_not_install| unavailable[Tell the user this skill cannot run without the executor]\n    install --> run\n    install -.-> unavailable\n    run --> end_node((End))\n    unavailable --> end_node"
      },
      "functions": {
        "check": {
          "step1": "sys.run('{executor_version}') -> installed",
          "on_error": {
            "command_error": "ask"
          },
          "execute_mode": "inline"
        },
        "ask": {
          "step1": "sys.io.confirm('This AISP skill runs only with an executor, and {executor} is not installed. Install the latest version now ({executor_install})?', options=['install', 'do_not_install']) -> choice",
          "step2": "Return choice as the branch label",
          "constraints": [
            "Wait for the user's answer, even if that ends this turn; never choose for the user."
          ],
          "execute_mode": "inline"
        },
        "install": {
          "step1": "sys.run('{executor_install}') -> install_log",
          "step2": "sys.run('{executor_version}') -> installed",
          "on_error": {
            "command_error": "unavailable"
          },
          "execute_mode": "inline"
        },
        "run": {
          "step1": "sys.run('{executor_command}') -> printed",
          "step2": "Do what printed says, to the end of this turn",
          "execute_mode": "inline"
        },
        "unavailable": {
          "step1": "sys.io.notify('This AISP skill cannot run without an executor, so this request was not run. To run it, install {executor} ({executor_install}) and ask again.')",
          "constraints": [
            "Do not execute aisp.aisop.json or carry out this skill's steps yourself."
          ],
          "execute_mode": "inline"
        },
        "end_node": {
          "step1": "End this turn",
          "execute_mode": "inline"
        }
      }
    }
  }
]
```

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
'''

PREVIOUS_POLICY_INTERFACE = r'''---
name: "simple"
description: "AISP-backed bridge for Minimal valid AISP skill for validator tests. Use when test a valid AISP skill. Do not use when no test requested."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "agent_skills_bridge"
---

# AISP Skill (run with an executor)

<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_skill_md.py -->

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "run_with_executor_aisp",
      "name": "Run this AISP skill with an executor",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "This SKILL.md is a thin bridge, not the source of truth: the executor set in params (SoulRun by default), an AISP/AISOP runtime, runs the same-folder aisp.aisop.json. Without an executor this skill does not run.",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "params": {
        "executor": "soulrun",
        "executor_version": "soulrun --version",
        "executor_command": "soulrun --aisp \"<the folder of this SKILL.md>\" --soulrun-cache-dir \"<your working folder>/.soulrun_cache\" --user-message-file \"<a file holding the user message>\" --host-tool \"agent=<true if you can start a sub-agent, otherwise false>\"",
        "executor_install": "python -m pip install --upgrade \"soulrun>=1.0.0\"",
        "executor_help": "soulrun",
        "executor_version_policy": {
          "requirement": ">=1.0.0",
          "source": "explicit"
        }
      },
      "system_prompt": "For help, run {executor_help}."
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": {
          "mode": "auto_or_manual",
          "when_to_use": [
            "the request matches the Use when part of this skill's description"
          ],
          "when_not_to_use": [
            "the request matches the Do not use when part of this skill's description"
          ]
        },
        "non_negotiable": [
          {
            "rule": "Run every request this skill is used for in this conversation through aisop.main the same way, a repeated one too; do not answer it yourself.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Run this skill only through the executor; never execute or continue aisp.aisop.json yourself. Reading it through the executor's commands, or reviewing it when the user asks, is not running it.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Install, upgrade or downgrade the executor only after the user agrees.",
            "enforced_by": "ask.step1:sys.io.confirm"
          }
        ],
        "risk_level": "medium"
      },
      "aisop": {
        "main": "graph TD\n    check{Check the executor package version} -->|satisfied| run[Run this skill with the executor]\n    check -->|mismatch| prepare_install[Verify the requested installation target]\n    check -.-> probe_error{Classify the failed probe}\n    probe_error -->|missing| prepare_install\n    probe_error -->|unusable| unavailable[Tell the user this request cannot run]\n    prepare_install --> ask{Ask the user to install the required executor}\n    ask -->|install| install[Install and verify the executor]\n    ask -->|do_not_install| unavailable\n    install --> run\n    install -.-> unavailable\n    run --> end_node((End))\n    unavailable --> end_node"
      },
      "functions": {
        "check": {
          "step1": "sys.run('{executor_version}') -> version_probe",
          "step2": "sys.assert('The probe unambiguously identifies the configured executor package version as three non-negative numeric components; do not use the protocol or bundled engine version, and never treat unknown output as compatible')",
          "step3": "Compare the numeric version components with executor_version_policy.requirement. Return satisfied for >= when installed is at least the bound, or for == only when equal; otherwise return mismatch. A satisfied version runs directly without asking to install or upgrade. Do not query a package index during this check.",
          "on_error": {
            "command_error": "probe_error",
            "assertion_error": "unavailable",
            "command_timeout": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline"
        },
        "ask": {
          "step1": "sys.io.confirm('This skill requires {executor} with the frozen executor_version_policy. State the installed version or absence, required constraint, actual target version policy, environment and any upgrade/downgrade. Install it using {executor_install}?', options=['install', 'do_not_install']) -> choice",
          "step2": "Return choice as the branch label",
          "constraints": [
            "Wait for the user's answer, even if that ends this turn; never choose for the user."
          ],
          "execute_mode": "inline"
        },
        "install": {
          "step1": "sys.run('{executor_install}') -> install_log",
          "step2": "sys.run('{executor_version}') -> installed",
          "on_error": {
            "command_error": "unavailable",
            "command_timeout": "unavailable",
            "assertion_error": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline",
          "step3": "sys.assert('After installation, reparse the configured executor package version and verify executor_version_policy.requirement using numeric components; == requires equality, >= requires at least the bound. Unparseable, failed or mismatching rechecks stop without execution, retries or fallback')"
        },
        "run": {
          "step1": "sys.run('{executor_command}') -> printed",
          "step2": "Do what printed says, to the end of this turn",
          "execute_mode": "inline",
          "constraints": [
            "Only run after a verified matching installed version or a successful installation and matching recheck. Do not suppress the skill's own business confirmation gates. A business run failure is not permission to reinstall or upgrade."
          ]
        },
        "unavailable": {
          "step1": "sys.io.notify('This request was not run because the required executor is missing, unusable, unverified or incompatible, or installation was declined or failed. Explain the actual reason and the declared version requirement; do not claim execution. The configured installation command is {executor_install}.')",
          "constraints": [
            "Do not execute aisp.aisop.json or carry out this skill's steps yourself."
          ],
          "execute_mode": "inline"
        },
        "end_node": {
          "step1": "End this turn",
          "execute_mode": "inline"
        },
        "probe_error": {
          "step1": "Return missing only when the probe proves the configured executor executable is not installed in the current environment. A started-but-failed command, permission denial, timeout or ambiguous failure returns unusable; do not reinstall to conceal it.",
          "execute_mode": "inline"
        },
        "prepare_install": {
          "step1": "For >=, the installation target is the latest stable executor release satisfying the frozen lower bound. For ==, the target is exactly the declared release, even if the installed version is newer. Identify the current version, target, environment and any downgrade; use the configured executor_install command, not an invented alternative.",
          "step2": "sys.assert('The configured installation command targets the requested release: latest stable satisfying >=, or exactly the version after ==; an unpinned latest command is not an exact-version installation. If its target cannot be established, stop instead of executing or silently rewriting it')",
          "on_error": {
            "assertion_error": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline"
        }
      }
    }
  }
]
```

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
'''

PUBLISHED_INTERFACE = r'''---
name: "simple"
description: "AISP-backed bridge for Minimal valid AISP skill for validator tests. Use when test a valid AISP skill. Do not use when no test requested."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "agent_skills_bridge"
---

# AISP Skill (run with an executor)

<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_skill_md.py -->

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "run_with_executor_aisp",
      "name": "Run this AISP skill with an executor",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "This SKILL.md is a thin bridge, not the source of truth: the executor set in params (SoulRun by default), an AISP/AISOP runtime, runs the same-folder aisp.aisop.json. Without an executor this skill does not run.",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "params": {
        "executor": "soulrun",
        "executor_version": "soulrun --version",
        "executor_command": "soulrun --aisp \"<the folder of this SKILL.md>\" --soulrun-cache-dir \"<your working folder>/.soulrun_cache\" --user-message-file \"<a file holding the user message>\" --host-tool \"agent=<true if you can start a sub-agent, otherwise false>\"",
        "executor_install": "python -m pip install --upgrade \"soulrun>=1.0.0\"",
        "executor_help": "soulrun",
        "executor_version_policy": {
          "requirement": ">=1.0.0",
          "source": "explicit"
        }
      },
      "system_prompt": "For help, run {executor_help}."
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": {
          "mode": "auto_or_manual",
          "when_to_use": [
            "the request matches the Use when part of this skill's description"
          ],
          "when_not_to_use": [
            "the request matches the Do not use when part of this skill's description"
          ]
        },
        "non_negotiable": [
          {
            "rule": "Run every request this skill is used for in this conversation through aisop.main the same way, a repeated one too; do not answer it yourself.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Run this skill only through the executor; never execute or continue aisp.aisop.json yourself. Reading it through the executor's commands, or reviewing it when the user asks, is not running it.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Install, upgrade or downgrade the executor only after the user agrees.",
            "enforced_by": "ask.step1:sys.io.confirm"
          }
        ],
        "risk_level": "medium"
      },
      "aisop": {
        "main": "graph TD\n    check{Check the executor package version} -->|satisfied| run[Run this skill with the executor]\n    check -->|mismatch| prepare_install[Verify the requested installation target]\n    check -.-> probe_error{Classify the failed probe}\n    probe_error -->|missing| prepare_install\n    probe_error -->|unusable| unavailable[Tell the user this request cannot run]\n    prepare_install --> ask{Ask the user to install the required executor}\n    ask -->|install| install[Install and verify the executor]\n    ask -->|do_not_install| unavailable\n    install --> run\n    install -.-> unavailable\n    run --> end_node((End))\n    unavailable --> end_node"
      },
      "functions": {
        "check": {
          "step1": "sys.run('{executor_version}') -> version_probe",
          "step2": "sys.assert('The probe unambiguously identifies the configured executor package version as three non-negative numeric components; do not use the protocol or bundled engine version, and never treat unknown output as compatible')",
          "step3": "Compare the numeric version components with executor_version_policy.requirement. Return satisfied for >= when installed is at least the bound, or for == only when equal; otherwise return mismatch. A satisfied version runs directly without asking to install or upgrade. Do not query a package index during this check.",
          "on_error": {
            "command_error": "probe_error",
            "assertion_error": "unavailable",
            "command_timeout": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline"
        },
        "ask": {
          "step1": "sys.io.confirm('This skill requires {executor} with the frozen executor_version_policy. State the installed version or absence, required constraint, actual target version policy, environment and any upgrade/downgrade. Install it using {executor_install}?', options=['install', 'do_not_install']) -> choice",
          "step2": "Return choice as the branch label",
          "constraints": [
            "Wait for the user's answer, even if that ends this turn; never choose for the user."
          ],
          "execute_mode": "inline"
        },
        "install": {
          "step1": "sys.run('{executor_install}') -> install_log",
          "step2": "sys.run('{executor_version}') -> installed",
          "on_error": {
            "command_error": "unavailable",
            "command_timeout": "unavailable",
            "assertion_error": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline",
          "step3": "sys.assert('After installation, reparse the configured executor package version and verify executor_version_policy.requirement using numeric components; == requires equality, >= requires at least the bound. Unparseable, failed or mismatching rechecks stop without execution, retries or fallback')"
        },
        "run": {
          "step1": "sys.run('{executor_command}') -> printed",
          "step2": "Do what printed says, to the end of this turn",
          "execute_mode": "inline",
          "constraints": [
            "Only run after a verified matching installed version or a successful installation and matching recheck. Do not suppress the skill's own business confirmation gates. A business run failure is not permission to reinstall or upgrade."
          ]
        },
        "unavailable": {
          "step1": "sys.io.notify('This request was not run because the required executor is missing, unusable, unverified or incompatible, or installation was declined or failed. Explain the actual reason and the declared version requirement; do not claim execution. The configured installation command is {executor_install}.')",
          "constraints": [
            "Do not execute aisp.aisop.json or carry out this skill's steps yourself."
          ],
          "execute_mode": "inline"
        },
        "end_node": {
          "step1": "End this turn",
          "execute_mode": "inline"
        },
        "probe_error": {
          "step1": "Return missing only when the probe proves the configured executor package or entry point is not installed in the current environment, including a proven missing executor module behind an available launcher. A missing unrelated dependency/helper, invalid command, permission denial, timeout, other started-but-failed command or ambiguous failure returns unusable; do not reinstall to conceal it.",
          "execute_mode": "inline"
        },
        "prepare_install": {
          "step1": "For >=, the installation target is the latest stable executor release satisfying the frozen lower bound. For ==, the target is exactly the declared release, even if the installed version is newer. Identify the current version, target, environment and any downgrade; use the configured executor_install command, not an invented alternative.",
          "step2": "sys.assert('The configured installation command targets the requested release: latest stable satisfying >=, or exactly the version after ==; an unpinned latest command is not an exact-version installation. If its target cannot be established, stop instead of executing or silently rewriting it')",
          "on_error": {
            "assertion_error": "unavailable",
            "default": "unavailable"
          },
          "execute_mode": "inline"
        }
      }
    }
  }
]
```

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
'''


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

    def assert_old_interface_rejected(self, old, expected_code):
        path = self.skill / "SKILL.md"
        path.write_bytes(old.encode("utf-8"))
        before = path.read_bytes()
        with patch.object(tool.urllib.request, "urlopen", side_effect=AssertionError("refusal must be offline")) as network:
            for action in ("--check", "--write"):
                code, output = self.run_tool(action)
                self.assertEqual(code, 1, output)
                self.assertIn(expected_code, output)
                self.assertIn("Back up the file", output)
                self.assertEqual(path.read_bytes(), before)
            network.assert_not_called()
        path.unlink()
        with patch.object(tool, "_latest_soulrun_requirement", return_value=">=1.0.1") as resolver:
            self.assertEqual(self.run_tool("--write")[0], 0)
            resolver.assert_called_once()
        self.assertEqual(tool.validate_skill_md(self.skill), [])
        self.assertEqual(tool._executor_input(self.skill)[0][tool.VERSION_POLICY_KEY],
                         {"requirement": ">=1.0.1", "source": "latest_stable"})

    def test_previous_callability_bootstrap_is_refused_without_migration(self):
        self.assert_old_interface_rejected(CALLABILITY_INTERFACE, "CONFIG")
        path = self.skill / "SKILL.md"
        path.write_text(CALLABILITY_INTERFACE.replace("Do what printed says", "Do something else"), encoding="utf-8")
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

    def test_old_policy_bodies_are_refused_until_deleted(self):
        for old in (PREVIOUS_POLICY_INTERFACE, PUBLISHED_INTERFACE):
            with self.subTest(old_policy="previous" if old == PREVIOUS_POLICY_INTERFACE else "published"):
                self.assert_old_interface_rejected(old, "BODY")
                for damaged in (old.replace("do not reinstall to conceal it", "reinstall immediately"),
                                old.replace('"source": "explicit"', '"source": "unknown"')):
                    path = self.skill / "SKILL.md"
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
        self.assertIn("Do not answer the request yourself, not even partly: give no substitute result, analysis or advice. You may only offer other help and wait for the user to choose.", functions["unavailable"]["constraints"])
        self.assertIn("After a failed installation or upgrade, run {executor_version} again and tell the user truthfully whether a previously installed executor still works; even if it does, never run this skill with an executor that does not satisfy executor_version_policy, in any environment.", functions["unavailable"]["constraints"])
        self.assertIn("Write the file holding the user message inside your working folder, never in a system temporary folder or anywhere else outside it.", functions["run"]["constraints"])
        self.assertIn("missing executor module behind an available launcher", functions["probe_error"]["step1"])
        self.assertIn("missing unrelated dependency/helper", functions["probe_error"]["step1"])
        self.assertEqual(program["aisp_contract"]["non_negotiable"][2]["enforced_by"], "ask.step1:sys.io.confirm")


if __name__ == "__main__":
    unittest.main()
