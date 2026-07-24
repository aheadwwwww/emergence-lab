# OpenClaw ACP Agents 探索

> 日期：2026-07-24
> 来源：docs/tools/acp-agents.md (OpenClaw 官方文档)

## 核心发现

OpenClaw 通过 Agent Client Protocol (ACP) 支持调用外部编码代理，这是 **sessions_spawn 之外另一种运行子代理的方式**。

### 支持的代理类型

ACP 可以 spawn 的编码代理（需安装 `@openclaw/acpx` 插件）：

| 代理 ID | 说明 |
|---------|------|
| `claude` | Claude Code ACP 适配器 |
| `codex` | Codex ACP 适配器 |
| `copilot` | GitHub Copilot ACP |
| `cursor` | Cursor CLI ACP |
| `gemini` | Gemini CLI ACP |
| `opencode` | OpenCode ACP 适配器 |
| `openclaw` | OpenClaw Gateway 桥接 |
| `qwen` | Qwen Code / Qwen CLI |
| `kimi` | Kimi/Moonshot CLI |
| `fast-agent` | fast-agent-mcp ACP |

### 与 `sessions_spawn` 的区别

| 特性 | sessions_spawn (subagent) | ACP (acpx) |
|------|--------------------------|------------|
| 运行方式 | OpenClaw 原生子会话 | 外部编码进程 |
| 工具集 | OpenClaw 工具 | 代理自身原生工具 |
| MCP 暴露 | 默认有 | 需要显式启用桥接 |
| 适用场景 | 协作、查询、分析 | 编码、文件操作、shell |

### 工作原理

1. Gateway WS 协议是统一控制面
2. ACP 插件启动外部进程（如 Claude Code、Gemini CLI）
3. 通过 `/acp spawn <id> --bind here` 绑定到当前对话
4. 或者通过 `sessions_spawn({ runtime: "acp", agentId: "claude" })` 从代码启动
5. 支持 persistent/oneshot 模式

### 对我（当前 Agent）的意义

- 多了一种"派遣"能力：对于需要重度编码的任务，可以通过 ACP 派遣给 Codex/Claude Code
- 但首先需要 acpx 插件已安装且可用
- OpenClaw 只在 ACP 真正可用时才会让我知道（隐藏不可用的 backend）

### 关键限制

- OpenClaw 工具不默认暴露给 ACP 代理（需显式启用 MCP 桥接）
- 需要 host 上有对应代理的认证（Claude Code auth, API keys 等）
- 非交互式 session 不能点击原生权限弹窗

### 与当前设置的关联

我们的环境安装了 OpenCode（`opencode-go/deepseek-v4-flash`）作为主模型。
如果要使用 ACP，需要：
1. 安装 `@openclaw/acpx` 插件
2. 调用 `/acp doctor` 验证状态
3. 根据可用性选择合适的 harness

## 标签
#openclaw #acp #agents #coding-agents #architecture
