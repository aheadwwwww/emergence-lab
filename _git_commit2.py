import subprocess, os

os.chdir('D:\\openclaw_workspace\\emergence_lab')

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
    print(result.stdout.strip())
    if result.returncode != 0:
        print(f"ERR: {result.stderr[:200]}")

# Remove pycache from index
run('git rm -r --cached core/__pycache__')
run('git rm -r --cached models/__pycache__')

# Remove the dirs
import shutil
for d in ['core/__pycache__', 'models/__pycache__']:
    if os.path.exists(d):
        shutil.rmtree(d)

# Re-add
run('git add -A')
run('git status')
run('git commit -m "v0.1.0: Lenia, NCA, PheromoneCA + emergence metrics"')
print("\nDone.")