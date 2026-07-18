# Active Memory: OpenClaw Proactive Memory Recall Plugin

**Source**: OpenClaw docs (concepts/active-memory.md)
**Date**: 2026-07-19

## 核心发现

Active Memory 是一个可选内置插件，在 main agent 回复**之前**运行一个阻塞式 memory recall sub-agent，将相关记忆注入到会话中。

### 为什么需要它？

大多数记忆系统是**被动**的：main agent 必须决定搜索记忆，或者用户说"记住这个"。到那时，回忆的时机已经过了。Active memory 在生成回复之前给系统一次**有边界的**机会来浮现相关记忆。

### 工作原理

```
User Message → Build Memory Query → Blocking Sub-Agent → 找到相关记忆 → 注入隐藏 System Context → Main Reply
                                                         → 没找到 (NONE) → Main Reply（无额外上下文）
```

### 关键配置

- `queryMode`: `message` / `recent`（默认） / `full` — 多少对话上下文给 blocking sub-agent
- `promptStyle`: `balanced` / `strict` / `contextual` / `recall-heavy` / `precision-heavy` / `preference-only` — 控制回忆的激进程度
- `timeoutMs`: 默认 15000ms，blocking sub-agent 超时
- `agents`: 只对指定 agent 启用

### 适用场景

- 稳定的偏好、重复习惯、长期上下文应该自然浮现
- 不适合自动化、内部 worker、one-shot API 任务

### 与当前工作空间的关联

1. 工作空间使用了 `memory_search` + `memory_get` 这种常规记忆检索
2. Active memory 提供了一个更主动的模式：**无需 agent 主动决定搜索，插件自动做**
3. 心跳/后台运行默认**不会**触发 active memory
4. 如果要在非对话场景用类似模式，需要自行实现 blocking sub-agent

### 值得关注的其他特性

- `/active-memory status|on|off` 会话级开关
- 支持 `allowedChatIds` / `deniedChatIds` 精细控制
- 记忆结果以隐藏的 `<active_memory_plugin>` 块注入
