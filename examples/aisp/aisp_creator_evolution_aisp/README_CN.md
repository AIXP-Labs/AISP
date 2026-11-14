# aisp_creator_evolution_aisp

一个**AISP 原生 creator/evolution 元技能**：创建新的 conformant AISP 技能、进化现有 AISP 技能，并将现有 Agent Skills 适配/转换为原生 AISP 技能包。严格遵循 AISP V1.0.0 spec 与规则（仅建在 AISOP 上、独立于其它协议）。

`README.md` 是由 `aisp.aisop.json` 确定性生成的英文自举投影；本 `README_CN.md` 是人工维护的中文深度说明，面向审查、进化和运行排障。两者分工不同，不要求章节一一同构；若事实字段冲突，以 `aisp.aisop.json` 与生成式 `README.md` 为准。

## 是什么

- **一个技能 = 一个 `<id>_aisp/` 技能包**（M2/M7）：固定业务入口是 `aisp.aisop.json`，同目录还必须有生成式 `SKILL.md`；不能把整个技能包说成只有一个文件。`aisop` 内含 `main`（按意图路由 create / evolve）+ `research`（两路共享的研究子图）。
- **合同在 user 消息**（M3）：`user.content.aisp_contract`（真 object），`profile: "aisp.skill.v1"`。
- **红线即代码**（M4）：6 条 `non_negotiable` 全部 `enforced_by` 到真实机制——
  - `aisop.main`（按图执行、不跳研究/校验/人审）
  - `run_research.step2:sys.assert`（研究必须经子图完成）
  - `assert_research_complete.step1:sys.assert`（研究完成前不得进入设计）
  - `validate_candidate.step5:sys.assert`（轻量 M1–M6、安全检查及包含 M7 的实际候选发布门均须通过）
  - `review_candidate.step2:sys.io.confirm`（交付前人审）
  - `tools`（不越输出目录、不擅发布/破坏）
