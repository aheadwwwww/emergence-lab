import subprocess, os

dst = 'D:\\temp_emergence_lab'
os.chdir(dst)

token = "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"
username = "aheadwwwww"

# Set credential helper
subprocess.run(f'git config credential.helper store', shell=True, capture_output=True)

# Push with token in URL (different format)
repo_url = f"https://{username}:***@github.com/{username}/emergence-lab.git"
subprocess.run(f'git remote set-url origin {repo_url}', shell=True, capture_output=True)

# Try push
env = os.environ.copy()
env['GIT_TERMINAL_PROMPT'] = '0'

result = subprocess.run(
    'git push -u origin main',
    shell=True,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    env=env
)

print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
    print("\n尝试另一种方式...")
    
    # Alternative: use GIT_ASKPASS
    # Create a temp script that outputs the token
    with open('D:\\temp_credential.bat', 'w') as f:
        f.write(f'@echo {token}')
    
    env['GIT_ASKPASS'] = 'D:\\temp_credential.bat'
    subprocess.run(f'git remote set-url origin https://github.com/{username}/emergence-lab.git', shell=True, capture_output=True)
    
    result = subprocess.run('git push -u origin main', shell=True, capture_output=True, text=True, env=env)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Still error: {result.stderr}")
    else:
        print("SUCCESS!")
else:
    print("\n=== SUCCESS! ===")
    print("https://github.com/aheadwwwww/emergence-lab")
