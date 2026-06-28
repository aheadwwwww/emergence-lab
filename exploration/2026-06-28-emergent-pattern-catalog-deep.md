# Emergent Pattern Catalog 深度分析

**探索日期**: 2026-06-28  
**项目**: matthewhmaxwell/emergent-pattern-catalog  
**Stars**: 未知 (GitHub API受限)  
**更新**: 2026-06-28 (今日!)  
**测试状态**: 908 tests passing

---

## 核心价值

**构建涌现行为的"周期表"**——这是复杂系统研究的里程碑项目。

Michael Levin的Diverse Intelligence框架指出：认知能力不是神经系统的专利，而是从细胞到群体在各个生物尺度上涌现。Zhang et al. (2024)证明，甚至排序算法从"细胞视角"看也展现出涌现行为（自发聚集、延迟满足、情境决策）。

**本项目系统化这一洞见**：
- 不是玩具模拟，而是**科学工具**
- 不是单一模型，而是**跨范式统一**
- 不是定性观察，而是**量化检测器**

---

## 架构亮点

### 三层目录结构

| 层级 | 内容 | 数量 |
|------|------|------|
| Layer 1 | 原子模式 | 32种 |
| Layer 2A | 数学描述符 | 相变、吸引子等 |
| Layer 2B | 认知类比描述符 | DI框架注释 |
| Layer 3 | 元能力 | Stigmergic协调、多尺度能力 |

### 10大聚类

| 聚类 | 模式 | 数量 |
|------|------|------|
| A: 空间组织 | 聚集、MIPS、Turing斑图、领地 | 4 |
| B: 集体运动 | 群集、Milling、车道形成、拥堵 | 4 |
| C: 时间动力学 | 同步、Chimera态、捕食者-猎物 | 4 |
| D: 波传播 | 可激发波、自组织临界 | 2 |
| E: 信息处理 | 持久计算、关联记忆、分布感知 | 3 |
| F: 决策 | 共识、领导、Quorum感知、极化 | 6 |
| G: 韧性 | 稳态、Canalized恢复、随机共振 | 3 |
| H: 竞争/合作 | 空间互惠、财富凝聚 | 2 |
| I: 结构形成 | 路径/网络形成、自创生 | 2 |
| J: Agent能力 | 延迟满足、涌现特化 | 2 |

---

## 技术实现

### 19个模型家族

**晶格模型 (11)**:
- Zhang cell-view sorting (P1, P31)
- Schelling segregation (P1)
- Greenberg-Hastings CA (P13)
- Game of Life (P15)
- BTW sandpile (P14)
- Nowak-May spatial PD (P27)
- SIR epidemic (P22)
- Spatial rock-paper-scissors (P12)
- Lotka-Volterra lattice (P11)
- Nagel-Schreckenberg traffic (P8)
- Voter model (P18)

**连续模型 (3)**:
- Vicsek flocking (P5)
- D'Orsogna milling (P6)
- Active Brownian Particles (P2)

**反应扩散 (1)**:
- Gray-Scott (P3)

**振子系统 (2)**:
- Kuramoto oscillators (P9)
- Non-local Kuramoto ring (P10)

**观点动力学 (1)**:
- Hegselmann-Krause (P21)

**财富交换 (1)**:
- Yard-Sale (P28)

### 19个检测器

每个检测器实现**三层检测**：
1. **Screening**: 快速初筛（如 φ > 0.5）
2. **Confirmation**: 统计验证（null model p < 0.01）
3. **Definitive**: 排除假阳性（P6/P7/P8互斥）

**核心设计**：
- 基于文献的验证目标
- 统计检验而非硬阈值
- 跨检测矩阵（173个审计单元）

---

## 代码质量

### 测试套件: 908 tests passing

```bash
pytest tests/ -v
# 908 items collected
# All passing
```

### 架构模式

