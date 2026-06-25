import subprocess, os

dst = 'D:\\temp_emergence_lab'
os.chdir(dst)

# Use the token user provided (飞书脱敏前的原始值)
# 如果你的 token 是 ghp_xxxxx 格式，请直接告诉我完整值
# 现在先尝试用环境变量方式

token = os.environ.get('GITHUB_TOKEN', '')
if not token:
    print("ERROR: 需要完整的 token（ghp_ 开头）")
    print("飞书把你的 token 脱敏成 github…4w6G 了")
    print("请重新发送完整 token，或者用其他方式给我")
else:
    username = "aheadwwwww"
    repo_url = f"https://{username}:{token}@github.com/{username}/emergence-lab.git"
    
    subprocess.run(f'git remote set-url origin {repo_url}', shell=True, capture_output=True)
    result = subprocess.run('git push -u origin main', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")