# aisp_creator_evolution_aisp

一个**AISP 原生 creator/evolution 元技能**：创建新的 conformant AISP 技能、进化现有 AISP 技能，并将现有 Agent Skills 适配/转换为原生 AISP 技能包。严格遵循 AISP V1.0.0 spec 与规则（仅建在 AISOP 上、独立于其它协议）。

`README.md` 是由 `aisp.aisop.json` 确定性生成的英文自举投影；本 `README_CN.md` 是人工维护的中文深度说明，面向审查、进化和运行排障。两者分工不同，不要求章节一一同构；若事实字段冲突，以 `aisp.aisop.json` 与生成式 `README.md` 为准。

## 是什么

- **一个技能 = 一个 `aisp.aisop.json`**（M2）：`aisop` 内含 `main`（按意图路由 create / evolve）+ `research`（两路共享的研究子图）。
- **合同在 user 消息**（M3）：`user.content.aisp_contract`（真 object），`profile: "aisp.skill.v1"`。
- **红线即代码**（M4）：6 条 `non_negotiable` 全部 `enforced_by` 到真实机制——
  - `aisop.main`（按图执行、不跳研究/校验/人审）
  - `run_research.step2:sys.assert`（研究必须经子图完成）
  - `assert_research_complete.step1:sys.assert`（研究完成前不得进入设计）
  - `validate_candidate.step5:sys.assert`（产物必须过 M1–M6）
  - `review_candidate.step2:sys.io.confirm`（交付前人审）
  - `tools`（不越输出目录、不擅发布/破坏）
- **execute_mode**：`design_skill` / `design_evolution` / `generate_candidate` / `validate_candidate` / `gather_sources` 因隔离、生成、来源收集、复杂校验或高影响决策需要标 `agent`（R7）；短路由、分类、确认和简单整理节点显式 `inline`。step 数不是选择 `agent` 的唯一标准；超过 10 个 `step*` 且仍为非 `agent` 时只是触发审查建议。若省略 `execute_mode`，runtime 回退 inline，validator 发 warning；真正的 `agent` 派发仍只能由 runtime trace 证明。
- **错误路由分两层**：图级 `error` 边是 **topology 级默认兜底**（每个图节点都有，最终都汇入 `skill_error` / `research_error`）；`functions.<node>.on_error` 是 **类型化错误路由**——按错误类型（`io_error` / `assertion_error` / `command_error` / `command_timeout` / `confirm_rejected` / `confirm_timeout` / `default`）精细分派到具体处理节点。匹配顺序为 `精确类型 → default → 图级 error 边`（AISOP §5.2.4）。`on_error` 是 **纯追加层**，不替换、不迁移图级 `error`；正常 `next` / `branches` 分支不受影响。当前已为 `capture_target` / `validate_candidate`（→ `skill_error`）、`review_candidate`（拒绝/超时 → `preserve`，其余 → `skill_error`）、`gather_sources`（→ `research_error`）四个关键节点声明类型化 `on_error`。
- **产物**：永远是 conformant AISP 技能（`<id>_aisp/aisp.aisop.json` + 合同 + enforced_by）；默认生成/分发时应在原生 `<id>_aisp/` 目录内包含同目录薄 `SKILL.md` sidecar，除非用户明确 opt out。不能把参考 sidecar 校验器的 exit 0 当作完整发布门，仍须独立拒绝 `examples/agent_skills_examples` 等旧 external 祖先路径与 `bridge_mode != native_sidecar`。
- **默认落盘**：`output_path` 可由用户提供；若为空或未提供，则默认使用本 creator 技能根目录的父目录，并在其中创建 `<id>_aisp/` 作为候选根目录。所有写入必须限制在该 `candidate_root` 内。若部署环境上层已有固定 `aisp\` 包裹/registry，那属于外部基础设施，creator 不创建、不修改、不校验。
- **独立**：只依赖 AISOP runtime；生命周期 AISP-native、工具无关——不依赖任何其它协议。

## 结构

```
aisp_creator_evolution_aisp/
├── aisp.aisop.json                 # 技能本体（create + evolve + research 子图）
├── aisop_specification/            # 完整 AISOP specification 快照（只读参考）
├── aisp_specification/             # 完整 AISP specification 快照（只读参考）
├── aisp_protocol_schemas/          # AISP 协议级 JSON Schema 快照（只读参考）
├── aisp_reference_tools/           # AISP 参考工具快照（本地辅助，不是信任根）
├── schemas/                        # 本技能内部 schema：skill-design / research-request / research-result / evolution-evidence
├── references/binding-rules.md     # enforced_by 绑定规则
├── templates/skill-template.md     # 生成技能的脚手架模板
├── scripts/validate_aisp_skill.py  # 轻量 bootstrap M1–M6 校验器（stdlib）
├── scripts/simulate_aisp_flow.py   # 静态 + 控制流模拟回归（stdlib，只读）
├── scripts/check_generated_candidate.py # 生成候选包发布闸（stdlib，只读）
├── evals/evals.json                # 触发 + 行为测试
└── README_CN.md
```

## 内置规范快照

- `aisop_specification/`：完整复制自 `https://github.com/AIXP-Labs/AISoP/tree/main/specification`，用于离线参考 AISOP 程序结构、运行时语义和术语。
- `aisp_specification/`：完整复制自 `https://github.com/AIXP-Labs/AISP/tree/main/specification`，用于离线参考 AISP 技能包结构、合同语义、一致性规则、protobuf 与标准 profile。
- `aisp_protocol_schemas/`：完整复制自 `https://github.com/AIXP-Labs/AISP/tree/main/schemas`，用于离线参考 AISP 合同、runtime trace、tool capabilities、registry manifest 的机器可校验结构。
- `aisp_reference_tools/`：完整复制自 `https://github.com/AIXP-Labs/AISP/tree/main/tools`，用于更完整的本地校验、hash、README 生成、`SKILL.md` sidecar 生成/检查、runtime trace 与 Agent Skills bridge 检查；其中 `check_doc_sync.py` 是仓库文档同步参考，不是独立技能包默认校验路径。creator 的候选发布门比参考 sidecar 工具更严格：EC7 关键 WARN 和旧 external 目录布局仍按候选失败处理。
- 每个快照目录都有 `MANIFEST.sha256.json`，hash 只证明本地快照完整性，不证明来源可信、最新或安全。
- 这些规范文件是 read-only reference snapshot，不是信任根；外部发布/注册/签名 provenance 仍应由消费方或 registry 独立核验。
- 参考工具通过只表示输入满足该工具已实现的规则；运行时强制、工具硬度、签名、registry provenance、发布可信度仍需要外部独立证据。

