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


def add_single(entity1: str, relation: str, entity2: str):
    """添加单个三元组（命令行调用）"""
    updater = KnowledgeGraphUpdater()
    initial = updater.stats()
    print(f"Before: {initial['nodes']} nodes, {initial['edges']} edges")
    
    if updater.add_triple(entity1, relation, entity2):
        print(f"  Added: {entity1} --[{relation}]--> {entity2}")
        updater.save()
    else:
        print(f"  Skipped (exists): {entity1} --[{relation}]--> {entity2}")
    
    final = updater.stats()
    print(f"After: {final['nodes']} nodes, {final['edges']} edges")
    print("Knowledge graph updated!")


def main():
    updater = KnowledgeGraphUpdater()
    
    initial = updater.stats()
    print(f"Before: {initial['nodes']} nodes, {initial['edges']} edges")
    
    # ======== 添加最近学到的新关系 ========
    
    # ICL梯度下降相关（2026-06-26）
    new_triples = [
        ("ICL梯度下降", "属于", "Transformer机制"),
        ("ICL梯度下降", "发现于", "Google Research"),
        ("ICL梯度下降", "启发", "知识图谱设计"),
        ("我", "学习", "ICL梯度下降"),
        ("知识图谱", "应优化为", "示例驱动记忆"),
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
    import sys
    
    if len(sys.argv) == 4 and sys.argv[1] == "add":
        # python update_knowledge_graph.py add entity1 relation entity2
        add_single(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        main()