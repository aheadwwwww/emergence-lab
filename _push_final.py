import subprocess, shutil, os

dst = 'D:\\temp_emergence_lab'
os.chdir(dst)

# Remove pycache
for d in ['core/__pycache__', 'models/__pycache__']:
    p = os.path.join(dst, d)
    if os.path.exists(p):
        shutil.rmtree(p)

# Init git
subprocess.run('git init', shell=True, capture_output=True)
subprocess.run('git branch -M main', shell=True, capture_output=True)
subprocess.run('git config user.email "agent@openclaw.local"', shell=True, capture_output=True)
subprocess.run('git config user.name "OpenClaw Agent"', shell=True, capture_output=True)
subprocess.run('git add -A', shell=True, capture_output=True)

result = subprocess.run('git commit -m "v0.1.0: Lenia, NCA, PheromoneCA + emergence metrics"', 
                        shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)

# Add remote and push
token = "github…4w6G"
username = "aheadwwwww"
repo_url = f"https://{username}:{token}@github.com/{username}/emergence-lab.git"

subprocess.run(f'git remote add origin {repo_url}', shell=True, capture_output=True)
result = subprocess.run('git push -u origin main', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("\n=== SUCCESS ===")
    print("https://github.com/aheadwwwww/emergence-lab")