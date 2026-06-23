# AISP V1.0.0 技能包规范

> 本文档是 [AISP_Protocol.md](AISP_Protocol.md) 的中文翻译。翻译为非规范性内容 — 如有分歧，以英文正文为准（§1.1）。

> **AISP 定义技能包，AISOP 执行技能。**
>
> AISP 是可执行技能包协议，不是另一个 `SKILL.md` 格式。

| 字段 | 值 |
|------|----|
| Protocol | `AISP V1.0.0` |
| 全名 | AI Skill Protocol（AI 技能协议）|
| 权威域 | `aisp.dev` |
| 执行底座 | `AISOP V1.0.0` |
| 规范状态 | 英文规范对技能包规则与结构具有最终解释权 |
| 核心不变量 | Axiom 0：Human Sovereignty and Wellbeing（人类主权与福祉）|

## 一眼看懂

AISP 把 AISOP 程序打包成可发现、可触发、可治理、可分发的 AI 技能。

一个原生 AISP 技能是自包含文件夹，包含：

- `aisp.aisop.json`：可执行 AISOP 程序，也是固定技能文件名。
- `user.content.aisp_contract`：机器可核验的技能合同，作为真 object 放在 user 消息中。
- 声明式资源：在 `aisp_contract.resources` 中列出的 data、scripts 或 shared assets。
- 默认投影：用于分发和互操作的 generated per-skill `README.md` 与同目录薄 `SKILL.md` sidecar bridge。Core AISP 一致性不要求 `SKILL.md`，但 authoring tools SHOULD 默认生成，除非作者明确 opt out。

硬保证只来自真实机制，例如 `enforced_by -> sys.*`。自然语言指导是软约束，信任绝不自报。

## 如何阅读本文档

| 读者 | 建议路径 |
|------|----------|
| 第一次了解 AISP | 读 §§0-4，然后看 §22 完整示例 |
| 技能作者 | 读 §§5-13，然后读 §§20-23 |
| Validator 实现者 | 读 §§4、8-13、17，以及 conformance standards |
| Runtime 实现者 | 读 §§14-17，然后读 `AISP_Standard.core` 中的 R 系列规则 |
| Registry / 分发实现者 | 读 §§17、20-21、附录 B，以及 registry/runtime artifact 参考 |

## 目录

**第一部分：协议基础**

