# 发布证据矩阵

[English](release-evidence-matrix.md)

> AISP 仓库和技能包的发布检查清单。本页把每个发布门证明什么、不能证明什么分开说明。

发布门故意分层。静态校验、生成文档检查、runtime trace 检查、clean-tree 检查是不同类型的证据。全部通过代表仓库达到可发布状态；但这仍不代表任何未签名来源的技能包已经可信。

---

## 读者路径

| 读者 | 起点 | 后续阅读 |
|------|------|----------|
| 技能作者 | [`docs/guides/first-aisp-skill.md`](../guides/first-aisp-skill.md) | [`docs/guides/conformance-walkthrough_CN.md`](../guides/conformance-walkthrough_CN.md), [`docs/reference/generated-readme.md`](generated-readme.md) |
| Runtime 实现者 | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`specification/AISP_Protocol_cn.md`](../../specification/AISP_Protocol_cn.md) |
| 发布审查者 | 本页 | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`docs/topics/security-model.md`](../topics/security-model.md) |
| Registry 维护者 | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/threat-taxonomy.md`](threat-taxonomy.md), [`docs/topics/discovery-and-registry.md`](../topics/discovery-and-registry.md) |

---

## 证据层级

| 证据层级 | 由谁产生 | 适合证明 | 不适合证明 |
|----------|----------|----------|------------|
| 静态包证据 | `aisp_validate.py`、schemas、index checks | 文件夹形状、合同形状、绑定、资源路径、静态安全规则 | runtime 行为 |
| 派生投影证据 | `aisp_readme.py`、`aisp_skill_md.py`、bridge validator | `README.md` / `SKILL.md` 是 `aisp.aisop.json` 的确定性投影 | 安全、信任或平台执行 |
| Runtime trace 证据 | `aisp_check_runtime_trace.py`、`--runtime-trace` | 所提供 trace 中发生过的部分 R 系列行为 | 未签名 trace source 本身可信 |
| 完整性证据 | `aisp_hash.py`、manifests | 本地内容完整性可重算 | 背书、安全性或 provenance 本身 |
| 仓库卫生证据 | 文档检查、测试、clean-tree 检查 | 文档、链接、测试和已提交产物一致 | 外部信任或 runtime 行为 |

---

## 发布门

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

使用 `-IncludePytest` 可额外运行 pytest；使用 `-RequireClean` 执行最终发布前的
clean-tree 检查。可审计的展开命令如下：

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

只有明确更新派生产物时才运行写入命令：

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

---

## 命令矩阵

| 命令 | 产生的证据 | 预期发布结果 |
|------|------------|--------------|
| `powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1` | 本地发布门封装，并额外执行残留、私密路径、禁用 AIAP 结构扫描 | 所有内置检查通过时 PASS；`-RequireClean` 仅在有意改动已提交后使用。 |
| `python -B tools/aisp_validate.py examples/aisp` | 所有示例的静态 M/SE/EC 包校验 | PASS。纯静态运行中，使用 `enforced_by: tools` 的技能可能保留 `AISP_W_R6_TOOLS_CONDITIONAL`；除非提供 runtime/tool 证据，否则这是诚实 warning。 |
| `python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp` | 低风险参考技能的机器可读静态校验输出 | 零 failure。 |
| `python -B tools/aisp_validate.py --strict-tools --runtime-trace ... stock_analysis_aisp` | 股票示例的严格 R6/R7 证据消费 | 只有事件型 runtime trace 证据匹配该技能时才 PASS。 |
| `python -B tools/aisp_validate.py --strict-tools --runtime-trace ... aisp_creator_evolution_aisp` | creator 示例的严格 R6 证据消费 | 只有事件型 runtime trace 证据匹配该技能时才 PASS。 |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp ... hard-pass.json` | stock 的直接 runtime trace schema / 行为检查 | 被检查 trace PASS。 |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp ... hard-pass.json` | creator 的直接 runtime trace schema / 行为检查 | 被检查 trace PASS。 |
| `python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp` | 可重算的包完整性 manifest | 输出确定性 hash；不是信任证明。 |
| `python -B examples/aisp/aisp_list.py --check` | 发现索引一致性 | `aisp_list.json` 与文件夹一致时 PASS。 |
| `python -B tools/aisp_readme.py examples --check-all` | 生成式单技能 README 一致性 | README 投影确定且最新时 PASS。 |
| `python -B tools/aisp_skill_md.py examples --check-all` | 生成式同目录 `SKILL.md` 投影一致性 | sidecar 确定且最新时 PASS。 |
| `python -B tools/aisp_validate.py --strict-readme examples/aisp` | 发布 profile 下的 README 要求 | 不存在缺失、手写漂移或标记错误的 README 时 PASS。 |
| `python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme` | 薄 sidecar bridge 形状加原生 AISP 校验 | `SKILL.md` sidecar 保持 truth-source 安全时 PASS。 |
| `python -B tools/check_doc_sync.py --root .` | 命令引用同步、snapshot、workflow、ADR mirror 检查 | 文档和生成快照不漂移时 PASS。 |
| `python -B tools/check_markdown_links.py --root .` | 本地 Markdown 链接和 heading anchor 解析 | 仓库内文档链接可解析时 PASS。 |
| `git diff --check` | 空白和冲突标记卫生 | 无空白错误时 PASS。 |
| `git diff --exit-code` | 已跟踪文件干净 | 只有所有已跟踪的有意改动已提交后才 PASS。 |
| `git status --porcelain=v1 --untracked-files=all` | 完整工作树干净，包含未跟踪文件 | 只有没有任何输出时才 PASS。 |
| `python -B -m unittest discover -s tests` | 回归测试套件 | 工具行为和 fixtures 仍匹配预期时 PASS。 |

---

## Warning 策略

Warning 不是同一种信号：

| Warning 类别 | 含义 | 发布处理 |
|--------------|------|----------|
| `AISP_W_R6_TOOLS_CONDITIONAL` | 技能使用 `enforced_by: tools`，但当前检查是纯静态或缺少 hard evidence。 | 静态审查中可预期。严格发布门需要用事件型 runtime trace 或带 provenance 的 hard tool capability evidence 消解。 |
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | runtime/tool artifact 声称 hard enforcement，但缺少独立证据。 | 不得当作 proof。补事件/provenance 证据，或保留 warning。 |
| EC7 `SKILL.md` warnings | 可选/默认 sidecar 缺失或漂移。 | Core AISP 仍可有效；release profile 可要求 sidecar，除非明确 opt out。 |
| EC8 generated README warnings | 非 strict 模式下，单技能 README 缺失、手写或漂移。 | 重新生成；或使用 strict release profile 让漂移失败。 |
| Missing `execute_mode` warnings | 函数未显式声明 dispatch intent；runtime fallback inline。 | 兼容性 fallback 可接受，但发布级示例应显式声明 `inline` 或 `agent`。 |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | 非 agent 函数超过 10 个数字 `stepN` 执行步骤。 | 审查是否应使用 `agent`。该阈值是审查启发式，不是短高隔离节点使用 `agent` 的限制条件。 |

---

## 信任边界

该发布门证明仓库和包的一致性，不证明来自不可信来源的包可以安全运行。

- 生成式 README 检查通过，只证明派生一致性，不证明信任。
- `SKILL.md` bridge 检查通过，只证明 sidecar 形状，不证明 Agent Skills 平台上的硬执行。
- Hash 检查通过，只证明本地完整性，不证明背书。
- Runtime trace 检查通过，只证明所提供 trace 记录的内容，且受 trace provenance 限制。
- 外部信任仍来自 registry policy、签名、provenance、人工审查和 runtime 的真实 enforcement 行为。

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
