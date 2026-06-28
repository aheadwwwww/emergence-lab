import re

with open("D:\\openclaw_workspace\\meyo\\main.js", "r", encoding="utf-8") as f:
    c = f.read()

# Search for fetch/axios call patterns
for m in re.finditer(r'(?:fetch|axios|get|post)\s*\([^)]*?["\x27](/api[^"\x27]+)["\x27]', c):
    print(m.group(1)[:120])

# Search for URL patterns with params 
for m in re.finditer(r'`/api[^`]+`', c):
    print(f"TEMPLATE: {m.group()[:120]}")

# Search for route definitions  
for m in re.finditer(r'(?:path|route)\s*:\s*["\x27](/api[^"\x27]+)["\x27]', c):
    print(f"ROUTE: {m.group(1)[:120]}")

# Search window.__APP_STATE__ or similar
for m in re.finditer(r'window\.__[A-Z_]+__', c):
    print(f"STATE: {m.group()}")