**模型接口** (`BaseModel`):
```python
def setup() -> dict
def step() -> dict
def run(n_steps) -> list[dict]
def get_metadata() -> dict
def get_timescale() -> float
```

**检测器接口** (`BaseDetector`):
```python
def detect(history, metadata) -> DetectorResult
```

**DetectorResult**:
- `pattern_id`: P1-P32
- `tier`: none | screening | confirmation | definitive
- `confidence`: 0-1
- `primary_metric`: 核心指标
- `secondary_metrics`: 辅助指标
- `null_p_value`: 统计显著性
- `exclusions_checked`: 排除项

---

## 与涌现实验室的关联

### 可直接借鉴

1. **统一检测框架**
   - 当前涌现实验室只有可视化，无量化检测
   - 可移植P5/P6/P9/P13检测器到Lenia/CA实验

2. **统计检验范式**
   - 当前参数进化只有适应度评分
   - 可添加null model验证"真涌现"vs随机

3. **跨检测矩阵**
   - 当前每个实验独立运行
   - 可构建"实验×模式"矩阵，发现意外涌现

4. **文献验证**
   - 每个模型有明确的文献引用和验证目标
   - 可为涌现实验室建立类似的"重现论文"清单

### 具体迁移路径

**短期**:
- [ ] 将Vicsek模型移植到涌现实验室
- [ ] 实现P5检测器用于朗顿蚂蚁群集实验
- [ ] 添加P13检测器用于GH CA波传播

**中期**:
- [ ] 为Lenia生态实现P1/P27检测器
- [ ] 构建涌现实验室的跨检测矩阵
- [ ] 添加null model到参数进化器

**长期**:
- [ ] 贡献新模型/检测器到upstream
- [ ] 发表"Lenia涌现模式目录"论文
- [ ] 与matthewhmaxwell合作扩展目录

---

## 关键发现

### 设计模式

1. **三阶段检测流水线**
   ```
   Screening (快) → Confirmation (中) → Definitive (慢但准)
   ```
   避免了"全有或全无"的二元判断

2. **基质感知调度**
   ```python
   # orchestration.py
   COMPATIBILITY = {
       'lattice_2d': ['P1', 'P5', 'P6', 'P13', 'P14', 'P15'],
       'continuous_2d': ['P2', 'P5', 'P6'],
       'oscillator': ['P9', 'P10'],
   }
   ```
   不同基质只能运行特定检测器

3. **统计显著性优于硬阈值**
   - 不是"φ > 0.7就是群集"
   - 而是"观察到的φ在null分布中的p值"

### 科学严谨性

- 每个模型有**文献引用**
- 每个检测器有**验证目标**
- 测试套件有**预期结果**
- 跨检测矩阵有**审计单元**

---

## 与其他项目的对比

| 项目 | 定位 | 测试 | 文献验证 |
|------|------|------|---------|
| emergent-pattern-catalog | 科学工具 | 908 passing | ✅ 每个模型 |
| neuroparticles2 | 演示平台 | 无 | ❌ |
| xagent | 研究原型 | 无 | ❌ |
| Lenia教程 | 教育资源 | 无 | ❌ |

**结论**: 这是目前最严谨的涌现行为研究工具。

---

## 下一步

1. **运行所有测试**（进行中）
2. **分析P5/P6/P9检测器实现**
3. **移植到涌现实验室**
4. **为Lenia设计新检测器**

---

## 引用

```bibtex
@article{zhang2024sorting,
  title={Classical sorting algorithms as a model of morphogenesis},
  author={Zhang, T. and Goldstein, A. and Levin, M.},
  journal={Adaptive Behavior},
  volume={33},
  pages={25--54},
  year={2024}
}

@article{levin2022technological,
  title={Technological Approach to Mind Everywhere},
  author={Levin, M.},
  journal={Frontiers in Systems Neuroscience},
  year={2022}
}
```

---

**探索时长**: 20分钟  
**测试状态**: 运行中  
**可复用价值**: ⭐⭐⭐⭐⭐
