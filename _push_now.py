import subprocess, os

dst = 'D:\\temp_emergence_lab'
os.chdir(dst)

token = "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"
username = "aheadwwwww"
repo_url = f"https://{username}:***@github.com/{username}/emergence-lab.git"

subprocess.run(f'git remote set-url origin {repo_url}', shell=True, capture_output=True)
result = subprocess.run('git push -u origin main', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("\n=== SUCCESS! ===")
    print("Repository: https://github.com/aheadwwwww/emergence-lab")
