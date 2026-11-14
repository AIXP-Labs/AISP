# 一致性检查指南

AISP 技能通过一套一致性框架检查：技能规则 **M1-M7**、runtime 规则 **R1-R7**，以及 **SE**（安全）和 **EC**（生态）扩展。本指南说明如何检查一个技能、阅读结果，并修复常见违规。静态一致性是执行前的一致性门禁，不证明运行期强制机制或业务行为已经验证。

---

## 概览

一个一致的 AISP 技能首先必须是**合法 AISOP V1.0.0 程序**（M1），然后满足 M2～M7，包括必需的生成式兼容接口。规则来源如下：

| 系列 | 来源 | 范围 |
|------|------|------|
| M1-M7 | `AISP_Standard.core` | 技能一致性（违规为 FAIL） |
| R1-R7 | `AISP_Standard.core` | Runtime 一致性 |
| SE1-SE8, ST1-ST6 | `AISP_Standard.security` | 安全 + 威胁分类 |
| EC1-EC8 | `AISP_Standard.ecosystem` | `aisp/` 目录 + 生命周期复用 + 生成式技能 README |

---

## 运行一致性检查

使用零依赖参考验证器执行静态检查：

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

逐条命令的证据层级、预期 warning 处理和信任边界，见 [Release Evidence Matrix](../reference/release-evidence-matrix_CN.md)。在纯静态运行中，`AISP_W_R6_TOOLS_CONDITIONAL` 是 `enforced_by: tools` 的预期诚实信号；只有带事件证据的 runtime trace 或带 provenance 的 hard tool capability evidence 才能消解它。

只有在明确需要更新派生文件时，才运行生成命令：

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

验证器覆盖 M1～M7 与静态 SE/EC。运行 trace 由 `aisp_check_runtime_trace.py` 检查；`--strict-tools` 拒绝裸 hard 自报，并要求现有事件/provenance 证据。`aisp_hash.py` 生成发布哈希，不授予信任；README 检查只证明派生一致性。必需的生成式 SKILL.md 由核心与桥共同使用的只读 M7 函数检查：文件存在、派生头部、固定引导正文、五个合法命令字符串及冻结版本策略。缺失、旧版、漂移均 FAIL，无 opt-out。格式通过不认证执行器、安全、信任或执行完成；执行 MUST 使用合规执行器，默认 SoulRun，不能宿主自行执行。

### 第 1 步：确认它是合法 AISOP 程序（M1）

解析 `aisp.aisop.json`。它 MUST 是 2-message array；`data[0].content` MUST 包含 `protocol == "AISP V1.0.0"`、`loading_mode == "node"`，以及 `axiom_0` / `id` / `name` / `version` / `flow_format`；`data[1].content` MUST 包含 `instruction` / `aisop.main` / `functions`。每个函数需要字符串类型的数字 `stepN`；显式 `execute_mode` 只能为 `inline` 或 `agent`，省略时回退 inline 并 warning。`license` SHOULD 存在。

### 第 2 步：检查技能包规则（M2-M7）

| 规则 | 检查 |
|------|------|
| **M2** | 文件夹名 == `id`，以 `_aisp` 结尾；文件名为 `aisp.aisop.json` |
| **M3** | `user.content.aisp_contract` 是真 object；`profile` 为带版本的 `aisp.skill.v<major>`；包含 `invocation` + `non_negotiable` |
| **M4** | 每条 `non_negotiable.enforced_by` 都指向实际存在的机制 |
| **M5** | 每条 `resources[].path` 是相对路径、无 `../`；`mode` 在枚举内；脚本声明 `requires_tools` |
| **M6** | 不自报信任（`trusted` / `verified` / `safe`） |
| **M7** | 必需的同目录 SKILL.md、派生头部、固定执行器引导正文；仅五个合法命令字符串及冻结版本策略可变 |

### 第 3 步：详细验证红线绑定（M4）

对每个 `enforced_by`：