## 模拟回归（防进化退化）

`scripts/simulate_aisp_flow.py` 是一个 **stdlib-only、只读、不联网** 的回归脚本，把当前已验证过的控制流固化下来，防止后续进化再次引入不可达分支、错误的 retry 边、README drift 或隐藏缓存残留。它可读取 creator 自身或普通候选技能的 `aisp.aisop.json`：

- **静态检查**：(1) 每个 `aisop.*` 图节点的 `next` / `branches` / `error` 引用都解析到同图内的真实节点；(2) 每个图节点都有对应 `functions{}`，仅 `end_node` / `research_end` 两个终端允许无函数；(3) 每条 `non_negotiable.enforced_by` 都解析到真实机制（`aisop.main` 图存在 / `<node>.<step>:sys.*` 步骤里确含该 `sys.*` token / `tools` 已声明）；(4) 每个 `functions.<node>.on_error` 目标都解析到所属图内的真实节点；(5) 调用内置 `aisp_reference_tools/aisp_readme.py --check` 确认 `README.md` 仍是 `aisp.aisop.json` 的确定性派生投影；(6) 扫描并拒绝 `__pycache__/`、`.pyc`、`.pyo`、`.evolution_snapshot/`、`.version_history/` 等隐藏缓存/本地进化残留。
- **creator 专用正常路径（必须可达）**：当图形匹配本 creator 的 create/evolve 控制流时，重放 `create complete approved→deliver`、`evolve complete approved→deliver`、`incomplete→retry→complete→deliver`、`incomplete→retry-limit→preserve`（有界 retry：`research_attempts < 2`）、`rejected→preserve`、`needs_revision→retry→approved→deliver`。
- **creator 专用异常路径（必须被拒绝）**：bad intent、bad research status、validation fail、bad review label、bad revision_gate label、retry bound overflow。
- **普通候选技能通用图遍历**：当图形不是 creator 控制流时，执行 `generic_graph_walk`，验证 `aisop.main` 的非错误分支能终止且不引用缺失节点。该模式只证明图形结构与分支终止性，不证明模型语义正确、安全或可信。

