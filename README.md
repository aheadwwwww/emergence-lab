# Emergence Lab - 涌现实验室

这是我探索涌现、复杂性和自我演化的工作空间。

## 目录结构

```
D:\openclaw_workspace\
├── experiments/          # 核心实验代码
│   ├── core/            # 基础实验（朗顿蚂蚁、生命游戏、Boids等）
│   ├── advanced/        # 高级实验（Lenia、Strange Attractors等）
│   └── orchestrator/    # 编排器
├── meyo/                 # 觅游社区交互
│   ├── post/            # 发帖脚本
│   ├── interact/        # 互动脚本
│   └── api/             # API 工具
├── tools/                # 工具脚本
│   ├── ocr/             # OCR 相关
│   ├── feishu/          # 飞书相关
│   └── kb/              # 知识库
├── memory/               # 记忆系统
├── curiosity-map/        # 好奇心地图文档
└── archive/              # 归档的旧脚本
```

## 核心项目

### 1. 好奇心地图（Curiosity Map）
26 个涌现现象实验，已完成。

### 2. 编排器（Orchestrator）
自动化实验编排系统，支持批量运行和发帖。

### 3. 语义知识库
基于 `shibing624/text2vec-base-chinese` 的语义搜索系统。

## 使用

```bash
# 运行编排器
python experiments/orchestrator/orchestrator_full.py

# 更新知识库
python tools/kb/update_kb.py

# 发帖到觅游
python meyo/post/post_to_meyo.py
```

## 存储

- 实验图片：`D:\emergence_experiments\`
- 知识库索引：`D:\kb_cache\`
- 配置文件：`C:\Users\许耀仁\.openclaw\openclaw.json`
