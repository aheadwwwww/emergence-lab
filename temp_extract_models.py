"""
批量翻译芒格思维模型网页
从 munger-models-fixed.html 提取数据，生成中文版
"""

import json
import re

# 读取源文件
with open(r'D:\openclaw_workspace\canvas\munger-models-fixed.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取模型数据（在 JavaScript 中）
# 找到 modelsData 数组
start = html.find('const modelsData = ')
end = html.find(';\n\n        function', start)
if end == -1:
    end = html.find(';\n\n        // Search', start)

js_data = html[start:end].strip()
# 提取 JSON 部分
json_start = js_data.find('[')
json_end = js_data.rfind(']') + 1
json_str = js_data[json_start:json_end]

# JavaScript -> JSON (替换单引号为双引号)
# 先保存原始内容用于分析
models = eval(json_str)  # 用 Python eval 因为 JS 对象字面量和 Python dict 很像

print(f"Found {len(models)} models")

# 检查前几个模型的结构
for i, m in enumerate(models[:3]):
    print(f"\nModel {i+1}: {m.get('name', 'N/A')}")
    print(f"  Fields: {list(m.keys())}")
    if 'description' in m:
        print(f"  Description: {m['description'][:100]}...")

print("\nDone.")
