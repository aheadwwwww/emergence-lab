import igraph as ig
import json

print("读取知识图谱数据...")

# 读取三元组
triples = []
with open('memory/knowledge-graph.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        triples.append(json.loads(line))

print(f"三元组数量: {len(triples)}")

# 构建实体列表
entities = set()
for triple in triples:
    entities.add(triple['entity1'])
    entities.add(triple['entity2'])

entities = list(entities)
print(f"实体数量: {len(entities)}")

# 创建igraph图
print("创建igraph图...")
g = ig.Graph()

# 添加节点
g.add_vertices(len(entities))
g.vs["name"] = entities

# 添加边
edges = []
relations = []
sources = []

for triple in triples:
    source_idx = entities.index(triple['entity1'])
    target_idx = entities.index(triple['entity2'])
    edges.append((source_idx, target_idx))
    relations.append(triple['relation'])
    sources.append(triple.get('source', ''))

g.add_edges(edges)
g.es["relation"] = relations
g.es["source"] = sources

print(f"节点数: {g.vcount()}")
print(f"边数: {g.ecount()}")

# 保存
g.write_pickle('memory/knowledge-graph.pkl')
print("已保存到 memory/knowledge-graph.pkl")

# 测试查询
print("\n=== 测试查询 ===")

# 查找"树林"节点
try:
    node = g.vs.find(name="树林")
    print(f"\n节点: {node['name']}")
    
    # 获取邻居
    neighbors = node.neighbors()
    print(f"邻居节点: {[n['name'] for n in neighbors]}")
    
    # 获取连接的边
    edges = node.incident()
    print(f"关系:")
    for edge in edges:
        target = g.vs[edge.target]['name']
        relation = edge['relation']
        print(f"  → {relation} → {target}")
        
except Exception as e:
    print(f"查询失败: {e}")

# 测试多跳查询
print("\n=== 测试多跳查询 ===")
try:
    # 从"树林"到"第一性原理"的路径
    source_idx = entities.index("树林")
    target_idx = entities.index("第一性原理")
    
    paths = g.get_shortest_paths(source_idx, to=target_idx)
    
    if paths and len(paths[0]) > 0:
        print(f"从'树林'到'第一性原理'的路径:")
        for path in paths:
            nodes_in_path = [entities[node_id] for node_id in path]
            print(f"  {' → '.join(nodes_in_path)}")
    else:
        print("没有找到路径")
        
except Exception as e:
    print(f"多跳查询失败: {e}")

print("\nigraph知识图谱构建完成！")