import re
html = open(r'D:\openclaw_workspace\canvas\munger-models-zh.html', 'r', encoding='utf-8').read()
titles = re.findall(r"title: '([^']+)'", html)
print(f'Total models: {len(titles)}')
for t in titles[:5]:
    print(f'  - {t}')
# Check if Chinese
cn_count = sum(1 for t in titles if any('\u4e00' <= c <= '\u9fff' for c in t))
print(f'Chinese titles: {cn_count}/{len(titles)}')
