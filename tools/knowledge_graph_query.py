"""
知识图谱查询工具

提供对igraph知识图谱的查询功能：
- 多跳查询
- 按类型查询
- 按关系查询
- 路径查询
- 社区检测
"""

import igraph as ig
import json
from typing import List, Dict, Optional

class KnowledgeGraphQuery:
    def __init__(self, graph_path: str = "memory/knowledge-graph.pkl"):
        """初始化知识图谱查询工具"""
        self.g = ig.Graph.Read_Pickle(graph_path)
        self.entity_types = {
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
    
    def multi_hop_query(self, entity_name: str, hops: int = 2) -> Dict:
        """多跳查询：从某个实体出发，找到N跳内的所有节点"""
        try:
            node = self.g.vs.find(name=entity_name)
            node_idx = node.index
            
            result = {"entity": entity_name, "hops": {}}
            
            # BFS遍历
            visited = {node_idx}
            current_level = [node_idx]
            
            for hop in range(1, hops + 1):
                next_level = []
                for idx in current_level:
                    neighbors = self.g.vs[idx].neighbors()
                    for neighbor in neighbors:
                        neighbor_idx = neighbor.index
                        if neighbor_idx not in visited:
                            visited.add(neighbor_idx)
                            next_level.append(neighbor_idx)
                
                result["hops"][hop] = [self.g.vs[idx]["name"] for idx in next_level]
                current_level = next_level
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def query_by_type(self, entity_type: str) -> List[str]:
        """按类型查询：找所有某个类型的节点"""
        results = []
        for node in self.g.vs:
            name = node["name"]
            node_type = self.entity_types.get(name, "概念")
            if node_type == entity_type:
                results.append(name)
        return results
    
    def query_by_relation(self, relation: str) -> List[str]:
        """按关系查询：找所有某种关系的三元组"""
        results = []
        for edge in self.g.es:
            if edge["relation"] == relation:
                source = self.g.vs[edge.source]["name"]
                target = self.g.vs[edge.target]["name"]
                results.append(f"{source} → {relation} → {target}")
        return results
    
    def find_path(self, source_name: str, target_name: str) -> Optional[List[str]]:
        """路径查询：找到两个节点之间的路径"""
        try:
            source_idx = self.g.vs.find(name=source_name).index
            target_idx = self.g.vs.find(name=target_name).index
            
            paths = self.g.get_shortest_paths(source_idx, to=target_idx, mode="out")
            
            if paths and len(paths[0]) > 0:
                return [self.g.vs[node_id]["name"] for node_id in paths[0]]
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_key_nodes(self, top_n: int = 10) -> List[tuple]:
        """关键节点查询：获取度数最高的节点"""
        degrees = self.g.degree()
        node_degrees = [(self.g.vs[i]["name"], degrees[i]) for i in range(self.g.vcount())]
        return sorted(node_degrees, key=lambda x: x[1], reverse=True)[:top_n]
    
    def detect_communities(self) -> List[List[str]]:
        """社区检测：使用igraph的社区检测算法"""
        try:
            communities = self.g.community_multilevel()
            result = []
            for community in communities:
                if len(community) > 1:
                    nodes_in_community = [self.g.vs[node_id]["name"] for node_id in community]
                    result.append(nodes_in_community)
            return result
        except Exception as e:
            return []
    
    def get_entity_info(self, entity_name: str) -> Dict:
        """获取实体的详细信息"""
        try:
            node = self.g.vs.find(name=entity_name)
            neighbors = node.neighbors()
            edges = node.incident()
            
            return {
                "name": entity_name,
                "type": self.entity_types.get(entity_name, "概念"),
                "degree": node.degree(),
                "neighbors": [n["name"] for n in neighbors],
                "relations": [
                    {
                        "target": self.g.vs[e.target if e.source == node.index else e.source]["name"],
                        "relation": e["relation"]
                    }
                    for e in edges
                ]
            }
        except Exception as e:
            return {"error": str(e)}


# 使用示例
if __name__ == "__main__":
    kg = KnowledgeGraphQuery()
    
    print("=== 多跳查询 ===")
    result = kg.multi_hop_query("树林", hops=2)
    print(f"从'树林'出发，2跳内节点: {result}")
    
    print("\n=== 按类型查询 ===")
    methods = kg.query_by_type("方法")
    print(f"方法类节点: {methods}")
    
    print("\n=== 按关系查询 ===")
    propose_relations = kg.query_by_relation("提出")
    print(f"'提出'关系数量: {len(propose_relations)}")
    
    print("\n=== 关键节点 ===")
    key_nodes = kg.get_key_nodes(5)
    print(f"度数最高的5个节点: {key_nodes}")
    
    print("\n=== 实体信息 ===")
    info = kg.get_entity_info("树林")
    print(f"'树林'的信息: {info}")