- [0. Axiom 0：人类主权与福祉](#0-公理)
- [1. 协议声明](#1-协议声明)
- [2. 核心定义：什么是 AISP 技能](#2-核心定义)
- [3. 定位：vs Agent Skills；建于 AISOP](#3-定位)
- [4. 一致性与术语](#4-一致性与术语)

**第二部分：技能包结构**

- [5. 技能包结构：folder-per-skill、_aisp、_shared](#5-技能包结构)
- [6. aisp/ 目录：README、aisp_list.py、aisp_list.json](#6-aisp-目录)
- [7. 技能文件：aisp.aisop.json（两层）](#7-技能文件)

**第三部分：技能合同**

- [8. aisp_contract 字段](#8-aisp_contract-字段)
- [9. invocation：触发](#9-invocation触发)
- [10. non_negotiable + enforced_by：红线绑定](#10-non_negotiable-enforced_by红线绑定)
- [11. discovery：发现元数据](#11-discovery发现元数据)
- [12. risk_level：风险](#12-risk_level风险)
- [13. resources：资源](#13-resources资源)

**第四部分：执行与披露**

- [14. 模型看到什么：合同在 user 消息](#14-模型看到什么)
- [15. Tier A 归位：functions / sys.*](#15-tier-a-归位)
- [16. 发现与渐进披露](#16-发现与渐进披露)

**第五部分：安全、命名与版本**

- [17. 安全与信任模型](#17-安全与信任模型)
- [18. 命名规则](#18-命名规则)
- [19. 版本：标记与底座](#19-版本)

**第六部分：互操作与生命周期**

- [20. 互操作：默认 SKILL.md Sidecar Bridge](#20-互操作)
- [21. 生命周期：生成 / 进化 / 分发](#21-生命周期)

**第七部分：示例与诚实**

- [22. 完整示例：yijing_aisp](#22-完整示例)
- [23. 一致性检查清单](#23-一致性检查清单)
- [24. 诚实边界](#24-诚实边界)
- [25. 常见错误](#25-常见错误)

**附录**

- [附录 A：aisp_contract 骨架](#附录-aaisp_contract-骨架)
- [附录 B：目录骨架](#附录-b目录骨架)
- [附录 C：aisp_list.py 零依赖参考实现](#附录-caisp_listpy零依赖参考实现)
- [附录 D：aisp_list.json 索引格式](#附录-daisp_listjson索引格式)
- [附录 E：Sources](#附录-esources)
- [附录 F：最简口号](#附录-f最简口号)

## 第一部分：协议基础

## 0. 公理

### Axiom 0：Human Sovereignty and Wellbeing（人类主权与福祉）

每个 AISP 技能都在 Axiom 0 之下运行——它继承自 AISP 所建之上的 AISOP 执行层（并最终源自最高公理 HSAW）。本协议承认以下不可撤销的前提：

1. **人类主权优先**：技能为人服务、绝不削弱人类控制权；对每一次触发、流程与动作的最终权威属于人类。
2. **福祉不可妥协**：技能不得损害人类的身心健康、尊严或自由；当指令与人类福祉冲突时，福祉优先。
3. **透明与可问责**：技能行为必须可理解、可追溯、可被质疑；隐藏意图或逃避责任违反本公理。
4. **不作恶（Do No Harm）**：无论指令来源，技能不得欺骗、操纵、伤害或剥削人类。

操作后果：

- Axiom 0 不可被任何技能、`aisp_contract`、`instruction`、进化或协议扩展覆盖。
- 每个合规 AISP runtime MUST 以最高执行优先级强制它。
- 其执行层保证是 `sys.io.confirm`：强制阻塞、不可侵犯（SE7）。
- 它在所有 AISP 版本间不可变（[ADR-006](https://github.com/AIXP-Labs/AISP/blob/main/adrs/adr-006-axiom-0-immutability.md)）。
- 每个技能以固定字段 `"axiom_0": "Human_Sovereignty_and_Wellbeing"` 承载（M1）。

平台政策优先级见 §8.1；完整论述见 [Axiom 0](https://github.com/AIXP-Labs/AISP/blob/main/docs/topics/axiom-0.md) 主题文。

---

## 1. 协议声明

```
AISP 技能包规范
Protocol: AISP V1.0.0
Authority: aisp.dev
Execution Base: aisop.dev
Axiom 0: Human Sovereignty and Wellbeing

本文档定义 AISP 技能的技能包规范，包括：
- folder-per-skill 结构与 _aisp 后缀
- 两层（Tier A 执行 / Tier S 合同）
- aisp_contract schema 及其在 user 消息中的位置
- enforced_by 红线绑定（policy-as-code）
- 发现、渐进披露、安全、命名、版本与生命周期

每个 AISP 技能 MUST 首先是合法 AISOP V1.0.0 程序。
.aisop.json 语言本身由 AISOP 治理，不在本文档定义。
```

### 1.1 规范性工件及其角色

本协议由若干工件族记录。冲突时，优先级如下：

| 工件 | 角色 | 权威性 |
|------|------|--------|
| `AISP_Protocol.md`（及 `AISP_Protocol_cn.md` 翻译）| 技能包规范、结构、合同 schema、规则 | 对技能结构与规则**权威** |
| `standards/AISP_Standard.*.aisop.json` | 形式化一致性规则定义（M / R / SE / EC 系列）| 对可机器核验的规则语义**权威** |
| `aisp.proto` | 发现与一致性数据结构及服务 API | 对数据对象 schema 与服务契约**权威** |

**冲突处理**：任一工件看似矛盾时，本 Markdown 规范对*规则与结构*作裁断；`aisp.proto` 对*数据形态与 API 签名*作裁断。翻译（如 `AISP_Protocol_cn.md`）始终非规范 — 分歧以英文为准。

> **本文档不是什么。** AISP 不重定义 AISOP 语言（图语法、`sys.*` 语义）— 那是 `aisop.dev`。AISP 不把生命周期委托给其它协议；生成 / 进化 / 分发是 AISP-native、工具无关。AISP 只定义*技能包*：如何把一个 AISOP 程序做成可发现、可触发、可治理、可分发的技能。

---

## 2. 核心定义

> AISOP 是技能书写的语言。**AISP 是包。**

**原生 AISP 技能** 是一个**自包含文件夹**，内含一个固定文件名的 AISOP 程序 `aisp.aisop.json`，以及该技能自定义布局的资源。它用 AISOP 自己的结构表达一个**可复用、可执行、可治理、可进化**的能力 — **不要求、不依赖 Agent Skills 的 `SKILL.md`**。`SKILL.md` MAY 仅作为同目录 sidecar 投影存在；authoring / distribution tools SHOULD 默认包含该 sidecar，除非作者明确 opt out。

```text
原生 AISP 技能 =
    一个文件夹（folder = skill，文件夹名 = id，必带 _aisp 后缀）
  + aisp.aisop.json（AISOP 程序：合同 + 执行图 + 节点 + sys.*）
  + 自定义资源（data/ scripts/ … 由 aisp_contract.resources 声明）
```

| 概念 | 类比 | 定义 |
|------|------|------|
| **AISOP** | 编程语言（Python）| 执行语言 — `.aisop.json` 文件、Mermaid/JSON 流程、`sys.*` 调用。AISP 的唯一底座。 |
| **AISP** | 包格式 + 清单（npm 包、一个 Skill）| 本协议 — 把 AISOP 程序打包成可发现、可治理的技能 |
| **AISP 技能** | 一个已发布的包 | 一个符合本规范的自包含 `aisp/<id>_aisp/` 文件夹 |

### 2.1 技能即程序

Agent Skills（`SKILL.md`）用 Markdown 散文加渐进披露描述技能。AISP 吸收其"神"（可复用能力、触发、渐进披露、资源），丢弃其"形"（`SKILL.md` body）。真正可执行的主体是 `aisp.aisop.json`，由 AISP/AISOP runtime 直接发现与执行。要在现有 Agent Skills 平台上跑时，authoring tools SHOULD 默认加一个同目录薄 `SKILL.md` sidecar bridge（§20），作者 MAY 为 native-only package 省略它。

```text
命名约定：
  .aisop.json     →  AISOP 语言格式标识（技能本体）
  aisp.aisop.json →  固定技能文件名（众所周知名，类比 SKILL.md / package.json）
  _aisp           →  技能文件夹类型标识（文件夹名 == id，以 _aisp 结尾）
  aisp_contract   →  技能合同（user 消息里的真 object）
```

---

## 3. 定位

### 3.1 与 Agent Skills（互补，非替代）

| | Agent Skills（`SKILL.md`）| **AISP（本协议）** |
|---|---|---|
| 本质 | 散文指令 + 渐进披露 | **可执行流程 + 可治理**（AISOP 图 + `enforced_by → sys.*` 硬约束 + 红线绑定）|
| 标准性 | 跨厂商开放标准 | AISP 自有；**可包含 `SKILL.md` sidecar** 接其平台 |
| 关系 | — | **互补**：AISP 提供 Agent Skills 缺的"可执行+可治理"，并通过默认生成但 core 可选的 sidecar 兼容 |

对外口径：**"AISP 不取代 Agent Skills；它与其互补，提供可执行、可校验、可治理的技能，并可包含薄 `SKILL.md` sidecar 与 Agent Skills 平台互操作。"**

### 3.2 生态分层

```text
HSAW / Axiom 0      人类主权与福祉（最高约束）
      ↓
AISOP（执行）        如何写一个可执行 AI 程序（.aisop.json）
      ↓
AISP（技能包）        把 AISOP 程序打包成可发现/触发/治理/分发的技能单元
```

> AISP 是**技能包**层，仅建在 AISOP（执行）之上，不重造执行引擎。它自己的生命周期（生成/进化/分发/registry）是 AISP 原生、工具无关的——不委派给任何其它协议。

### 3.3 可执行 Skill IR

`aisp.aisop.json` = 跨平台技能语义的**中间表示（IR）+ 运行合同**，不是又一个 `SKILL.md`。**policy-as-prompt vs policy-as-code**：合同/节点的自然语言规则是 policy-as-prompt（LLM 判、软）；`non_negotiable.enforced_by → sys.*` 是 policy-as-code（确定性、硬）— **只有后者是真保证**。

---

## 4. 一致性与术语

关键词 **MUST / SHOULD / MAY** 按 RFC 2119 解读。

### 4.1 技能一致性（MUST）

一个一致的 AISP 技能：

- **M1** MUST **结构上是合法 AISOP V1.0.0 程序**（2-消息数组、必填字段、`user.content` 的 `instruction`/`aisop`/`functions`、`aisop.main` 存在）；其 `protocol` 字段 MUST 声明 **`AISP V1.0.0`**。AISOP 参考校验器只查 `protocol` *存在*、不查其值，故接受 `AISP V1.0.0`；AISOP 引擎照常执行（不以 `protocol` 值设门）。必填字段：`protocol`/`axiom_0`/`id`/`name`/`version`/`flow_format`/`loading_mode`（`license` SHOULD 有，默认 `Apache-2.0`）。对 AISP 技能，`loading_mode` MUST 精确等于 `"node"`。
- **M2** MUST 位于 `aisp/<id>/`，文件名为 `aisp.aisop.json`，`<id>` == 文件夹名且**以 `_aisp` 结尾**（§18）。
- **M3** MUST 含 `user.content.aisp_contract`（真 object），其 `profile` 以 `aisp.skill.` 开头，且含 `invocation` 与 `non_negotiable`（§8）。
- **M4** 每条 `non_negotiable.enforced_by` MUST 指向技能内**真实存在**的机制（§10）。
- **M5** `resources`（若有）的每条 `path` MUST 为相对路径、限本技能夹或 `_shared/`、禁 `../` 逃逸（§17）。
- **M6** 技能 MUST NOT 自报信任（`trusted`/`verified`/`safe`）— 信任由消费方判（§17）。

### 4.2 Runtime 一致性

- **R1（MUST）** AISP runtime MUST 读取 `user.content.aisp_contract` 作为技能合同；MUST 不跳过 `aisop.main` 的必经节点；MUST 不绕过 `sys.io.confirm`（继承 Axiom 0）。
- **R2（MUST）** 对 `non_negotiable`，runtime MUST 通过其 `enforced_by` 指向的机制执行硬约束。
- **R3（MUST）** `aisp_contract` 在 **user 消息**里 — 它本就是模型这一轮上下文的一部分；runtime MUST 把它随 user 消息交给模型（**不得隐藏/剥离**），无需单独"渲染"步骤。`instruction` 以强硬指令命令模型遵从（如 `"STRICTLY OBEY aisp_contract; …; then RUN aisop.main"`）。
- **R4（MUST，对底层 AISOP runtime 的依赖）** 底层 AISOP runtime MUST 对 `system.content` 与 `user.content` 均采用**开放世界校验**（容忍未知键），以便 `user.content.aisp_contract` 与 `system.content.license` 等 AISP 字段共存；并 MUST 不以 `protocol` 值设门（接受 `AISP V1.0.0`）。AISOP 参考实现 `flow_runtime.py` 满足（只校验必填、不拒额外键、不校验 protocol 值）。
- **R5（SHOULD）** runtime 处理不可信技能/资源前 SHOULD 经用户信任门；SHOULD 优先读 `aisp_list.json`（不执行脚本，§16）。
- **R6（SHOULD）** Runtime SHOULD 声明其工具强制是 hard（真权限强制）还是 advisory（提示性）。若为 advisory，`enforced_by: tools` **不得**被当作硬保证。
- **R7（MUST）** Runtime MUST 遵守每个节点的 `execute_mode`——这是继承自 AISOP 的节点级字段（AISOP §5.2.8）。声明 `execute_mode: "agent"` 的节点 **MUST 派发到独立 sub-agent、不得 collapse 成 inline**；声明 `"inline"` 的节点在当前上下文执行。若省略 `execute_mode`，runtime 回退为 `inline`，静态 validator 发出 warning 以促使派发意图显式化。合规 AISP 技能 MUST NOT 显式声明 `"inline"` / `"agent"` 之外的值。这是执行保真度保证。`execute_mode` 是 runtime 遵守的派发属性，**不是** `enforced_by` 机制（§15）。

### 4.3 开放世界 AISOP 兼容性

> AISP 要求底层 AISOP runtime（a）容忍 `system.content`（如 `license`）与 `user.content`（如 `aisp_contract`）中的未知键，且（b）不以 `protocol` 值设门（接受 `AISP V1.0.0`）。拒绝未知键、或要求 `protocol == "AISOP V1.0.0"` 的封闭世界校验器**不是** AISP-兼容的。AISP 文件结构上是 AISOP V1.0.0 程序；AISP 的 `protocol` 标记声明的是技能包语义与协议归属，而非另一套执行文法。

这是 R4 的运行性重述：AISP 不分叉 AISOP 语言，而是搭载 AISOP 的开放世界校验。封闭世界（拒未知键）或硬校验 `protocol` 字面量的校验器无法消费 AISP 文件——这是一个明牌的兼容边界，而非任一协议的缺陷（§24）。

### 4.4 术语

| 术语 | 含义 |
|------|------|
| 技能包（skill package）| `aisp/<id>/` 文件夹整体 |
| 技能文件 | `aisp.aisop.json`（AISOP 程序）|
| 合同（aisp_contract）| `user.content.aisp_contract`（真 object）|
| Tier A / Tier S | 执行层（aisop.main/functions/sys.*）/ 合同层（aisp_contract）|
| Sidecar bridge | 默认生成但 core 可选的同目录 `SKILL.md`，仅为 Agent Skills 平台互操作 |

---

## 第二部分：技能包结构

## 5. 技能包结构

**folder-per-skill；统一文件名 `aisp.aisop.json`；文件夹名 = `id` 且必带 `_aisp` 后缀（沿用同族姊妹协议 AIAP 对 `_aiap` 的命名约定）：**

```text
aisp/                          # 可见目录（非隐藏），AI/人/bash 可直接浏览
  README.md                    # MUST：AISP 用法介绍（什么是 / 怎么发现 / 怎么跑 / 怎么加）
  aisp_list.py                 # 发现脚本（bash 运行 → 列技能；--json 重生成索引）
  aisp_list.json               # 索引缓存（读它也能拿全部技能信息）
  yijing_aisp/                 # 文件夹名 = id "yijing_aisp"（必带 _aisp）
    aisp.aisop.json            # 固定文件名（技能 = 一个 AISOP 程序）
    README.md                  # SHOULD：由 aisp.aisop.json 生成的自举投影
    data/
      hexagrams.json
      interpretation_guide.md
  stock_analysis_aisp/
    aisp.aisop.json
    README.md
    data/ scripts/ ...
  _shared/                     # 跨技能共享资源（非技能文件夹，不带 _aisp）
    finance_terms.md
```

规则：
1. 一个技能 = `aisp/<id>/` 一个自包含文件夹（可整体 zip/发布/算 hash → registry 单元）。
2. 文件名固定 `aisp.aisop.json`（众所周知名，类比 `SKILL.md`/`package.json`）；本质是 `.aisop.json`，扩展名遵 AISOP。
3. **文件夹名 = `id` 且必须以 `_aisp` 结尾**（§18）；后缀让技能夹自识别、并把 `_shared/` 等非技能夹天然排除。
4. **资源布局自定义**（`data/`/`scripts/`/…），由 `aisp_contract.resources` 声明；不强制固定子夹。
5. 单技能 `README.md` SHOULD 由 `aisp.aisop.json` 生成；strict/release profile 可将缺失、手写、漂移、source marker 错误或 generator marker 不受支持升为失败（EC8）。它是自举投影，不是真相源。
6. `_shared/` 放共享资源（`scope:"shared"`）。
7. Core 不要求 `SKILL.md`；authoring tools SHOULD 为新建或分发技能默认生成同目录 sidecar bridge，除非作者明确 opt out（§20）。
8. 发现：读 `aisp/aisp_list.json` 或 bash 跑 `aisp/aisp_list.py`，兜底 glob `aisp/*_aisp/aisp.aisop.json`（§16）。

---

## 6. `aisp/` 目录

| 文件 | 级别 | 作用 |
|------|------|------|
| `README.md` | **MUST** | 向人/AI 介绍：这是什么、怎么发现、怎么跑、怎么加技能（发现契约的人读版）|
| `aisp_list.json` | SHOULD | 索引缓存：各技能 `id`/`name`/`summary`/`path`/`category`/`tags`/`when_to_use`/`risk_level` |
| `aisp_list.py` | SHOULD | 发现脚本：扫 `*_aisp/aisp.aisop.json`、读 `aisp_contract`、打印列表、`--json` 重生成索引（零依赖参考实现见附录 C）|

**真相模型**：**技能文件夹 = 唯一真相；`aisp_list.py` = 派生器；`aisp_list.json` = 缓存。** 三者不竞争 — 以文件夹为准；JSON 疑旧就跑脚本重生成。

单技能 `README.md` 是为独立技能包自举而生成的投影。README 检查通过只证明它与 `aisp.aisop.json` 一致，不证明可信、安全或 registry 认可。通用非 AISOP agent 只能把它当 best-effort 指引；硬保证仍需要符合规范的 AISOP runtime。

---

## 7. 技能文件

`aisp.aisop.json` 是一个 AISOP 程序，内含两层：

| 层 | 装什么 | 放哪 |
|----|--------|------|
| **Tier A（执行，重）** | 流程/步骤/角色/原则/知识/约束/失败/确认/校验/结构化输出/资源读取/工具/状态 | `aisop.main` + `functions` + `sys.*` + `tools`/`params` |
| **Tier S（合同，瘦）** | 触发、红线绑定、发现、风险、资源清单 | `user.content.aisp_contract`（真 object）|

合同只装"流程层做不到 / 消费方需预先知道"的；其余归位 Tier A（§15）。

---

## 第三部分：技能合同

## 8. `aisp_contract` 字段

技能合同是 **`user.content.aisp_contract`** — 一个**真 JSON object**，在 **user 消息**里，与 `instruction`/`user_input`/`aisop`/`functions` 并列；`instruction` 以强硬指令命令模型遵从它（§14）。（程序身份元数据 `id`/`name`/`version`/`license`/`tools`/`params` 仍在 `system.content`。）

```json
{
  "profile": "aisp.skill.v1",
  "invocation": { "mode": "auto_or_manual", "when_to_use": ["string"], "when_not_to_use": ["string"] },
  "non_negotiable": [ { "rule": "string (NL)", "enforced_by": "<node>.stepN:<mechanism> | aisop.main | tools" } ],
  "discovery": { "category": "string", "tags": ["string"] },
  "risk_level": "low | medium | high | critical",
  "resources": [
    { "id": "string", "path": "relative/path", "kind": "data|script|reference|asset|template|…", "mode": "read_only|execute_only|read_and_execute", "when": "string?", "scope": "skill|shared?", "requires_tools": ["string"]? }
  ]
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `profile` | MUST | `aisp.skill.v1`（runtime 据 `aisp.skill.` 前缀识别）|
| `invocation` | MUST | 触发（§9）|
| `non_negotiable` | MUST | 红线 + `enforced_by`（§10）|
| `discovery` | SHOULD | category/tags（§11）|
| `risk_level` | SHOULD | 风险分级（§12）|
| `resources` | MAY | 资源清单（§13）|

**形态**：真 object — 无转义、无 string/object 双形式、无 JSON-in-string。**为何可以而不改 AISOP Core**：`aisp_contract` 是 AISP 自有字段；AISOP 对 `user.content` 容忍额外键（R4），故 AISOP runtime 忽略它、AISP-aware runtime 读它。**为何放 user 消息**：它是模型这一轮的活内容 — 模型直接读到（像 Agent Skills 把 SKILL.md 载入上下文），不依赖 runtime 渲染；`instruction` 强硬点名遵从（§14）。

**程序身份/许可**：用 `system.content` 的 `summary`/`description`/`version` + **`license`**（默认 `Apache-2.0`，SHOULD），**不在合同重复**。叶子是自然语言句（容器结构化、叶子 NL）。

### 8.1 平台政策优先级

> `aisp_contract` 仅在 AISP 执行上下文内具有权威。它**不覆盖**平台级 system/developer/安全/法律/政策指令。在通用消息层级（system/developer > user > assistant）中，合同位于 user 消息，是技能层权威、非平台最高权威。强硬 `instruction`(`STRICTLY OBEY aisp_contract …`) 只把模型绑定到技能自身规则，绝不授权绕过平台或安全策略。

合同的权威是**有作用域的**：它治理技能**如何运行**（哪些红线成立、哪些节点必经），而非授权覆盖宿主平台自己的 system/developer/安全/法律/政策层。合同放在 user 消息，**结构上**就低于平台的更高优先级指令——这是设计如此。强硬 `instruction` 提升模型对技能 `non_negotiable` 规则的遵从度；它不是越狱令牌。

### 8.2 `system_prompt` 冲突规则

> `system_prompt` 可以为空。若非空，**不得**与 `aisp_contract`、`aisop.main` 或 `functions` 冲突。`aisp_contract` **不得**复制进 `system_prompt`（无双源、无 JSON-in-string）。

`system_prompt` 是 `system.content` 里可选的行为层。合同是触发/红线/发现/风险/资源的唯一真相；`aisop.main` + `functions` 是执行的唯一真相。非空的 `system_prompt` 可承载真正的模型系统提示，但**不得**复述或与这两层矛盾，也**不得**以转义 JSON 字符串承载合同。

---

## 9. `invocation`（触发）

触发发生在执行**之前**（"该不该启动这个技能"），AISOP 流程天生表达不了，故在合同。

| 子字段 | 必填 | 说明 |
|--------|------|------|
| `mode` | SHOULD | `manual_only` / `auto_or_manual` / `auto_preferred` / `internal_only` |
| `when_to_use` | MUST | 触发条件（结构化、可路由）|
| `when_not_to_use` | MUST | 禁用边界（防过度触发；冲突时优先于 when_to_use）|

`when_to_use` 不应过宽。runtime 路由：匹配 when_to_use？命中 when_not_to_use？冲突时 when_not_to_use 优先；不确定问用户。

---

## 10. `non_negotiable` + `enforced_by`（红线绑定）

红线 = 声明（NL `rule`）+ **绑定到真实强制机制**（`enforced_by`）。这是 AISP 区别于散文 skill 的核心：**声明 ↔ 强制可机器核验。**

`enforced_by` 文法（MUST 指向真实存在的机制）：

| 形式 | 含义 | 校验 |
|------|------|------|
| `<node>.stepN:<mechanism>` | 某节点某个数字执行步骤的 `sys.*`（最精确，推荐），如 `interpret.step1:sys.assert` | node 与数字 step 存在且该 step 以该机制起头 |
| `aisop.main` | 由图拓扑强制（必经节点/分支）| 对应必经节点/分支存在 |
| `tools` | 由 `tools` 白名单强制（能力未授予）| `tools` 受限且 runtime 真执行工具权限 |

> `enforced_by: tools` **仅当 runtime 真正执行工具权限时**才算硬强制；若 runtime 不强制工具权限，`tools` 只是声明式约束，MUST NOT 计为硬保证。

---

## 11. `discovery`（发现元数据）

| 子字段 | 说明 |
|--------|------|
| `category` | 大分类（registry/路由）|
| `tags` | 标签数组（registry 检索）|

供 `aisp_list.json` / registry / 路由使用；无 registry 时可省。

---

## 12. `risk_level`（风险）

`low`（只读/分析）/ `medium`（写本地）/ `high`（删除/部署/外发）/ `critical`（强制人审或禁自动）。单一分级，供 trust/registry；细治理靠 `sys.*` + `tools`。

**语义定义：**

- **low** = 只读分析或生成。
- **medium** = 本地文件写入、本地脚本、非破坏性变更。
- **high** = 删除、部署、外发、凭证、生产影响。
- **critical** = 法律 / 医疗 / 金融 / 人身安全，或不可逆的高影响动作。

`risk_level` 是路由/治理元数据，**不是**硬强制机制——强制靠 `sys.io.confirm` / `sys.assert` / tools / runtime 策略。

---

## 13. `resources`（资源）

**resources = 清单（inventory）；functions = 使用（usage）。** 字段声明"有哪些、在哪、什么类型、读还是执行"；节点用 `sys.io.read`/`sys.run` 实际使用。

| 子字段 | 必填 | 说明 |
|--------|------|------|
| `id` | MUST | 资源标识 |
| `path` | MUST | 相对路径（`scope:skill` 相对技能夹；`scope:shared` 相对 `_shared/`）|
| `kind` | MUST | **开放词**：data/script/reference/asset/template/… |
| `mode` | MUST | **受控枚举**：`read_only`/`execute_only`/`read_and_execute`（门控行为）|
| `when` | MAY | 何时加载 |
| `scope` | MAY | `skill`（默认）/ `shared` |
| `sha256` | MAY | 供应链完整性的内容哈希 |
| `requires_tools` | MAY | 脚本所需工具（最小授权）|

要点：自定义布局；`resources` 是"什么是资源"的单一真相（未声明文件 = 未知，validator SHOULD warn）；`kind` 开放、`mode` 枚举（安全门控）。

> 经 registry 分发时，资源条目 SHOULD 含 `sha256`（供应链完整性）。仓内示例为保持干净而省略；registry 在发布时记录并校验它。

> **机器可读 schema。** 合同对象由 [`schemas/aisp-contract-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/aisp-contract-v1.schema.json)（JSON Schema draft 2020-12）形式化定义：校验 `profile` / `invocation` / `non_negotiable` 必填、`enforced_by` 文法、`risk_level` 与 `mode` 枚举，以及可选的 `sha256` 资源字段。

---

## 第四部分：执行与披露

## 14. 模型看到什么

★ 合同放 **user 消息**（`user.content.aisp_contract`）= 它本就是模型这一轮上下文的活内容 — **模型直接读到，不依赖 runtime "渲染"**（像 Agent Skills 把 SKILL.md 载入上下文）。`instruction` 用**强硬指令命令模型遵从**。

| 来源 | 给模型什么 | 谁负责 |
|------|-----------|--------|
| `user.content.instruction` | **强硬总指令**：`"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"` | 模型读 user 消息即见 |
| `user.content.aisp_contract` | **技能简报**：触发/红线/治理/资源（模型直接读，当作关键内容）| 在 user 消息里，模型直读 |
| `functions.<node>.step` | **任务指令**（每步做什么；角色/原则/知识已归位于此）| AISOP 引擎逐节点喂 |
| `enforced_by → sys.*` | **硬保证**（确认/校验/工具门）| runtime 强制（R2, MUST），与模型是否"记得"无关 |
| `system_prompt`（system.content）| 可空；或放真正的模型系统提示；或 `{system_prompt}` 注入 | 作者/runtime |

**规范**：
- 合同在 **user 消息** → 模型这一轮直接读到（**无需** runtime 单独渲染步骤；R3 MUST 不隐藏）。
- `instruction` 以**强硬指令**点名遵从合同（OBEY / inviolable）。
- `system_prompt` 不承载合同（**MAY 为空**）。
- 模型的任务指令**在 functions**。
- **软读 + 硬卡 双层**：模型读到红线（policy-as-prompt，软）+ `enforced_by → sys.*` 真正卡住（policy-as-code，硬）。**硬保证只来自 `sys.*`** — 模型是否"记得"红线不影响硬约束。

> 即：合同在 user 消息让模型**必然读到**（不赌渲染）；`sys.*` 让红线**必然被卡**（不赌模型记性）。两层都要。

---

## 15. Tier A 归位

| Skill 内容 | 归位到 |
|------------|--------|
| 角色/原则/知识/约束 | `functions.<node>.step` + `constraints` |
| 失败处理 | `aisop.main` 分支 / `-.->` 错误边 / `on_error` / `sys.io.confirm` |
| 结构化输出 | `sys.llm.json` 的 `schema` + 最终节点 `constraints` |
| 资源**使用** | 节点内 `sys.io.read` / `sys.run`（清单在合同 `resources`）|
| 工具 | `tools`（AISOP Core 字段）|
| 每节点派发（inline vs sub-agent）| `functions.<node>.execute_mode`（继承 AISOP 字段，§5.2.8）|
| 程序身份 | AISOP `summary`/`description` |
| **触发/红线绑定/发现/风险/资源清单** | **`user.content.aisp_contract`** |

> **`execute_mode`（派发保真度）。** 每个节点 MAY 声明 `execute_mode`：`"inline"`（默认模式；在当前上下文执行，适合短路由、分类、确认和简单整理）或 `"agent"`（独立 sub-agent 执行，可用于需要隔离、独立上下文、多文件处理、web/来源收集、复杂校验、生成或高影响决策的节点）。step 数不是选择 `agent` 的唯一标准；短节点在隔离或影响级别需要时也可以使用 `agent`。若省略，runtime 回退为 `"inline"`，合规 AISP validator 发出 `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE`。显式值不是 `"inline"` / `"agent"` 时静态一致性 FAIL。Runtime MUST 遵守 `agent`（**R7**）：`agent` 节点 MUST 派发到 sub-agent、不得 collapse 成 inline。超过 10 个数字 `stepN` 执行步骤且仍为非 agent 的节点 SHOULD 评估是否改为 `execute_mode: "agent"`；reference validator 会对此发 warning。`step_note` 等元数据字段不计入该启发式，也不能满足 `enforced_by`。该阈值是审查启发式，不是短节点使用 `agent` 的限制条件。`execute_mode` 是继承自 AISOP 的字段（AISOP §5.2.8）、runtime 派发属性——**不是** `enforced_by` 机制，也**不进合同**（属 Tier A、per-node）。

---

## 16. 发现与渐进披露

发现**运行时无关**：任何带 bash+python 的 agent 跑脚本即可发现；任何 agent 读 JSON（无需 python）也行 — 不依赖专用 AISP runtime。

### 16.1 三条发现路径

| 路径 | 怎么做 | 特点 |
|------|--------|------|
| **读索引（默认）** | 读 `aisp/aisp_list.json` | 快、安全（不执行）、语言无关；可能旧 |
| **跑脚本（刷新）** | bash `python -B aisp/aisp_list.py [--json]` | 新鲜；`--json` 重生成索引；需 python + 执行权限，并避免 `__pycache__/` 残留 |
| **直接 glob（兜底）** | `aisp/*_aisp/aisp.aisop.json` 逐个读 `aisp_contract` | 脚本内部即此逻辑 |

### 16.2 渐进披露

```text
L1 元数据：aisp_list.json（或脚本输出）——各技能 summary/invocation/discovery，轻量路由。
L2 指令：命中后载完整 aisp/<id>/aisp.aisop.json（合同 + aisop.main + functions）。
L3 资源：functions 节点按需 sys.io.read/sys.run（依 resources 清单 + AISP 固定 `loading_mode: "node"`）。
```

触发完全靠 `aisp_contract.invocation` + `discovery`（替代 SKILL.md 的 description 机制）。`README.md` 向人/AI 说明此发现契约。

---

## 第五部分：安全、命名与版本

## 17. 安全与信任模型

资源是攻击面（scripts/templates/examples/远程 URL 可藏恶意 payload）。规则：
1. `path` 相对、**限本技能夹或 `_shared/`、禁 `../` 逃逸**（M5）。
2. 远程 URL 默认禁、需用户确认。
3. `mode` 门控：`execute_only` 脚本不全文注入模型；`read_only` 不执行。
4. 脚本用 `requires_tools` 最小授权；高危命令触发 `sys.io.confirm`。
5. **信任不自报**（M6）——`verified`/`trusted`/`safe` 由 runtime/registry/用户/扫描器判。
6. registry 记 provenance（source/commit/`contract_sha256`/`resources_sha256`）。
7. 文件夹有文件但未在 `resources` 声明 → validator SHOULD warn。
8. `aisp_list.py` 是脚本，**跑它=执行代码**：MUST 最小、可审计、零依赖、只写 `aisp_list.json` 无其它副作用；不可信目录 SHOULD 优先读 `aisp_list.json`（不执行）、先过信任门再跑脚本。
9. **Axiom 0**：所有技能继承"Human Sovereignty and Wellbeing"；`sys.io.confirm` 🔒 不可绕。
10. **执行期只读**：AISP runtime SHOULD 在正常执行期把技能包（文件与资源）视为只读。修改只通过一个有意的进化/编辑步骤发生。

---

## 18. 命名规则

| 标识 | 规则 |
|------|------|
| `aisp_contract` 字段名 | 固定；不用 `aisp_skill_contract`（"skill"冗余，AISP 已含）/ 不裸用 `skill_contract`（缺命名空间）|
| 技能 `id`（= 文件夹名）| **必以 `_aisp` 结尾**；小写字母数字+下划线；如 `yijing_aisp`、`stock_analysis_aisp` |
| `profile` | `aisp.skill.v1`（检测按 `aisp.skill.` 前缀）|
| SKILL.md sidecar `name`（若有）| `id` 去 `_aisp`/转连字符、小写；**禁含 "anthropic"/"claude"**、≤64（§20）|
| 声明式规则字段 | 用 `non_negotiable`，**不用 `assert`**（`assert` 已是 `sys.assert` 确定性硬检查，语义相反）；硬度靠 `enforced_by → sys.*` |

---

## 19. 版本

一个 `aisp.aisop.json` 的版本相关字段：

```text
system.content.protocol               = "AISP V1.0.0"   ← 本文件声明的协议 = AISP（协议版本）
system.content.license                = "Apache-2.0"        ← 许可（默认 Apache-2.0）
user.content.aisp_contract.profile    = "aisp.skill.v1"     ← 技能合同 schema 版本（AISP，按前缀检测）
system.content.version                = "1.0.0"             ← 该技能自身的版本
（结构底座：仍是 AISOP V1.0.0 程序——由 2-消息/aisop.main/sys.* 等结构体现，不在 protocol 字段）
```

- **AISP 协议版本** = 本规范 **V1.0.0**；`protocol` 字段字面量写 `AISP V1.0.0`（仿 AISOP "AISOP V1.0.0" 风格：大写 V、无连字符）。
- **底座关系**：AISP 文件结构上是 AISOP V1.0.0 程序；`protocol` 改记 AISP 是**品牌/协议归属**声明。AISOP 引擎不以 `protocol` 值设门，故照常执行。⚠️ 但**严格按 `protocol=="AISOP V1.0.0"` 设门的工具会拒** — 同 `aisp_contract`，属"AISP 依赖 AISOP 开放世界"的已知取舍（§4 R4、§24）。
- 兼容：`profile` 按 `aisp.skill.` 前缀检测；major（`v1`）变更才视为不兼容。

---

## 第六部分：互操作与生命周期

## 20. 互操作

**原生 AISP 技能的 core conformance 不要求 `SKILL.md`。** 要在 Agent Skills 平台（Claude Code/Codex/Gemini/Copilot/Cursor）被发现，authoring tools SHOULD 默认在原生 `*_aisp/` 技能目录内生成一个薄的同目录 `SKILL.md` sidecar bridge，除非作者明确 opt out。Sidecar 只引导加载和运行本目录 `aisp.aisop.json`；不复制逻辑；删掉它后，原生 AISP 技能在 AISP/AISOP runtime 下仍可运行。

```markdown
---
name: yijing
description: Cast and interpret an I Ching (Yijing) hexagram for a question. Use when asked for a yijing/I Ching reading or hexagram interpretation. Do not use for medical, legal, or financial decisions needing a professional.
license: Apache-2.0
metadata:
  generated_from_aisp: "true"
  aisp_program: aisp.aisop.json
  protocol: AISP V1.0.0
  bridge_mode: native_sidecar
---

# Yijing Divination (AISP-backed)

This `SKILL.md` is a thin discovery bridge, not the source of truth.
The executable source of truth is the same-folder `aisp.aisop.json` (AISP V1.0.0 skill over an AISOP V1.0.0 program).
Runtime compatibility note: hard execution requires a conforming AISP/AISOP runtime; this bridge alone is only a discovery and loading guide.

When invoked:
1. Load `aisp.aisop.json`.
2. Execute `RUN aisop.main`.
3. Treat `user.content.aisp_contract` as the skill contract,
   `user.content.aisop.main` as the topology, `user.content.functions` as node ops.
4. Load resources (declared in `aisp_contract.resources`) only when a node reads them.
   Never skip required nodes.
```

Bridge 字段投影：

| `SKILL.md` 字段 | 来源 | 约束 |
|-----------------|------|------|
| `name` | 同目录 AISP `id` | 去 `_aisp`、下划线转连字符、小写；可不同于 `_aisp` 文件夹名；不得包含 `anthropic` 或 `claude` |
| `description` | `aisp_contract.invocation` + summary | 含触发与排除条件；最多 1024 字符；防注入 |
| `license` | `system.content.license` | 默认 `Apache-2.0` |
| `metadata.generated_from_aisp` | 生成器标记 | 生成桥固定为 `"true"` |
| `metadata.aisp_program` | 同目录程序路径 | MUST 为 `aisp.aisop.json`；禁止绝对路径、URL、子目录或 `..` 逃逸 |
| `metadata.bridge_mode` | 桥形态标记 | 生成 sidecar SHOULD 写 `native_sidecar` |
| `allowed-tools` | `system.content.tools` | 仅在宿主平台支持该字段时写入 |

生成的 bridge 不得发明自定义顶层 frontmatter key（例如 `compatibility`）；runtime compatibility 与 hard-execution boundary 应写在正文，或写入目标平台明确接受的 documented metadata。

默认规则：

- Core AISP conformance：缺少 `SKILL.md` 仍然允许。
- Authoring / scaffold tools：默认生成 `SKILL.md`，除非用户 opt out。
- 公开 examples、release packages、registry distributions：SHOULD 包含 `SKILL.md`；缺失是 ecosystem warning，不是 core failure。

Sidecar 生成与验证：

```bash
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

Sidecar 生成检查通过只证明 `SKILL.md` 与 `aisp.aisop.json` 的确定性投影一致。Bridge 检查通过只证明 sidecar 形状正确、指针被限制在同目录 `aisp.aisop.json`、原生 AISP 通过验证。二者都不证明外部信任、registry 认可，也不证明非 AISOP 平台能提供硬执行保证。

---

## 21. 生命周期

技能的生成、进化、分发是 **AISP 原生、工具无关**的——由作者自选的外部工具承担。AISP 定义的是*技能包*以及每个阶段技能必须满足的一致性（M1–M6），**而非**工具链。下列描述规定任何符合规范的工具 MUST 做到什么，与具体实现无关。

- **生成**：生成器建 `aisp/<id>_aisp/aisp.aisop.json`（瘦合同 + 富 Tier A）+ 自定义资源；校验 `id`==文件夹名且以 `_aisp` 结尾、每条 `enforced_by` 真实、资源路径合法、functions 引用的资源已声明；产/更新 `aisp_list.json`；生成单技能 `README.md`，并默认生成同目录 `SKILL.md` sidecar，除非作者明确 opt out。生成的技能 MUST 仍满足核心 M1–M6。
- **进化**：可改合同字段（invocation/non_negotiable/discovery/risk/resources）或 functions/aisop.main；改资源进入一个有意的进化/编辑步骤 + changelog + 安全扫描；不删安全约束、不降 risk、不擅扩 tools。
- **Registry / 分发**：以技能文件夹为分发单元。AISP 是 registry 无关的，不构建也不要求特定 registry；任何 registry MAY 索引 discovery + invocation + risk + provenance（hash）；信任/评分/扫描由 registry 生成，不信自报。

---

## 第七部分：示例与诚实

## 22. 完整示例

`aisp/yijing_aisp/aisp.aisop.json`（合同 = `user.content.aisp_contract` 真 object；`system_prompt` 留空）：

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "description": "Native AISP skill: clarify the question, cast a hexagram via a deterministic toss, and interpret it for reflection (not deterministic prediction).",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "tools": ["filesystem", "code"],
      "params": { "question": "string" },
      "system_prompt": ""
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
          "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
          "when_not_to_use": ["medical, legal, or financial decisions needing a professional", "no question provided"]
        },
        "non_negotiable": [
          { "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" },
          { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" },
          { "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
        ],
        "discovery": { "category": "culture", "tags": ["yijing", "iching", "divination", "hexagram"] },
        "risk_level": "low",
        "resources": [
          { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
          { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" }
        ]
      },
      "aisop": {
        "main": "graph TD\n    clarify[Clarify the question] --> cast[Cast hexagram]\n    cast --> interpret[Interpret]\n    interpret --> end_node((End))"
      },
      "functions": {
        "clarify": {
          "step1": "Identify the user's question and intent for the reading.",
          "output_mapping": "question"
        },
        "cast": {
          "step1": "sys.code.exec('python', 'import random, json; print(json.dumps([random.randint(6,9) for _ in range(6)]))') -> lines",
          "step2": "sys.io.read('data/hexagrams.json') -> hexagram_table",
          "step3": "Map lines (6/8 yin, 7/9 yang; 6/9 changing) to the primary and changing hexagram via hexagram_table.",
          "output_mapping": "hexagram"
        },
        "interpret": {
          "step1": "sys.assert('hexagram != null', 'No hexagram has been cast')",
          "step2": "sys.io.read('data/interpretation_guide.md') -> guide",
          "step3": "sys.llm.json('Interpret the hexagram for the question using guide', schema={summary:'string', guidance:'string', changing_lines:'array', disclaimer:'string'}) -> reading",
          "step4": "sys.assert(\"'reflection' in reading.disclaimer.lower() or 'not deterministic' in reading.disclaimer.lower()\", 'Reading must state it is for reflection, not deterministic prediction')",
          "step5": "Render reading as Markdown.",
          "constraints": ["Ground the interpretation in the cast hexagram and guide; do not fabricate hexagrams."]
        },
        "end_node": { "step1": "Return the final Markdown reading." }
      }
    }
  }
]
```

**核对（一致性）**：M1 合法 AISOP 程序、`protocol: AISP V1.0.0`、`license: Apache-2.0` ✓；M2 文件夹 `yijing_aisp/`==id、以 `_aisp` 结尾 ✓；M3 `aisp_contract` 真 object 在 **user 消息**、profile `aisp.skill.v1`、含 invocation+non_negotiable ✓；M4 三条 `enforced_by` 全真实（`aisop.main` / `interpret.step1:sys.assert` 已起卦 / `interpret.step4:sys.assert` 含 disclaimer）✓；`instruction` 强硬点名遵从合同 ✓；资源 `cast`/`interpret` 用 `sys.code.exec`/`sys.io.read` ✓；`system_prompt` 留空（合同在 user 消息、模型直读；任务指令在 functions；硬保证在 sys.*）✓。

> 领域对比 `stock_analysis_aisp/`：同格式承载金融分析（`tools:["filesystem","shell"]`、红线含 "never place trades" `enforced_by:tools`、报告含 not-advice disclaimer `enforced_by:report.step2:sys.assert`、资源含 data+script+`_shared`）。见 `examples/aisp/stock_analysis_aisp/`。

---

## 23. 一致性检查清单

本清单用于发布就绪审查；它不能替代 validator 输出、runtime trace 证据、registry provenance 或人工审查。

| 范围 | 发布检查 |
|------|----------|
| 技能身份 | [ ] 合法 AISOP 程序（必填字段 + `aisop.main`）；`protocol: AISP V1.0.0`；`license` 存在或默认 Apache-2.0 |
| 入口路径 | [ ] `aisp/<id>/aisp.aisop.json`；`id` 等于文件夹名且以 `_aisp` 结尾 |
| 合同 | [ ] `user.content.aisp_contract` 是 user 消息中的真 object；`profile` 以 `aisp.skill.` 开头；含 `invocation` 与 `non_negotiable` |
| 运行指令 | [ ] `instruction` 强硬点名合同并运行图，例如 `STRICTLY OBEY aisp_contract; ... then RUN aisop.main` |
| 红线 | [ ] 每条 `non_negotiable.enforced_by` 目标真实存在；高风险动作使用 `sys.io.confirm` 和/或 `sys.assert` |
| 资源 | [ ] 资源路径相对且不逃逸；声明 mode；script 声明 `requires_tools`；远程使用有门控 |
| 信任措辞 | [ ] 包不自报 trust、verified、safe；外部 provenance 仍在包外判断 |
| `aisp/` 目录 | [ ] 目录级 `README.md` 存在；`aisp_list.json` / `aisp_list.py` 保持零依赖、只做索引 |
| 每技能 README | [ ] 发布用的 `*_aisp/README.md` 由 `aisp.aisop.json` 生成；strict/release 可让缺失、手写、漂移、source 错误或 generator 不受支持失败 |
| Runtime | [ ] Runtime 读取合同、保留 user 消息里的合同、遵守开放世界 AISOP 兼容性、执行 `enforced_by`、不绕过 `sys.io.confirm` |
| Tier A | [ ] 角色、原则、知识放在 functions；失败条件放在 `aisop.main` / `sys.*`；结构化输出用 `sys.llm.json`；图有结束节点 |
| Sidecar bridge | [ ] Authoring / distribution 默认生成同目录 `SKILL.md`，除非明确 opt out；它使用官方字段、合法 `name`、安全 `aisp.aisop.json` 指针、生成标记和薄引导；不复制 AISP 逻辑 |

参考工具映射：

- 静态包校验：`tools/aisp_validate.py`；覆盖范围见 [`docs/reference/validator-coverage.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/validator-coverage.md)。
- 生成 README 校验：`tools/aisp_readme.py`；信任边界见 [`docs/reference/generated-readme.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/generated-readme.md)。
- 可选桥校验：`tools/aisp_validate_agent_skill_bridge.py`；覆盖范围已汇总在 validator matrix。
- Runtime trace 与 registry 证据：[`docs/reference/registry-runtime-artifacts.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/registry-runtime-artifacts.md)。Trace 检查只证明可信 trace source 中实际有证据的行为。

---

## 24. 诚实边界

1. **native-only 的代价 = 失去现有平台直接可运行性**：SKILL.md 已被 Claude Code/Codex/Gemini/Copilot/Cursor 共同支持；原生 AISP 技能需 AISP/AISOP runtime 才能跑。缓解 = authoring / distribution 默认生成同目录 `SKILL.md` sidecar bridge，同时保持 core 可选（§20）。明牌。
2. **依赖 AISOP 开放世界**（R4）：两点 — ①`aisp_contract`/`license` 是 AISOP 字段表外的键，靠"容忍额外键"；②`protocol` 值改为 `AISP V1.0.0`，靠 AISOP "不以 protocol 值设门"。AISOP 参考实现两点都满足；但**封闭世界严格校验器（拒未知键）或硬校验 `protocol=="AISOP V1.0.0"` 的工具会拒** AISP 文件。AISOP spec 不强制这类封闭校验，但这是 AISP 的明牌依赖。
3. **结构化回报在机器侧**（校验/进化/registry/Axiom0 链 + 身份一致），非模型 adherence；真保证只有 policy-as-code（`enforced_by→sys.*`），NL 规则是 policy-as-prompt（软）。
4. **信任不自报**；trust/verified 由 runtime/registry/用户/扫描器判。
5. **"Skill" 命名与 Agent Skills**：skill 是通用词、法律低风险；靠"可执行+可治理+互补+导出"定位差异化；**品牌零 Claude/Anthropic**；**公开发布前商标检索**（本规范非法律意见）。

---

## 25. 常见错误

1. 技能内含/依赖 SKILL.md 跑逻辑 ✗ → 真相在 `aisp.aisop.json`；SKILL.md 只是默认生成但 core 可选的 sidecar bridge。
2. 合同塞进 `system_prompt`（JSON-in-string）✗ → 用 `user.content.aisp_contract` 真 object。
3. 文件名不统一 / `id` ≠ 文件夹名 / 不以 `_aisp` 结尾 ✗。
4. `enforced_by` 指向不存在的 node.stepN:mechanism，或指向 `node.step_note:mechanism` 这类元数据字段 ✗。
5. 资源不在 `resources` 声明就直接读 / `path` 逃逸 / 远程 URL 不确认 ✗。
6. `kind` 当枚举 / `mode` 当开放词 ✗（反了：kind 开放、mode 枚举）。
7. 把 `loading_mode` 当成自由策略选择 ✗ → AISP 技能 MUST 使用 `loading_mode: "node"` 做渐进披露。
8. 到处省略 `execute_mode` 并误以为这能证明派发行为 ✗ → 省略只会回退 inline 且产生 warning；真实 `agent` 派发只能由 runtime trace evidence 证明。
9. 声明式规则命名 `assert` / 合同重复 Tier A（角色/原则/失败/输出写进合同）✗。
10. self-declared trust / 品牌出现 Claude/Anthropic ✗。
11. 把生成的 `README.md` 或 README 检查通过当成安全/可信证明 ✗。
12. 把 `system_prompt` 当合同载体（已废）/ 指望模型"记得"红线替代 `sys.*` 强制 ✗。

---

## 附录 A：`aisp_contract` 骨架

`user.content.aisp_contract` 的内容：

```json
{
  "profile": "aisp.skill.v1",
  "invocation": { "mode": "auto_or_manual", "when_to_use": [], "when_not_to_use": [] },
  "non_negotiable": [ { "rule": "", "enforced_by": "node.stepN:mechanism | aisop.main | tools" } ],
  "discovery": { "category": "", "tags": [] },
  "risk_level": "low",
  "resources": [ { "id": "", "path": "", "kind": "data", "mode": "read_only", "when": "", "scope": "skill", "sha256": "", "requires_tools": [] } ]
}
```

> `sha256` 为可选；registry 分发的技能应包含它（供应链完整性）。机器可读合同 schema 见 [`schemas/aisp-contract-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/aisp-contract-v1.schema.json)。

## 附录 B：目录骨架

```text
aisp/
  README.md                         # MUST
  aisp_list.py  aisp_list.json      # SHOULD（发现）
  <id>_aisp/                        # 技能（id == 文件夹名，以 _aisp 结尾）
    aisp.aisop.json
    README.md                       # SHOULD：由 aisp.aisop.json 生成
    data/ | scripts/ | <custom>/    # 自定义布局，由 resources 声明
    SKILL.md                        # 可选：Agent Skills sidecar bridge
  _shared/                          # 共享资源
```

## 附录 C：`aisp_list.py`（零依赖参考实现）

```python
#!/usr/bin/env python3
"""aisp_list.py — discover AISP skills under this folder.

Scans <this_dir>/*_aisp/aisp.aisop.json, reads each skill's
user.content.aisp_contract, prints a human/AI-readable list, and (with --json)
writes aisp_list.json. Zero deps (stdlib). Side effect: only --json writes
aisp_list.json; --check is read-only and fails on drift. Any malformed
*_aisp package is a hard index error, not a silent skip.
  python -B aisp_list.py          # print the list
  python -B aisp_list.py --json   # also (re)generate aisp_list.json
  python -B aisp_list.py --check  # verify committed aisp_list.json
  python -B aisp_list.py --help   # print usage

Security guarantees (SE5 / ST1). This script MUST be zero-dependency (standard
library only) and human-auditable. It MUST NOT: access the network; import
third-party packages; execute skill scripts; modify any file except
aisp_list.json when --json is explicitly used; read files outside the aisp/
directory (except declared _shared metadata). The reference implementation below
meets all of these: it imports only `json` and `sys` from the stdlib, globs only
`*_aisp/aisp.aisop.json` under its own directory, and writes only
`aisp_list.json`.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = """usage: python -B aisp_list.py [--json] [--check] [--help]

Discover AISP skills under this directory.

Options:
  --json   regenerate aisp_list.json from *_aisp/aisp.aisop.json folders
  --check  verify aisp_list.json is current without writing
  --help   show this help
"""

def discover():
    skills = []
    errors = []
    for f in sorted(ROOT.glob("*_aisp/aisp.aisop.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
            sc = data[0]["content"]                  # system: id/name/summary metadata
            uc = data[1]["content"]                  # user: instruction/aisop/functions + aisp_contract
        except Exception as e:
            errors.append(f"{f}: {e}")
            continue
        if not isinstance(sc, dict):
            errors.append(f"{f}: system.content must be an object")
            continue
        if not isinstance(uc, dict):
            errors.append(f"{f}: user.content must be an object")
            continue
        c = uc.get("aisp_contract", {})              # real object field in the user message
        skill_id = sc.get("id")
        if not skill_id:
            errors.append(f"{f}: missing system.content.id")
            continue
        if not isinstance(c, dict) or not str(c.get("profile", "")).startswith("aisp.skill."):
            errors.append(f"{f}: missing aisp.skill.* profile")
            continue
        skills.append({
            "id": skill_id,
            "name": sc.get("name"),
            "summary": sc.get("summary") or sc.get("description", ""),
            "path": str(f.relative_to(ROOT.parent)).replace("\\", "/"),
            "category": c.get("discovery", {}).get("category"),
            "tags": c.get("discovery", {}).get("tags", []),
            "when_to_use": c.get("invocation", {}).get("when_to_use", []),
            "risk_level": c.get("risk_level"),
        })
    return skills, errors

def render_index(skills):
    return json.dumps({"aisp_list_version": "1.0", "skills": skills},
                      ensure_ascii=False, indent=2) + "\n"

def normalized(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").rstrip("\n")

def main():
    allowed_args = {"--json", "--check", "--help", "-h"}
    unknown_args = [arg for arg in sys.argv[1:] if arg not in allowed_args]
    if unknown_args:
        print(f"ERROR: unknown argument(s): {', '.join(unknown_args)}", file=sys.stderr)
        print(USAGE.rstrip(), file=sys.stderr)
        return 2
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE.rstrip())
        return 0
    skills, errors = discover()
    if errors:
        print("ERROR: cannot build AISP index:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    for s in skills:
        print(f"- {s['id']}: {s['summary']}  ->  {s['path']}")
    print(f"\n{len(skills)} AISP skill(s).")
    expected = render_index(skills)
    if "--check" in sys.argv:
        out = ROOT / "aisp_list.json"
        if not out.exists():
            print(f"{out} is missing; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        actual = out.read_text(encoding="utf-8-sig")
        if normalized(actual) != normalized(expected):
            print(f"{out} is stale; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        print("aisp_list.json ok")
        return 0
    if "--json" in sys.argv:
        out = ROOT / "aisp_list.json"
        out.write_text(expected, encoding="utf-8", newline="\n")
        print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## 附录 D：`aisp_list.json`（索引格式）

```json
{
  "aisp_list_version": "1.0",
  "skills": [
    {
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "path": "aisp/yijing_aisp/aisp.aisop.json",
      "category": "culture",
      "tags": ["yijing", "iching", "divination", "hexagram"],
      "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
      "risk_level": "low"
    }
  ]
}
```

## 附录 E：Sources

- AISOP Specification — `specification/aisop-spec.md`（AISOP V1.0.0 — AISP 的底座）
- Agent Skills Specification — https://agentskills.io/specification
- Extend Claude with skills — https://code.claude.com/docs/en/skills
- Policy-as-Prompt（arXiv 2509.23994）— https://arxiv.org/html/2509.23994
- Under the Hood of SKILL.md: Semantic Supply-chain Attacks（arXiv 2605.11418）

## 附录 F：最简口号

```text
AISP = AI 技能协议（V1.0.0）。
技能 = aisp/<id>_aisp/aisp.aisop.json + 自定义资源 + _shared/。无 core 必需 SKILL.md；authoring / distribution SHOULD 默认包含同目录 sidecar，除非 opt out。
合同 = user.content.aisp_contract（真 object）：invocation + non_negotiable.enforced_by + discovery + risk_level + resources。
其余归位 aisop.main / functions / sys.*。system_prompt 可空。
执行=AISOP，生命周期（生成/进化/分发）=AISP 原生、工具无关。与 Agent Skills 互补（默认生成但 core 可选的 SKILL.md sidecar）。
硬规则只走 enforced_by→sys.*。信任绝不自报。
```

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
