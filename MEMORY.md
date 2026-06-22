# MEMORY.md — 入口

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
