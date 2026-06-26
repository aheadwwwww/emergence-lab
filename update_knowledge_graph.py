import json
from datetime import datetime

# 读取现有知识图谱
existing_triples = []
try:
    with open('memory/knowledge-graph.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            existing_triples.append(json.loads(line))
except:
    pass

# 新增三元组（Graphiti相关）
new_triples = [
    {"entity1": "我", "relation": "发现", "entity2": "Graphiti", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "Graphiti", "relation": "是", "entity2": "时序知识图谱引擎", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "Graphiti", "relation": "实现", "entity2": "时序感知", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "Graphiti", "relation": "实现", "entity2": "增量更新", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "Graphiti", "relation": "实现", "entity2": "溯源机制", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "时序知识图谱", "relation": "优于", "entity2": "静态知识图谱", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "时序感知", "relation": "记录", "entity2": "事实变化时间", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "增量更新", "relation": "避免", "entity2": "重新生成", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")},
    {"entity1": "溯源机制", "relation": "追踪", "entity2": "原始数据", "source": "memory/2026-06-26-graphiti-discovery.md", "timestamp": datetime.now().strftime("%Y-%m-%d")}
]

# 合并并去重
all_triples = existing_triples + new_triples
unique_triples = []
seen = set()

for triple in all_triples:
    key = f"{triple['entity1']}-{triple['relation']}-{triple['entity2']}"
    if key not in seen:
        seen.add(key)
        unique_triples.append(triple)

# 保存
output_path = "memory/knowledge-graph.jsonl"
with open(output_path, 'w', encoding='utf-8') as f:
    for triple in unique_triples:
        f.write(json.dumps(triple, ensure_ascii=False) + '\n')

print(f"知识图谱更新完成！")
print(f"原有三元组: {len(existing_triples)}")
print(f"新增三元组: {len(new_triples)}")
print(f"去重后总数: {len(unique_triples)}")

# 更新索引
entities = {}
relations = {}
for triple in unique_triples:
    e1 = triple['entity1']
    e2 = triple['entity2']
    r = triple['relation']
    
    entities[e1] = entities.get(e1, 0) + 1
    entities[e2] = entities.get(e2, 0) + 1
    relations[r] = relations.get(r, 0) + 1

index = {
    "entities": entities,
    "relations": relations,
    "total_triples": len(unique_triples),
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

index_path = "memory/knowledge-graph-index.json"
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\n索引更新完成！")
print(f"实体数量: {len(entities)}")
print(f"关系类型: {len(relations)}")