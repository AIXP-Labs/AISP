# 如何贡献 AISP

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
- 规范变更请使用 `spec-change` issue 模板
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
- 文档之间用相对链接互相引用

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
