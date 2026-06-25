import subprocess, sys, os

os.chdir('D:\\openclaw_workspace')

# Initialize git in emergence_lab
os.chdir('emergence_lab')

# Run git commands
def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"ERROR: {cmd}\n{result.stderr}")
        return False
    print(result.stdout.strip())
    return True

# Check if already a git repo
if not os.path.exists('.git'):
    run('git init')
    run('git branch -M main')

# Remove existing remote if any
subprocess.run('git remote remove origin', capture_output=True, shell=True)

# Add all files
run('git add -A')
run('git status')

print("\nReady to push.")
print("Run: git remote add origin https://github.com/YOUR_USERNAME/emergence-lab.git")
print("Run: git push -u origin main")