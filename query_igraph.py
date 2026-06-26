import igraph as ig
import json

print("加载知识图谱...")
g = ig.Graph.Read_Pickle('memory/knowledge-graph.pkl')

print(f"节点数: {g.vcount()}")
print(f"边数: {g.ecount()}")

# 1. 多跳查询：从"树林"出发，找到所有2跳内的节点
print("\n=== 多跳查询测试 ===")
try:
    node = g.vs.find(name="树林")
    node_idx = node.index
    
    # 获取所有邻居（1跳）
    neighbors_1hop = node.neighbors()
    print(f"从'树林'出发，1跳邻居: {[n['name'] for n in neighbors_1hop]}")
    
    # 获取所有2跳邻居
    neighbors_2hop = []
    for n1 in neighbors_1hop:
        n1_neighbors = n1.neighbors()
        for n2 in n1_neighbors:
            if n2 != node and n2 not in neighbors_1hop and n2 not in neighbors_2hop:
                neighbors_2hop.append(n2)
    
    print(f"从'树林'出发，2跳邻居: {[n['name'] for n in neighbors_2hop]}")
    
except Exception as e:
    print(f"查询失败: {e}")

# 2. 按类型查询：找所有"方法"类型的节点
print("\n=== 按类型查询 ===")
methods = []
for node in g.vs:
    name = node["name"]
    # 检查节点名称中是否包含"方法"或"模型"
    if "方法" in name or "模型" in name or "思维" in name:
        methods.append(name)

print(f"方法类节点: {methods}")

# 3. 按关系查询：找所有"提出"关系
print("\n=== 按关系查询 ===")
propose_relations = []
for edge in g.es:
    if edge["relation"] == "提出":
        source = g.vs[edge.source]["name"]
        target = g.vs[edge.target]["name"]
        propose_relations.append(f"{source} → 提出 → {target}")

print(f"'提出'关系:")
for r in propose_relations[:10]:
    print(f"  {r}")

# 4. 路径查询：从"树林"到"第一性原理"的所有路径
print("\n=== 路径查询 ===")
try:
    source_idx = g.vs.find(name="树林").index
    target_idx = g.vs.find(name="第一性原理").index
    
    # 获取最短路径
    paths = g.get_shortest_paths(source_idx, to=target_idx, mode="out")
    
    if paths and len(paths[0]) > 0:
        print(f"从'树林'到'第一性原理'的路径:")
        for path in paths:
            nodes_in_path = [g.vs[node_id]["name"] for node_id in path]
            print(f"  {' → '.join(nodes_in_path)}")
    else:
        print("没有找到路径")
        
except Exception as e:
    print(f"路径查询失败: {e}")

# 5. 关键节点查询：度数最高的节点
print("\n=== 关键节点查询 ===")
degrees = g.degree()
node_degrees = [(g.vs[i]["name"], degrees[i]) for i in range(g.vcount())]
sorted_nodes = sorted(node_degrees, key=lambda x: x[1], reverse=True)

print("度数最高的节点（前10）:")
for name, degree in sorted_nodes[:10]:
    print(f"  {name}: {degree} 条关系")

# 6. 社区检测：使用igraph的社区检测算法
print("\n=== 社区检测 ===")
try:
    communities = g.community_multilevel()
    print(f"检测到 {len(communities)} 个社区")
    
    for i, community in enumerate(communities):
        if len(community) > 1:
            nodes_in_community = [g.vs[node_id]["name"] for node_id in community]
            print(f"社区 {i+1}: {nodes_in_community}")
except Exception as e:
    print(f"社区检测失败: {e}")

# 7. 保存查询结果
print("\n=== 保存查询结果 ===")
query_results = {
    "total_nodes": g.vcount(),
    "total_edges": g.ecount(),
    "top_nodes": sorted_nodes[:10],
    "propose_relations": propose_relations,
    "methods": methods
}

with open("memory/knowledge-graph-query-results.json", "w", encoding="utf-8") as f:
    json.dump(query_results, f, ensure_ascii=False, indent=2)

print("已保存到 memory/knowledge-graph-query-results.json")

print("\n查询测试完成！")