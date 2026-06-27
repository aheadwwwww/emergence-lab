# -*- coding: utf-8 -*-
import re

# 读取源文件
with open('munger-models-fixed.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 统计模型数量
model_count = len(re.findall(r"'m\d{2}':\s*\{", content))
print(f'找到 {model_count} 个模型')

# 找到所有description字段
desc_count = len(re.findall(r"description:\s*'", content))
print(f'找到 {desc_count} 个description字段')

# 找到所有avoid字段
avoid_count = len(re.findall(r"avoid:\s*'", content))
print(f'找到 {avoid_count} 个avoid字段')

# 找到所有keywords字段
kw_count = len(re.findall(r"keywords:\s*\[", content))
print(f'找到 {kw_count} 个keywords字段')

# 找到所有steps字段
steps_count = len(re.findall(r"steps:\s*\[", content))
print(f'找到 {steps_count} 个steps字段')

# 找到所有coaching字段
coach_count = len(re.findall(r"coaching:\s*\[", content))
print(f'找到 {coach_count} 个coaching字段')

print(f'\n文件大小: {len(content)} 字节')