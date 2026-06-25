"""重构 emergence-lab 为标准 src 布局"""
import shutil, os

src = r'D:\temp_emergence_lab'
dst = r'D:\temp_emergence_lab_v2'

# Create fresh structure
os.makedirs(dst, exist_ok=True)

# Copy non-code files
for f in ['README.md', 'requirements.txt', '.gitignore']:
    if os.path.exists(os.path.join(src, f)):
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))

# Create src/emergence_lab
pkg_dir = os.path.join(dst, 'src', 'emergence_lab')
os.makedirs(pkg_dir, exist_ok=True)

# Copy all python files
for root, dirs, files in os.walk(src):
    if '__pycache__' in root or '.git' in root or 'egg-info' in root:
        continue
    for f in files:
        if f.endswith('.py') or f.endswith('.md') or f.endswith('.txt') or f.endswith('.toml'):
            rel_path = os.path.relpath(os.path.join(root, f), src)
            dest_path = os.path.join(pkg_dir, rel_path)
            # Skip files in root that are setup/config files
            if rel_path in ['setup.py', 'pyproject.toml']:
                continue
            if rel_path.startswith('_'):
                continue
            # Skip files that should be in docs/
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(os.path.join(root, f), dest_path)

# Copy core, models, experiments subdirs
for sub in ['core', 'models', 'experiments', 'examples', 'docs']:
    src_sub = os.path.join(src, sub)
    dst_sub = os.path.join(pkg_dir, sub)
    if os.path.exists(src_sub):
        if os.path.exists(dst_sub):
            shutil.rmtree(dst_sub)
        shutil.copytree(src_sub, dst_sub, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))

# Create pyproject.toml in root
with open(os.path.join(dst, 'pyproject.toml'), 'w') as f:
    f.write("""[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "emergence-lab"
version = "0.1.0"
description = "Programmable emergence experiment framework"
requires-python = ">=3.8"
dependencies = [
    "jax>=0.4.0",
    "numpy>=1.20.0",
    "scipy>=1.7.0",
    "matplotlib>=3.5.0",
    "imageio>=2.9.0",
]

[tool.setuptools.packages.find]
where = ["src"]
""")

print("Done! Structure created at:", dst)
print("Contents:")
for root, dirs, files in os.walk(dst):
    level = root.replace(dst, '').count(os.sep)
    indent = ' ' * (level * 2)
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        print(f"{indent}  {f}")
