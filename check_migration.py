import os, subprocess

oc = os.path.expandvars(r'%USERPROFILE%\.openclaw')
print('C: .openclaw exists:', os.path.exists(oc))
if os.path.exists(oc):
    total = 0
    for r, d, files in os.walk(oc):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(r, f))
            except:
                pass
    print('C: .openclaw size:', round(total/1024/1024, 1), 'MB')

d_oc = r'D:\openclaw_workspace\.openclaw'
print('D: .openclaw exists:', os.path.exists(d_oc))
if os.path.exists(d_oc):
    total = 0
    for r, d, files in os.walk(d_oc):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(r, f))
            except:
                pass
    print('D: .openclaw size:', round(total/1024/1024, 1), 'MB')

# Check env var
r = subprocess.run(['powershell', '-Command', '[System.Environment]::GetEnvironmentVariable("OPENCLAW_HOME", "User")'], capture_output=True, text=True)
val = r.stdout.strip()
print('OPENCLAW_HOME (User):', val if val else 'NOT SET')

r2 = subprocess.run(['powershell', '-Command', '[System.Environment]::GetEnvironmentVariable("OPENCLAW_HOME", "Machine")'], capture_output=True, text=True)
val2 = r2.stdout.strip()
print('OPENCLAW_HOME (Machine):', val2 if val2 else 'NOT SET')

# Check if Gateway is running
r3 = subprocess.run(['powershell', '-Command', 'Get-Process -Name "node" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime'], capture_output=True, text=True)
print('\nNode processes:')
print(r3.stdout[:500] if r3.stdout else 'None')
