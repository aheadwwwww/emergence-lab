html = open(r'D:\openclaw_workspace\canvas\munger-models-cn.html', 'r', encoding='utf-8').read()
cn = sum(1 for c in html if '\u4e00' <= c <= '\u9fff')
print(f'Chinese chars: {cn}')
print(f'File size: {len(html)} bytes')
# Check structure
print(f'Has </html>: {"</html>" in html}')
print(f'Has modelsData: {"modelsData" in html}')
# Count model entries
import re
titles = re.findall(r"title:\s*'([^']+)'", html)
print(f'Models found: {len(titles)}')
for t in titles[:5]:
    print(f'  - {t}')
