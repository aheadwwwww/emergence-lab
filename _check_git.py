import subprocess, os

os.chdir('D:\\openclaw_workspace\\emergence_lab')

# Check branch
result = subprocess.run('git branch', shell=True, capture_output=True, text=True)
print(f"Branches:\n{result.stdout}")

# Check commits
result = subprocess.run('git log --oneline', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"Commits:\n{result.stdout}")

# Check status
result = subprocess.run('git status', shell=True, capture_output=True, text=True)
print(f"Status:\n{result.stdout}")
