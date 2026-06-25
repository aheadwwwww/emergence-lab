import subprocess, shutil, os

# Move emergence_lab to temp location
src = 'D:\\openclaw_workspace\\emergence_lab'
dst = 'D:\\temp_emergence_lab'

print("Moving emergence_lab...")
shutil.copytree(src, dst)
print(f"Copied to {dst}")

# Remove old git stuff
shutil.rmtree(os.path.join(dst, '.git'))

# Create new git repo
os.chdir(dst)

subprocess.run('git init', shell=True, capture_output=True)
subprocess.run('git branch -M main', shell=True, capture_output=True)
subprocess.run('git config user.email "agent@openclaw.local"', shell=True, capture_output=True)
subprocess.run('git config user.name "OpenClaw Agent"', shell=True, capture_output=True)
subprocess.run('git add -A', shell=True, capture_output=True)

result = subprocess.run('git commit -m "v0.1.0: Lenia, NCA, PheromoneCA + emergence metrics"', 
                        shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)

print("\nNew repo ready at:", dst)
print("Now need to push...")