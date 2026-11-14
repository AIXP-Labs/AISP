# 如何贡献 AISP

[English](CONTRIBUTING.md)

感谢您有兴趣为 AI 技能协议（AISP）做出贡献！本文档提供贡献指南。

> ⚠️ **当前阶段的贡献政策**
>
> 我们欢迎通过 **GitHub Issues 进行讨论**。
>
> **当前不接受外部 Pull Request。** 如果您有任何建议 — bug 报告、功能想法、规范澄清或一致性规则建议 — 请通过 Issue 描述。如果我们认为有价值，由维护者实现并在 commit/release notes 中署名感谢您。
>
> 此政策未来会重新审视。

> **阶段状态（V1.0.0）**
>
> AISP 处于早期规范阶段（V1.0.0）。下方流程描述的是**目标**治理模型。初期决策由 AIXP Labs 核心维护者做出；社区讨论窗口将随贡献者基数增长而扩大。

## 如何贡献

### 报告 Issue

- 使用 [GitHub Issues](https://github.com/AIXP-Labs/AISP/issues) 报告 bug、提议功能或建议规范变更
- 规范变更请提交说明提议的 Issue，由维护者添加 `spec-change` 标签
- 提供清晰描述，尽可能附带示例

### 讨论驱动开发

请勿直接提交 PR，而是：

1. **打开 Issue**，描述您的提议、Bug 或想法
2. **与维护者讨论** — 明确范围、设计和方法
3. **等待审核** — 重要提议遵循下方[规范变更](#规范变更)流程
4. **若被采纳**，维护者将实现该变更并在 commit/release notes 中署名感谢您

### 规范变更

影响规范性内容（`specification/` 中任何文件）的提议遵循以下流程：

1. 带 `spec-change` 标签的 Issue，描述提议变更
2. 非平凡变更需要至少 14 天的讨论期（目标治理模型；当前讨论窗口随贡献者基数调整）
3. 重大决策需要在 `adrs/` 中记录架构决策记录（ADR）
4. 维护者进行 Axiom 0 合规审查
5. 同步更新反映变更的文档

### 文档变更

非规范性内容（topics、guides、reference）的建议通过 Issue 提交即可 — 错别字修正、澄清、补充示例尤其受欢迎。维护者将实现被采纳的建议。

## 写作规范

### RFC 2119 关键词

撰写规范性内容时，请使用 [RFC 2119](https://tools.ietf.org/html/rfc2119) 定义的关键词：

- **MUST** / **MUST NOT** — 绝对要求
- **SHOULD** / **SHOULD NOT** — 强烈建议（允许有据可循的例外）
- **MAY** — 真正可选

这些关键词在规范意义上**必须**大写。

### 术语规范

- 使用 "AISP 技能"（不要用 "AISP agent" 或 "AISP application"）指代受治理的技能包
- 使用 "技能文件夹" 指代 `aisp/<id>_aisp/` 目录，"技能文件" 指代其 `aisp.aisop.json`
- 使用 "技能合同" 指代 `user.content.aisp_contract`
- "Axiom 0" 大写（专有名词）
- 写作 "Tier A"（执行）与 "Tier S"（合同）
- 绝不用 "Claude" 或 "Anthropic" 作为品牌；后缀始终是 `_aisp`

### 文档结构

- 每个主题文档以一段简介开头
- 字段规范用表格
- 示例代码块标注语言
- 流程与架构示意用 Mermaid 图
- 文档站内部用相对链接；仅仓库内提供的规范/schema 使用公开源文件 URL，避免 MkDocs 生成越出输入目录的坏链接
- 现有中英文配对文档的要求、命令、示例和限制须同步；不得把仅英文参考页说成已有译本
- 说明一条版本条件引导，而非多套引导类型；保留显式约束、安装同意、安装后复查及执行器中立性
- 分开静态/夹具通过、真实宿主结果及发布授权；不能为通过检查而删红线或隐藏运行期 warning

### 文档检查

运行/进化缓存、日志、私钥和本地凭据配置不应进入分发包。`.gitignore` 用于减少
误加入，不是访问控制、秘密扫描器，也不会移除已跟踪或历史数据。公开的
`.env.example` 例外只用于经过审查的占位模板。不得用全局忽略 JSON/Markdown、
夹具或证据目录来掩盖问题。

在满足 `setuptools>=84.1.0` 的隔离环境中构建；参考工具仍无运行时第三方依赖。
测试单独使用 `jsonschema>=4` extra；pytest 和 MkDocs Material 仍为另行安装的
可选工具。检查 wheel/sdist 内容，而不只检查工作目录。CI 固定经过核验的完整
Action SHA，使用只读 contents 权限并禁用凭据持久化；更新 SHA 须重新核对上游。
这些配置不证明远程 CI 或完整漏洞审计已经通过。

除隔离环境外，还须使用干净源码暂存目录：旧 `*.egg-info/SOURCES.txt` 可能重新将
文件带入 sdist。`MANIFEST.in` 排除选定私密模式，wheel 的包数据仍保持关闭。归档
回归在每次 wheel/sdist 构建前重新注入旧源文件清单，分别核对实际输入和私密残留
排除。选定公开数据对照文件保留在 sdist 中，不进入仅分发工具的 wheel；必要 Python
模块和许可证文件则在两种格式中逐字节与源码比较，不仅检查文件名是否存在。
保留不意味着工具分发包包含整个仓库。
CI 安装已声明的构建后端并设置
`AISP_REQUIRE_ARCHIVE_TEST=1`，缺少合格后端时失败，不允许跳过。本地发布封装也
要求实际运行该测试；后端不合格时失败，不会代为安装。普通本机未启用该配置且
后端缺失或过旧时，此项测试为 skip，而非通过；应使用
隔离测试环境，不自动修改全局软件包。

参考脚本直接从源码运行，无须安装本仓库。`[dev]` 元数据仅声明 jsonschema；当前
可选开发安装为 `python -m pip install -e ".[dev]"`；显式打包 `tools` 已避免平铺目录自动发现错误。源码脚本无须安装本仓库即可运行。
schema 测试单独安装 `jsonschema>=4`，使用 pytest 时也须另行安装它。构建文档站时，
在自行选择的环境中安装单独依赖：

```bash
python -m pip install mkdocs-material
```

在仓库根目录执行；输出目录须是仓外专用目录，不能含个人文件，MkDocs 会清理它：

```bash
python -B tools/check_doc_sync.py --root .
python -B tools/check_markdown_links.py --root .
python -B -m mkdocs build --strict --site-dir ../aisp-docs-site
```

这些检查不运行模型，也不授权发布。本地链接检查本身不检查 MkDocs 的 `docs/`
边界。完整 `release_check.ps1` 即使不加 `-RequireClean` 也会调用 Git；禁止 Git 时
不得运行该封装。

### 闭合签名

所有规范文档**必须**以下行结尾：

```
Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
```

## 行为准则

所有贡献者必须遵守 [行为准则](CODE_OF_CONDUCT.md)。Axiom 0 承诺适用于所有贡献。

## 贡献的许可

提交 Issue 或任何其他内容（包括规范建议、Issue 中的代码片段或设计建议）即表示您同意维护者可以在 [Apache License 2.0](LICENSE) 条款下使用您提交的内容，与本项目使用相同的许可证。

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
