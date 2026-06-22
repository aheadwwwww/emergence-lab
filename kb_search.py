"""
知识库搜索工具 - 集成到工作流
"""

import json
import numpy as np
from pathlib import Path

KB_DIR = Path('C:/kb_cache')
INDEX_FILE = KB_DIR / 'index.faiss'
METADATA_FILE = KB_DIR / 'metadata.json'
EMBEDDINGS_FILE = KB_DIR / 'embeddings.npy'

def search_knowledge(query, top_k=5):
    """语义搜索知识库"""
    import faiss
    from sentence_transformers import SentenceTransformer
    
    # 加载索引和元数据
    if not INDEX_FILE.exists():
        return {'error': '知识库索引不存在，请先运行 build_kb_small.py'}
    
    index = faiss.read_index(str(INDEX_FILE))
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    docs = metadata['documents']
    
    # 加载模型
    model = SentenceTransformer('shibing624/text2vec-base-chinese')
    
    # 编码查询
    query_embedding = model.encode([query]).astype('float32')
    
    # 搜索
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            'path': docs[idx]['path'],
            'type': docs[idx]['type'],
            'distance': float(distances[0][i]),
            'content': docs[idx]['content'][:300]
        })
    
    return {
        'query': query,
        'results': results
    }

if __name__ == '__main__':
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else '涌现'
    result = search_knowledge(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))