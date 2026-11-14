# AISP — AI 技能协议

[English README](README.md)

[![Validate](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml/badge.svg)](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-AISP_V1.0.0-brightgreen.svg)](https://aisp.dev)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![Axiom 0](https://img.shields.io/badge/Axiom_0-Human_Sovereignty_and_Wellbeing-orange.svg)](GOVERNANCE.md)

**AISP 把可执行、可治理、可分发的 AI 技能打包成自包含技能文件夹。**

AISP 是以 AISOP 为执行基础、借 Agent Skills 标准桥接的可治理技能包。

> **AISP V1.0.0 协议修订版：**必需的 M7 接口和版本条件引导已实现。SoulRun 是可替换默认值，不是协议依赖。本地一致性检查不认证全部运行期保证、外部副本或发布资格。详见[发布证据要求](docs/reference/release-evidence-matrix_CN.md)。

[协议规范](specification/AISP_Protocol_cn.md) | [快速开始](#快速开始) | [示例](#示例) | [发布证据](docs/reference/release-evidence-matrix_CN.md) | [验证器覆盖](docs/reference/validator-coverage.md) | [AIXP Labs](#aixp-labs-aixpdev)

| 事实 | 值 |
|------|----|
| 协议 | AISP V1.0.0 |
| 全称 | AI Skill Protocol（AI 技能协议）|
| 权威域名 | [aisp.dev](https://aisp.dev) |
| 执行层 | [aisop.dev](https://aisop.dev) |
| 默认执行器（可替换）| SoulRun（`soulrun.dev`）|
| 基础公理 | Human Sovereignty and Wellbeing（人类主权与福祉）|

## AISP 是什么？

AISP 定义 AI 的**技能包层**。[Agent Skills](https://agentskills.io/specification)（`SKILL.md`）用散文加渐进披露描述技能；AISP 解决的是另一个问题：如何把一个技能打包成**真正可执行的程序**，并带有可机器检查的合同、声明式资源、验证规则和分发生命周期。

一个原生 AISP 技能是一个文件夹 `aisp/<id>_aisp/`，包含固定文件名的 AISOP 程序 `aisp.aisop.json`、必需的生成式 `SKILL.md` 接口和已声明资源。生成式 `README.md` 用于介绍技能包（通常推荐，strict/release profile 必需）。技能合同是程序内部的 `user.content.aisp_contract` 真 JSON object，不是另一个文件。生成、进化和分发由作者自选的外部工具承担。

**核心理念**：硬保证是强制出来的，不是提示出来的。红线通过 `non_negotiable.enforced_by -> sys.*`、`aisop.main` 或受限 tools 绑定到真实机制。信任绝不自报。

**互补，非替代**：业务定义保留在 `aisp.aisop.json`；所有合规包 MUST 包含生成的同目录 `SKILL.md` 兼容接口（M7）。固定引导程序将执行交给合规执行器，默认 SoulRun。没有执行器就停止，不自行执行或续跑；经执行器读取及用户要求的代码审查仍允许。

## 仓库范围

| 本仓库包含 | 用途 |
|------------|------|
| `specification/` | 规范性协议文档、一致性标准和 Proto schema |
| `schemas/` | 合同、runtime trace、registry manifest、工具能力的 JSON Schema |
| `tools/` | 零运行时依赖的参考 validator、hash 工具、README/SKILL.md 生成器和 bridge 检查器 |
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
- **必需的 `SKILL.md` 兼容接口** — M7 检查文件存在、技能派生的 name/description/license 和固定执行器引导正文。五个命令字符串和一个冻结版本策略可变；它们是配置值，不是多套引导流程。业务逻辑保留在 AISP 程序中。
- **Axiom 0 强制** — 每个技能继承人类主权与福祉；`sys.io.confirm` 保持强制阻塞。

## 协议栈

```text
应用层
  |
AISP  - 技能包层（本协议）
  |
AISOP - 执行层（.aisop.json 流程程序）
  |
合规 AISP/AISOP 执行器（默认 SoulRun，可替换）
```

AISP 把 AISOP 程序打包成可发现、可触发、可治理、可分发的技能单元。它建在 AISOP 之上用于执行，不重新定义执行引擎。每一层都独立持守 Axiom 0。

## 技能如何运行

只有**一条引导流程、一个核心判断**：所配执行器已安装的包版本是否满足冻结的 `executor_version_policy.requirement`？

| 版本状态 | 行为 |
|---|---|
| 满足 `>=X.Y.Z` 或 `==X.Y.Z` | 直接交给执行器运行，不询问安装/升级。 |
| 已证实未安装，或不满足约束 | 询问是否安装满足约束的版本。仅在同意后安装，再核对同一条件，满足才运行。 |

拒绝、安装失败或安装后复查失败/仍不满足时停止。版本输出未知、权限拒绝和超时是探测错误，不是未安装证明，不能因此重装。`==` 必须安装精确版本；涉及降级时也须明示并取得同意。

SoulRun 默认下限在首次生成或显式刷新时解析最新稳定版，并冻结成具体版本。普通重生成保留冻结下限，运行期版本检查不查询 latest；显式约束优先。仓内示例目前为 `>=1.0.1`，不代表协议永久最低版本，也不声称它是今天的最新版。安装仅在用户同意后才可访问包源。版本满足也不豁免技能自身的业务确认门。

## 快速开始

前置条件：Python 3.11 或更高版本。参考工具运行时只用 Python 标准库；`jsonschema` 只用于 schema 相关测试覆盖。

直接在源码目录运行参考脚本，无须安装本仓库。schema 相关测试需要单独安装已声明的测试依赖：

```bash
python -m pip install "jsonschema>=4"
```

可选开发安装：`python -m pip install -e ".[dev]"`。
打包配置显式包含 `tools`；已检查离线 editable 元数据、wheel 构建及干净 venv
安装后的八个命令入口。wheel 包含参考工具，不包含技能示例、schema 或运行器。
下方源码命令仍可在不安装本仓库时使用。安装成功或检查通过不代表获准发布。

打包需要仅构建期使用的 `setuptools>=84.1.0`；安装后的参考工具仍只依赖标准库。
忽略规则不会清理已跟踪文件、历史或分发归档。分享前须检查本地产物和构建制品，
详见[安全政策（英文）](SECURITY.md#repository-hygiene)。
wheel 的包数据设置与源码归档选取分开处理：[`MANIFEST.in`](MANIFEST.in) 会在存在
旧源文件清单时仍从 sdist 排除已知私密文件及运行、测试、构建和 `.venv` 残留。这是有界防护，不是完整秘密
检测器；仍须使用干净源码构建并检查实际归档。

### 1. 查看包结构

规范性的 AISP 包结构如下：

```text
aisp/
└── yijing_aisp/            # 文件夹名 == id，必须以 _aisp 结尾
    ├── README.md           # 生成式介绍；SHOULD，strict/release 必需
    ├── SKILL.md            # MUST：生成式 Agent Skills 兼容接口
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

使用 `-IncludePytest` 可额外运行 pytest 且不写入 `.pytest_cache/`；须先另行安装
`pytest`；`[dev]` 元数据仅声明 `jsonschema`，不包含 pytest。
`-RequireClean` 增加最终工作树检查，但不加该参数，封装脚本也会执行
`git diff --check`。禁止 Git 时，不得运行该封装；仅单独运行获准的非 Git
检查，并如实说明完整发布门未运行。

下列共享参考命令不是封装/CI 的逐项展开：两者还检查 JSON 语法，封装额外扫描
残留和私密路径，CI 则用 `git diff-tree --check --root -r HEAD` 检查已提交空白。
精确步骤以 [`scripts/release_check.ps1`](scripts/release_check.ps1) 和
[workflow](.github/workflows/validate.yml) 为准。

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

### 5. 通过接口或执行器运行

在 Agent Skills 宿主中，按该宿主支持的技能发现方式提供目标技能目录，使用其生成式 `SKILL.md`。接口检查上述版本条件，再把同目录业务程序交给所配执行器。本仓库本身不是宿主插件或运行时安装器。

直接调用 SoulRun 时，先满足声明的版本要求。在本仓库之外准备私有工作目录（下例使用同父目录下的 `../aisp-demo-run/`），把用户实际请求的可移动副本放入其中的 `message.txt`。在仓库根目录运行：

```bash
soulrun --aisp examples/aisp/yijing_aisp --soulrun-cache-dir ../aisp-demo-run/.soulrun_cache --user-message-file ../aisp-demo-run/message.txt --host-tool "agent=false"
```

`agent=false` 如实关闭了本例所不需要的子代理能力；不能用它把其它技能的 `agent` 节点压成 inline。运行记录可能含用户消息和模型回答，SoulRun 还可能把消息文件移入该场运行。须实际核对访问权限及忽略文件状态；`.gitignore` 不是访问控制，也不防止有意公开。CLI 输出是交给宿主/模型的本轮指令，退出 0 不代表业务已完成；完成须有运行结束记录和对应产物，停在确认门上也不等于同意。

其它合规执行器通过自身支持的接口载入 `aisp.aisop.json`，执行 `user.content.aisop.main` 并遵守 `user.content.aisp_contract`。宿主不得自行解释执行或续跑业务程序。

## 验证边界

参考工具链是一致性门禁，不是信任 oracle。

| 检查 | 证明什么 | 不证明什么 |
|------|----------|------------|
| 静态 validator | M1-M7 加静态 SE/EC 包检查 | 完整 runtime 行为或外部信任 |
| Runtime trace checker | 已发布 v1 trace 的形状及部分 R 系列事件一致性检查 | 通用 schema 校验、完整运行期合规、独立认证事件真实或 trace 来源可信 |
| 生成 README 检查 | 与 `aisp.aisop.json` 派生一致 | 技能安全、可信或 registry 认可 |
| Hash 工具 | 可重算的本地完整性记录 | 安全性、背书或 provenance 本身 |
| SKILL.md 生成/检查 | 文件存在、技能派生头部、固定引导正文、执行器配置与版本策略格式（M7）| 执行器认证、平台行为、安全、信任或执行完成 |
| Bridge validator | 共享 M7，加头部/路径安全和原生包校验 | 运行期硬保证或执行完成 |

缺失、旧版或漂移的 `SKILL.md` 均为 M7 failure，无 opt-out。核心与桥检查共用只读函数；通过只证明引导未改、格式正确，不认证执行器、信任、安全或执行完成。明确迁移、执行器配置与版本策略与会话限制见规范 §20。

`enforced_by: tools` 在纯静态模式下仍是条件性保证。`--strict-tools` 要求满足检查器的事件/provenance 证据条件，裸 `tool_enforcement: "hard"` 自报不足以通过。但满足这些条件并不独立认证证据来源，也不自动证明真实的硬执行；硬保证仍取决于运行时实际权限控制和可信的证据来源。

工具能力产物在消费证据前也须通过 v1 有界形状检查，即使未启用 `--strict-tools`，
畸形产物也会失败，而非降为 warning。README/SKILL.md 写入拒绝符号链接输出，
并逐文件原子替换。批量预检不等于多文件事务；后续 I/O 失败可能保留明确报告的先前写入。

文档检查拒绝缺失或越界的扫描目标，并从正文而非围栏/行内代码示例识别锚点；
它是有界 Markdown 检查器，不是完整渲染引擎。trace 中明确否认合同读取或可见性、
却又存在相应肯定事件时会失败；一致性仍不等于 trace 真实性认证。已知 inline 节点
（包括省略模式时的默认值）若记录了派发事件，也必须保持 inline。非法链接路径或
不可读的锚点目标会返回失败，而非异常崩溃。

严格校验拒绝 `null` 等非程序 JSON 值；解析失败不是成功的空报告。
已知可选文本字段出现时须为字符串，`params` 须为对象，`tools` 须为非空白字符串数组；
除非另有绑定要求工具白名单，否则允许省略 `tools` 或使用空数组。这不新增必填字段，
不认证许可证标识，也不证明提示语义。只有许可证缺失或字符串仅含空白才触发存在性
warning；非字符串许可证仍按类型错误 FAIL，不混报为缺失许可证。
索引检查同时比较目录派生的路由元数据及 id/path，陈旧缓存仍按 EC2 发 warning。
哈希输出拒绝覆盖业务程序和声明资源输入，包括别名。
读取文件前还须确认共享资源根仍在所选 `aisp/` 目录内。接口检查保留 `SKILL.md`
的链接身份并拒绝符号链接；递归投影拒绝越界技能目录。发现脚本扫描是有界 AST
检查，不是沙箱，也不证明代码无害。
资源模式检查覆盖选定的字面量读取和 run/bg 调用，包括常见的带引号 Python 路径及
无害的点/分隔符别名；动态命令和运行期真实模式门控仍不由这项静态检查证明。
Python 组合选项与文件操作数分别识别。不同 scope 的资源可以同名。若所有匹配声明
都禁止当前操作，SE3 失败；其余目标不明的字面量用法发 warning，不证明所选 scope，
也不合并权限。

## 示例

以下示例包含必需的生成式接口；版本策略是具体查询快照，不是协议永久最低版本。离线合规不能替代真实宿主验收或发布授权。

### 原生 AISP 示例

| # | 技能 | 风险 | 演示内容 |
|---|------|:----:|---------|
| 1 | [`yijing_aisp/`](examples/aisp/yijing_aisp/) | **low** | 单技能只读占卜；确定性图；`enforced_by -> sys.assert`；必需的同目录 `SKILL.md` 兼容接口 |
| 2 | [`stock_analysis_aisp/`](examples/aisp/stock_analysis_aisp/) | **medium** | 股票分析示例；声明式 data/script/eval 资源；示例本地 trace 夹具用于检验严格证据检查，不独立认证真实运行期硬执行；必需的同目录 `SKILL.md` 兼容接口 |
| 3 | [`aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/) | **medium** | AISP 创建/进化/转换 meta-skill；严格候选校验；必需的同目录 `SKILL.md` 兼容接口 |

### AISP Creator / Evolution 示例

本仓库包含一个原生 AISP creator/evolution 示例：[`examples/aisp/aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/)。它演示如何用一个 AISP 技能辅助创建、进化、研究、验证和审查其它原生 AISP 技能，同时保持在 AISP 技能包模型内。该示例内置 specification 快照、schemas、reference tools、templates 和可回放 eval 证据，便于离线审查。

creator 是示例技能，不是信任机构，也不是生产 runtime。它内置的 snapshots 与 manifests 只提供本地参考和完整性证据，不证明上游信任、freshness 或 registry 认可。由它生成或进化的技能仍必须通过 reference validators、必需接口及 README 派生一致性检查、人工审查门，以及发布方要求的外部 provenance / registry 检查。本地校验或回放夹具不代表每种创建/进化流程都已通过真实模型测试。

发现演练与 `aisp/` 目录契约见 [`examples/README.md`](examples/README.md)。

Creator 候选发布门包含可执行脚本回归，不只是只读检查。静态/证据预检失败时
跳过回放，回放出现非预期失败时停止，并保留参考验证器的 warning。
须先审查、信任工具与用例命令并使用隔离宿主；`shell=False` 不等于沙箱或禁网保证。

## 文档

| 文档 | 说明 |
|------|------|
| [AISP 协议规范](specification/AISP_Protocol_cn.md) / [English](specification/AISP_Protocol.md) | 完整协议规范 |
| [一致性标准](specification/standards/) | 可机器核验的 M / R / SE / EC 一致性规则 |
| [一致性检查指南](docs/guides/conformance-walkthrough_CN.md) / [English](docs/guides/conformance-walkthrough.md) | 如何运行并解读 validator 输出 |
| [发布证据矩阵](docs/reference/release-evidence-matrix_CN.md) / [English](docs/reference/release-evidence-matrix.md) | 发布检查清单、证据层级、预期 warning 和信任边界 |
| [验证器覆盖（英文）](docs/reference/validator-coverage.md) | 参考工具的静态、trace 证据与 bridge 检查覆盖范围 |
| [生成式技能 README（英文）](docs/reference/generated-readme.md) | 单技能 README 的生成、检查与信任边界 |
| [Agent Skills 接口（英文）](docs/topics/interoperability-with-agent-skills.md) | 必需的 SKILL.md、版本条件、明确迁移与宿主边界 |
| [Registry 与 Runtime 产物（英文）](docs/reference/registry-runtime-artifacts.md) | Runtime trace、registry manifest 与工具能力 schema |
| [快照发布流程（英文）](docs/guides/snapshot-release-workflow.md) | 刷新 creator 内嵌快照与发布 metadata 的流程 |
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
| [HSAW](https://hsaw.dev) | 人类主权与福祉 —— Axiom 0 白皮书（基石） | hsaw.dev |
| [AIZP](https://aizp.dev) | AI Zenith-Zero Protocol —— 运行时行为对齐 | aizp.dev |
| [AIIP](https://aiip.dev) | AI Intent Protocol（AI 意图协议）—— 意图树治理、优先级与反馈 | aiip.dev |
| [AIKP](https://aikp.dev) | AI Knowledge Protocol（AI 知识协议）—— 长期知识组织、导航与治理 | aikp.dev |
| [AIJP](https://aijp.dev) | AI Job Protocol（AI 作业协议）—— 可调度的工作树与作业图 | aijp.dev |
| [AINP](https://ainp.dev) | AI Neogenesis Protocol（AI 创生协议）—— 可治理的生成项目：计划 + 内容 + 证据 | ainp.dev |
| [AILP](https://ailp.dev) | AI List Protocol —— agent 发现与能力广告 | ailp.dev |
| [AIVP](https://aivp.dev) | AI Value Protocol —— 国际商务、加密资产结算 | aivp.dev |
| [AIRP](https://airp.dev) | AI RMB Protocol —— 中国大陆商务、人民币持牌结算 | airp.dev |
| [AIBP](https://aibp.dev) | AI Bot Protocol —— 社交通信与信任 | aibp.dev |
| [AIAP](https://aiap.dev) | AI Application Protocol —— 治理与合规 | aiap.dev |
| [AISP](https://aisp.dev) | AI Skill Protocol —— 目录式技能包，以 AISOP 技能入口和可执行契约绑定为核心 **（本项目）** | aisp.dev |
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol —— 流程程序定义 | aisop.dev |
| [AIXPStore](https://aixpstore.dev) | AIAP 程序与 AISP 技能官方市场 —— 发现、发布和分发 AI 能力包 | aixpstore.dev |
| [SoulSkill](https://soulskill.dev) | AISP 技能参考库 & 多 CLI 插件分发 | soulskill.dev |
| [SoulAgent](https://soulagent.dev) | 任何 CLI / SDK / IDE 直接调用的 drop-in AI agent | soulagent.dev |
| [SoulBot](https://soulbot.dev) | AI agent 运行时 & 自编排框架（定时、建 agent、agent 间通信） | soulbot.dev |
| [SoulRun](https://soulrun.dev) | 一个调用的 AISOP 执行引擎 —— 为任何宿主运行 AIAP 程序与 AISP 技能 | soulrun.dev |
| [SoulACP](https://soulacp.dev) | 适配库 —— 桥接 CLI 工具与 LLM 提供方 | soulacp.dev |

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

<a id="values-philosophy"></a>

## ⚓ 价值观与哲学 (Alignment & Philosophy)

### Axiom 0: [HSAW | Human Sovereignty and Wellbeing](https://hsaw.dev)

- **No HITL, HSAW.**
  *人类主权与福祉是第零公理，无需虚伪的人机协同。*
- **No w.a.s.h, Real h.s.a.w.**
- **人非蝼蚁，人为道。**
- **We are not beggars. We the People.**
