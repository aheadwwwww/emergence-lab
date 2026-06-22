"""
使用更小的中文向量模型
"""

import os
from pathlib import Path
import json
import numpy as np

def collect_documents():
    """收集所有需要索引的文档"""
    workspace = Path(r'C:\Users\许耀仁\.openclaw\workspace')
    docs = []
    
    # 收集 memory/ 目录
    memory_dir = workspace / 'memory'
    if memory_dir.exists():
        for f in memory_dir.glob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
            except:
                try:
                    content = f.read_text(encoding='utf-8-sig')
                except:
                    continue
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': content,
                'type': 'memory'
            })
    
    # MEMORY.md
    memory_file = workspace / 'MEMORY.md'
    if memory_file.exists():
        try:
            content = memory_file.read_text(encoding='utf-8')
        except:
            content = memory_file.read_text(encoding='utf-8-sig')
        docs.append({
            'path': 'MEMORY.md',
            'content': content,
            'type': 'memory'
        })
    
    # experiments/
    experiments_dir = workspace / 'experiments'
    if experiments_dir.exists():
        for f in experiments_dir.glob('*.py'):
            try:
                content = f.read_text(encoding='utf-8')
            except:
                continue
            lines = content.split('\n')[:30]
            summary = '\n'.join(lines)
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': summary,
                'type': 'experiment'
            })
    
    # curiosity-map/
    curiosity_dir = workspace / 'curiosity-map'
    if curiosity_dir.exists():
        for f in curiosity_dir.glob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
            except:
                continue
            docs.append({
                'path': str(f.relative_to(workspace)),
                'content': content,
                'type': 'curiosity-map'
            })
    
    print(f'收集到 {len(docs)} 个文档')
    return docs

def main():
    print('=== 加载模型 ===')
    from sentence_transformers import SentenceTransformer
    
    # 使用更小更快的模型
    model_name = 'shibing624/text2vec-base-chinese'
    print(f'加载模型: {model_name}')
    model = SentenceTransformer(model_name)
    
    # 收集文档
    docs = collect_documents()
    
    # 编码
    print('编码文档...')
    texts = [d['content'] for d in docs]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # 建立索引
    import faiss
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 保存
    KB_DIR = Path('C:/kb_cache')
    KB_DIR.mkdir(exist_ok=True)
    
    faiss.write_index(index, str(KB_DIR / 'index.faiss'))
    np.save(str(KB_DIR / 'embeddings.npy'), embeddings)
    
    with open(KB_DIR / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump({'documents': docs, 'dimension': dimension}, f, ensure_ascii=False, indent=2)
    
    print(f'\n索引建立完成: {len(docs)} 个文档, 维度 {dimension}')
    
    # 测试
    print('\n=== 测试搜索 ===')
    test_queries = ['涌现实验', '朗顿蚂蚁', '我犯过的错误']
    for q in test_queries:
        print(f'\n查询: {q}')
        q_emb = model.encode([q]).astype('float32')
        D, I = index.search(q_emb, 3)
        for i, idx in enumerate(I[0]):
            print(f'  [{docs[idx]["type"]}] {docs[idx]["path"]} (dist: {D[0][i]:.3f})')

if __name__ == '__main__':
    main()