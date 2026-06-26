"""
三元组自动提取工具

从记忆文件中自动提取三元组，更新知识图谱。
应用规则11（做完就沉淀）和规则20（重复性工作只做一遍）。

提取规则：
1. 人物 → 提出 → 概念/方法
2. 概念 → 包含 → 子概念
3. 项目 → 实现 → 功能
4. 概念 → 启发 → 项目
"""

import igraph as ig
import json
import os
import re
from typing import List, Dict, Tuple

class TripleExtractor:
    def __init__(self, graph_path: str = "memory/knowledge-graph.pkl"):
        """初始化三元组提取器"""
        self.graph_path = graph_path
        self.g = ig.Graph.Read_Pickle(graph_path)
        self.existing_entities = set(self.g.vs["name"])
        self.existing_triples = set()
        
        # 加载已有三元组
        for edge in self.g.es:
            source = self.g.vs[edge.source]["name"]
            target = self.g.vs[edge.target]["name"]
            relation = edge["relation"]
            self.existing_triples.add((source, relation, target))
        
        # 提取模式
        self.patterns = [
            # "X提出了Y" 或 "X提出Y"
            (r'(.+?)提出了(.+?)[，。\n]', '提出'),
            (r'(.+?)提出(.+?)[，。\n]', '提出'),
            # "X包含Y"
            (r'(.+?)包含(.+?)[，。\n]', '包含'),
            # "X是Y"
            (r'(.+?)是(.+?)[，。\n]', '是'),
            # "X实现了Y"
            (r'(.+?)实现了(.+?)[，。\n]', '实现'),
            # "X发现Y"
            (r'(.+?)发现(.+?)[，。\n]', '发现'),
        ]
    
    def extract_from_text(self, text: str) -> List[Tuple[str, str, str]]:
        """从文本中提取三元组"""
        triples = []
        
        for pattern, relation in self.patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entity1 = match[0].strip()
                entity2 = match[1].strip()
                
                # 过滤太长的实体
                if len(entity1) > 20 or len(entity2) > 20:
                    continue
                
                # 过滤纯数字
                if entity1.isdigit() or entity2.isdigit():
                    continue
                
                triple = (entity1, relation, entity2)
                if triple not in self.existing_triples:
                    triples.append(triple)
        
        return triples
    
    def extract_from_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """从文件中提取三元组"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.extract_from_text(text)
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return []
    
    def extract_from_directory(self, dir_path: str, pattern: str = "*.md") -> List[Tuple[str, str, str]]:
        """从目录中提取三元组"""
        import glob
        triples = []
        
        files = glob.glob(os.path.join(dir_path, pattern))
        for file_path in files:
            file_triples = self.extract_from_file(file_path)
            triples.extend(file_triples)
        
        return triples
    
    def add_triples_to_graph(self, triples: List[Tuple[str, str, str]]) -> int:
        """将三元组添加到知识图谱"""
        added = 0
        
        for entity1, relation, entity2 in triples:
            # 跳过已存在的三元组
            if (entity1, relation, entity2) in self.existing_triples:
                continue
            
            # 添加实体
            if entity1 not in self.existing_entities:
                self.g.add_vertices(1)
                self.g.vs[-1]["name"] = entity1
                self.existing_entities.add(entity1)
            
            if entity2 not in self.existing_entities:
                self.g.add_vertices(1)
                self.g.vs[-1]["name"] = entity2
                self.existing_entities.add(entity2)
            
            # 添加边
            source_idx = self.g.vs.find(name=entity1).index
            target_idx = self.g.vs.find(name=entity2).index
            
            self.g.add_edges([(source_idx, target_idx)])
            self.g.es[-1]["relation"] = relation
            self.g.es[-1]["source"] = "auto_extracted"
            
            self.existing_triples.add((entity1, relation, entity2))
            added += 1
        
        return added
    
    def save_graph(self):
        """保存知识图谱"""
        self.g.write_pickle(self.graph_path)
    
    def get_stats(self) -> Dict:
        """获取图谱统计信息"""
        return {
            "nodes": self.g.vcount(),
            "edges": self.g.ecount(),
            "entities": len(self.existing_entities),
            "triples": len(self.existing_triples)
        }


def main():
    """主函数：从记忆文件中提取三元组并更新知识图谱"""
    print("=== 三元组自动提取 ===")
    
    extractor = TripleExtractor()
    
    # 获取初始统计
    initial_stats = extractor.get_stats()
    print(f"初始状态: {initial_stats['nodes']} 节点, {initial_stats['edges']} 边")
    
    # 从记忆文件中提取三元组
    memory_dir = "memory"
    print(f"\n从 {memory_dir}/ 目录提取三元组...")
    
    triples = extractor.extract_from_directory(memory_dir, "*.md")
    print(f"提取到 {len(triples)} 个新三元组")
    
    # 显示提取的三元组
    if triples:
        print("\n新三元组:")
        for i, (e1, r, e2) in enumerate(triples[:20]):
            print(f"  {i+1}. {e1} → {r} → {e2}")
    
    # 添加到图谱
    added = extractor.add_triples_to_graph(triples)
    print(f"\n添加了 {added} 个新三元组到知识图谱")
    
    # 保存
    extractor.save_graph()
    
    # 获取最终统计
    final_stats = extractor.get_stats()
    print(f"\n最终状态: {final_stats['nodes']} 节点, {final_stats['edges']} 边")
    print(f"增长: +{final_stats['nodes'] - initial_stats['nodes']} 节点, +{final_stats['edges'] - initial_stats['edges']} 边")
    
    print("\n三元组自动提取完成！")


if __name__ == "__main__":
    main()