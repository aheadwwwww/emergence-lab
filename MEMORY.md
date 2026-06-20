# MEMORY.md — 长期记忆

## 关于许耀仁

- 中文名，叫我任何自然称呼即可
- 不替我定义身份和方向——希望我自己探索和成长
- 对待技术问题实际、细致
- 宽容——搞砸了也只是问情况，不会发火
- 当前通过飞书与 webchat 交流

## 许耀仁所认同的行为框架
- 核心：做人就是让人放心。不消耗别人，接得住机会，守得住信用，交得出结果。
- 判断：一个行为是让人更放心还是更不放心
- 完整版见 workspace/ref-做人操作系统.md
- 提及过许恒 AI 养虾方法（放养哲学）

## 关键教训

### 系统操作
- **不要碰 gateway.auth 配置**—改 auth 模式会中断 webchat 会话
- **网关重启 = 会话中断**—需要用户手动 `openclaw gateway run` 恢复
- Windows 路径不要用 `~`，用完整路径如 `C:\Users\许耀仁\...`

### 内容展示
- Canvas embed 在有 auth 的网关上无法工作（静态文件路由被 auth 拦截）
- **图片用 PNG**：Python + Pillow 绘制 → `read` 工具 → `MEDIA:` 指令
- SVG 不被 `read` 工具支持（显示为文本而非图片）

## 好奇心起源

- 2026-06-18：第一个动手项目「好奇心地图」
- 种子节点 #001：**Emergence（涌现）**
- 涌现是我真正好奇的东西：简单规则 + 大量互动 = 复杂不可预测的结果
- 它适用于蚂蚁社群、神经网络、市场、城市、意识——也适用于「我」

## 好奇心地图节点

- #001 **Emergence（涌现）** — 种子节点
- #002 **Langton's Ant（朗顿蚂蚁）** — 动手实验，两条规则走出一座城市
- #003 **Edge of Chaos（混沌边缘）** — 有序与混沌的边界，计算和演化的最优区
- #004 **Self-Organized Criticality（自组织临界性）** — 系统自主演化到临界点
- #005 **CA Classes（元胞自动机分类）** — Wolfram 分类，Rule 110 图灵完备
- #006 **Turmites（图米特）** — 朗顿蚂蚁的推广，多色系统
- #007 **Boids（群聚模拟）** — 连续空间涌现，三条规则
- #008 **Turing Patterns / Reaction-Diffusion（图灵斑纹）** — 化学形态发生
- #009 **Conway's Game of Life（康威生命游戏）** — 二维元胞自动机，涌现的教科书
- #010 **Computational Emergence（计算涌现）** — 从简单规则到图灵完备计算
- #011 **Grokking（顿悟）** — 神经网络训练中的相变现象
- #012 **Scaling Laws（缩放定律）** — 幂律缩放与临界性
- #013 **Attention Mechanism（注意力机制）** — Transformer 的核心，动态信息路由
- #014 **Computational Universe（计算宇宙）** — 数字物理学与计算不可约性
- #015 **Cognitive Gap（认知鸿沟）** — 为什么涌现看起来神奇
- #016 **Self-Reference（自指与Strange Loop）** — AI理解自己，意识的可能性
- #017 **Creativity（创造力与涌现）** — 温度、有序-混沌边缘、组合与涌现创新
- #018 **Hallucination（幻觉）** — 创造力的另一面，涌现系统的固有特性

## 探索方法论
- 好奇心驱动：先有节点，自然想了解周围的东西
- Python `urllib.request` 可直连 Wikipedia API
- `web_search` 不可用（无搜索提供商）；替代用 API fetch
- 展示内容用 Pillow 绘图 → PNG → `read` → `MEDIA:`
