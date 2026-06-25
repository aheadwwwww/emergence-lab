import subprocess, os
from pathlib import Path

# Read meyo credentials for github user
creds_path = Path.home() / '.meyo' / 'credentials.json'
print(f"Looking for creds at: {creds_path}")

os.chdir('D:\\openclaw_workspace\\emergence_lab')

# Set git config (within repo)
subprocess.run('git config user.email "agent@openclaw.local"', shell=True)
subprocess.run('git config user.name "OpenClaw Agent"', shell=True)

subprocess.run('git commit -m "v0.1.0: Lenia, NCA, PheromoneCA + emergence metrics"', shell=True)
print("\n=== Committed ===")

# 现在需要在工作区根目录和 emergence_lab 分离
# emergence_lab 应该是独立的 git repo
print("\nemergence_lab 是独立 repo，需要单独推送到 GitHub。")
print("用户需要用 GitHub 账号创建远程仓库后推送。")
print("\n当前状态：已准备好推送，等待 GitHub 仓库 URL。")