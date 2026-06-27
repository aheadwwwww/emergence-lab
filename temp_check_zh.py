import re
html = open(r'D:\openclaw_workspace\canvas\munger-models-zh.html', 'r', encoding='utf-8').read()
count = len(re.findall(r"title:\s*'([^']+)'", html))
cn_count = len(re.findall(r'[\u4e00-\u9fff]', html))
print(f'Models: {count}')
print(f'Chinese chars: {cn_count}')
idx = html.find('description')
if idx > 0:
    snippet = html[idx:idx+200]
    print(f'Sample: {snippet[:150]}...')
