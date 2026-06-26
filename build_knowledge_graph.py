import json
import re
import os
from datetime import datetime

# 知识图谱三元组列表
triples = []

def add_triple(entity1, relation, entity2, source):
    """添加三元组到知识图谱"""
    triple = {
        "entity1": entity1,
        "relation": relation,
        "entity2": entity2,
        "source": source,
        "timestamp": datetime.now().strftime("%Y-%m-%d")
    }
    triples.append(triple)

# 从树林语料消化报告中提取
print("从树林语料消化报告提取三元组...")

# 核心概念
add_triple("树林", "提出", "四词方法论", "memory/2026-06-26-shulin-corpus.md")
add_triple("四词方法论", "包含", "自动化", "memory/2026-06-26-shulin-corpus.md")
add_triple("四词方法论", "包含", "专门化", "memory/2026-06-26-shulin-corpus.md")
add_triple("四词方法论", "包含", "外显化", "memory/2026-06-26-shulin-corpus.md")
add_triple("四词方法论", "包含", "复利化", "memory/2026-06-26-shulin-corpus.md")

add_triple("树林", "提出", "熔炉系统", "memory/2026-06-26-shulin-corpus.md")
add_triple("熔炉系统", "包含", "采集", "memory/2026-06-26-shulin-corpus.md")
add_triple("熔炉系统", "包含", "炼", "memory/2026-06-26-shulin-corpus.md")
add_triple("熔炉系统", "包含", "铸器", "memory/2026-06-26-shulin-corpus.md")
add_triple("熔炉系统", "包含", "输出", "memory/2026-06-26-shulin-corpus.md")

add_triple("树林", "提出", "认知三角公式", "memory/2026-06-26-shulin-corpus.md")
add_triple("认知三角公式", "包含", "认知", "memory/2026-06-26-shulin-corpus.md")
add_triple("认知三角公式", "包含", "时间", "memory/2026-06-26-shulin-corpus.md")
add_triple("认知三角公式", "包含", "金钱", "memory/2026-06-26-shulin-corpus.md")

# 判断框架
add_triple("树林", "提出", "判断力斜率", "memory/judgment-frameworks.md")
add_triple("判断力斜率", "等于", "认知加经验加上下文", "memory/judgment-frameworks.md")

# 芒格思维模型
add_triple("芒格", "提出", "多元思维模型", "memory/mental-models-library.md")
add_triple("芒格", "提出", "第一性原理", "memory/mental-models-library.md")
add_triple("芒格", "提出", "二阶思维", "memory/mental-models-library.md")
add_triple("芒格", "提出", "逆向思维", "memory/mental-models-library.md")
add_triple("芒格", "提出", "能力圈", "memory/mental-models-library.md")

# 思维模型分类
add_triple("思维模型", "分类", "决策与分析类", "memory/mental-models-library.md")
add_triple("思维模型", "分类", "认知与行为类", "memory/mental-models-library.md")
add_triple("思维模型", "分类", "系统与战略类", "memory/mental-models-library.md")
add_triple("思维模型", "分类", "问题解决与创新类", "memory/mental-models-library.md")

# 发现的项目
add_triple("我", "发现", "Plato", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("Plato", "是", "自主科学研究Agent", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("Plato", "实现", "审稿人面板", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("审稿人面板", "评估", "方法论", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("审稿人面板", "评估", "统计", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("审稿人面板", "评估", "新颖性", "memory/2026-06-26-plato-agent-discovery.md")
add_triple("审稿人面板", "评估", "写作", "memory/2026-06-26-plato-agent-discovery.md")

add_triple("我", "发现", "24hr-research", "memory/2026-06-26-24hr-research-discovery.md")
add_triple("24hr-research", "是", "深度研究Agent", "memory/2026-06-26-24hr-research-discovery.md")
add_triple("24hr-research", "架构", "三Agent协作", "memory/2026-06-26-24hr-research-discovery.md")

add_triple("我", "发现", "Memary", "memory/2026-06-26-memary-discovery.md")
add_triple("Memary", "是", "Agent记忆层", "memory/2026-06-26-memary-discovery.md")
add_triple("Memary", "实现", "知识图谱", "memory/2026-06-26-memary-discovery.md")

# 我自己
add_triple("我", "实现", "审稿人面板系统", "memory/reviewer-panel-system.md")
add_triple("审稿人面板系统", "评估", "实用性", "memory/reviewer-panel-system.md")
add_triple("审稿人面板系统", "评估", "可复用性", "memory/reviewer-panel-system.md")
add_triple("审稿人面板系统", "评估", "真实性", "memory/reviewer-panel-system.md")
add_triple("审稿人面板系统", "评估", "清晰度", "memory/reviewer-panel-system.md")

add_triple("我", "实现", "知识图谱系统", "memory/knowledge-graph-system.md")
add_triple("知识图谱系统", "存储", "三元组", "memory/knowledge-graph-system.md")

# 保存到文件
output_path = "memory/knowledge-graph.jsonl"
with open(output_path, 'w', encoding='utf-8') as f:
    for triple in triples:
        f.write(json.dumps(triple, ensure_ascii=False) + '\n')

print(f"提取完成！共 {len(triples)} 个三元组")
print(f"保存到: {output_path}")

# 创建索引
entities = {}
relations = {}
for triple in triples:
    e1 = triple['entity1']
    e2 = triple['entity2']
    r = triple['relation']
    
    entities[e1] = entities.get(e1, 0) + 1
    entities[e2] = entities.get(e2, 0) + 1
    relations[r] = relations.get(r, 0) + 1

index = {
    "entities": entities,
    "relations": relations,
    "total_triples": len(triples),
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

index_path = "memory/knowledge-graph-index.json"
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\n索引创建完成！")
print(f"实体数量: {len(entities)}")
print(f"关系类型: {len(relations)}")
print(f"保存到: {index_path}")