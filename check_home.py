import os, subprocess, datetime

# Check env var
r = subprocess.run(['powershell', '-Command', '[System.Environment]::GetEnvironmentVariable("OPENCLAW_HOME", "User")'], capture_output=True, text=True)
print('OPENCLAW_HOME:', r.stdout.strip() or 'NOT SET')

# Check both locations
c_oc = os.path.expandvars(r'%USERPROFILE%\.openclaw')
d_oc = r'D:\openclaw_workspace\.openclaw'
print('C exists:', os.path.exists(c_oc))
print('D exists:', os.path.exists(d_oc))

# Check which one Gateway is using
for loc, label in [(c_oc, 'C'), (d_oc, 'D')]:
    if os.path.exists(loc):
        agents_dir = os.path.join(loc, 'agents', 'main', 'agent')
        db = os.path.join(agents_dir, 'openclaw-agent.sqlite')
        if os.path.exists(db):
            size = os.path.getsize(db)
            mtime = os.path.getmtime(db)
            mt = datetime.datetime.fromtimestamp(mtime)
            print(label, 'sqlite:', round(size/1024/1024, 1), 'MB, modified', mt)
        else:
            print(label, 'sqlite: not found')
