import os
examples_dir = r'D:\openclaw_workspace\emergence_lab\examples'
old = "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
new = "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))"
for fname in os.listdir(examples_dir):
    if fname.endswith('.py'):
        fpath = os.path.join(examples_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if old in content:
            content = content.replace(old, new)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {fname}')
print('Done')