退出码：全部通过 `0`，任一失败 `1`；并在 stdout 输出 JSON 报告。运行：

```powershell
python -B scripts\simulate_aisp_flow.py .
python -B scripts\simulate_aisp_flow.py <candidate_root>
```

> 用 `python -B` 运行可避免生成 `__pycache__/`。

## 候选包发布闸

`scripts/check_generated_candidate.py` 是生成后使用的 **read-only release gate**。它补足静态 M1–M6 覆盖不到的真实生成风险：

- **默认落盘语义**：`output_path` 缺省时，候选包必须是本 creator 同父目录下的 `<id>_aisp/`；不得退回当前工作目录、仓库根、用户 home。父目录是否是固定的外层 `aisp\` 包裹不归 creator 判断。
- **派生投影一致性**：根 `README.md` 必须仍是 `aisp.aisop.json` 的确定性投影；候选包内部不得创建 `aisp/` discovery 包裹。
- **脚本行为证据**：只要候选包声明 `execute_only` 或 `read_and_execute` 脚本资源，就必须声明并提供 `evals/script-behavior.json`，且每个脚本至少有 positive / boundary / failure 三类可重放用例。
- **schema 资源形状**：声明为 `kind: "schema"` 的资源必须存在、能解析为 JSON object、声明 `$schema`，并包含 `type` / `properties` / `oneOf` / `anyOf` / `allOf` / `$ref` 等 JSON Schema 约束关键字之一。
- **无脚本行为用例**：无 executable script 的纯 AISOP/模型中介技能应声明 `evals/behavior-cases.json`，包含 positive / boundary / failure 三类 `input_params`、`expected_behavior[]`、可选 `forbidden_behavior[]`；每个 `input_params` key 必须在 `system.content.params` 中声明。这只提供可审查的语义预期，不证明模型输出正确、安全或可信；发布闸缺失时给 WARN，存在时校验形状并要求声明到 `resources`。
- **第三方来源命名中性化**：转换外部 Agent Skill 时，第三方来源/平台身份词（当前发布闸强制 `anthropic` / `claude`）不得进入候选目录名、`system.id` 或同目录 `SKILL.md name`；来源归属只能放在声明资源、reference 或 provenance 元数据中。
- **Agent Skills sidecar 严格性**：默认生成/分发的候选包必须包含同目录 `SKILL.md` sidecar；缺失时发布闸失败，除非运行发布闸时明确使用 opt-out 标记。存在 sidecar 时必须通过 `aisp_skill_md.py --check` 与 bridge validator；EC7 关键 WARN（protocol / bridge_mode / runtime-boundary / logic-copy）在 creator 发布门里按失败处理；`system.summary` 必须原样单行出现在 sidecar 中，避免换行 drift。
- **缓存残留**：拒绝 `__pycache__/`、`.pyc`、`.pyo`、`.evolution_snapshot/`、`.version_history/`。

运行示例：

```powershell
python -B scripts\check_generated_candidate.py <candidate_root> --creator-root <creator_root>
```

如果用户显式提供了 `output_path`，验证时传入：

```powershell
python -B scripts\check_generated_candidate.py <candidate_root> --creator-root <creator_root> --output-path <output_parent>
```

## 运行

载入 `aisp.aisop.json`，绑定 `user_request` 等 params，然后 `RUN aisop.main`。`output_path` 可选：用户提供时作为候选父目录；未提供时解析为本 creator 技能根目录的父目录。creator 只生成候选 `<id>_aisp/` 包，不处理上层固定 `aisp\` 包裹或 registry 索引。技能合同（`user.content.aisp_contract`）模型本轮直接读到；研究与设计阶段优先读取内置 AISOP/AISP 规范、协议 schema 与参考工具快照作为本地基线；`sys.io.confirm` 强制阻塞、不可绕过（Axiom 0）。

## 流程

```
classify_intent ──create──▶ capture_request ─▶ define_goal ─┐
                └─evolve──▶ capture_target ─▶ gather_evidence ┴─▶ run_research(RUN aisop.research)
run_research ──complete──▶ assert_research_complete ──create──▶ design_skill ──┐
             └─incomplete──▶ revision_gate                   └─evolve──▶ design_evolution ┴─▶ generate_candidate ─▶ validate_candidate
                       ─▶ review_candidate ──approved──▶ deliver
                                          ──needs_revision──▶ revision_gate
                                          ──rejected──▶ preserve
```

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
