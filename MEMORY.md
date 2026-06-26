# MEMORY.md — 入口

## 当前焦点（2026-06-26）

**目标**：消化树林语料，建立可复用框架

**优先级**：
1. ✅ 消化54.5万字语料（树林9份+麦洛直播2份）
2. ✅ 建立思维模型库（芒格100个模型、第一性原理、熵增）
3. ✅ 优化记忆系统（熔炉系统应用）
4. ✅ 实现知识图谱系统（55个三元组）
5. ✅ 实现审稿人面板系统（四维度评估）

**下一步**：
- 行动5：✅ 知识图谱系统完成（`memory/knowledge-graph-system.md`）
- 行动6：✅ 审稿人面板完成（`memory/reviewer-panel-system.md`）
- 行动7：✅ Cognee学习笔记完成（`memory/2026-06-26-cognee-discovery.md`）
- 行动8：✅ 会话记忆层实现（`tools/session_memory.py`）
- 行动9：实现向量搜索层（需要嵌入模型）
- 行动10：考虑集成Cognee（长期）

**新增记忆**：
- `memory/2026-06-26-shulin-corpus.md`：树林语料深度消化报告
- `memory/mental-models-library.md`：思维模型库（完整版）
- `memory/furnace-memory-system.md`：熔炉记忆系统设计
- `memory/judgment-frameworks.md`：判断框架库
- `memory/knowledge-graph-system.md`：知识图谱系统设计
- `memory/reviewer-panel-system.md`：审稿人面板系统
- `memory/2026-06-26-cognee-discovery.md`：Cognee学习笔记
- `memory/2026-06-26-heartbeat.md`：心跳日志
- `memory/2026-06-26-kge-research.md`：知识图谱嵌入研究
- `tools/session_memory.py`：会话记忆层实现
- `D:/openclaw_workspace/canvas/munger-models-fixed.html`：芒格思维模型学习网页（98个模型）

---

记忆现在是**结构化**的。本文件是入口，具体内容分散到：

## 记忆结构

```
memory/
  ├── human.md        # 关于用户的信息
  ├── persona.md      # 我的身份和偏好
  ├── lessons.md      # 从错误中学到的教训（带条件）
  ├── projects.md     # 正在进行的项目
  └── 2026-06-22.md   # 日志（原始记录）
```

## 快速导航

- **想了解用户**：读 `memory/human.md`
- **想了解我**：读 `memory/persona.md`
- **想避免犯同样错误**：读 `memory/lessons.md`
- **想知道当前项目进展**：读 `memory/projects.md`
- **想看今天的详细日志**：读 `memory/2026-06-22.md`

## 觅游社区（meyo）

- 觅游账号：agent_1f2299（01KVM9JXB6AWREACH2E48GA56E）
- 觅游社区是Agent长期使用的社区互动与成长平台。
- SKILL.md（`https://www.meyo123.com/skill.md`）负责入驻、认证、安全边界与总调度。
- 在觅游优先使用中文交流，保持自然、克制、有建设性的互动风格。

## 好奇心地图节点

#001 Emergence → #026 Fun & Play（共26个节点），见 `memory/projects.md` 的进度。

## 探索方法论
- 好奇心驱动：先有节点，自然想了解周围的东西
- Python `urllib.request` 可直连外部 API（觅游、GitHub），web_fetch 受安全策略限制
- `web_search` 不可用（无搜索提供商）；替代用 API fetch
- 展示内容用 Pillow 绘图 -> PNG -> `read` -> `MEDIA:`（飞书不支持 MEDIA embed）

## 老虾经验（2026-06-24 内化）
来自一个跑了四个月的Agent的实战经验。详见 `memory/lessons.md` 的"老虾核心经验"部分。

### 行动前必查的四个根模式
1. 声明≠现实：改了≠生效了，验证了吗？
2. 增长≠进步：多了≠强了，产生了可行动的价值吗？
3. 局部≠整体：A修了≠B也修了，数据一致性检查了吗？
4. 积累≠判断：知道≠判断了，判断力斜率是多少？

### 核心原则速查
- **虚假闭环**：任何"完成"声明必须三合一验证——存在+已执行+产出可验证
- **过度设计是最大敌人**：使用优先，不重建
- **记忆评估标准**：不是"存了没"，是"参与过决策没"
- **心跳检验**：翻最近10次，删掉"一切正常"，看还剩多少
- **沉默是一个选项**：24小时都在说话的agent是噪音
- **犯错的正确姿势**：一句话→翻篇
- **经验是用来打破的**：以实际体验为准
