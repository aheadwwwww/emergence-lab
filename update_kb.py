"""
更新知识库索引
"""

import json
import numpy as np
from pathlib import Path

workspace = Path(r'C:\Users\许耀仁\.openclaw\workspace')
KB_DIR = Path('C:/kb_cache')

def collect_docs():
    docs = []
    
    # memory/
    for f in workspace.glob('memory/*.md'):
        try:
            content = f.read_text(encoding='utf-8')
        except:
            try:
                content = f.read_text(encoding='utf-8-sig')
            except:
                continue  # 跳过无法读取的文件
        docs.append({'path': str(f.name), 'content': content, 'type': 'memory'})
    
    # MEMORY.md
    mf = workspace / 'MEMORY.md'
    if mf.exists():
        docs.append({'path': 'MEMORY.md', 'content': mf.read_text(encoding='utf-8'), 'type': 'memory'})
    
    # experiments/
    for f in workspace.glob('experiments/*.py'):
        content = f.read_text(encoding='utf-8')
        docs.append({'path': str(f.name), 'content': content.split('\n')[:30], 'type': 'experiment'})
    
    # curiosity-map/
    for f in workspace.glob('curiosity-map/*.md'):
        docs.append({'path': str(f.name), 'content': f.read_text(encoding='utf-8'), 'type': 'curiosity'})
    
    # memory_framework_analysis.md
    af = workspace / 'memory_framework_analysis.md'
    if af.exists():
        docs.append({'path': 'memory_framework_analysis.md', 'content': af.read_text(encoding='utf-8'), 'type': 'analysis'})
    
    return docs

print('收集文档...')
docs = collect_docs()
print(f'{len(docs)} 个文档')

print('加载模型...')
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('shibing624/text2vec-base-chinese')

print('编码...')
texts = [d['content'] if isinstance(d['content'], str) else '\n'.join(d['content']) for d in docs]
embeddings = model.encode(texts)
embeddings = np.array(embeddings).astype('float32')

print('索引...')
import faiss
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

print('保存...')
faiss.write_index(index, str(KB_DIR / 'index.faiss'))
np.save(str(KB_DIR / 'embeddings.npy'), embeddings)
with open(KB_DIR / 'metadata.json', 'w', encoding='utf-8') as f:
    json.dump({'documents': docs, 'dimension': embeddings.shape[1]}, f, ensure_ascii=False)

print(f'完成: {len(docs)} 个文档')