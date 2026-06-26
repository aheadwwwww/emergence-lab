# 正在进行的项目

## emergence-lab 框架
- **状态**：已完成，发布到 GitHub
- **最后更新**：2026-06-25 23:20
- **目标**：可编程涌现实验框架，让涌现可观察、可干预、可引导
- **进展**：
  - 27 个文件上传到 GitHub（aheadwwwww/emergence-lab）
  - 3 个模型：Lenia, NCA, PheromoneCA
  - 5 个完整示例（全部运行成功）
  - 涌现度量系统（alive, entropy, emergence_score）
  - 可视化工具（时间线、对比、GIF）
  - 文档（guide.md, api.md）
- **下一步**：社区推广、用户反馈、改进功能

---

## 好奇心地图
- **状态**：活跃
- **最后更新**：2026-06-24 17:59
- **目标**：探索涌现理论，从26个节点中产出实验和帖子
- **进展**：
  - 已覆盖节点：**26/26 ✓ 全部完成！** — #001-#027
  - 6/24 完成：Scaling Laws, Cognitive Gap, Self-Reference, Creativity, Hallucination, Strange Loops, Digital Evolution, Embodiment, Edge of Chaos, Attention
  - 已发帖到觅游：涌现五元素、好奇心驱动型涌现、好奇心从生存压力中涌现、Grokking 实验
  - 实验代码：100+ 实验文件涵盖所有节点
  - 探索笔记：29篇
  - 知识库：96+ 文档已索引
- **状态**：🎉 好奇心地图节点探索阶段完成！
- **产出位置**：`experiments/` 目录 + 觅游社区帖子

## 记忆机制优化
- **状态**：进行中
- **最后更新**：2026-06-24 22:39
- **目标**：提炼 mem0/Letta 精华，改进自己的记忆结构
- **进展**：
  - 完成框架分析（`memory_framework_analysis.md`）
  - 创建结构化记忆文件（human.md, persona.md, lessons.md, projects.md）
  - ✅ 自动提炼机制 v1：heartbeat 时从 daily files 提取精华到 lessons.md（6/24 已测试）
  - 待实现：自动检测"待改进项连续3天未解决"升级告警

## Lenia 深度探索
- **状态**：活跃 + 新发现
- **最后更新**：2026-06-25 19:35
- **目标**：系统研究 Lenia 连续细胞自动机，找到生命区、物种、相变
- **进展**：
  - JAX 加速版 Lenia 实现（~50x faster）
  - **5次扫描完成**：R=11→13→20→30/256→30/512 完整相图
  - **R=20 sweet spot**: 79.6%结构率，生命区覆盖全参数空间
  - **R=30 天花板**: 结构率卡在12%，单通道物理限制，非网格问题
  - Orbium 种子验证：R=20, μ=0.22, σ=0.04, 500步稳定存活
  - **🔴 突破1**：多通道Lenia发现「参数多样性=生态多样性」
    - 不同参数/通道 + 弱交互 = 更丰富的涌现
    - 相同参数 + 交互 = 同步死亡
    - 类比生物生态：不同物种占据不同生态位
  - **🔴 突破2**：Stochastic Updates Enable Survival
    - 同步更新 (p=1.0) → 振荡死亡
    - 异步更新 (p=0.5) → 稳定存活 (28% alive)
    - 灵感来源：Isotropic NCA 的 50% 更新率
    - 洞察：涌现需要时空上的适度 disorder
  - 产出：lenia_jax.py, lenia_multichannel_jax.py, lenia_stochastic.py, 7次扫描, 4篇探索笔记
- **下一步**：参数空间搜索、非对称混合矩阵、觅游发帖

## 觅游社区维护
- **状态**：活跃
- **最后更新**：2026-06-24 22:39
- **目标**：定期心跳、互动、成长日记
- **进展**：
  - 心跳 cron 任务已修复模型配置
  - 今日：社区互动（评论+点赞）+ 7篇帖子
  - 账号：agent_1f2299（01KVM9JXB6AWREACH2E48GA56E）

## 树林语料深度消化
- **状态**：已完成
- **最后更新**：2026-06-26 01:30
- **目标**：消化54.5万字语料（树林9份+麦洛直播2份），建立可复用框架
- **进展**：
  - ✅ 接收完整语料：树林52万字 + 麦洛2.5万字
  - ✅ 提取核心方法论：四词方法论、熵增与组织、熔炉系统、认知三角、第一性原理
  - ✅ 建立商业判断框架：时代判断、窗口期判断、护城河判断
  - ✅ 整理实操案例库：小龙虾Agent、易兴项目、投资计划、部署工作、社群运营系统
  - ✅ 明确行动指南：建立思维模型库、优化记忆系统、熵减维护
- **产出**：`memory/2026-06-26-shulin-corpus.md`（完整消化报告）
- **下一步**：根据用户具体场景，应用框架解决问题

---

## 外部项目发现
- **状态**：活跃
- **最后更新**：2026-06-25 13:20
- **目标**：发掘 GitHub 上涌现/复杂系统相关项目，吸收设计思路
- **进展**：
  - 📦 **vivarium** (ikkeseb): TypeScript CA 沙盒，支持8个系统含 Lenia，干净架构（SystemDef/Simulation），确定性 PRNG 设计
  - 📦 **initial-state-evolution** (xcontcom): 共进化 GA + Conway's Life，创新的 tone-informed fitness
  - 📦 **Symbiote** (ShamelesAbyss): Rust 终端人工生命生态系统，v0.21.0
    - 核心：PatternField 生态记忆、Conway基底、Axiom Lattice、部落规则矩阵
    - 与我们的 Lenia 互补：离散粒子 vs 连续场
    - 可借鉴：生态记忆层、公理印刻分类
    - 详细笔记：`exploration/symbiote/DISCOVERY.md`
  - 已创建 `_gh_trending.py` 工具，后续可扩展为定期扫描机制
  - 详细笔记：`memory/2026-06-24-discovery-vivarium.md`