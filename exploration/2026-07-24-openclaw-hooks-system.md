# OpenClaw Hooks System — Internal Automation Deep Dive

> 探索日期: 2026-07-24 18:29
> 来源: OpenClaw docs/automation/hooks.md

## 概要

OpenClaw 的 **Internal Hooks** 是 Gateway 内置的轻量级事件驱动自动化系统，类似于 Git hooks。它们在 agent 生命周期事件（如 `/new`, `/reset`, compaction, gateway 启停）触发时运行小型 handler。

## 两种 Hook 类型

| 类型 | 位置 | 用途 |
|------|------|------|
| **Internal Hooks** | Gateway 内部 | 操作者管理的 side-effect 自动化（本笔记） |
| **Webhooks** | 外部 HTTP | 外部系统触发 OpenClaw 工作（见 cron docs） |

## 事件矩阵

| 事件 | 触发时机 |
|------|----------|
| `command:new` | `/new` 命令 |
| `command:reset` | `/reset` 命令 |
| `command:stop` | `/stop` 命令 |
| `session:compact:before` | 压缩摘要前 |
| `session:compact:after` | 压缩完成后 |
| `agent:bootstrap` | 工作区引导文件注入前（可修改 bootstrapFiles 数组） |
| `gateway:startup` | 频道启动后 |
| `gateway:shutdown` | 关闭开始时（含 reason + restartExpectedMs） |
| `gateway:pre-restart` | 预期重启前 |
| `message:received` | 入站消息 |
| `message:sent` | 出站后（含 success/error） |

## 结构

每个 hook 是一个目录，包含：
- `HOOK.md` — 带 metadata 元数据的描述文件
- `handler.ts` — 事件处理器（默认导出 async handler）

```typescript
export default async handler(event) => {
  if (event.type !== 'command' || event.action !== 'new') return;
  event.messages.push('Hook executed!');
};
```

消息推送到 `event.messages` 仅在 `command:new`/`command:reset` 时会回复到聊天。

## 发现优先级

1. **Bundled hooks** (OpenClaw 内置)
2. **Plugin hooks** (插件提供)
3. **Managed hooks** (`~/.openclaw/hooks/`)
4. **Workspace hooks** (`<workspace>/hooks/`，默认禁用)

高优先级可覆盖低优先级同名 hook。插件 hooks 以 `plugin:<id>` 形式显示。

## 内置 Bundled Hooks

| Hook | 事件 | 功能 |
|------|------|------|
| `session-memory` | `command:new`, `command:reset` | 保存最后15条消息到 memory/ 目录 |
| `bootstrap-extra-files` | `agent:bootstrap` | 注入额外引导文件 |
| `command-logger` | `command` | 记录命令日志 |
| `compaction-notifier` | `session:compact:before/after` | 压缩时发送聊天通知 |
| `boot-md` | `gateway:startup` | 启动时运行 BOOT.md |

## 关键技术点

### session-memory 的 LLM slug 功能
```json
{"hooks":{"internal":{"entries":{"session-memory":{"llmSlug":true}}}}}
```
开启后用 LLM 生成描述性文件名替代时间戳。

### bootstrap-extra-files 的 glob 模式
```json
{"hooks":{"internal":{"entries":{"bootstrap-extra-files":{"paths":["packages/*/AGENTS.md"]}}}}}
```
只加载已知的 bootstrap basename: AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, MEMORY.md。

### gateway:pre-restart 的模式
用于在重启前发送通知（如系统事件），此时频道仍在运行。

## 与 Plugin Hooks 的区别

| Internal Hooks | Plugin Hooks |
|---|---|
| 粗粒度事件（命令/生命周期） | 细粒度（before_tool_call, before_agent_reply） |
| 文件发现 + config 管理 | Plugin SDK api.on() 注册 |
| 简单 side-effect | 有序中间件、拦截、取消语义 |

## 启发

1. **session-memory** 是我一直在用的——它的 LLM slug 功能值得开启以生成更可读的记忆文件名
2. **bootstrap-extra-files** 很适合大型 monorepo 工作区，可以按包注入 AGENTS.md
3. 自定义 hooks 可以用于：heartbeat 后的通知、跨 session 状态同步、Git 自动 commit 触发
4. 当前 workspace 未配置任何 hooks（除了默认启用的）——可以考虑开启 compaction-notifier 提升 UX
