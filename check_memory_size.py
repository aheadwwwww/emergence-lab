import os

files = ['human.md', 'persona.md', 'lessons.md', 'projects.md', 'mental-models-library.md']
for f in files:
    path = f'memory/{f}'
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print(f'{f}: {size/1024:.1f} KB')