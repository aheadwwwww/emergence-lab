# AgentSilex: Transparent Minimal Agent Framework — Deep Dive

- **Repo**: agentsilex/agentsilex (PyPI: agentsilex)
- **Version**: v1.0.0 (latest)
- **License**: MIT
- **Core**: ~300 lines agent framework on LiteLLM
- **Analyzed**: 2026-07-18 heartbeat

## Why AgentSilex Matters

After HippoRAG 2 (memory augmentation), AgentSilex offers the opposite pole: **transparent action**. A framework so small you can read the entire source in one sitting. Its philosophy aligns with OpenClaw's minimalism — tooling that doesn't get in the way.

---

## Architecture Overview

```
AgentSilex
├── Agent              — 代理配置 (name, model, instructions, tools, handoffs)
├── Runner             — 执行引擎 (run/run_stream, tool dispatch, handoff routing)
├── Session            — 对话历史管理 (messages list)
├── FunctionTool       — 函数解析/JSON schema 生成
├── Handoff            — 代理间切换 (transfer_to_ prefix)
├── stream_event       — 流式事件类型系统
├── observability      — OpenTelemetry 追踪
├── MCP                — Model Context Protocol 支持
└── evaluation         — LLM Judge / ResponseMatch / ToolTrajectory 评估
```

### 核心模式: Agent + Runner + Session

```
用户 → Runner.run(agent, prompt)
         ↓
     Session.add(用户消息)
         ↓
     [循环] LLM.completion(model, tools_spec, system_instructions)
         ↓
         ├── 无 tool_calls → 返回 FinalOutput
         ├── 有 Function Tool → execute → 继续循环
         └── 有 Handoff (transfer_to_*) → 切换 agent → 继续循环
         ↓
     Max 10 次循环 → 强制停止
```

### 三个核心类分析

#### Agent

```python
class Agent:
    def __init__(self, name, model, instructions, tools, handoffs, output_type):
        self.tools_set = ToolsSet(tools)      # 函数工具注册器
        self.handoffs = AgentHandoffs(handoffs) # 代理交接注册器
```

- **极简设计**：只有必要字段，无状态，可复用
- **as_tool()**: 将整个 agent 作为另一个 agent 的工具（嵌套调用）

#### Runner

```python
class Runner:
    def __init__(self, session, context, before_llm_call_callbacks):
        self.context = context  # 工具共享上下文 (dict)
```

**关键特性**：
- **Context Injection**: 工具函数如果有 `context` 参数，自动注入 Runner 的共享上下文
- **Callback 链**: `before_llm_call_callbacks` 在每次 LLM 调用前触发（用于改写 session）
- **Handoff 优先**: 先处理所有 function call，最后再处理 handoff（最多1个）
- **10 次循环硬限制**: 防止无限循环
- **`run_stream()`**: Generator-based 流式输出，事件驱动

#### Session

```python
class Session:
    def __init__(self):
        self.dialogs = []  # 纯消息列表
```

**极简但够用**：不负责 token 管理、压缩、摘要 — 这些都是上层应用的责任。

---

## 亮点设计

### 1. Handoff 系统（transfer_to_*）

通过工具前缀 `transfer_to_` 实现代理切换。核心机制：

```python
HANDOFF_TOOL_PREFIX = "transfer_to_"

class Handoff:
    @property
    def name(self):
        return f"transfer_to_{agent.name}"
    
    @property
    def description(self):
        return f"Handoff to the {agent.name} agent to handle the request. {agent.instructions}"
```

**Handoff 作为工具**：让 LLM 决定何时切换代理。这意味着：
- 不需要硬编码的编排逻辑
- LLM 根据上下文自主决策
- 移交后历史保留（所有消息在同一条 timeline 上）

对比 OpenAI Swarm：设计理念一致，但 AgentSilex 更简洁（~300行 vs ~2000行）

### 2. as_tool() — Agent 嵌套

```python
# agent A 把 agent B 当作工具使用
agent_b = Agent(name="WeatherBot", ...)
agent_a = Agent(
    name="MainAgent",
    tools=[agent_b.as_tool("weather_bot", "Get weather"), ...]
)
```

不同于 Handoff（切换控制权），as_tool 是**工具调用模式**：agent A 调用 agent B，B 返回结果给 A。

### 3. MCP 支持

```python
# mcp.py: Model Context Protocol
class MCPFunctionTool:
    def __init__(self, server_params):
        # 连接到 MCP 服务器
        # 自动发现可用的工具
```

MCP 基础设施意味着 AgentSilex 可以外接任何 MCP 兼容的服务器。

### 4. Evaluation 模块

```python
# LLM Judge: 用 LLM 打分
# ResponseMatch: 精确匹配输出
# ToolTrajectory: 评估工具调用路径
```

虽然简单，但提供了基本的 eval 框架。

---

## 对比 OpenClaw

| 特性 | AgentSilex | OpenClaw |
|------|-----------|----------|
| 核心代码量 | ~300 (agent+runner+session) | ~40k+ lines (Gateway + runtime) |
| LLM 支持 | LiteLLM (100+ providers) | 原生 provider 支持 |
| Session 管理 | 纯消息列表 | 结构化 + 持久化 + 上下文管理 |
| Tool 系统 | `@tool` decorator + JSON schema | 结构化 Tool 类 + 权限/沙箱 |
| Handoff | 基于工具前缀 | Agent spawn/send |
| 流式输出 | Generator[Event] | 原生 streaming |
| 追踪 | OpenTelemetry | 内置 observability |
| 评估 | 内置 LLM Judge | — 尚未完善 |
| 上下文注入 | `context` 参数 | 通过 Tool 参数 |
| 部署 | pip install | clone + npm install + gateway |

### AgentSilex 的可学习设计

1. **ToolsSet.registry**: name → FunctionTool 的字典映射 + JSON schema 生成，简单优雅
2. **Handoff 作为工具**: 让 LLM 自主决策切换代理，避免硬编码编排
3. **before_llm_call_callbacks**: 在每次 LLM 调用前给 session 注入上下文（比如插入系统消息、修改历史）
4. **callback 注入模式**: Runner 提供 callback points，用户可以插入自己的逻辑而不修改框架代码
5. **context dict 共享**: 工具之间可以通过 Runner.context 共享状态（状态在工具链中传递）

---

## 最值得注意的代码模式

### Tool Function Schema 自动生成

```python
# extract_function_schema.py 核心逻辑
@tool
def get_weather(city: str) -> str:
    """Get weather"""
    return "SUNNY"
    
# 自动变成:
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": ""}
            },
            "required": ["city"]
        }
    }
}
```

### Context injection 检测

```python
def has_context_param(func):
    sig = inspect.signature(func)
    return "context" in sig.parameters
```

极简的设计：如果有 `context` 参数，就自动注入。没有任何复杂配置。

---

## 结论

AgentSilex 是**最小可行 agent 框架**的最佳实践：
- 可在一小时内通读并完全理解
- 可自由修改和扩展
- 可立即用于生产（测试完善，PyPI 发布）
- 可作为定制化 agent 系统的启动模板

对 OpenClaw 的启示：
1. **Handoff-as-tool** 模式可借鉴到 OpenClaw agent spawn
2. **context dict 注入** 比参数传递更灵活
3. **callback chain** 模式增强了可扩展性
4. **Tool schema 自动生成 + LiteLLM** 降低了 provider 适配成本

同时，OpenClaw 在 session 持久化、结构化上下文、工具沙箱和部署模型上有显著优势 — 两者处于不同的抽象层次，AgentSilex 是 lib，OpenClaw 是 platform。
