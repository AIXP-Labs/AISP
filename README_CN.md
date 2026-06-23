# AISP — AI 技能协议

[English README](README.md)

[![Validate](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml/badge.svg)](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-AISP_V1.0.0-brightgreen.svg)](https://aisp.dev)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![Axiom 0](https://img.shields.io/badge/Axiom_0-Human_Sovereignty_and_Wellbeing-orange.svg)](GOVERNANCE.md)

**AISP 把可执行、可治理、可分发的 AI 技能打包成自包含技能文件夹。**

它不是另一个 `SKILL.md` 格式。AISP 定义技能包；AISOP 执行其中的程序。

[协议规范](specification/AISP_Protocol_cn.md) | [快速开始](#快速开始) | [示例](#示例) | [发布证据](docs/reference/release-evidence-matrix_CN.md) | [Validator Coverage](docs/reference/validator-coverage.md) | [AIXP Labs](#aixp-labs-aixpdev)

| 事实 | 值 |
|------|----|
| 协议 | AISP V1.0.0 |
| 全称 | AI Skill Protocol（AI 技能协议）|
| 权威域名 | [aisp.dev](https://aisp.dev) |
| 执行层 | [aisop.dev](https://aisop.dev) |
| 运行时示例 | [soulbot.dev](https://soulbot.dev) |
| 基础公理 | Human Sovereignty and Wellbeing（人类主权与福祉）|

## AISP 是什么？

AISP 定义 AI 的**技能包层**。[Agent Skills](https://agentskills.io/specification)（`SKILL.md`）用散文加渐进披露描述技能；AISP 解决的是另一个问题：如何把一个技能打包成**真正可执行的程序**，并带有可机器检查的合同、声明式资源、验证规则和分发生命周期。

一个原生 AISP 技能是一个文件夹 `aisp/<id>_aisp/`，其中包含固定文件名的 AISOP 程序 `aisp.aisop.json` 以及该技能自己的资源。执行体是 AISOP 程序；技能合同是 `user.content.aisp_contract`（真 JSON object）；生成、进化、分发由作者自选的外部工具承担。

**核心理念**：硬保证是强制出来的，不是提示出来的。红线通过 `non_negotiable.enforced_by -> sys.*`、`aisop.main` 或受限 tools 绑定到真实机制。信任绝不自报。

**互补，非替代**：AISP 不取代 Agent Skills。它提供可执行、可治理的技能包。核心一致性不要求 `SKILL.md`，但创作 / 分发工具 SHOULD 默认包含同目录薄 `SKILL.md` sidecar，以接入 Agent Skills 平台；作者可明确 opt out。

## 仓库范围

| 本仓库包含 | 用途 |
|------------|------|
| `specification/` | 规范性协议文档、一致性标准和 Proto schema |
| `schemas/` | 合同、runtime trace、registry manifest、工具能力的 JSON Schema |
| `tools/` | 零运行时依赖的参考 validator、hash 工具、README 生成器和 bridge 检查器 |
| `examples/aisp/` | 原生 AISP 技能包示例，用于演示和验证 |
| `docs/` | 指南、参考、ADR、生命周期说明和信任边界文档 |
| `tests/` | 回归测试以及有效/无效 fixture |

本仓库**不**内置生产级 AISOP runtime、registry 服务或信任授权机构。你可以在这里读取、发现、验证、hash 和审查技能。要执行技能，需要使用遵守 AISP runtime 规则的 AISOP-compatible runtime。

## 核心特性

- **可执行 Skill IR** — 技能本体是合法 AISOP V1.0.0 程序（`aisop.main`、`functions`、`sys.*`），不是散文指令。
- **合同在 user 消息** — `user.content.aisp_contract` 是真 JSON object，模型在这一轮直接读到。
- **Policy-as-Code 红线** — `non_negotiable.enforced_by` 把规则绑定到真实机制；只有 runtime 真执行的机制才是硬保证。
- **Folder-per-Skill** — 一个技能就是一个自包含文件夹；文件夹名等于 `id` 且以 `_aisp` 结尾。
- **运行时无关发现** — `aisp_list.json`、`aisp_list.py` 和文件夹 glob 让 agent 不运行 runtime 也能发现技能。
- **两层结构** — Tier A 放可执行结构与操作；Tier S 放触发、红线、发现、风险和资源清单。
- **机器可检查一致性** — M/R/SE/EC 规则族明确包、runtime、安全和生态预期。
- **默认 `SKILL.md` sidecar bridge** — 生成/分发的原生技能目录 SHOULD 默认包含一个薄 Agent Skills sidecar，只引导加载 `aisp.aisop.json`，绝不复制可执行逻辑；核心一致性仍不强制。
- **Axiom 0 强制** — 每个技能继承人类主权与福祉；`sys.io.confirm` 保持强制阻塞。

## 协议栈

```text
应用层
  |
AISP  - 技能包层（本协议）
  |
AISOP - 执行层（.aisop.json 流程程序）
  |
AISOP-compatible runtime（SoulBot 是一个示例）
```

AISP 把 AISOP 程序打包成可发现、可触发、可治理、可分发的技能单元。它建在 AISOP 之上用于执行，不重新定义执行引擎。每一层都独立持守 Axiom 0。

## 快速开始

前置条件：Python 3.11 或更高版本。参考工具运行时只用 Python 标准库；`jsonschema` 只用于 schema 相关测试覆盖。

如需运行完整测试套件，先安装一次可选开发依赖：

```bash
python -m pip install -e ".[dev]"
```

### 1. 查看包结构

规范性的 AISP 包结构如下：

```text
aisp/
└── yijing_aisp/            # 文件夹名 == id，必须以 _aisp 结尾
    ├── README.md           # 生成的自举投影
    ├── SKILL.md            # 默认 Agent Skills sidecar 投影；core 可选
    ├── aisp.aisop.json     # 固定文件名；技能本体
    └── data/
        ├── hexagrams.json
        └── interpretation_guide.md
```

在本仓库中，示例包位于 `examples/aisp/`：

```text
examples/aisp/
├── README.md
├── aisp_list.json
├── aisp_list.py
├── _shared/
├── yijing_aisp/
├── stock_analysis_aisp/
└── aisp_creator_evolution_aisp/
```

### 2. 阅读合同片段

完整示例见 [`examples/aisp/yijing_aisp/aisp.aisop.json`](examples/aisp/yijing_aisp/aisp.aisop.json)。它的合同位于 user 消息中：

```json
{
  "role": "user",
  "content": {
    "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
    "aisp_contract": {
      "profile": "aisp.skill.v1",
      "invocation": {
        "mode": "auto_or_manual",
        "when_to_use": ["..."],
        "when_not_to_use": ["..."]
      },
      "non_negotiable": [
        { "rule": "...", "enforced_by": "interpret.step1:sys.assert" }
      ],
      "discovery": { "category": "culture", "tags": ["..."] },
      "risk_level": "low",
      "resources": [
        { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" }
      ]
    }
  }
}
```

### 3. 发现示例技能

```bash
# 安全读取已生成索引；不执行脚本。
python -B -m json.tool examples/aisp/aisp_list.json

# 扫描示例技能文件夹并重新生成索引。
python -B examples/aisp/aisp_list.py --json
```

技能文件夹是真相源。`aisp_list.py` 是生成器，`aisp_list.json` 是缓存。

### 4. 执行前验证

最小本地检查：

```bash
python -B tools/aisp_validate.py examples/aisp
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

完整发布门检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

使用 `-IncludePytest` 可额外运行 pytest 且不写入 `.pytest_cache/`；只有最终发布前
才使用 `-RequireClean` 检查工作树完全干净。展开后的 CI 等价命令如下：

```bash
python -B tools/aisp_validate.py examples/aisp
python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
python -B examples/aisp/aisp_list.py --check
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate.py --strict-readme examples/aisp
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
python -B tools/check_doc_sync.py --root .
python -B tools/check_markdown_links.py --root .
git diff --check
git diff --exit-code
git status --porcelain=v1 --untracked-files=all
python -B -m unittest discover -s tests
```

`git diff --exit-code` 检查已跟踪文件漂移。最终 clean-tree 检查中，`git status --porcelain=v1 --untracked-files=all` 必须没有任何输出；它同时覆盖已跟踪漂移和未跟踪生成物。

每条命令证明什么、哪些 warning 是预期信号、哪些场景必须提供 runtime evidence，见 [发布证据矩阵](docs/reference/release-evidence-matrix_CN.md)。在纯静态校验中，`AISP_W_R6_TOOLS_CONDITIONAL` 是 `enforced_by: tools` 的诚实边界信号，不是默认 failure。

只有在明确更新派生产物时才运行写入命令：

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

### 5. 用 AISOP runtime 执行

本仓库负责验证和打包技能；它不声称自己直接执行技能。要运行技能，请把目标 `aisp.aisop.json` 载入 AISP/AISOP-compatible runtime，然后执行 `RUN aisop.main`。

例如，runtime 应载入：

```text
examples/aisp/yijing_aisp/aisp.aisop.json
```

然后执行 `user.content.aisop.main` 中的图，同时遵守 `user.content.aisp_contract` 中的合同。

## 验证边界

参考工具链是一致性门禁，不是信任 oracle。

| 检查 | 证明什么 | 不证明什么 |
|------|----------|------------|
| 静态 validator | M1-M6 加静态 SE/EC 包检查 | 完整 runtime 行为或外部信任 |
| Runtime trace checker | trace 中有证据的 R 系列行为 | 未签名 trace source 本身可信 |
| 生成 README 检查 | 与 `aisp.aisop.json` 派生一致 | 技能安全、可信或 registry 认可 |
| Hash 工具 | 可重算的本地完整性记录 | 安全性、背书或 provenance 本身 |
| SKILL.md 生成/检查 | 默认同目录 sidecar 投影与合同一致 | Agent Skills 平台行为、安全性或外部信任 |
| Bridge validator | 安全薄 `SKILL.md` sidecar 形状和原生 AISP 校验 | 非 AISOP 平台上的硬执行保证 |

缺少 `SKILL.md` 是 EC7 warning，不是 Core AISP failure。Authoring、distribution 或 creator release profile 可以把缺失默认 sidecar 升级为 failure，除非作者明确 opt out。

`enforced_by: tools` 在纯静态模式下仍是条件性保证。只有带事件证据的 runtime trace，或带 provenance 的 hard tool capability evidence，才能让它成为硬保证；裸 `tool_enforcement: "hard"` 自报不足以通过 `--strict-tools`。

## 示例

以下示例演示原生 AISP 技能包；公开 examples 默认包含同目录 Agent Skills `SKILL.md` sidecar，但 core conformance 仍不强制。

### 原生 AISP 示例

| # | 技能 | 风险 | 演示内容 |
|---|------|:----:|---------|
| 1 | [`yijing_aisp/`](examples/aisp/yijing_aisp/) | **low** | 单技能只读占卜；确定性图；`enforced_by -> sys.assert`；默认同目录 `SKILL.md` sidecar |
| 2 | [`stock_analysis_aisp/`](examples/aisp/stock_analysis_aisp/) | **medium** | 股票分析示例；声明式 data/script/eval 资源；`enforced_by -> tools` 条件边界由示例本地 runtime trace evidence 在发布检查中闭合；默认同目录 `SKILL.md` sidecar |
| 3 | [`aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/) | **medium** | AISP 创建/进化/转换 meta-skill；严格候选校验；默认同目录 `SKILL.md` sidecar |

### AISP Creator / Evolution 示例

本仓库包含一个原生 AISP creator/evolution 示例：[`examples/aisp/aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/)。它演示如何用一个 AISP 技能辅助创建、进化、研究、验证和审查其它原生 AISP 技能，同时保持在 AISP 技能包模型内。该示例内置 specification 快照、schemas、reference tools、templates 和可回放 eval 证据，便于离线审查。

creator 是示例技能，不是信任机构，也不是生产 runtime。它内置的 snapshots 与 manifests 只提供本地参考和完整性证据，不证明上游信任、freshness 或 registry 认可。由它生成或进化的技能仍必须通过 reference validators、README 派生一致性检查、人工审查门，以及发布方要求的外部 provenance / registry 检查。

发现演练与 `aisp/` 目录契约见 [`examples/README.md`](examples/README.md)。

## 文档

| 文档 | 说明 |
|------|------|
| [AISP 协议规范](specification/AISP_Protocol_cn.md) / [English](specification/AISP_Protocol.md) | 完整协议规范 |
| [一致性标准](specification/standards/) | 可机器核验的 M / R / SE / EC 一致性规则 |
| [一致性检查指南](docs/guides/conformance-walkthrough_CN.md) / [English](docs/guides/conformance-walkthrough.md) | 如何运行并解读 validator 输出 |
| [发布证据矩阵](docs/reference/release-evidence-matrix_CN.md) | 发布检查清单、证据层级、预期 warning 和信任边界 |
| [Validator Coverage](docs/reference/validator-coverage.md) | 参考工具的静态、trace 证据与 bridge 检查覆盖范围 |
| [Generated Skill README](docs/reference/generated-readme.md) | 单技能 README 的生成、检查与信任边界 |
| [Registry 与 Runtime Artifacts](docs/reference/registry-runtime-artifacts.md) | Runtime trace、registry manifest 与工具能力 schema |
| [Snapshot Release Workflow](docs/guides/snapshot-release-workflow.md) | 刷新 creator 内嵌快照与发布 metadata 的流程 |
| [aisp.proto](specification/aisp.proto) | 技能发现与一致性服务的 Proto3 schema |
| [主题](docs/topics/) | 概念指南：Axiom 0、技能合同、安全模型、enforced_by、资源、生命周期 |
| [指南](docs/guides/) | 分步教程：入门、第一个技能、发现、一致性 |
| [参考](docs/reference/) | 字段参考、文法、术语表、错误码和威胁分类 |
| [ADR](adrs/) | 架构决策记录 |
| [CHANGELOG](CHANGELOG.md) | 版本历史 |

## AIXP Labs [aixp.dev](https://aixp.dev)

AIXP Labs 开发和维护以下核心项目：

| 项目 | 描述 | 网站 |
|------|------|------|
| [HSAW](https://hsaw.dev) | 人类主权与福祉 — 公理 0 白皮书（基座） | hsaw.dev |
| [AISP](https://aisp.dev) | AI Skill Protocol — 可执行、可治理的技能包（本项目） | aisp.dev |
| [AIAP](https://aiap.dev) | AI Application Protocol — 治理与合规 | aiap.dev |
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol — 流程程序定义 | aisop.dev |
| [AIBP](https://aibp.dev) | AI Bot Protocol — 社交通信与信任 | aibp.dev |
| [AIVP](https://aivp.dev) | AI Value Protocol — 国际商业、加密资产结算 | aivp.dev |
| [AILP](https://ailp.dev) | AI List Protocol — 代理发现与能力广告 | ailp.dev |
| [SoulBot](https://soulbot.dev) | AI 代理运行时与框架 | soulbot.dev |
| [SoulACP](https://soulacp.dev) | 适配器库 — 桥接 CLI 工具与 LLM 提供商 | soulacp.dev |

## 贡献

AISP 是一个开放协议，欢迎贡献、反馈和讨论。

- **Issue**：[GitHub Issues](https://github.com/AIXP-Labs/AISP/issues)
- **贡献指南**：[CONTRIBUTING_CN.md](CONTRIBUTING_CN.md) / [CONTRIBUTING.md (English)](CONTRIBUTING.md)

## 免责声明

本协议规范及参考实现仅供**研究和教育用途**。它们是**实验性**软件，不适用于生产环境。使用风险由用户自行承担。作者对因使用本软件造成的任何损害不承担责任。完整条款见 [LICENSE](LICENSE)（Apache 2.0）。

## 许可证

[Apache License 2.0](LICENSE) - Copyright 2026 AIXP Labs AIXP.dev | AISP.dev

> AIXP 生态统一使用 **Apache 2.0** 许可证（aisop.dev、aiap.dev、aisp.dev、soulbot.dev 所有层），提供专利保护与生态一致性。详见 [GOVERNANCE.md](GOVERNANCE.md#the-layered-chain)。

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
