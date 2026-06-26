with open('D:/openclaw_workspace/canvas/munger-models-complete.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import sys
sys.stdout.reconfigure(encoding='utf-8')

# 查找最后几行
print("Last 30 lines:")
for i, line in enumerate(lines[-30:], start=len(lines)-30):
    print(f"{i}: {line.rstrip()}")