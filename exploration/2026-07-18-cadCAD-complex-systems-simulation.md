# cadCAD: Complex Adaptive Dynamics — Architecture Deep Dive

- **Repo**: cadCAD-org/cadCAD (PyPI: cadCAD)
- **Version**: 0.5.3
- **Stars**: 612 | **Forks**: 275
- **Domain**: Complex systems design, simulation, validation
- **Used by**: Token engineering, DAO design, mechanism design
- **Analyzed**: 2026-07-18 heartbeat (23:59)

## Why cadCAD Matters

cadCAD is the most mature Python framework for **parameterized complex systems simulation**. Unlike Lenia (emergent spatial dynamics) or Mesa (agent-based modeling), cadCAD excels at **mechanism design**: defining state variables, policies, and state update functions, then sweeping parameters across Monte Carlo runs.

Its design philosophy: **explicit mechanisms matter more than agent behavior**.

---

## Architecture

```
cadCAD/
├── configuration/     ← Experiment + Configuration classes
│   ├── __init__.py    (10.8k) — Configuration(), Experiment()
│   └── utils/         — Parameter sweep, PSUB triggers, depreciation
├── engine/
│   ├── __init__.py    (10.3k) — ExecutionContext, ExecutionMode
│   ├── simulation.py  (10.9k) — Executor (policy → state update loop)
│   └── execution.py   (4.9k)  — single/multi/local proc dispatch
├── tools/             — Reporting, visualization helpers
├── types.py           — TypedDicts: PolicyFunction, StateUpdateBlock, etc.
└── utils/             — flatten, key_filter
```

### Core Loop: Policy → State Update → Next Timestep

```
For each timestep T:
  For each mechanism (PSUB) in partial_state_update_blocks:
    1. Execute all policies → policy_input dict
    2. Apply aggregators → merged input
    3. Execute all state update functions → new state
    4. Append to state history (sL)
```

### Key Components

#### `Configuration` — One simulation run
```python
class Configuration:
    sim_config: {N (MC runs), T (timesteps), M (parameters)}
    initial_state: genesis state dict
    partial_state_update_blocks: [{policies, variables}] per substep
    env_processes: environmental processes (triggers)
    seeds: random seeds for reproducibility
```

#### `Experiment` — Composable experiment builder
```python
exp = Experiment()
exp.append_model(
    sim_configs=[{"N": 100, "T": range(50), "M": sweeps}],
    initial_state={"stability": 0.5, "agents": 10},
    partial_state_update_blocks=[
        {"policies": {"update_policy": f}, "states": {"x": state_update_fn}}
    ]
)
```

#### `Executor` — Policy/State function runner
```python
class Executor:
    def get_policy_input(...) → policy_input dict
    def run(...) → runs the PSUB loop
```

### Types (TypedDicts)

```python
PolicyFunction = Callable[[Parameters, Substep, StateHistory, State], PolicyOutput]
StateUpdateFunction = Callable[[Parameters, Substep, StateHistory, State, PolicyOutput], 
                               Tuple[str, StateVariable]]
StateUpdateBlock = TypedDict({policies: dict, variables: dict})
```

---

## Why This Architecture Works

### 1. **Policy/State Separation**
cadCAD cleanly separates *what should happen* (policies) from *how state changes* (state updates). This mirrors the RL "policy → environment" interaction and makes experiments composable.

### 2. **Parameter Sweep Built-In**
The `M` parameter in `sim_config` supports list-of-values, enabling automatic Cartesian product sweeps across parameters. Each combination gets its own simulation run.

### 3. **Monte Carlo by Default**
`N` controls how many runs per parameter set. cadCAD treats stochasticity as first-class, not an afterthought.

### 4. **PSUB Mechanism Blocks**
Each state update block groups related policies + state updates into a "mechanism." Models can have multiple mechanisms per timestep, each representing a different system process.

### 5. **Execution Mode Flexibility**
- `single_proc`: single config, single process
- `multi_proc`: multiple configs in parallel
- `local_proc`: local dispatch
- `distributed`: IPython parallel / Dask

---

## Comparison with Our Emergence Systems

| Feature | cadCAD | Lenia | emergence-lab |
|---------|--------|-------|---------------|
| Spatial | No (state vector) | Yes (continuous grid) | Yes (grid/world) |
| Time | Discrete timesteps | Continuous integration | Configurable |
| Policies | Explicit mechanism functions | Implicit (kernel rules) | Behavior functions |
| MC Runs | Built-in (`N`) | Manual | Manual |
| Parameter Sweep | First-class (`M`) | Manual scanning | Config-driven |
| Parallelism | Multi-proc built-in | JAX vectorization | JAX-based |
| Agent Modeling | Manual state management | Implicit (field-based) | Agent class |
| Validation | Statistical (MC) | Visual/structural | Metrics |

---

## What We Can Learn

1. **Explicit mechanism separation** — Our experiments would benefit from grouping policies + state updates into named "mechanisms" (like cadCAD's PSUB blocks) rather than monolithic simulation loops

2. **Parameter sweep as config** — cadCAD's `M` parameter approach is cleaner than our current manual scanning scripts. A config-driven sweep system would improve experiment reproducibility

3. **Monte Carlo by default** — Adding N-run averaging to our emergence experiments would make results more robust

4. **Env processes / triggers** — cadCAD's environmental process triggers (time-based events) could model our "resource pulses" in Lenia experiments more cleanly

5. **State history tracking** — The `sL` (state history list) approach is simpler and more accessible than our current structured storage

---

## Code Worth Stealing

### PSUB trigger pattern (for time-dependent state updates)
```python
def var_substep_trigger(timestep_range):
    def trigger(y, f):
        def wrapper(_g, step, sL, s, _input, **kwargs):
            if step in timestep_range:
                return y, f(_g, _input)
            return y, s[y]  # passthrough
        return wrapper
    return trigger
```

### Experiment append_model pattern (composable experiment builder)
```python
exp.append_model(
    sim_configs=config_sim({"N": 100, "T": range(50), "M": params}),
    initial_state=genesis_state,
    partial_state_update_blocks=psub_list(mechanisms, steps)
)
```

---

## Conclusion

cadCAD is a **validation-first complex systems framework** — it excels at answering "does this mechanism design produce the expected behavior under many parameter combinations?" Its strength is not emergence or spatial dynamics (where Lenia shines), but **explicit mechanism design with rigorous statistical validation**.

For emergence-lab, the most valuable pattern to adopt is the **config-driven parameter sweep + MC averaging** approach, which would make our experimental results more rigorous and reproducible.

## Links
- Website: https://www.cadcad.org
- Docs: https://github.com/cadCAD-org/cadCAD/blob/main/documentation
- Discord: https://discord.gg/DX9uH8m4qY
