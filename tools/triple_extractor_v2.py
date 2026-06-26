# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import igraph as ig
import json
import os
import re
from typing import List, Dict, Tuple, Set

class SmartTripleExtractor:
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
        
        self.known_entities = {
            "树林", "芒格", "我", "四词方法论", "熔炉系统", "认知三角公式",
            "判断力斜率", "多元思维模型", "第一性原理", "二阶思维", "逆向思维",
            "能力圈", "思维模型", "Plato", "24hr-research", "Memary",
            "Graphiti", "HippoRAG", "Cognee", "审稿人面板", "审稿人面板系统",
            "知识图谱", "知识图谱系统", "会话记忆层", "Agent记忆层",
            "深度研究Agent", "自主科学研究Agent", "三Agent协作",
            "自动化", "专门化", "外显化", "复利化", "采集", "炼", "铸器", "输出",
            "认知", "经验", "上下文", "认知加经验加上下文",
            "金钱", "时间", "决策与分析类", "认知与行为类", "系统与战略类",
            "问题解决与创新类", "估计与风险类", "产品与创新类",
            "实用性", "可复用性", "真实性", "清晰度",
            "时序知识图谱", "静态知识图谱", "时序感知", "增量更新",
            "溯源机制", "原始数据", "事实变化时间", "重新生成",
            "时序知识图谱引擎", "智能路由", "AI记忆平台",
            "四大操作", "remember", "recall", "forget", "improve",
            "写作", "统计", "新颖性", "方法论",
            "工作操作系统", "状态五要素", "闭环公式", "投资消费负债",
            "Lenia", "NCA", "涌现", "好奇心地图", "觅游", "ig"
        }
    
    def extract_from_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        triples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return triples
        
        lines = content.split('\n')
        current_h2 = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('## '):
                current_h2 = line[3:].strip()
                if '：' in current_h2 or ':' in current_h2:
                    parts = re.split('[：:]', current_h2, maxsplit=1)
                    if len(parts) == 2:
                        e1, e2 = parts[0].strip(), parts[1].strip()
                        if e1 in self.known_entities and e2 in self.known_entities:
                            triples.append((e1, "contains", e2))
            
            if line.startswith('- ') and ('：' in line or ':' in line):
                content_text = line[2:].strip()
                parts = re.split('[：:]', content_text, maxsplit=1)
                if len(parts) == 2:
                    e1, e2 = parts[0].strip(), parts[1].strip()
                    if e1 in self.known_entities and e2 in self.known_entities:
                        triples.append((e1, "contains", e2))
        
        return triples
    
    def extract_from_directory(self, dir_path: str) -> List[Tuple[str, str, str]]:
        triples = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    file_triples = self.extract_from_file(file_path)
                    triples.extend(file_triples)
        
        return triples
    
    def add_triples_to_graph(self, triples: List[Tuple[str, str, str]]) -> int:
        added = 0
        
        for entity1, relation, entity2 in triples:
            if (entity1, relation, entity2) in self.existing_triples:
                continue
            
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
            self.g.es[-1]["source"] = "auto_extracted_v2"
            
            self.existing_triples.add((entity1, relation, entity2))
            added += 1
        
        return added
    
    def save_graph(self):
        self.g.write_pickle(self.graph_path)
    
    def get_stats(self) -> Dict:
        return {
            "nodes": self.g.vcount(),
            "edges": self.g.ecount(),
            "entities": len(self.existing_entities),
            "triples": len(self.existing_triples)
        }


def main():
    print("=== Triple Extraction v2 ===")
    
    extractor = SmartTripleExtractor()
    
    initial_stats = extractor.get_stats()
    print(f"Initial: {initial_stats['nodes']} nodes, {initial_stats['edges']} edges")
    
    print("\nExtracting from memory/ ...")
    triples = extractor.extract_from_directory("memory")
    
    unique_triples = list(set(triples))
    print(f"Found {len(unique_triples)} unique triples")
    
    if unique_triples:
        print("\nNew triples:")
        for i, (e1, r, e2) in enumerate(unique_triples[:30]):
            print(f"  {i+1}. {e1} --[{r}]--> {e2}")
    
    added = extractor.add_triples_to_graph(unique_triples)
    print(f"\nAdded {added} new triples")
    
    extractor.save_graph()
    
    final_stats = extractor.get_stats()
    print(f"\nFinal: {final_stats['nodes']} nodes, {final_stats['edges']} edges")
    print(f"Growth: +{final_stats['nodes'] - initial_stats['nodes']} nodes, +{final_stats['edges'] - initial_stats['edges']} edges")
    
    print("\nDone!")


if __name__ == "__main__":
    main()