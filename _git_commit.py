import subprocess, os

os.chdir('D:\\openclaw_workspace\\emergence_lab')

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    else:
        print(result.stdout.strip())

run('git rm -r --cached __pycache__')
run('git add -A')
run('git status')
run('git commit -m "v0.1.0: Lenia, NCA, PheromoneCA models + emergence metrics"')
print("\nReady for GitHub push.")