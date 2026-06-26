with open('D:/openclaw_workspace/canvas/munger-models-complete.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 查找 initSidebar 函数
match = re.search(r'function initSidebar\(\)', content)
print('Found initSidebar:', match is not None)

if match:
    start = match.start()
    print("\nInitSidebar function:")
    print(content[start:start+1500])