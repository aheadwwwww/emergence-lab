import re
html = open(r'D:\openclaw_workspace\canvas\munger-models-cn.html', 'r', encoding='utf-8').read()
titles = re.findall(r'<h2 class="model-title">([^<]+)</h2>', html)
cn = sum(1 for c in html if '\u4e00' <= c <= '\u9fff')
print(f'{len(titles)} models, {len(html)} bytes, {cn} Chinese chars')
if len(titles) > 34:
    print('New models (35-50):')
    for t in titles[34:]:
        print(f'  {t}')
