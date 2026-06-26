import json
import re

# 读取完整模型数据
with open('models_full_data.json', 'r', encoding='utf-8') as f:
    models = json.load(f)

def escape_js_string(text):
    """正确转义JavaScript字符串"""
    if not text:
        return ""
    # 转义顺序很重要
    text = text.replace('\\', '\\\\')  # 先转义反斜杠
    text = text.replace("'", "\\'")     # 转义单引号
    text = text.replace('"', '\\"')     # 转义双引号
    text = text.replace('\n', ' ')      # 换行转空格
    text = text.replace('\r', ' ')      # 回车转空格
    text = text.replace('\t', ' ')      # 制表符转空格
    # 移除其他控制字符
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text

# 生成JavaScript模型数据
js_lines = ["const models = {"]
for mid, m in sorted(models.items()):
    js_lines.append(f"  '{mid}': {{")
    js_lines.append(f"    title: '{escape_js_string(m['title'])}',")
    js_lines.append(f"    title_en: '{escape_js_string(m['title_en'])}',")
    js_lines.append(f"    category: '{escape_js_string(m['category'])}',")
    js_lines.append(f"    description: '{escape_js_string(m['description'])}',")
    js_lines.append(f"    avoid: '{escape_js_string(m['avoid'])}',")
    
    # 关键词数组
    keywords_escaped = [escape_js_string(k) for k in m['keywords']]
    js_lines.append(f"    keywords: {json.dumps(keywords_escaped, ensure_ascii=False)},")
    
    # 步骤数组
    steps_escaped = [escape_js_string(s) for s in m['steps']]
    js_lines.append(f"    steps: {json.dumps(steps_escaped, ensure_ascii=False)},")
    
    # 教练问题数组
    coaching_escaped = [escape_js_string(q) for q in m['coaching']]
    js_lines.append(f"    coaching: {json.dumps(coaching_escaped, ensure_ascii=False)}")
    js_lines.append(f"  }},")

js_lines.append("};")
js_models = '\n'.join(js_lines)

print(f"生成JavaScript数据: {len(models)}个模型")
print(f"数据大小: {len(js_models)} 字符")

# 保存
with open('models_js_fixed.txt', 'w', encoding='utf-8') as f:
    f.write(js_models)

print("已保存到 models_js_fixed.txt")