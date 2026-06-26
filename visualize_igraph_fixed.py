import igraph as ig
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager

# 设置中文字体
print("查找中文字体...")
fonts = [f.name for f in font_manager.fontManager.ttflist]
chinese_fonts = [f for f in fonts if 'SimHei' in f or 'Microsoft YaHei' in f or 'SimSun' in f]
print(f"可用中文字体: {chinese_fonts[:5]}")

# 使用支持中文的字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

print("\n加载igraph知识图谱...")
g = ig.Graph.Read_Pickle('memory/knowledge-graph.pkl')

print(f"节点数: {g.vcount()}")
print(f"边数: {g.ecount()}")

# 设置节点颜色
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

# 设置节点大小
degrees = g.degree()
sizes = [d * 3 + 10 for d in degrees]
g.vs["size"] = sizes

# 绘制图
print("\n绘制知识图谱（修复中文字体）...")
fig, ax = plt.subplots(figsize=(18, 14))

layout = g.layout("fruchterman_reingold")
ig.plot(g, 
        target=ax,
        layout=layout,
        vertex_label=g.vs["name"],
        vertex_color=g.vs["color"],
        vertex_size=g.vs["size"],
        vertex_label_size=8,
        edge_label=g.es["relation"],
        edge_width=1,
        edge_arrow_size=0.8,
        edge_label_size=6)

ax.set_title("知识图谱 - 我的记忆网络", fontsize=20, fontproperties={'family': 'Microsoft YaHei'})
ax.axis("off")

plt.tight_layout()
plt.savefig('memory/knowledge-graph-igraph-fixed.png', dpi=150, bbox_inches='tight')
print("已保存到 memory/knowledge-graph-igraph-fixed.png")

plt.close()

print("\nigraph可视化完成！")