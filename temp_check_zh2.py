import re
html = open(r'D:\openclaw_workspace\canvas\munger-models-zh.html', 'r', encoding='utf-8').read()
cn = len(re.findall(r'[\u4e00-\u9fff]', html))
print(f'Chinese chars: {cn}')
# Check model content
idx = html.find('First Principles')
snippet = html[idx:idx+500]
print(f'Sample around First Principles:')
print(snippet[:400])
