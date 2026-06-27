"""
提取芒格网页中所有模型的关键字段，生成中英文对照表
"""
import re

with open(r'D:\openclaw_workspace\canvas\munger-models-fixed.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取所有模型标题
titles = re.findall(r"title:\s*'([^']+)'", html)
print(f"Found {len(titles)} models\n")

# 提取每个模型的description（前150字符）
descriptions = re.findall(r"description:\s*'([^']+)'", html)
for i, (t, d) in enumerate(zip(titles, descriptions)):
    print(f"{i+1}. {t}")
    print(f"   {d[:120]}...")
    print()
