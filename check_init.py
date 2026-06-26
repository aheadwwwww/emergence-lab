with open('D:/openclaw_workspace/canvas/munger-models-complete.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找最后的初始化代码
import re
match = re.search(r'// 初始化', content)
if match:
    start = match.start()
    print("\nInitialization code:")
    print(content[start:start+300])