- `<node>.stepN:<mechanism>` -> `functions[node][stepN]` 作为数字执行步骤存在，且该 step 以对应 mechanism 开头。
- `aisop.main` -> 必要节点/分支存在于图中。
- `tools` -> `tools` 是受限 allow-list；并注意：只有 runtime 真正执行工具权限时才是硬保证。

### 第 4 步：应用安全与生态扩展

核对静态 SE/EC 覆盖，并另行评估仅运行期可验证的要求：SE1-SE8 包括路径限制、远程资源门禁、mode 门控、最小授权、发现脚本安全、不自报信任、确认不变量和执行期只读；EC1-EC8 包括目录/索引、共享作用域、provenance、生成、进化、EC7 到 M7 的必需接口映射及生成式 README。静态验证器不会实际执行每条安全规则。

---

## 示例：`yijing_aisp`

| 规则 | 结果 | 原因 |
|------|:----:|------|
| M1 | PASS | 2-message array；`protocol: AISP V1.0.0`；`license: Apache-2.0`；存在 `aisop.main` |
| M2 | PASS | 文件夹 `yijing_aisp/` == id，以 `_aisp` 结尾；文件为 `aisp.aisop.json` |
| M3 | PASS | `aisp_contract` 是 user message 中的真 object；`profile: aisp.skill.v1`；包含 `invocation` + `non_negotiable` |
| M4 | PASS | `aisop.main` 保证 cast -> interpret 顺序；`interpret.step1:sys.assert` 存在；`interpret.step4:sys.assert` 存在 |
| M5 | PASS | `data/hexagrams.json`、`data/interpretation_guide.md` 均为相对路径、已声明、`read_only` |
| M6 | PASS | 无自报信任 |
| M7 | PASS | 生成式接口与技能、执行器配置和固定引导正文一致 |

干净技能会在 M1-M7 上全部 PASS。

M4 只检查绑定存在和机制前缀，不求值断言，也不证明条件准确表达了红线。当前免责声明示例比较约定的精确文本，不再仅检查存在，但仍须运行器实际求值；即使业务完成，不支持的表达式或运行器接受的未验证结果仍须明确保留。

---

## 常见违规与修复

### M4 违规：幽灵 enforcement

**问题。** `non_negotiable` 声明 `enforced_by: "interpret.step9:sys.assert"`，但 `interpret` 没有 `step9`。

**影响。** 这是一个看起来安全、实际不存在的硬保证，是最危险的失败类型之一。

**修复。** 修正绑定，在运行时支持的真实步骤中实现预期检查，再验证通过与失败行为。不能仅为通过校验而删除或弱化红线；有意修改合同须另经人工审查和授权。

### M5 违规：路径逃逸

**问题。** 资源 `path` 是 `../secrets.json`。

**影响。** 技能越过自身文件夹访问外部文件，构成资源逃逸威胁（ST4）。

**修复。** 将路径限制在技能文件夹内；或把文件移动到 `_shared/` 并设置 `scope: "shared"`。

### M6 违规：自报信任

**问题。** 合同包含 `"verified": true`。

**影响。** 消费方可能基于技能自己的声明降低防备（ST6）。

**修复。** 移除该字段。信任和 provenance 由 registry / scanner / 用户判断，不能由技能自报。

### M2 违规：后缀错误

**问题。** 文件夹名为 `yijing/`，没有 `_aisp`。

**影响。** 发现 glob `*_aisp/aisp.aisop.json` 找不到它。

**修复。** 将文件夹重命名为 `yijing_aisp/`，并同步设置 `id`。

---

## 总结

按优先级检查一致性：

1. **先合法**：它是否是合法 AISOP 程序（M1）？
2. **再绑定**：每条红线是否指向真实机制（M4）？
3. **再安全**：路径受限、无自报信任、确认未被绕过（M5 / M6 / SE7）。

硬保证要求运行时实际执行所绑定的机制：`sys.*`、图拓扑或真正受限的工具权限。静态绑定或自报 trace 不证明强制执行已经发生。接口只应用一个版本判断：匹配即直接执行；已证实缺失/不匹配才询问安装，安装后复查匹配；探测出错就停止。

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
