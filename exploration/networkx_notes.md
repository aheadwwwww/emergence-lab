# NetworkX - Graph Theory & Complex Networks

## Overview
NetworkX is a Python library for the creation, manipulation, and study of complex networks/graphs. Version 3.6.1 is installed locally.

## Why It Matters for Emergence Experiments
Complex systems are networks: interactions between agents, information flow between cells, causal relations between states. NetworkX provides the mathematical tools to analyze these structures.

## Core Concepts

### Graph Types
- **Graph**: undirected, no self-loops
- **DiGraph**: directed edges
- **MultiGraph/MultiDiGraph**: multiple edges between nodes

### Key Network Metrics

| Metric | What It Measures | Emergence Relevance |
|--------|-----------------|---------------------|
| Degree Centrality | Node importance by connections | Which cells/rules drive system behavior? |
| Clustering Coefficient | How clustered neighbors are | Does local order emerge? |
| Betweenness Centrality | Bridge nodes | Where does information bottleneck? |
| Small-Worldness | High clustering + short paths | Efficient information flow |
| Modularity | Community structure | Do functional groups emerge? |
| Assortativity | Similar-node connections | Homophily in the system |
| Rich-Club Coefficient | Hub-hub connections | Elite structure emergence |
| Graph Laplacian | Diffusion dynamics | How do patterns spread? |

### Small-World Networks (Watts-Strogatz)
- High clustering (like regular lattices)
- Short average path length (like random graphs)
- **Crucial insight**: Small changes to structure → massive changes in dynamics
- Surprising: just 1% random rewiring makes a lattice behave like a random graph globally

### Scale-Free Networks (Barabási-Albert)
- Power-law degree distribution: P(k) ~ k^(-γ)
- A few hubs carry most connections
- **Fragile to targeted attack, robust to random failure**

## Applications to Orchestrator Experiments

### 1. Biological Neural Networks in Boids
- Boids' interactions form a dynamic graph
- Network analysis can reveal leadership emergence
- Betweenness centrality identifies which agents control flock cohesion

### 2. Cellular Automata as Graphs
- Game of Life grid = regular lattice graph
- Clustering coefficient measures local pattern formation
- Entropy of degree distribution = complexity metric

### 3. Phase Transitions via Graph Metrics
- Ising model: graph connected components = magnetic domains
- Critical temperature = percolation threshold in the graph
- Cluster size distribution follows power law at criticality

### 4. Turing Patterns on Networks
- Reaction-diffusion on graphs (instead of grids)
- Network topology drastically changes pattern formation
- Small-world networks accelerate pattern emergence

## Key Code Patterns

```python
import networkx as nx

# Create a grid graph (like cellular automata)
G = nx.grid_2d_graph(100, 100)

# Add diagonal connections
G.add_edges_from([
    ((i, j), (i+1, j+1)) for i in range(99) for j in range(99)
])

# Analyze
clustering = nx.average_clustering(G)
path_length = nx.average_shortest_path_length(G)
communities = nx.community.louvain_communities(G)
```

## Connection to Existing Work

### Phase Transitions (Ising Model)
- Cluster size distribution at critical T → power law
- Can use NetworkX to extract and analyze magnetic domains
- Compare percolation threshold vs critical temperature

### Sandpile (SOC)
- Avalanche propagation = cascade on graph
- Betweenness centrality predicts which nodes trigger large avalanches
- Modular structure alters avalanche statistics

### Food for Thought
- **Emergence + Networks**: The orchestration of interactions IS the graph structure
- Could we evolve the graph topology AS the experiment parameter?
- "The network is the system" — Kevin Kelly

## References
- NetworkX docs: https://networkx.org/documentation/stable/
- Newman, "Networks: An Introduction" (2010)
- Watts & Strogatz, "Collective dynamics of small-world networks" (1998)
- Barabási & Albert, "Emergence of scaling in random networks" (1999)
