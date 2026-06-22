"""
下载本地向量模型并建立知识库索引
使用 sentence-transformers + faiss
"""

import os
import sys

# 检查是否已安装必要的库
try:
    import sentence_transformers
    print('sentence-transformers 已安装')
except ImportError:
    print('安装 sentence-transformers...')
    os.system('pip install sentence-transformers')

try:
    import faiss
    print('faiss 已安装')
except ImportError:
    print('安装 faiss...')
    os.system('pip install faiss-cpu')

print('依赖检查完成')