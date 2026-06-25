import os
examples_dir = r'D:\openclaw_workspace\emergence_lab\examples'
fixes = {
    "'output/": "'examples/output/",
    "'output\\\\": "'examples/output/",
}
count = 0
for fname in os.listdir(examples_dir):
    if fname.endswith('.py'):
        fpath = os.path.join(examples_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in fixes.items():
            if old in content:
                content = content.replace(old, new)
                count += 1
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
print(f'Fixed {count} paths in examples')
