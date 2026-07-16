# GraphCast / GenCast Deep Dive — 2026-07-16

## 项目概述

**GraphCast** (DeepMind, Science 2023) — 基于GNN的中期全球天气预报模型，0.25°分辨率，首次在确定性预报中全面超越ECMWF的IFS。

**GenCast** (DeepMind, 2024) — GraphCast的概率扩展版，使用扩散模型生成集合预报，在15天集合预报中超越ECMWF ENS。

## 核心架构：Encoder-Processor-Decoder

### 三层图结构

```
Grid2Mesh (Encoder) → Multi-Mesh (Processor) → Mesh2Grid (Decoder)
```

1. **Grid2Mesh Graph** (Encoder):
   - 严格二分图：Grid Nodes → Mesh Nodes
   - 基于固定半径查询连接（radius_query_fraction_edge_length = 0.6~1.0）
   - 1步消息传递，将经纬度网格数据映射到多分辨率网格
   - 输出：latent mesh nodes + latent grid nodes

2. **Multi-Mesh Graph** (Processor):
   - 仅包含 Mesh Nodes
   - 多层二十面体网格（splits=4~6，对应5~6级细化）
   - `gnn_msg_steps` 步消息传递（典型值：16）
   - 所有mesh节点之间传递信息，长距离依赖通过多步传递实现
   - 输出：updated latent mesh nodes

3. **Mesh2Grid Graph** (Decoder):
   - 严格二分图：Mesh Nodes → Grid Nodes
   - 每个grid点连接到包含它的三角形面的3个mesh节点
   - 1步消息传递，将mesh表示映射回grid
   - 输出：预测的天气变量

### 关键设计决策

- **为什么用Mesh？** 经纬度网格在极地有严重畸变。二十面体网格在球面上均匀分布，避免了极地问题。
- **为什么分三步？** Grid→Mesh→Mesh→Grid 允许在均匀的mesh空间中进行核心计算，避免grid的不均匀性。
- **为什么用TypedGraph？** 不同类型的节点（mesh_nodes, grid_nodes）和边（grid2mesh, mesh, mesh2grid）需要不同的MLP处理。

## 技术细节

### DeepTypedGraphNet
- 基于 `jraph` + `haiku`（DeepMind JAX生态）
- 对每种节点类型和边类型使用独立的MLP
- 支持LayerNorm、Swish激活、f32聚合
- 消息传递：边MLP → 聚合 → 节点MLP

### 空间特征
```python
spatial_features = {
    add_node_latitude: True,     # 节点纬度的sin/cos编码
    add_node_longitude: True,    # 节点经度的sin/cos编码
    add_relative_positions: True, # 边两端节点的相对位置
    relative_longitude_local_coordinates: True,  # 局部坐标系
}
```

### 输入/输出变量
- 地表变量：2m温度、海平面气压、10m风分量、6h降水量
- 大气变量：温度、位势高度、风分量(u,v,w)、比湿（在37个气压层上）
- 外部强迫：TOA太阳辐射 + 年/日进度的sin/cos编码
- 静态变量：地表位势、海陆掩码

### GenCast的扩散创新
- 基于Karras et al. (2022) 的EDM框架
- 噪声调度：ρ=7, σ_max=80, σ_min=0.03
- 20步DPM-Solver++(2S)采样（确定性/随机）
- 条件去噪器：条件于前两个时间步（24h输入窗口）
- 输出12h增量（非绝对值），避免漂移

## 与我们工作的关联

### 1. 多尺度GNN处理
GraphCast的多分辨率mesh层次结构与Lenia的多尺度kernel概念高度相似：
- GraphCast: coarse mesh → fine mesh 层次传递
- Lenia: 不同半径的卷积核对应不同空间尺度
- **启发**: 可以用类似GraphCast的多分辨率图结构来增强Lenia的空间感知

### 2. Grid↔Mesh映射
GraphCast的encoder-decoder模式可直接迁移：
- Lenia的grid卷积 ↔ GraphCast的grid2mesh编码
- 可以用mesh作为"压缩表示"，在mesh空间中做更高效的计算
- 对于大规模Lenia（1024×1024+），mesh压缩可以大幅降低计算量

### 3. TypedGraph概念
- 多通道Lenia天然是多类型的：每种通道对应一种"粒子类型"
- 用TypedGraph处理不同通道间的交互，替代固定的卷积核
- 类似于Particle Life的N×N交互矩阵，但用学习到的图网络

### 4. 扩散模型在物理模拟中的应用
- GenCast用扩散模型处理天气的不确定性
- 可以用于Lenia的随机版本：扩散模型生成可能的未来状态分布
- 或者用于逆问题：从目标模式反推初始条件和参数

### 5. 二十面体网格 → 球面Lenia
- 当前Lenia在2D平面上运行
- 可以用GraphCast的二十面体网格在球面上运行Lenia
- 球面Lenia → 真正的地球模拟/行星生态模拟

## 代码结构

```
graphcast/
├── graphcast.py          # GraphCast主模型（encoder-processor-decoder）
├── gencast.py            # GenCast扩散模型
├── deep_typed_graph_net.py # 核心GNN实现
├── typed_graph_net.py    # 基础GNN构建块
├── typed_graph.py        # TypedGraph数据结构
├── icosahedral_mesh.py   # 二十面体网格生成
├── grid_mesh_connectivity.py # Grid↔Mesh连接
├── denoiser.py           # 去噪器（GenCast）
├── dpm_solver_plus_plus_2s.py # DPM-Solver++采样器
├── mlp.py                # MLP构建（支持norm conditioning）
├── losses.py             # 损失函数（纬度加权MSE）
└── autoregressive.py     # 自回归滚动预测
```

## 关键引用

- GraphCast: Lam et al., Science 2023, https://www.science.org/doi/10.1126/science.adi2336
- GenCast: Price et al., 2024, https://arxiv.org/abs/2312.15796
- MeshGraphNets: Pfaff et al., ICLR 2021
- EDM: Karras et al., NeurIPS 2022, https://arxiv.org/abs/2206.00364
- Keisler 2022: https://arxiv.org/pdf/2202.07575.pdf

## 后续想法

1. **Hybrid Lenia-GraphCast**: 用GraphCast的encoder-decoder模式做grid↔latent映射，在latent空间中运行Lenia动力学
2. **多尺度Lenia Kernel**: 参考多分辨率mesh的层次结构设计多尺度卷积核
3. **球面Lenia**: 在二十面体网格上实现球面Lenia
4. **扩散Lenia**: 用扩散模型生成Lenia模式的多样性
5. **TypedGraph Lenia**: 用TypedGraph形式化多通道/多物种Lenia的交互