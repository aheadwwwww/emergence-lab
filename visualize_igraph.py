import igraph as ig
import matplotlib.pyplot as plt

print("加载igraph知识图谱...")
g = ig.Graph.Read_Pickle('memory/knowledge-graph.pkl')

print(f"节点数: {g.vcount()}")
print(f"边数: {g.ecount()}")

# 设置节点颜色（根据类型）
entity_types = {
    "树林": "人物",
    "芒格": "人物",
    "我": "人物",
    "四词方法论": "方法",
    "熔炉系统": "方法",
    "认知三角公式": "方法",
    "判断力斜率": "概念",
    "多元思维模型": "概念",
    "第一性原理": "方法",
    "二阶思维": "方法",
    "逆向思维": "方法",
    "能力圈": "方法",
    "思维模型": "概念",
    "Plato": "项目",
    "24hr-research": "项目",
    "Memary": "项目",
    "Graphiti": "项目",
    "HippoRAG": "项目"
}

type_colors = {
    "人物": "#ff6b6b",
    "概念": "#4ecdc4",
    "方法": "#95e1d3",
    "项目": "#f38181",
    "工具": "#aa96da",
    "系统": "#fcbad3",
    "维度": "#f9ed69"
}

colors = []
for node in g.vs:
    name = node["name"]
    type = entity_types.get(name, "概念")
    color = type_colors.get(type, "#4ecdc4")
    colors.append(color)

g.vs["color"] = colors

# 设置节点大小（根据度数）
degrees = g.degree()
sizes = [d * 3 + 10 for d in degrees]
g.vs["size"] = sizes

# 绘制图
print("绘制知识图谱...")
fig, ax = plt.subplots(figsize=(16, 12))

layout = g.layout("fruchterman_reingold")
ig.plot(g, 
        target=ax,
        layout=layout,
        vertex_label=g.vs["name"],
        vertex_color=g.vs["color"],
        vertex_size=g.vs["size"],
        edge_label=g.es["relation"],
        edge_width=1,
        edge_arrow_size=1)

ax.set_title("知识图谱 - 我的记忆网络", fontsize=20)
ax.axis("off")

plt.tight_layout()
plt.savefig('memory/knowledge-graph-igraph.png', dpi=150, bbox_inches='tight')
print("已保存到 memory/knowledge-graph-igraph.png")

plt.close()

# 统计信息
print("\n=== 统计信息 ===")
print(f"度数最高的节点:")
top_nodes = sorted(zip(g.vs["name"], degrees), key=lambda x: x[1], reverse=True)[:10]
for name, degree in top_nodes:
    print(f"  {name}: {degree} 条关系")

print(f"\n关系类型分布:")
relations = g.es["relation"]
relation_counts = {}
for r in relations:
    relation_counts[r] = relation_counts.get(r, 0) + 1

sorted_relations = sorted(relation_counts.items(), key=lambda x: x[1], reverse=True)
for relation, count in sorted_relations:
    print(f"  {relation}: {count} 次")

print("\nigraph可视化完成！")