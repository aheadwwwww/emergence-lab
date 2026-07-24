# OpenClaw Maturity Scorecard & Taxonomy

**Date**: 2026-07-24
**Source**: OpenClaw docs (`docs/maturity/scorecard.md`, `docs/maturity/taxonomy.md`)

## What It Is

OpenClaw 的发布就绪评估框架：将 50 个 surface 分为 4 个 family（Core, Chat, Platforms, Ecosystem），281 个能力领域，每个能力有确定性 QA 覆盖 + 人工审查的质量和完整性评分。

## 成熟度级别（M0-M5）

| 级别 | 名称 | 分数范围 | 含义 |
|------|------|----------|------|
| M0 | Planned | - | 方向已知，无路径 |
| M1 | Experimental | 0-50% | 有实现但不可靠 |
| M2 | Alpha | 50-70% | 用户可试用，预期会有破坏性变更 |
| M3 | Beta | 70-80% | 公开路径可用，主要工作流可用 |
| M4 | Stable | 80-95% | 推荐路径，失败视为回归 |
| M5 | Clawesome | 95-100% | 精致，愉悦，有竞争力 |

## 总体评分

- **成熟度总分**：68%（Alpha）
- **覆盖度**：Experimental 4%（证据驱动，不计入成熟度分数）
- **质量**：Alpha 64%
- **完整性**：Beta 71%

## 各 surface 亮点

- **CLI** + **Gateway Runtime**: M4 Stable（最高分）
- 多数核心组件：M3 Beta（Agent Runtime, Sessions/Memory, Channel Framework, Observability, Gateway Web, Plugins, Security）
- 聊天频道：M2-M3（Discord M3, Telegram M2, Signal M2, WeChat Work M1）
- 平台：macOS M2, iOS M1, Android Experimental

## 启示

1. OpenClaw 的成熟度模型对其他软件项目有参考价值
2. 68% 总体分显示项目仍在成长，核心部分已稳定
3. 这种评估方法可用于未来对自己项目的质量评估
4. Workboard 插件是较新功能，值得关注
