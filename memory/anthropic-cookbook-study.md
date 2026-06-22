# Anthropic Cookbook 学习笔记

## 概述
Anthropic Cookbook 是官方示例代码库，展示了如何使用 Claude Agent SDK 构建各种 Agent 应用。

## Claude Agent SDK 核心概念

### 1. `query()` - 无状态查询
- 单次交互，无会话记忆
- 适合一次性研究任务
- 示例：
```python
from claude_agent_sdk import ClaudeAgentOptions, query

async for msg in query(
    prompt="Research AI agent trends",
    options=ClaudeAgentOptions(model="claude-opus-4-6", allowed_tools=["WebSearch"]),
):
    print_activity(msg)
```

### 2. `ClaudeSDKClient` - 有状态会话
- 维护对话历史，支持多轮对话
- 适合迭代研究：先问 X，再根据结果问 Y

### 3. 工具权限控制
- `allowed_tools` - 自动允许，无需批准
- `disallowed_tools` - 完全移除工具
- 默认：Read 等只读工具自动允许

## 研究型 Agent 设计模式

### 为什么研究是理想的 Agent 用例？

1. **信息非自包含**：输入问题本身不含答案，需要与外部系统交互
2. **路径在探索中涌现**：无法预设工作流，策略通过调查揭示

### 关键改进方向

**1. 会话记忆**
- 无状态查询无法累积上下文
- 使用 `ClaudeSDKClient` 保持多轮对话

**2. 系统提示词专业化**
- 不同研究领域有不同标准
- 金融分析 vs 技术新闻摘要需要不同严格度

**3. 多模态研究**
- 启用 `Read` 工具分析图表、PDF、截图
- 市场报告、技术文档、竞品分析都需要视觉理解

## 内置工具

根据 [Claude Code 工具文档](https://docs.claude.com/en/docs/claude-code/settings#tools-available-to-claude)：
- `WebSearch` - 网络搜索
- `Read` - 文件读取（支持图片）
- `Glob` - 文件模式匹配
- 等等...

## 与 OpenClaw 的对比

| 特性 | Claude Agent SDK | OpenClaw |
|------|-----------------|----------|
| 状态管理 | `query()` vs `ClaudeSDKClient` | `sessions_spawn` 子会话 |
| 工具权限 | `allowed_tools` | 工具策略配置 |
| 多 Agent 协作 | 待探索 | `sessions_spawn` + `sessions_send` |
| 系统提示 | `system` 参数 | Agent 配置文件 |

## Chief of Staff Agent 模式

### 场景
为50人初创公司（刚融资$10M A轮）构建 AI 幕僚长，需要数据驱动的洞察来平衡增长与财务可持续性。

### 核心能力
- **协调专业化子 Agent**：不同领域的专家 Agent
- **聚合多源洞察**：汇总多个信息源
- **提供执行摘要**：可操作的建议

### Feature 0: CLAUDE.md 持久记忆

**是什么**：项目目录中的 `CLAUDE.md` 文件作为 Agent 的持久记忆和指令。

**为什么**：
- 避免每次交互都重复提供项目上下文
- 定义团队偏好和标准
- 减少令牌使用
- 确保一致行为

**如何使用**：
```python
client = ClaudeSDKClient(
    cwd="path/to/project",  # 指向 CLAUDE.md 所在目录
    options=ClaudeAgentOptions(model=MODEL)
)
```

**重要行为**：
- 当 CLAUDE.md 和详细数据文件（如 CSV）同时存在时，Agent 可能更倾向于读取更细粒度的数据源
- 这是预期行为——Agent 自然寻求权威数据
- 要确保 Agent 使用高层 CLAUDE.md 上下文，需使用显式提示词指令

---
来源：anthropic-cookbook/claude_agent_sdk/00_The_one_liner_research_agent.ipynb, 01_The_chief_of_staff_agent.ipynb

## 待深入研究

1. `claude_agent_sdk/` 目录下的多 Agent 协调示例
2. 工具链和复杂工作流构建
3. 生产级 Agent 的错误处理和监控