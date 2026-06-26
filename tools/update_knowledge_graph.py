# -*- coding: utf-8 -*-
"""
知识图谱更新工具

手动添加最近学到/发现的关键关系。
应用规则11：做完就沉淀——每次学到新东西，立刻加入图谱。
"""

import igraph as ig
import json
from typing import List, Tuple

class KnowledgeGraphUpdater:
    def __init__(self, graph_path: str = "memory/knowledge-graph.pkl"):
        self.graph_path = graph_path
        self.g = ig.Graph.Read_Pickle(graph_path)
        self.existing_entities = set(self.g.vs["name"])
        self.existing_triples = set()
        
        for edge in self.g.es:
            source = self.g.vs[edge.source]["name"]
            target = self.g.vs[edge.target]["name"]
            relation = edge["relation"]
            self.existing_triples.add((source, relation, target))
    
    def add_triple(self, entity1: str, relation: str, entity2: str) -> bool:
        """添加一个三元组"""
        if (entity1, relation, entity2) in self.existing_triples:
            return False
        
        if entity1 not in self.existing_entities:
            self.g.add_vertices(1)
            self.g.vs[-1]["name"] = entity1
            self.existing_entities.add(entity1)
        
        if entity2 not in self.existing_entities:
            self.g.add_vertices(1)
            self.g.vs[-1]["name"] = entity2
            self.existing_entities.add(entity2)
        
        source_idx = self.g.vs.find(name=entity1).index
        target_idx = self.g.vs.find(name=entity2).index
        
        self.g.add_edges([(source_idx, target_idx)])
        self.g.es[-1]["relation"] = relation
        self.g.es[-1]["source"] = "manual_update"
        
        self.existing_triples.add((entity1, relation, entity2))
        return True
    
    def save(self):
        self.g.write_pickle(self.graph_path)
        
        # 同时更新 JSON Lines
        triples = []
        for edge in self.g.es:
            source = self.g.vs[edge.source]["name"]
            target = self.g.vs[edge.target]["name"]
            relation = edge["relation"]
            src = edge["source"] if "source" in edge.attributes() else ""
            triples.append({
                "entity1": source,
                "relation": relation,
                "entity2": target,
                "source": src
            })
        
        with open("memory/knowledge-graph.jsonl", 'w', encoding='utf-8') as f:
            for t in triples:
                f.write(json.dumps(t, ensure_ascii=False) + '\n')
    
    def stats(self) -> dict:
        return {
            "nodes": self.g.vcount(),
            "edges": self.g.ecount(),
            "entities": len(self.existing_entities),
            "triples": len(self.existing_triples)
        }


def main():
    updater = KnowledgeGraphUpdater()
    
    initial = updater.stats()
    print(f"Before: {initial['nodes']} nodes, {initial['edges']} edges")
    
    # ======== 添加最近学到的新关系 ========
    
    # 工作操作系统相关
    new_triples = [
        # 工作操作系统
        ("工作操作系统", "提出", "闭环公式"),
        ("工作操作系统", "提出", "状态五要素"),
        ("工作操作系统", "提出", "投资消费负债"),
        ("闭环公式", "是", "接收行动反馈结果"),
        ("状态五要素", "包含", "你是谁"),
        ("状态五要素", "包含", "做了什么"),
        ("状态五要素", "包含", "进度"),
        ("状态五要素", "包含", "结果画像"),
        ("状态五要素", "包含", "下一步时间点"),
        
        # igraph工具
        ("ig", "实现", "知识图谱查询工具"),
        ("知识图谱查询工具", "支持", "多跳查询"),
        ("知识图谱查询工具", "支持", "按类型查询"),
        ("知识图谱查询工具", "支持", "按关系查询"),
        ("知识图谱查询工具", "支持", "路径查询"),
        ("知识图谱查询工具", "支持", "社区检测"),
        ("知识图谱查询工具", "支持", "实体信息查询"),
        
        # 知识图谱
        ("知识图谱", "存储于", "ig"),
        ("知识图谱", "支持", "多跳查询"),
        ("知识图谱", "支持", "社区检测"),
        ("知识图谱", "检测到", "10个社区"),
        ("我", "使用", "ig"),
        ("我", "使用", "知识图谱"),
        
        # 与工作操作系统的关联
        ("我", "学习", "工作操作系统"),
        ("工作操作系统", "属于", "树林"),
        ("工作操作系统", "应用", "熔炉系统"),
        ("我", "应用", "状态五要素"),
        ("我", "应用", "闭环公式"),
    ]
    
    added = 0
    for e1, r, e2 in new_triples:
        if updater.add_triple(e1, r, e2):
            added += 1
            print(f"  Added: {e1} --[{r}]--> {e2}")
    
    updater.save()
    
    final = updater.stats()
    print(f"\nAfter: {final['nodes']} nodes, {final['edges']} edges")
    print(f"Growth: +{final['nodes'] - initial['nodes']} nodes, +{final['edges'] - initial['edges']} edges")
    print("\nKnowledge graph updated!")


if __name__ == "__main__":
    main()