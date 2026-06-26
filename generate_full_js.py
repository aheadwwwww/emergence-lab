import json

# 读取完整模型数据
with open('models_full_data.json', 'r', encoding='utf-8') as f:
    models = json.load(f)

# 生成JavaScript模型数据
js_models = "const models = {\n"
for mid, m in sorted(models.items()):
    # 转义特殊字符
    def escape_js(text):
        if not text:
            return ""
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        return text
    
    js_models += f"  '{mid}': {{\n"
    js_models += f"    title: '{escape_js(m['title'])}',\n"
    js_models += f"    title_en: '{escape_js(m['title_en'])}',\n"
    js_models += f"    category: '{escape_js(m['category'])}',\n"
    js_models += f"    description: '{escape_js(m['description'])}',\n"
    js_models += f"    avoid: '{escape_js(m['avoid'])}',\n"
    js_models += f"    keywords: {json.dumps(m['keywords'])},\n"
    js_models += f"    steps: {json.dumps([escape_js(s) for s in m['steps']])},\n"
    js_models += f"    coaching: {json.dumps([escape_js(q) for q in m['coaching']])}\n"
    js_models += f"  }},\n"
js_models += "};\n"

print(f"Generated JavaScript for {len(models)} models")
print(f"Total size: {len(js_models)} chars")

# 保存
with open('models_js_full.txt', 'w', encoding='utf-8') as f:
    f.write(js_models)

print("Saved to models_js_full.txt")