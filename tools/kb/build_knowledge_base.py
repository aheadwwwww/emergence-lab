"""
建立语义知识库
使用 sentence-transformers 下载本地模型，建立向量索引
"""

import os
import json
import pickle
from pathlib import Path
import numpy as np

# 延迟导入，避免启动慢
def get_model():
    from sentence_transformers import SentenceTransformer
    # 使用小型多语言模型，适合中英文混合
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return model

KB_DIR = Path(r'C:\Users\许耀仁\.openclaw\workspace\knowledge_base')
INDEX_FILE = KB_DIR / 'index.faiss'
METADATA_FILE = KB_DIR / 'metadata.json'
EMBEDDINGS_FILE = KB_DIR / 'embeddings.npy'

KB_DIR.mkdir(exist_ok=True)

def collect_documents():
    """收集所有需要索引的文档"""
    workspace = Path(r'C:\Users\许耀仁\.openclaw\workspace')
    docs = []
    
    # 收集 memory/ 目录下的所有 .md 文件
    memory_dir = workspace / 'memory'
    if memory_dir.exists():
        for f in memory_dir.glob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = f.read_text(encoding='utf-8-sig')
                except:
                    continue  # 跳过无法读取的文件
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': content,
                'type': 'memory'
            })
    
    # 收集 MEMORY.md
    memory_file = workspace / 'MEMORY.md'
    if memory_file.exists():
        try:
            content = memory_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = memory_file.read_text(encoding='utf-8-sig')
        docs.append({
            'path': 'MEMORY.md',
            'content': content,
            'type': 'memory'
        })
    
    # 收集 experiments/ 目录下的 .py 文件（代码摘要）
    experiments_dir = workspace / 'experiments'
    if experiments_dir.exists():
        for f in experiments_dir.glob('*.py'):
            try:
                content = f.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = f.read_text(encoding='utf-8-sig')
                except:
                    continue
            # 只取前50行作为摘要
            lines = content.split('\n')[:50]
            summary = '\n'.join(lines)
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': summary,
                'type': 'experiment'
            })
    
    # 收集 curiosity-map/ 目录下的 .md 文件
    curiosity_dir = workspace / 'curiosity-map'
    if curiosity_dir.exists():
        for f in curiosity_dir.glob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = f.read_text(encoding='utf-8-sig')
                except:
                    continue
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': content,
                'type': 'curiosity-map'
            })
    
    print(f'收集到 {len(docs)} 个文档')
    return docs

def build_index(docs, model):
    """建立向量索引"""
    import faiss
    
    texts = [d['content'] for d in docs]
    
    print('编码文档中...')
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # 建立 FAISS 索引
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 保存
    faiss.write_index(index, str(INDEX_FILE))
    np.save(str(EMBEDDINGS_FILE), embeddings)
    
    metadata = {
        'documents': docs,
        'dimension': dimension
    }
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f'索引已建立: {len(docs)} 个文档, 维度 {dimension}')
    return index, embeddings

def search(query, model, index, docs, top_k=5):
    """语义搜索"""
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')
    
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            'path': docs[idx]['path'],
            'type': docs[idx]['type'],
            'score': float(1 / (1 + distances[0][i])),  # 转换为相似度
            'content_preview': docs[idx]['content'][:200] + '...'
        })
    
    return results

if __name__ == '__main__':
    print('=== 建立知识库 ===')
    
    # 收集文档
    docs = collect_documents()
    
    # 下载模型并建立索引
    print('加载模型...')
    model = get_model()
    
    print('建立索引...')
    index, embeddings = build_index(docs, model)
    
    # 测试搜索
    print('\n=== 测试搜索 ===')
    test_queries = [
        '涌现实验',
        '朗顿蚂蚁',
        '我犯过的错误',
        '记忆机制',
    ]
    
    for q in test_queries:
        print(f'\n查询: {q}')
        results = search(q, model, index, docs)
        for r in results[:3]:
            print(f'  [{r["type"]}] {r["path"]} (score: {r["score"]:.3f})')
    
    print('\n知识库建立完成！')