- **execute_mode**：`design_skill` / `design_evolution` / `generate_candidate` / `validate_candidate` / `gather_sources` 因隔离、生成、来源收集、复杂校验或高影响决策需要标 `agent`（R7）；短路由、分类、确认和简单整理节点显式 `inline`。step 数不是选择 `agent` 的唯一标准；超过 10 个 `step*` 且仍为非 `agent` 时只是触发审查建议。若省略 `execute_mode`，runtime 回退 inline，validator 发 warning；真正的 `agent` 派发仍只能由 runtime trace 证明。
- **错误路由分两层**：已声明的图级 `error` 边是 **topology 级默认兜底**，通向 `skill_error` / `research_error`；不是每个网关、错误处理或终端节点都有此边。`functions.<node>.on_error` 是 **类型化错误路由**，按 `io_error` / `assertion_error` / `command_error` / `command_timeout` / `confirm_rejected` / `confirm_timeout` / `default` 分派。匹配顺序为 `精确类型 → 分类匹配 → default → 图级 error 边`（AISOP §5.2.4）。当前已为 `capture_target` / `validate_candidate`（→ `skill_error`）、`review_candidate`（拒绝/超时 → `preserve`，其余 → `skill_error`）、`gather_sources`（→ `research_error`）声明 `on_error`；不替换图级兜底或正常 `next` / `branches`。
- **产物**：必须是 conformant AISP 技能（M1–M7：`<id>_aisp/aisp.aisop.json` + 合同 + enforced_by + 同目录 `SKILL.md` 执行器接口），不提供缺接口豁免。接口固定为 `bridge_mode: agent_skills_bridge`，由工具派生头部及引导程序；业务逻辑只在 `aisp.aisop.json`。仍须独立拒绝旧 external / nested 桥目录，不能仅凭某一个工具 exit 0 放行。
- **默认落盘**：`output_path` 可由用户提供；若为空或未提供，则默认使用本 creator 技能根目录的父目录，并在其中创建 `<id>_aisp/` 作为候选根目录。所有写入必须限制在该 `candidate_root` 内。若部署环境上层已有固定 `aisp\` 包裹/registry，那属于外部基础设施，creator 不创建、不修改、不校验。
- **独立**：只依赖 AISOP runtime；生命周期 AISP-native、工具无关——不依赖任何其它协议。

## 结构

```
aisp_creator_evolution_aisp/
├── aisp.aisop.json                 # 技能本体（create + evolve + research 子图）
├── README.md                       # 生成式英文介绍，不是业务或信任来源
├── SKILL.md                        # M7 必需的同目录执行器接口
├── aisop_specification/            # 完整 AISOP specification 快照（只读参考）
├── aisp_specification/             # 完整 AISP specification 快照（只读参考）
├── aisp_protocol_schemas/          # AISP 协议级 JSON Schema 快照（只读参考）
├── aisp_reference_tools/           # AISP 参考工具快照（本地辅助，不是信任根）
├── schemas/                        # 本技能内部 schema：skill-design / research-request / research-result / evolution-evidence
├── references/binding-rules.md     # enforced_by 绑定规则
├── templates/skill-template.md     # 生成技能的脚手架模板
├── scripts/validate_aisp_skill.py  # 轻量 bootstrap M1–M6 校验器（stdlib）
├── scripts/check_research_result.py # stdin JSON 研究结果外壳检查（非完整 schema/来源验证）
├── scripts/simulate_aisp_flow.py   # 静态 + 控制流模拟回归（stdlib，只读）
├── scripts/check_generated_candidate.py # 静态预检 + 可执行回归发布门（stdlib，非沙箱）
├── evals/evals.json                # 触发 + 行为测试
└── README_CN.md
```

## 内置规范快照

- `aisop_specification/`：完整复制自 `https://github.com/AIXP-Labs/AISoP/tree/main/specification`，用于离线参考 AISOP 程序结构、运行时语义和术语。
- `aisp_specification/`：完整复制自 `https://github.com/AIXP-Labs/AISP/tree/main/specification`，用于离线参考 AISP 技能包结构、合同语义、一致性规则、protobuf 与标准 profile。
- `aisp_protocol_schemas/`：完整复制自 `https://github.com/AIXP-Labs/AISP/tree/main/schemas`，用于离线参考 AISP 合同、runtime trace、tool capabilities、registry manifest 的机器可校验结构。
- `aisp_reference_tools/`：源自 [AISP 工具](https://github.com/AIXP-Labs/AISP/tree/main/tools)，实际工作树来源及 SHA 以随包清单为准；覆盖静态 M1–M7、hash、README、执行器接口、runtime trace 形状等检查，不是外部信任根。其中 `check_doc_sync.py` 只作仓库文档同步参考。候选发布门保留旧 EC7 关键 WARN 拒绝规则以防陈旧工具混入，并拒绝 external 目录布局。
- 每个快照目录都有 `MANIFEST.sha256.json`，hash 只证明本地快照完整性，不证明来源可信、最新或安全。
- 接口版本策略：SoulRun 只是默认适配器，不绑定协议。首次生成/显式刷新默认策略时查询官方最新稳定版并冻结；离线生成或其他执行器使用显式 `--executor-version-requirement '>=X.Y.Z'` 或 `'==X.Y.Z'`。普通重生成/校验离线保留约束，用户显式约束不被刷新覆盖。安装/升级/降级须真人同意，之后复查匹配才执行。
- 这些规范文件是 read-only reference snapshot，不是信任根；外部发布/注册/签名 provenance 仍应由消费方或 registry 独立核验。
- 参考工具通过只表示输入满足该工具已实现的规则；运行时强制、工具硬度、签名、registry provenance、发布可信度仍需要外部独立证据。

## 静态验证与表达式边界

`validate_candidate` 从轻量 validator 的实际 JSON 取得 `m1_to_m6_pass` /
`safety_pass`，另以完整候选发布门取得 `candidate_release_report.pass`；
不能把完整 validator 的另一种报告形状冒充轻量报告。研究断言只使用 AISOP
支持的比较、点路径及 `&&` / `||`，不嵌入 Python 的 `isinstance`、
`.get()` 或生成器表达式。

`scripts/check_research_result.py` 从 stdin 接收本次真实 research_result，
输出 `valid/errors` JSON，退出码为 0 或 1。它只检查 status、findings、
citations 的外壳与必要成员类型，不证明完整内部 schema、引用真实性或研究质量；
非零退出、坏 JSON 和无法解析的 stdout 均应阻止继续。

## 模拟回归（防进化退化）

`scripts/simulate_aisp_flow.py` 是一个 **stdlib-only、只读、不联网** 的回归脚本，把当前已验证过的控制流固化下来，防止后续进化再次引入不可达分支、错误的 retry 边、README drift 或隐藏缓存残留。它可读取 creator 自身或普通候选技能的 `aisp.aisop.json`：

- **静态检查**：(1) 每个 `aisop.*` 图节点的 `next` / `branches` / `error` 引用都解析到同图内的真实节点；(2) 每个图节点都有对应 `functions{}`，仅 `end_node` / `research_end` 两个终端允许无函数；(3) 每条 `non_negotiable.enforced_by` 都解析到真实机制（`aisop.main` 图存在 / `<node>.<step>:sys.*` 数字步骤以该精确 `sys.*` 调用开头，不接受相似前缀、prose 提及或 step_note 元数据 / `tools` 已声明）；(4) 每个 `functions.<node>.on_error` 目标都解析到每个所属图内的真实节点；共享函数不会只检查第一个图；(5) 调用内置 `aisp_reference_tools/aisp_readme.py --check` 确认 `README.md` 仍是 `aisp.aisop.json` 的确定性派生投影；(6) 扫描并拒绝 `__pycache__/`、`.pyc`、`.pyo`、`.evolution_snapshot/`、`.version_history/`、`.execution_cache/`、`.soulrun_cache/` 等隐藏缓存/本地进化残留。
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

`scripts/check_generated_candidate.py` 是生成后使用的 **静态预检 + 可执行回归发布门**，调用权威静态 M1–M7 检查并补足交付约束。轻量 `validate_aisp_skill.py` 仅作 M1–M6 子集预检，报告 `m7_checked: false`，不能独自作合规结论。发布门不主动改写候选或联网，但脚本用例会使用调用者权限执行；它不提供只读、禁网或沙箱保证。
运行前须信任工具、候选脚本与 argv，并使用适当隔离环境。发布门会先完成静态检查和全部脚本用例形状预检，
失败不进入回放；回放出现非预期失败即停，回放后复查缓存残留。参考校验的 warning（包括 R6）保留在汇总，不洗成无警告。exit 0、conformant: true 若与失败计数/失败条目矛盾，或根本没有结果条目，发布门拒绝接受；空自报不是验证证据。
共享 schema 读取也先检查 `_shared/` 根仍在所属 `aisp/` 目录内，不能借根链接读包外文件。
轻量预检对入口/资源越界和非字符串 enforced_by 返回失败报告，不以异常崩溃替代检查；它仍不是完整 M7 或运行期验证。
桥报告同样拒绝顶层成功与失败摘要/子结果矛盾、空结果及畸形条目；合法 warning 保留。
候选 JSON（含 schema、评测产物和工具输出）拒绝重复键与 NaN/Infinity；一致性不认证工具来源或声明真实性。
stdin-only 的研究结果检查器也拒绝重复键与 NaN/Infinity；它仍只查 envelope，不查完整 schema、来源真实性或 grounding。

发布门检查：

- **默认落盘语义**：`output_path` 缺省时，候选包必须是本 creator 同父目录下的 `<id>_aisp/`；不得退回当前工作目录、仓库根、用户 home。父目录是否是固定的外层 `aisp\` 包裹不归 creator 判断。
- **派生投影一致性**：根 `README.md` 必须仍是 `aisp.aisop.json` 的确定性投影；候选包内部不得创建 `aisp/` discovery 包裹。
- **脚本行为证据**：只要候选包声明 `execute_only` 或 `read_and_execute` 脚本资源，就必须声明并提供 `evals/script-behavior.json`，且每个脚本至少有 positive / boundary / failure 三类可重放用例。用例名称、分类、argv、stdin、退出码、超时及输出匹配字段须类型正确；重复路径或畸形用例在执行前失败。
- **schema 资源形状**：声明为 `kind: "schema"` 的资源必须存在、能解析为 JSON object、声明 `$schema`，并包含 `type` / `properties` / `oneOf` / `anyOf` / `allOf` / `$ref` 等 JSON Schema 约束关键字之一。
- **无脚本行为用例**：无 executable script 的纯 AISOP/模型中介技能应声明 `evals/behavior-cases.json`，包含 positive / boundary / failure 三类 `input_params`、`expected_behavior[]`、可选 `forbidden_behavior[]`；每个 `input_params` key 必须在 `system.content.params` 中声明，即使 params 为空也不允许额外输入；`expected_behavior[]` 不可为空。这只提供可审查的语义预期，不证明模型输出正确、安全或可信；发布闸缺失时给 WARN，存在时校验形状并要求声明到 `resources`。
- **第三方来源命名中性化**：转换外部 Agent Skill 时，第三方来源/平台身份词（当前发布闸强制 `anthropic` / `claude`）不得进入候选目录名、`system.id` 或同目录 `SKILL.md name`；来源归属只能放在声明资源、reference 或 provenance 元数据中。
- **M7 必需接口**：缺 `SKILL.md`、旧 `native_sidecar`、坏配置、固定正文漂移均失败；旧 `--allow-missing-sidecar` 参数已移除，不能绕过。用 `aisp_skill_md.py --check` 和 bridge validator 共用的 M7 逻辑检查派生 name/description/license、固定引导程序、五个命令字符串和冻结版本策略，不另加“summary 必须完整原样出现”的冲突规则。合法执行器配置与版本策略保留，损坏报错；可识别旧模板只在明确 `--write` 时迁移；已有冻结策略的上一版正文迁移不会自行查询或更新下限。固定 bootstrap 可以有 functions，但不复制业务函数。
- **运行与信任边界**：SoulRun 是默认执行器，执行器配置与版本策略格式合格不等于执行器认证。不得绕过执行器自行执行或续跑业务程序；准备完成、等待确认和执行完成必须分开。默认会话作用域同时只支持一个活动会话，停门也占用作用域。静态检查不证明真实派发、工具硬门控或外部信任。
- **手工迁移回归边界**：本轮以 Creator 为协议消费者和测试样例，手工适配并在隔离目录实际运行工具，不启动 Creator/模型管线。工程回归不等于真实模型创建或进化成功。
- **缓存残留**：拒绝 `__pycache__/`、`.pyc`、`.pyo`、`.evolution_snapshot/`、`.version_history/`、`.execution_cache/`、`.soulrun_cache/`。运行缓存可能包含用户消息或模型回答，不因被忽略就适合分发；公开的回归证据目录仍保留。

运行示例：

```powershell
python -B scripts\check_generated_candidate.py <candidate_root> --creator-root <creator_root>
```

如果用户显式提供了 `output_path`，验证时传入：

```powershell
python -B scripts\check_generated_candidate.py <candidate_root> --creator-root <creator_root> --output-path <output_parent>
```

## 运行

使用同目录 `SKILL.md` 把执行交给合规 AISP/AISOP 执行器，默认 SoulRun，但不绑定厂商。只有一个版本判断：包版本满足冻结约束就直接执行；已证实未安装或不满足才询问安装，同意后安装并复查，满足才执行。拒绝、失败或探测出错就停止，不自行解释业务程序。执行器载入 `aisp.aisop.json`，绑定 `user_request` 等 params 后运行 `aisop.main`。`output_path` 可选：用户提供时作为候选父目录；未提供时使用本 creator 技能根目录的父目录。creator 只生成候选 `<id>_aisp/` 包，不处理上层固定 `aisp\` 包裹或 registry 索引。研究与设计阶段读取内置规范等快照作为本地参考；`sys.io.confirm` 强制阻塞，版本通过也不豁免业务确认（Axiom 0）。

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
