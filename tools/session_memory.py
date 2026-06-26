"""
会话记忆层 - 从Cognee学习的设计

实现两层记忆：
1. Session Memory（会话记忆）- 快速缓存
2. Knowledge Graph（知识图谱）- 永久存储

智能路由：
- 会话优先，图谱兜底
- 简单查询 → 向量搜索
- 关系查询 → 图谱查询
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

class SessionMemory:
    """会话记忆 - 快速缓存层"""
    
    def __init__(self, session_id: str, ttl_seconds: int = 3600):
        self.session_id = session_id
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.created_at = time.time()
    
    def remember(self, key: str, content: Any, tags: List[str] = None) -> None:
        """存入会话记忆"""
        self.cache[key] = {
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "ttl": self.ttl_seconds
        }
    
    def recall(self, key: str) -> Optional[Any]:
        """从会话记忆查询"""
        if key in self.cache:
            entry = self.cache[key]
            # 检查TTL
            if time.time() - self.created_at < entry["ttl"]:
                return entry["content"]
            else:
                del self.cache[key]
        return None
    
    def forget(self, key: str) -> bool:
        """删除会话记忆"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """列出所有键"""
        return list(self.cache.keys())
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return time.time() - self.created_at > self.ttl_seconds


class KnowledgeGraphMemory:
    """知识图谱记忆 - 永久存储层"""
    
    def __init__(self, graph_path: str = "memory/knowledge_graph.jsonl"):
        self.graph_path = Path(graph_path)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
    
    def remember(self, entity1: str, relation: str, entity2: str, 
                 source: str = None, metadata: Dict = None) -> None:
        """存入知识图谱"""
        triple = {
            "entity1": entity1,
            "relation": relation,
            "entity2": entity2,
            "source": source or "session",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        with open(self.graph_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(triple, ensure_ascii=False) + "\n")
    
    def recall(self, query: str, limit: int = 10) -> List[Dict]:
        """查询知识图谱（简单字符串匹配）"""
        results = []
        if not self.graph_path.exists():
            return results
        
        with open(self.graph_path, "r", encoding="utf-8") as f:
            for line in f:
                triple = json.loads(line)
                # 简单匹配：查询出现在任意实体或关系中
                if (query.lower() in triple["entity1"].lower() or
                    query.lower() in triple["relation"].lower() or
                    query.lower() in triple["entity2"].lower()):
                    results.append(triple)
                    if len(results) >= limit:
                        break
        
        return results
    
    def forget(self, entity: str) -> int:
        """删除包含某实体的所有三元组"""
        if not self.graph_path.exists():
            return 0
        
        kept = []
        removed = 0
        
        with open(self.graph_path, "r", encoding="utf-8") as f:
            for line in f:
                triple = json.loads(line)
                if entity in [triple["entity1"], triple["entity2"]]:
                    removed += 1
                else:
                    kept.append(triple)
        
        with open(self.graph_path, "w", encoding="utf-8") as f:
            for triple in kept:
                f.write(json.dumps(triple, ensure_ascii=False) + "\n")
        
        return removed


class SmartMemoryRouter:
    """智能记忆路由器 - 从Cognee学习的设计"""
    
    def __init__(self, session_id: str = "default"):
        self.session = SessionMemory(session_id)
        self.graph = KnowledgeGraphMemory()
    
    def remember(self, content: Any, key: str = None, 
                 to_graph: bool = False, triple: Dict = None) -> None:
        """
        智能存储记忆
        
        Args:
            content: 要存储的内容
            key: 会话缓存键
            to_graph: 是否同时存入知识图谱
            triple: 知识图谱三元组 {"entity1", "relation", "entity2"}
        """
        # 1. 存入会话记忆（快速）
        if key:
            self.session.remember(key, content)
        
        # 2. 存入知识图谱（永久）
        if to_graph and triple:
            self.graph.remember(
                triple["entity1"],
                triple["relation"],
                triple["entity2"],
                source=triple.get("source"),
                metadata=triple.get("metadata")
            )
    
    def recall(self, query: str, prefer_session: bool = True) -> Any:
        """
        智能查询记忆
        
        策略：
        1. 优先查会话记忆（快）
        2. 回退到知识图谱（慢但全）
        """
        # 1. 会话记忆
        if prefer_session:
            result = self.session.recall(query)
            if result is not None:
                return {
                    "source": "session",
                    "content": result
                }
        
        # 2. 知识图谱
        graph_results = self.graph.recall(query)
        if graph_results:
            return {
                "source": "graph",
                "content": graph_results
            }
        
        return None
    
    def forget(self, key: str = None, entity: str = None) -> Dict[str, int]:
        """
        智能删除记忆
        
        Returns:
            {"session": 删除数量, "graph": 删除数量}
        """
        result = {"session": 0, "graph": 0}
        
        if key and self.session.forget(key):
            result["session"] = 1
        
        if entity:
            result["graph"] = self.graph.forget(entity)
        
        return result


# 四大操作API（从Cognee学习）
def remember(content: Any, session_id: str = "default", 
             key: str = None, to_graph: bool = False, 
             triple: Dict = None) -> None:
    """存入记忆"""
    router = SmartMemoryRouter(session_id)
    router.remember(content, key, to_graph, triple)


def recall(query: str, session_id: str = "default", 
           prefer_session: bool = True) -> Any:
    """查询记忆"""
    router = SmartMemoryRouter(session_id)
    return router.recall(query, prefer_session)


def forget(key: str = None, entity: str = None, 
           session_id: str = "default") -> Dict[str, int]:
    """删除记忆"""
    router = SmartMemoryRouter(session_id)
    return router.forget(key, entity)


def improve(feedback: str, session_id: str = "default") -> None:
    """
    改进记忆（从反馈中学习）
    
    TODO: 实现反馈驱动的记忆优化
    """
    # 暂时只记录反馈
    router = SmartMemoryRouter(session_id)
    router.remember(feedback, key=f"feedback_{time.time()}")
    print(f"[improve] 反馈已记录: {feedback[:50]}...")


if __name__ == "__main__":
    # 测试
    print("=== 测试会话记忆层 ===")
    
    # 1. remember
    remember(
        content="Cognee是一个AI记忆平台，有22k stars",
        session_id="test",
        key="cognee_intro",
        to_graph=True,
        triple={
            "entity1": "Cognee",
            "relation": "是",
            "entity2": "AI记忆平台",
            "source": "test"
        }
    )
    print("[OK] remember 完成")
    
    # 2. recall
    result = recall("Cognee", session_id="test")
    print(f"[OK] recall 结果: {result}")
    
    # 3. improve
    improve("Cognee的四大操作设计很简洁", session_id="test")
    
    # 4. forget
    # deleted = forget(key="cognee_intro", entity="Cognee", session_id="test")
    # print(f"✓ forget 结果: {deleted}")
    
    print("\n=== 测试完成 ===")
