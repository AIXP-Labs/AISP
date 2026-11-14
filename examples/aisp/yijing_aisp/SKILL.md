---
name: "yijing"
description: "AISP-backed bridge for Cast and interpret an I Ching (Yijing) hexagram for a user's question. Use when cast an I Ching reading; interpret a hexagram. Do not use when medical, legal, or financial decisions needing a professional; no question provided."
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
        "executor_install": "python -m pip install --upgrade \"soulrun>=1.0.1\"",
        "executor_help": "soulrun",
        "executor_version_policy": {
          "requirement": ">=1.0.1",
          "source": "latest_stable"
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
            "Only run after a verified matching installed version or a successful installation and matching recheck. Do not suppress the skill's own business confirmation gates. A business run failure is not permission to reinstall or upgrade.",
            "Write the file holding the user message inside your working folder, never in a system temporary folder or anywhere else outside it."
          ]
        },
        "unavailable": {
          "step1": "sys.io.notify('This request was not run because the required executor is missing, unusable, unverified or incompatible, or installation was declined or failed. Explain the actual reason and the declared version requirement; do not claim execution. The configured installation command is {executor_install}.')",
          "constraints": [
            "Do not execute aisp.aisop.json or carry out this skill's steps yourself.",
            "Do not answer the request yourself, not even partly: give no substitute result, analysis or advice. You may only offer other help and wait for the user to choose.",
            "After a failed installation or upgrade, run {executor_version} again and tell the user truthfully whether a previously installed executor still works; even if it does, never run this skill with an executor that does not satisfy executor_version_policy, in any environment."
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
