import subprocess, os

os.chdir('D:\\openclaw_workspace\\emergence_lab')

token = "github…4w6G"
username = "aheadwwwww"
repo_url = f"https://{username}:{token}@github.com/{username}/emergence-lab.git"

# Set remote
result = subprocess.run(f'git remote add origin {repo_url}', shell=True, capture_output=True, text=True)
if result.returncode != 0:
    # Remote might already exist, try to set URL
    subprocess.run(f'git remote set-url origin {repo_url}', shell=True, capture_output=True, text=True)

# Push
result = subprocess.run('git push -u origin main', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("\n✓ Pushed successfully!")
    print("URL: https://github.com/aheadwwwww/emergence-lab")
