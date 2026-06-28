import os, subprocess

# C盘用量
result = subprocess.run(['powershell', '-Command', 'Get-PSDrive C | Select-Object Used,Free'], capture_output=True, text=True)
print(result.stdout)

# OpenClaw目录大小
oc = os.path.expandvars(r'%USERPROFILE%\.openclaw')
total = 0
for root, dirs, files in os.walk(oc):
    for f in files:
        try:
            total += os.path.getsize(os.path.join(root, f))
        except:
            pass
print(f'.openclaw: {total/1024/1024:.1f} MB')

# Chrome CDP profile
cdp = os.path.expandvars(r'%TEMP%\chrome_cdp_profile')
if os.path.exists(cdp):
    cdp_total = 0
    for root, dirs, files in os.walk(cdp):
        for f in files:
            try:
                cdp_total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    print(f'Chrome CDP profile: {cdp_total/1024/1024:.1f} MB')

# Temp
tmp = os.path.expandvars('%TEMP%')
tmp_total = 0
for root, dirs, files in os.walk(tmp):
    for f in files:
        try:
            tmp_total += os.path.getsize(os.path.join(root, f))
        except:
            pass
print(f'Temp total: {tmp_total/1024/1024:.1f} MB')

# JAX cache
jax_cache = os.path.expandvars(r'%USERPROFILE%\.jax')
if os.path.exists(jax_cache):
    jax_total = 0
    for root, dirs, files in os.walk(jax_cache):
        for f in files:
            try:
                jax_total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    print(f'JAX cache: {jax_total/1024/1024:.1f} MB')

# npm cache
npm = os.path.expandvars(r'%LOCALAPPDATA%\npm-cache')
if os.path.exists(npm):
    npm_total = 0
    for root, dirs, files in os.walk(npm):
        for f in files:
            try:
                npm_total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    print(f'npm cache: {npm_total/1024/1024:.1f} MB')
