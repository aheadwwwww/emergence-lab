# -*- coding: utf-8 -*-
"""
芒格思维模型完整翻译 - 直接生成中文HTML
使用正则表达式批量替换翻译内容
"""

import re
import os

source_path = 'munger-models-fixed.html'
target_path = 'munger-models-zh.html'

with open(source_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Category翻译
html = html.replace("category: 'General'", "category: '通用思维'")
html = html.replace("category: 'Science'", "category: '科学原理'")
html = html.replace("category: 'Psychology'", "category: '心理学'")
html = html.replace("category: 'Economics'", "category: '经济学'")
html = html.replace("category: 'Business'", "category: '商业'")
html = html.replace("category: 'Decision Making'", "category: '决策'")
html = html.replace("category: 'Systems Thinking'", "category: '系统思维'")
html = html.replace("category: 'Mathematics'", "category: '数学'")
html = html.replace("category: 'Physics'", "category: '物理学'")

# 更新标题
html = html.replace(
    '<title>芒格思维模型库 - 98个思维模型完整版</title>',
    '<title>芒格思维模型库 - 98个思维模型完整版（中文翻译版）</title>'
)

# 保存翻译后的文件
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"基础翻译完成！")
print(f"源文件大小: {os.path.getsize(source_path) / 1024:.1f} KB")
print(f"目标文件大小: {os.path.getsize(target_path) / 1024:.1f} KB")