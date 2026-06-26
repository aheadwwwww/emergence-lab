import json

# 读取完整模型数据
with open('models_full_data.json', 'r', encoding='utf-8') as f:
    models = json.load(f)

# 读取HTML模板
with open('munger-models-page.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# 生成JavaScript模型数据
def escape_js(text):
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    return text

js_models = "const models = {\n"
for mid, m in sorted(models.items()):
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

# 替换HTML中的script src为内联script
html_final = html_template.replace(
    '<script src="models_data.js"></script>',
    f'<script>\n{js_models}\n</script>'
)

# 保存为单文件
with open('D:/openclaw_workspace/canvas/munger-models-complete.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"Created complete HTML file with {len(models)} models")
print(f"File size: {len(html_final)} chars ({len(html_final)/1024:.1f} KB)")