import os

oc = os.path.expandvars(r'%USERPROFILE%\.openclaw')
print('=== .openclaw directory ===')

def walk_level(root, max_level=2):
    for entry in os.listdir(root):
        full = os.path.join(root, entry)
        if os.path.isdir(full):
            size = 0
            file_count = 0
            for r, d, files in os.walk(full):
                for f in files:
                    try:
                        size += os.path.getsize(os.path.join(r, f))
                    except:
                        pass
                    file_count += 1
            if size > 1024*1024:  # > 1MB
                print(f'  {entry}/ = {size/1024/1024:.1f} MB ({file_count} files)')

print('\nTop-level items:')
walk_level(oc)

# Check key subdirs
print('\nKey directories:')
for sub in ['agents', 'npm', 'memory', 'logs']:
    path = os.path.join(oc, sub)
    if os.path.exists(path):
        total = 0
        for r, d, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(r, f))
                except:
                    pass
        print(f'  {sub}/ = {total/1024/1024:.1f} MB')

# Check if workspace is in .openclaw
ws = os.path.join(oc, 'workspace')
if os.path.exists(ws):
    total = 0
    for r, d, files in os.walk(ws):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(r, f))
            except:
                pass
    print(f'  workspace/ = {total/1024/1024:.1f} MB')
else:
    print('  workspace/ = DOES NOT EXIST (good - workspace is on D:)')

# Check npm separately
npm = os.path.expandvars(r'%APPDATA%\npm')
if os.path.exists(npm):
    total = 0
    for r, d, files in os.walk(npm):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(r, f))
            except:
                pass
    print(f'\n%APPDATA%\\npm = {total/1024/1024:.1f} MB')
    # Show biggest subdirs
    dirs = {}
    for entry in os.listdir(npm):
        full = os.path.join(npm, entry)
        if os.path.isdir(full):
            size = 0
            for r, d, files in os.walk(full):
                for f in files:
                    try:
                        size += os.path.getsize(os.path.join(r, f))
                    except:
                        pass
            if size > 5*1024*1024:
                dirs[entry] = size
    for d, s in sorted(dirs.items(), key=lambda x: x[1], reverse=True):
        print(f'  {d}/ = {s/1024/1024:.1f} MB')
