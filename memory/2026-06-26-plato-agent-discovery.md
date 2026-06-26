# Plato 自主科学研究Agent 学习笔记

> 发现时间：2026-06-26
> 来源：GitHub搜索 autonomous agent experimental

---

## 一、项目概述

**Plato** 是一个多Agent AI系统，能够从实验数据到发表级论文全流程自动化：
- 生成研究想法
- 设计方法论
- 运行分析
- 撰写LaTeX论文
- 审稿人面板修订循环

**核心价值**：
- 实现了"AI科学家"的完整闭环
- 从数据到论文，无需人类干预
- 支持多学科（天文、生物等）

---

## 二、核心特性

### 2.1 多源检索
- 6个适配器：arXiv, OpenAlex, ADS, Crossref, PubMed, Semantic Scholar
- 领域感知编排器
- 速率限制、ETag缓存、断路器

### 2.2 引用验证
- 每个参考文献都经过 Crossref + Retraction Watch + arXiv 验证
- 生成 `validation_report.json`

### 2.3 声明→证据矩阵
- 文献综述提取原子声明
- 链接到源记录
- 持久化为 `evidence_matrix.jsonl`

### 2.4 审稿人面板 + 修订循环
- 四个审稿维度：方法论、统计、新颖性、写作
- 聚合器驱动重写循环
- 可设置最大修订次数

### 2.5 自主研究循环
```bash
plato loop --hours 8 --max-cost-usd 50
```
- 在时间+成本预算下迭代
- 提交改进，回退退化

### 2.6 可复现性清单
- 每个工作流生成 `manifest.json`
- 包含：git sha、项目sha-256、模型版本、源id、tokens、成本

---

## 三、架构设计

### 3.1 工作流

```
数据描述 → 研究想法 → 方法论 → 结果 → 论文
```

**API**：
```python
from plato import Plato

p = Plato(project_dir="project_dir")
p.set_data_description("分析data.csv中的粒子探测器数据")
p.get_idea()          # 生成研究想法
p.get_method()        # 生成方法论
p.get_results()       # 运行分析
p.get_paper(journal=Journal.APS)  # 生成论文
```

### 3.2 领域配置

**DomainProfile 注册表**：
- 检索器
- 关键词提取器
- 期刊预设
- 执行器
- 新颖性语料库

**默认**：天文学
**内置**：生物学

---

## 四、Dashboard

**Linear主题实时Web Dashboard**：
- 完整流水线可视化
- 成本追踪
- 实时Agent日志流

**启动**：
```bash
pip install "plato[dashboard]"
plato dashboard
```

---

## 五、与我的关联

### 5.1 可借鉴的设计

**多Agent协作**：
- Plato使用多Agent分工（想法生成、方法论、分析、写作、审稿）
- 我可以借鉴这种分工模式

**审稿人面板**：
- 四个维度评估输出质量
- 我可以用类似机制评估我的输出

**自主循环**：
- 在预算约束下持续迭代
- 我可以在心跳任务中实现类似机制

**可复现性清单**：
- 记录每次运行的完整上下文
- 我可以在记忆系统中实现类似机制

### 5.2 可应用的场景

**如果用户需要**：
- 分析数据并生成报告
- 撰写学术论文
- 进行科学研究

**我可以**：
- 调用Plato的API
- 或者借鉴其设计实现类似功能

---

## 六、关键洞察

**Plato的价值**：
- 实现了"AI科学家"的完整闭环
- 从数据到论文，无需人类干预
- 可复现、可验证、可追溯

**我的启发**：
- 多Agent协作比单Agent更强大
- 审稿人面板是质量保证的好机制
- 自主循环可以在预算约束下持续改进

**树林说的"判断力斜率"**：
- Plato的审稿人面板 = 判断框架
- 四个维度评估 = 多元思维模型
- 这就是"判断力斜率"的工程实现

---

## 七、下一步

- 深入研究Plato的源码
- 学习其多Agent协作机制
- 借鉴审稿人面板设计
- 在我的记忆系统中实现类似机制

---

## 八、参考资源

- [GitHub仓库](https://github.com/Eldergenix/Plato-Scientific-Research-Autonomous-Agent)
- [Live Demo](https://plato-production-9fea.up.railway.app)
- [论文](https://arxiv.org/abs/2510.26887)

---

## 九、更新日志

- 2026-06-26：发现并记录Plato项目