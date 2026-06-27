"""
Simple approach: Add Chinese labels to the HTML interface only.
The model content stays English (standard terminology),
but the UI labels become Chinese for navigation.
"""
import re

with open(r'D:\openclaw_workspace\canvas\munger-models-fixed.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace UI labels
replacements = {
    'Description': '描述',
    'When to Avoid': '何时避免',
    'Application': '应用场景',
    'Thinking Steps': '思考步骤',
    'Coaching Questions': '教练问题',
    'Keywords': '关键词',
    'Mark as Learned': '标记为已学习',
    'Learned': '已学习',
    'Search models...': '搜索模型...',
    'Select a model from the sidebar': '从侧边栏选择一个模型',
    'Click on a model to view details': '点击模型查看详情',
    'Models': '模型',
    'Categories': '分类',
    'Progress': '进度',
}

for en, zh in replacements.items():
    html = html.replace(en, zh)

# Update category names in sidebar
cat_map = {
    'General': '通用思维',
    'Science': '科学',
    'Mathematics': '数学',
    'Economics': '经济学',
    'Systems Thinking': '系统思维',
    'Human Nature': '人性',
    'Art': '艺术',
    'War': '战争',
}
for en, zh in cat_map.items():
    html = html.replace(f"'{en}'", f"'{zh}'")

with open(r'D:\openclaw_workspace\canvas\munger-models-zh.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done. Size: {len(html)} bytes")
