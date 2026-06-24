# Exploration #025: FastAPI Dependency Injection Architecture

**Date**: 2026-06-24
**Source**: https://github.com/tiangolo/fastapi (cloned)

## Key Observations

### Architecture
- Built on Starlette + Pydantic
- DI system uses `Dependant` model objects to represent dependency trees
- `solve_dependencies()` recursively resolves the tree
- Supports both sync and async dependencies via `run_in_threadpool`

### Interesting Patterns
1. **Generator-based lifecycle**: Dependencies can be generators (yield for cleanup), managed via `AsyncExitStack`
2. **Sub-dependencies**: Dependencies can declare their own dependencies, forming a DAG
3. **Caching**: `DependencyCacheKey` for per-request caching of shared dependencies
4. **Security integration**: `SecurityScopes` are first-class dependency parameters

### Relevance to Our Work
- The dependency tree pattern could apply to our experiment orchestrator
- Instead of flat parameter lists, experiments could declare dependencies (data sources, models, visualizers)
- A `solve_dependencies()` equivalent could auto-resolve experiment prerequisites

### Code Snippet (conceptual)
```python
# FastAPI's approach to dependency resolution
class Dependant:
    dependencies: list[Dependant]  # sub-dependencies
    call: Callable
    path_params, query_params, body_params: list[ModelField]
    use_cache: bool
    cache_key: DependencyCacheKey
```

## Verdict
FastAPI's DI is a clean example of recursive dependency resolution with lifecycle management. Worth considering for the orchestrator v3 if we want experiments to declare their own prerequisites.
