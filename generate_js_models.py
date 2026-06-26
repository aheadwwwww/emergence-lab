import json

# 读取模型数据
with open('models_data.json', 'r', encoding='utf-8') as f:
    models = json.load(f)

# 生成JavaScript模型数据
js_models = "const models = {\n"
for mid, m in sorted(models.items()):
    js_models += f"  '{mid}': {{\n"
    js_models += f"    title: '{m['title']}',\n"
    js_models += f"    title_en: '{m['title_en']}',\n"
    js_models += f"    category: '{m['category']}',\n"
    js_models += f"    description: '{m['description']}',\n"
    js_models += f"    avoid: '{m['avoid']}',\n"
    js_models += f"    keywords: {json.dumps(m['keywords'])},\n"
    js_models += f"    steps: {json.dumps(m['steps'])},\n"
    js_models += f"    coaching: {json.dumps(m['coaching'])}\n"
    js_models += f"  }},\n"
js_models += "};\n"

print(f"Generated JavaScript for {len(models)} models")
print("First 500 chars:")
print(js_models[:500])

# 保存到文件
with open('models_js_data.txt', 'w', encoding='utf-8') as f:
    f.write(js_models)

print(f"\nTotal size: {len(js_models)} chars")