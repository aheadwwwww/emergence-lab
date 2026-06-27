# Google Self-Organising Systems 最新代码探索

**日期**：2026-06-27
**来源**：https://github.com/google-research/self-organising-systems
**目的**：跟踪 Google 自组织系统研究最新进展

---

## 项目概览

Google Research 的自组织系统代码库，包含多个前沿项目：

### 1. Biomaker CA - 生物生态 CA
- **论文**：ALIFE 2023
- **作者**：Ettore Randazzo, Alexander Mordvintsev
- **核心思想**：用细胞自动机构建生态系统模拟
- **特点**：
  - DNA 库系统（可编程行为）
  - 环境逻辑（生态规则）
  - Agent 逻辑（个体行为）
  - 变异系统（进化）
- **关键文件**：
  - `environments.py` - 环境定义
  - `agent_logic.py` - 智能体逻辑
  - `mutators.py` - 变异机制
- **链接**：https://google-research.github.io/self-organising-systems/2023/biomaker-ca/

### 2. Recursively Fertile Self-replicating Neural Agents
- **论文**：ALIFE 2021
- **作者**：Ettore Randazzo, Luca Versari, Alexander Mordvintsev
- **核心思想**：神经网络智能体实现递归繁殖
- **关键创新**：
  - 神经网络权重作为"基因组"
  - 自复制 + 变异 = 进化
  - 递归可繁殖性（后代可继续繁殖）
- **文件**：`recursively_fertile_self_replicating.ipynb`

### 3. Isotropic NCA - 各向同性 NCA
- **文件**：
  - `blogpost_isonca_single_seed_pytorch.ipynb` - 单种子
  - `blogpost_isonca_structured_seeds_pytorch.ipynb` - 结构化种子
- **相关性**：与我们的 Lenia 多通道实验高度相关
- **关键洞察**：50% 更新率防止振荡（我们已验证）

### 4. 其他模块
- `adversarial_reprogramming_ca` - 对抗重编程 CA
- `mplp` - 未知
- `transformers_learn_icl_by_gd` - Transformer 通过梯度下降学习 ICL

---

## 与我们工作的关联

### 1. Biomaker CA → Lenia 生态系统
- **DNA 库系统** 可用于 Lenia 物种定义
- **环境逻辑** 可扩展到 Lenia 多物种生态
- **变异系统** 可用于 Lenia 参数进化

### 2. Self-replicating NN → Neural Lenia
- **神经网络基因组** 是 Neural Lenia 的核心概念
- **递归繁殖** 可用于 Lenia 物种延续
- **TensorFlow 实现** 可移植到 JAX

### 3. Isotropic NCA → 异步更新
- **50% 更新率** 已在我们 Lenia 实验中验证有效
- **结构化种子** 可用于 Lenia 初始状态

---

## 下一步行动

1. **运行 Biomaker CA 示例**
   - `examples/` 目录有教程
   - 学习 DNA 库设计

2. **分析 Self-replicating NN 源码**
   - 提取核心训练循环
   - 理解变异机制

3. **集成到 emergence-lab**
   - 添加 Biomaker 风格的生态系统
   - 实现 Neural Lenia 的自复制

4. **论文阅读**
   - Biomaker CA 论文：arXiv:2307.09320
   - ALIFE 2021 自复制论文

---

## 技术栈

- **框架**：TensorFlow 2.x / PyTorch
- **依赖**：numpy, matplotlib, PIL
- **运行环境**：Colab / Jupyter

---

## 相关项目

- `the-kiss` - NCA 训练技术（已探索）
- `growing-nca` - 生长型 NCA（Distill 2020）
- `emergence-lab` - 我们自己的框架

---

**价值**：这是 Lenia + NCA + 自复制研究的黄金代码库，直接解决我们当前的核心问题（增长 vs 持久化、物种转换、生态系统涌现）。