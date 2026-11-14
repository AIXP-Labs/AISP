# 发布证据矩阵

[English](release-evidence-matrix.md)

> AISP 仓库和技能包的发布检查清单。本页把每个发布门证明什么、不能证明什么分开说明。

发布门故意分层。静态校验、生成文档检查、runtime trace 检查、clean-tree 检查是不同类型的证据。仓库检查通过是发布的必要条件，不是充分条件：适用的真实宿主/运行时验收、已知限制审查及明确发布授权仍须分别满足。它们均不能让未签名来源的技能包自动可信。

---

## 读者路径

| 读者 | 起点 | 后续阅读 |
|------|------|----------|
| 技能作者 | [`docs/guides/first-aisp-skill.md`](../guides/first-aisp-skill.md) | [`docs/guides/conformance-walkthrough_CN.md`](../guides/conformance-walkthrough_CN.md), [`docs/reference/generated-readme.md`](generated-readme.md) |
| Runtime 实现者 | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`specification/AISP_Protocol_cn.md`](https://github.com/AIXP-Labs/AISP/blob/main/specification/AISP_Protocol_cn.md) |
| 发布审查者 | 本页 | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`docs/topics/security-model.md`](../topics/security-model.md) |
| Registry 维护者 | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/threat-taxonomy.md`](threat-taxonomy.md), [`docs/topics/discovery-and-registry.md`](../topics/discovery-and-registry.md) |

---

## 证据层级

| 证据层级 | 由谁产生 | 适合证明 | 不适合证明 |
|----------|----------|----------|------------|
| 静态包证据 | `aisp_validate.py`、schemas、index checks | 文件夹形状、合同形状、绑定、资源路径、静态安全规则 | runtime 行为 |
| 派生接口证据 | `aisp_readme.py`、`aisp_skill_md.py`、bridge validator | README 派生；SKILL.md 与业务程序、五个命令字符串及冻结版本策略、生成器修订一致 | 执行器认证、安全、信任或平台执行 |
| Runtime trace 证据 | `aisp_check_runtime_trace.py`、`--runtime-trace` | 核对所提供 trace 中部分 R 系列事件声明 | 独立证明事件真实发生，或 trace source 本身可信 |
| 完整性证据 | `aisp_hash.py`、manifests | 本地内容完整性可重算 | 背书、安全性或 provenance 本身 |
| 仓库卫生证据 | 文档检查、测试、clean-tree 检查 | 文档、链接、测试和已提交产物一致 | 外部信任或 runtime 行为 |

---

## 发布门

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

使用 `-IncludePytest` 可额外运行 pytest（须另行安装 pytest，`[dev]` 元数据仅声明
jsonschema）。`-RequireClean` 增加最终 clean-tree 检查，但封装始终会运行
`git diff --check`。禁止 Git 时，不得调用封装；只单独运行获准的非 Git
检查，并记录完整发布门未运行。

下列共享参考命令不是封装/CI 的逐项展开。两者还检查 JSON 语法，封装额外扫描
残留和私密路径，CI 检查的则是已提交空白，而非工作树 diff。

私密路径扫描仅检查 `.git` 之外小于 5 MB 文件中的选定通用路径/密钥标记，
不是完整的密钥或个人数据检测器。扫描范围内的文件不可读时明确失败，而非静默跳过；
可读的空文件合法。扫描器不内置针对个人账户名的拒绝列表。

被忽略的运行/进化缓存仍会使残留门失败。忽略规则不会清理已跟踪文件、历史或
分发归档；分享前须另行检查实际 wheel/sdist 内容和脱敏证据。凭据轮换及任何
历史清理均须另行授权维护。

归档回归需要已声明的构建后端，覆盖旧 `*.egg-info/SOURCES.txt` 和真实 wheel/sdist
内容。`MANIFEST.in` 排除选定私密模式；仅关闭 wheel 包数据并不能过滤 sdist。
每个构建入口的实际输入均与重新注入的旧清单比较。两种格式均拒绝选定私密样本；
公开数据对照文件保留在 sdist 中，不进入仅分发工具的 wheel。必要模块和许可证
文件则在两种格式中与源码逐字节比较；公开数据对照也须保留预期字节。wheel 按
路径和内容双重排除公开对照。近似目录名和名为 `build`／`dist` 的普通文件仍保留；
真正匹配裁剪规则的目录仍排除，公开源码应放在这些目录之外。对照不保证全仓打包。
CI 安装所需后端并设置 `AISP_REQUIRE_ARCHIVE_TEST=1`，不允许因后端问题跳过。
本机未启用该配置且后端缺失或过旧时，此项测试跳过，不形成归档已验证的证据。
本地发布封装同样要求实际执行归档测试，结束时恢复调用方原配置；它不会安装依赖，
须事先准备合格的构建后端。
有 PowerShell 时，回归使用子进程内的 `python` 替身产生受控原生退出码 `0`、
`1`（常见单测失败）和 `7`（额外非零对照），验证
提取出的真实单测门。标签和清理路径按 AST 字面值读取，允许普通引号变化；
替身逐项核对固定命令的参数数量、顺序和值，不比较拼接字符串，也不是通用
Shell 等价性检查器。标签／获准路径采用忽略大小写的序数比较；命令参数必须是
标量字符串，采用区分大小写的序数比较。数组和对象参数形式不在这一固定命令
测试配置支持范围内，并非 AISP 禁止；测试不模拟原生命令的参数数组展开。
配置设置／清理取自原脚本并保留源码顺序；不同初值可检出
环境变量交叉恢复。恢复后的环境值也采用序数比较；合法原始 Unicode 值须原样
保留，不做清洗或归一化。两个设置均包含混合大小写的 NFC／NFD 原值及零宽字符
对照。缺失与空值按宿主实际可观察表示核验。
不递归运行单测发现，也不执行含 Git 的完整发布封装；
这一有界回归不等于完整发布验收。

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
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp ... hard-pass.json` | stock 的v1 有界形状及选定运行规则检查 | 仅代表已实现形状/规则检查通过，不是事件认证或完整运行期认证。 |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp ... hard-pass.json` | creator 的v1 有界形状及选定运行规则检查 | 仅代表已实现形状/规则检查通过，不是事件认证或完整运行期认证。 |
| `python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp` | 可重算的包完整性 manifest | 输出确定性 hash；不是信任证明。 |
| `python -B examples/aisp/aisp_list.py --check` | 发现索引一致性 | `aisp_list.json` 与文件夹一致时 PASS。 |
| `python -B tools/aisp_readme.py examples --check-all` | 生成式单技能 README 一致性 | README 投影确定且最新时 PASS。 |
| `python -B tools/aisp_skill_md.py examples --check-all` | 必需接口 M7 一致性 | 固定引导、派生头部、执行器配置与版本策略合法且为当前形式才 PASS。 |
| `python -B tools/aisp_validate.py --strict-readme examples/aisp` | 发布 profile 下的 README 要求 | 不存在缺失、手写漂移或标记错误的 README 时 PASS。 |
| `python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme` | 共享 M7，加头部/路径与原生包校验 | PASS 不认证执行器，也不证明执行完成。 |
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
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | hard-enforcement 声明缺少检查器所要求的事件/provenance 结构。 | 不得当作 proof；结构满足也不代表证据已获独立认证。 |
| `AISP_W_M5_AMBIGUOUS_USE` | 字面量路径对应不同 scope 的资源；至少一项声明允许该操作，但目标仍不明确。若所有候选都禁止，SE3 直接失败。 | 审查运行期 scope 解析和门控，或使用不同路径；不合并权限，也不把 warning 当模式证明。 |
| M7 / 旧 EC7 接口失败 | 必需接口缺失、旧版、损坏或漂移。 | 核心失败，无 opt-out；精确识别的旧投影须明确迁移，固定正文漂移先修复再写。执行器配置与版本策略格式通过不认证执行器。 |
| EC8 generated README warnings | 非 strict 模式下，单技能 README 缺失、手写或漂移。 | 重新生成；或使用 strict release profile 让漂移失败。 |
| Missing `execute_mode` warnings | 函数未显式声明 dispatch intent；runtime fallback inline。 | 兼容性 fallback 可接受，但发布级示例应显式声明 `inline` 或 `agent`。 |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | 非 agent 函数超过 10 个数字 `stepN` 执行步骤。 | 审查是否应使用 `agent`。该阈值是审查启发式，不是短高隔离节点使用 `agent` 的限制条件。 |

`--warnings-fail` 让仍有 warning 的 CLI 返回非零；它不改写 warning 的严重度或代码，
也不把仅有 warning 的报告中 `conformant: true` 改成合规失败。`--strict-tools` 检查
R6 证据，`--strict-readme` 将 EC8 README 问题升为失败；两者都不消除 M5 歧义。
Creator 候选门保留非阻断的参考 warning，因此其通过本身不免除对这些 warning 的审查。
多目标检查中，任一目标出现合规或输入失败即返回 1；否则，启用 `--warnings-fail`
且任一目标有 warning 时返回 1。无论参数顺序如何，干净目标都不能抵消其它目标的
失败或 warning。

---

## 信任边界

该发布门证明仓库和包的一致性，不证明来自不可信来源的包可以安全运行。

- 仓内示例 trace 是回归夹具，不是独立采集的真实执行器记录或认证。事件和 provenance 字段本身也可能是自报，检查器接受其形状不等于认证来源。
- 一条版本条件引导可以通过多个场景验收。场景覆盖不代表多套引导实现、所有版本组合覆盖，也不能代替真实业务/运行期断言检查。
- 分清业务完成、断言未验证、预期拒绝/失败停止及委托代答。委托决策不证明“本人逐门确认”的验收要求已被实际覆盖。
- 生成式 README 检查通过，只证明派生一致性，不证明信任。
- M7/接口检查通过只证明引导未改、格式正确，不认证执行器或 Agent Skills 平台上的硬执行。
- Hash 检查通过，只证明本地完整性，不证明背书。
- Runtime trace 检查通过，只证明所提供 trace 记录的内容，且受 trace provenance 限制。
- 外部信任仍来自 registry policy、签名、provenance、人工审查和 runtime 的真实 enforcement 行为。

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
