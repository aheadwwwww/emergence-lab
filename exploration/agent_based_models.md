# Agent-Based Modeling Platforms & Libraries

## NetLogo - Classic ABM Platform

### Overview
NetLogo is the most widely used agent-based modeling platform, developed by Uri Wilensky at Northwestern. It's designed for education and research, with a simple but powerful language.

### Key Features
1. **Turtles** = agents (move on 2D grid)
2. **Patches** = grid cells (static, have state)
3. **Links** = connections between turtles
4. **Observer** = global controller

### NetLogo Models Library (600+ Models!)
**Biology**:
- Ants (foraging behavior)
- Termites (wood chip gathering)
- Flocking (boids)
- Wolf Sheep Predation
- Disease models

**Physics**:
- Ising Model
- Sandpile (SOC)
- Percolation
- Diffusion

**Social Science**:
- Segregation (Schelling model)
- Prisoner's Dilemma
- Traffic Basic
- El Farol Bar

### Connection to Orchestrator
Many of our experiments are ALREADY in NetLogo:
- Langton's Ant → "Ants" model
- Game of Life → "Life" model
- Boids → "Flocking" model
- Ising Model → "Ising" model
- Sandpile → "Sandpile" model

**Insight**: NetLogo is a goldmine of validated models and parameter ranges!

### Python Integration: PyNetLogo
```python
import pyNetLogo
netlogo = pyNetLogo.NetLogoLink()
netlogo.load_model('models/Sample Models/Biology/Ants.nlogo')
netlogo.command('setup')
for _ in range(100):
    netlogo.command('go')
ants = netlogo.report('count turtles')
```

## Mesa - Python ABM Framework

### Overview
Mesa is a modern Python framework for agent-based modeling, inspired by NetLogo but in pure Python.

### Key Features
```python
from mesa import Model, Agent
from mesa.space import Grid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

class MyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1
    
    def step(self):
        if self.wealth > 0:
            other = self.random.choice(self.model.schedule.agents)
            other.wealth += 1
            self.wealth -= 1

class MyModel(Model):
    def __init__(self, N, width, height):
        self.schedule = RandomActivation(self)
        self.grid = Grid(width, height, torus=True)
        for i in range(N):
            agent = MyAgent(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))
    
    def step(self):
        self.schedule.step()
```

### Mesa + Our Experiments
**Perfect fit for orchestrator!**
- Langton's Ant → Mesa Grid + Agent
- Boids → Mesa ContinuousSpace + Agent
- Game of Life → Mesa Grid (cells as agents?)
- Sandpile → Mesa Grid with threshold rule

**Advantages**:
- Native Python (no Java dependency)
- Easy integration with NumPy/Matplotlib
- Built-in data collection
- Batchrunner for parameter sweeps

### Mesa Extensions
- **Mesa-Geo**: Spatial ABMs with GIS
- **Mesa-Viz**: Interactive browser visualization
- **Mesa-Recursion**: Recursive models

## Other ABM Platforms

### 1. Repast (Java/C++)
- High-performance ABM
- Used in large-scale social simulations
- Steep learning curve

### 2. MASON (Java)
- Fast, flexible
- Good for multi-agent systems
- Used in robotics, AI research

### 3. GAMA (Java)
- Spatially explicit models
- GIS integration
- Used in environmental modeling

### 4. AgentScript (JavaScript)
- Browser-based ABM
- NetLogo-like syntax
- Good for web demos

## ABM Design Patterns for Emergence

### Pattern 1: Simple Rules, Complex Behavior
```python
# Boids: 3 simple rules → flocking
def step(self):
    separation = self.avoid_crowding(neighbors)
    alignment = self.match_velocity(neighbors)
    cohesion = self.move_to_center(neighbors)
    self.velocity += separation + alignment + cohesion
```

### Pattern 2: Threshold Dynamics
```python
# Sandpile: threshold → avalanches
def step(self):
    if self.grains >= 4:
        self.grains -= 4
        for neighbor in self.neighbors:
            neighbor.grains += 1
```

### Pattern 3: State Machines
```python
# Ants: state transitions
def step(self):
    if self.state == 'searching' and self.found_food():
        self.state = 'carrying'
    elif self.state == 'carrying' and self.at_nest():
        self.state = 'searching'
```

### Pattern 4: Evolutionary Selection
```python
# Genetic agents
def step(self):
    if self.fitness > threshold:
        self.reproduce()
    else:
        self.die()
```

## ABM Resources

### Books
- "Agent-Based and Individual-Based Modeling" by Railsback & Grimm
- "Growing Artificial Societies" by Epstein & Axtell
- "Patterns of Emergence" (various authors)

### Papers
- Wilensky, U. (1999). "NetLogo" (and 600+ models!)
- Grimm, V. (2006). "A standard protocol for describing IBMs" (ODD protocol)
- Sayama, H. (2015). "Introduction to the Modeling and Analysis of Complex Systems"

### Online
- NetLogo Models Library: https://ccl.northwestern.edu/netlogo/models/
- Mesa Examples: https://mesa.readthedocs.io/en/stable/examples.html
- Complexity Explorer: https://www.complexityexplorer.org/

## Integration Plan

### Phase 1: Study NetLogo Models
1. Browse models library for interesting patterns
2. Identify parameter ranges from validated models
3. Port successful models to Python

### Phase 2: Integrate Mesa
1. Refactor existing experiments to Mesa framework
2. Use Mesa's DataCollector for metrics
3. Use BatchRunner for parameter evolution

### Phase 3: Novel ABMs
1. Design new agent-based experiments
2. Combine multiple ABM patterns
3. Explore multi-scale ABMs (agents of agents)

## Code: Port NetLogo Ants to Mesa

```python
# Inspired by NetLogo Ants model
from mesa import Model, Agent
from mesa.space import Grid
from mesa.time import RandomActivation
import numpy as np

class Ant(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carrying = False
        self.direction = np.random.randint(0, 8)
    
    def step(self):
        # Follow pheromone gradient
        if self.carrying:
            # Return to nest
            nest_dir = self.towards_nest()
            self.move(nest_dir)
            self.deposit_pheromone()
        else:
            # Search for food
            if self.sniff_pheromone():
                self.move_towards_pheromone()
            else:
                self.random_walk()
            if self.at_food_source():
                self.pick_up_food()
    
    # ... movement logic ...

class AntColonyModel(Model):
    def __init__(self, n_ants, width, height):
        super().__init__()
        self.grid = Grid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.pheromone_grid = np.zeros((width, height))
        
        # Create ants
        for i in range(n_ants):
            ant = Ant(i, self)
            self.schedule.add(ant)
            # Place at nest
            self.grid.place_agent(ant, self.nest_pos)
```

## Theoretical Question

**Can we discover NEW emergent phenomena by:**
1. Randomly combining ABM design patterns?
2. Evolving agent rules with genetic algorithms?
3. Hybrid models (continuous + discrete)?

**Next Steps**:
1. Explore NetLogo models for inspiration
2. Implement Mesa-based experiments
3. Add emergence metrics to ABM framework
4. Create "ABM playground" for rapid prototyping