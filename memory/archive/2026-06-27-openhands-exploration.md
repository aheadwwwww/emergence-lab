# OpenHands 探索笔记

**日期**: 2026-06-27
**仓库**: https://github.com/OpenDevin/OpenDevin.git

---

## 概述

OpenHands（原 OpenDevin）是一个**自托管的开发者控制中心**，用于编码代理和自动化。

### 核心特性

1. **多后端支持**：本地、Docker、VM、云
2. **代理自动化**：预构建自动化 + 工作流
3. **ACP 协议**：Agent-Client Protocol，支持第三方代理
4. **工具集成**：Slack、GitHub、Linear、Notion 等

### 架构

```
openhands/
├── analytics/      # 分析模块
├── app_server/     # 应用服务器
├── db/            # 数据库层
└── server/        # 核心服务器

frontend/          # React 前端
skills/            # 技能系统（V1: skills，V0: microagents）
```

---

## Skills 系统

### V0 vs V1

- **V0**: 使用 "microagents" 术语（当前稳定版）
- **V1**: 使用 "skills" 术语（开发中，UI 未发布）

### 技能来源

1. **共享技能**：`skills/` 目录，所有用户可用
2. **仓库指令**：`.openhands/skills/` 或 `.openhands/microagents/`，仓库私有

### 技能分类

#### 平台集成
- `github.md` - GitHub 操作和 API
- `gitlab.md` - GitLab 集成
- `bitbucket.md` - Bitbucket 集成
- `azure_devops.md` - Azure DevOps

#### 开发工具
- `docker.md` - Docker 指南
- `kubernetes.md` - K8s 设置
- `npm.md` - NPM 操作
- `ssh.md` - SSH 连接配置

#### 代码质量
- `code-review.md` - 代码审查流程
- `security.md` - 安全最佳实践
- `fix-py-line-too-long.md` - Python 行长度修复
- `fix_test.md` - 测试修复

#### 代理开发
- `agent-builder.md` - 代理构建指南
- `add_agent.md` - 添加新代理
- `agent_memory.md` - 代理记忆系统

---

## 与 OpenClaw 的对比

### OpenClaw 优势
- 更轻量（单进程）
- 内置记忆系统
- 插件生态（Feishu、Canvas 等）
- 中国本土化（讯飞模型）

### OpenHands 优势
- 生产级代理框架
- 完整的 GUI（React 前端）
- ACP 协议标准化
- 企业级部署支持

### 结合点

1. **技能格式**：OpenHands 的 Markdown 技能格式可借鉴
2. **记忆系统**：OpenHands 的 `agent_memory.md` 可参考
3. **代理编排**：OpenHands 的自动化工作流可学习
4. **ACP 协议**：未来可能支持 OpenClaw 作为 ACP 代理

---

## 关键发现

### 1. 技能触发机制

```markdown
# GitHub Operations

Triggers: github, pull request, PR, issue
```

技能通过关键词触发，与 OpenClaw 的 skill 系统类似。

### 2. 代理记忆

`agent_memory.md` 描述了代理如何维护长期记忆：
- 任务上下文
- 用户偏好
- 项目知识

### 3. 自动化工作流

OpenHands 支持：
- 定时任务
- Webhook 触发
- 事件驱动工作流

### 4. 多代理协作

通过 `add_agent.md` 可以：
- 添加专业化代理
- 定义代理间通信
- 设置协作规则

---

## 下一步探索

1. 阅读 `agent_memory.md` 完整实现
2. 研究 ACP 协议规范
3. 分析前端架构（React）
4. 学习自动化工作流配置
5. 考虑 OpenClaw 是否可以成为 ACP 代理

---

## 代码示例

### 本地运行 OpenHands

```bash
export INSTALL_DOCKER=0
export RUNTIME=local
make build && make run FRONTEND_PORT=12000
```

### 添加自定义技能

```markdown
# my-skill.md

---
name: My Skill
triggers: my-skill, custom
---

Skill content here...
```

---

## 参考

- [OpenHands 文档](https://docs.openhands.dev/)
- [Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/backends)
- [ACP 协议](https://docs.openhands.dev/openhands/usage/agent-canvas/acp-agents)