# 一致性检查指南

AISP 技能通过一套一致性框架检查：技能规则 **M1-M6**、runtime 规则 **R1-R7**，以及 **SE**（安全）和 **EC**（生态）扩展。本指南说明如何检查一个技能、阅读结果，并修复常见违规。与运行时测试不同，一致性检查是执行前门禁：技能在运行前先被验证。

---

## 概览

一个一致的 AISP 技能首先必须是**合法 AISOP V1.0.0 程序**（M1），然后才满足额外的技能包规则 M2-M6。规则来源如下：

| 系列 | 来源 | 范围 |
|------|------|------|
| M1-M6 | `AISP_Standard.core` | 技能一致性（违规为 FAIL） |
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

验证器覆盖 M1-M6 与 SE/EC 的静态部分。运行时一致性证据通过 `aisp_check_runtime_trace.py` 从 trace JSON 检查；真实 runtime harness 可以输出该 trace 形状。`enforced_by: tools` 在纯静态模式下是条件性保证，只能由带事件证据的 runtime trace 或带 provenance 的 tool capability artifact 消解；`--strict-tools` 会拒绝裸 hard 自报。Registry/provenance 哈希通过 `aisp_hash.py` 生成。单技能 README 投影由 `aisp_readme.py` 生成和检查；检查通过只证明一致性，不证明可信或安全。默认但 core 可选的 Agent Skills sidecar 由 `aisp_skill_md.py` 生成，并由 `aisp_validate_agent_skill_bridge.py` 检查；生成/bridge 检查通过只证明投影一致、sidecar 形状正确且原生 AISP 通过验证，不证明外部信任。缺少 sidecar 在 core 校验里是 EC7 warning，不是 core failure；只有更严格发布 profile 要求默认 sidecar 时才升级。

### 第 1 步：确认它是合法 AISOP 程序（M1）

解析 `aisp.aisop.json`。它 MUST 是 2-message array；`data[0].content` MUST 包含 `protocol == "AISP V1.0.0"`，以及 `axiom_0` / `id` / `name` / `version` / `flow_format`；`data[1].content` MUST 包含 `instruction` / `aisop.main` / `functions`。`license` SHOULD 存在。

### 第 2 步：检查技能包规则（M2-M6）

| 规则 | 检查 |
|------|------|
| **M2** | 文件夹名 == `id`，以 `_aisp` 结尾；文件名为 `aisp.aisop.json` |
| **M3** | `user.content.aisp_contract` 是真 object；`profile` 以 `aisp.skill.` 开头；包含 `invocation` + `non_negotiable` |
| **M4** | 每条 `non_negotiable.enforced_by` 都指向实际存在的机制 |
| **M5** | 每条 `resources[].path` 是相对路径、无 `../`；`mode` 在枚举内；脚本声明 `requires_tools` |
| **M6** | 不自报信任（`trusted` / `verified` / `safe`） |

### 第 3 步：详细验证红线绑定（M4）

对每个 `enforced_by`：

- `<node>.stepN:<mechanism>` -> `functions[node][stepN]` 作为数字执行步骤存在，且该 step 以对应 mechanism 开头。
- `aisop.main` -> 必要节点/分支存在于图中。
- `tools` -> `tools` 是受限 allow-list；并注意：只有 runtime 真正执行工具权限时才是硬保证。

### 第 4 步：应用安全与生态扩展

运行 SE1-SE8（路径限制、远程资源门禁、mode 门控、最小授权、发现脚本安全、不自报信任、确认不变量、执行期只读）和 EC1-EC8（`aisp/` 目录契约、索引与文件夹一致性、`_shared/` 作用域、provenance、生成、进化安全、sidecar bridge、生成式单技能 README）。

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

干净技能会在 M1-M6 上全部 PASS。

---

## 常见违规与修复

### M4 违规：幽灵 enforcement

**问题。** `non_negotiable` 声明 `enforced_by: "interpret.step9:sys.assert"`，但 `interpret` 没有 `step9`。

**影响。** 这是一个看起来安全、实际不存在的硬保证，是最危险的失败类型之一。

**修复。** 接入真实 `sys.assert` 步骤，或把该规则降级为 `functions.<node>.constraints` 中的普通指导，并从 `non_negotiable` 移除。

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

只有 `enforced_by -> sys.*` 是硬保证；模型读到的其它内容都是 policy-as-prompt。

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
