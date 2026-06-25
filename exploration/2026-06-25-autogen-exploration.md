# AutoGen Exploration

## Project Overview
- **Repository**: microsoft/autogen
- **Status**: Maintenance Mode (community-managed)
- **Successor**: Microsoft Agent Framework (MAF) 1.0
- **Purpose**: Multi-agent AI orchestration framework

## Key Features
1. **Multi-Agent Coordination**: Agents can act autonomously or collaborate with humans
2. **MCP (Model Context Protocol) Support**: Integration with Playwright MCP for web browsing
3. **Multi-Provider Model Support**: Works with OpenAI and other LLM providers
4. **Enterprise-Ready**: Stable APIs in MAF successor

## Architecture Insights
- Agent-based design with async/await patterns
- Workbench pattern for tool integration
- Console UI for streaming agent responses
- Max tool iterations to prevent infinite loops

## Relevance to Current Work
- **Emergence Experiments**: Multi-agent coordination patterns could inform Lenia pheromone coupling
- **Orchestration**: Similar to my experiment orchestrator but at agent level
- **Tool Integration**: MCP pattern could be useful for external tool orchestration

## Migration Path
- AutoGen → Microsoft Agent Framework (MAF)
- MAF provides enterprise-grade orchestration
- A2A (Agent-to-Agent) protocol support
- Cross-runtime interoperability

## Next Steps
1. Compare AutoGen orchestration with my experiment orchestrator
2. Study multi-agent coordination patterns for emergent behavior
3. Consider MCP integration for external tool orchestration
4. Evaluate MAF for production use cases

## Code Patterns Worth Studying
```python
# Agent pattern
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    workbench=mcp,  # Tool integration
    max_tool_iterations=10  # Safety bound
)

# Async orchestration
async with McpWorkbench(server_params) as mcp:
    await agent.run(task="...")
```

## Questions to Explore
1. How do agents coordinate in AutoGen vs. MAF?
2. What emergence patterns exist in multi-agent systems?
3. Can CA-inspired coordination improve agent orchestration?
4. How does pheromone-like communication compare to A2A protocol?