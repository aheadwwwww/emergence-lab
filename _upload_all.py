import urllib.request, base64, json, os

token = "github…4w6G"
username = "aheadwwwww"
repo = "emergence-lab"
api_base = f"https://api.github.com/repos/{username}/{repo}/contents"

def upload_file(filepath, local_fullpath):
    """Upload a file to GitHub via API"""
    url = f"{api_base}/{filepath.replace(chr(92), '/')}"
    
    with open(local_fullpath, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
    
    data = json.dumps({
        "message": f"Add {filepath}",
        "content": content
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenClaw"
        },
        method="PUT"
    )
    
    try:
        urllib.request.urlopen(req, timeout=30)
        print(f"OK {filepath}")
        return True
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        msg = error.get('message', str(e))[:100]
        if "sha wasn't supplied" in msg or "already exists" in msg or msg.startswith("sha"):
            print(f"OK {filepath} (exists)")
            return True
        print(f"FAIL {filepath}: {msg}")
        return False

base = r'D:\openclaw_workspace\emergence_lab'

# Files to upload
files = [
    # Root files
    ('.gitignore', os.path.join(base, '.gitignore')),
    ('README.md', os.path.join(base, 'README.md')),
    ('setup.py', os.path.join(base, 'setup.py')),
    ('__init__.py', os.path.join(base, '__init__.py')),
    ('requirements.txt', os.path.join(base, 'requirements.txt')),
    
    # Core
    ('core/__init__.py', os.path.join(base, 'core', '__init__.py')),
    ('core/metrics.py', os.path.join(base, 'core', 'metrics.py')),
    ('core/visualization.py', os.path.join(base, 'core', 'visualization.py')),
    
    # Models
    ('models/__init__.py', os.path.join(base, 'models', '__init__.py')),
    ('models/lenia.py', os.path.join(base, 'models', 'lenia.py')),
    ('models/nca.py', os.path.join(base, 'models', 'nca.py')),
    ('models/pheromone.py', os.path.join(base, 'models', 'pheromone.py')),
    
    # Experiments
    ('experiments/__init__.py', os.path.join(base, 'experiments', '__init__.py')),
    ('experiments/compare.py', os.path.join(base, 'experiments', 'compare.py')),
    ('experiments/lenia_glider.py', os.path.join(base, 'experiments', 'lenia_glider.py')),
    
    # Examples
    ('examples/__init__.py', os.path.join(base, 'examples', '__init__.py')),
    ('examples/example_lenia_basic.py', os.path.join(base, 'examples', 'example_lenia_basic.py')),
    ('examples/example_parameter_sweep.py', os.path.join(base, 'examples', 'example_parameter_sweep.py')),
    ('examples/example_nca.py', os.path.join(base, 'examples', 'example_nca.py')),
    ('examples/example_pheromone.py', os.path.join(base, 'examples', 'example_pheromone.py')),
    ('examples/example_comparison.py', os.path.join(base, 'examples', 'example_comparison.py')),
    
    # Docs
    ('docs/guide.md', os.path.join(base, 'docs', 'guide.md')),
    ('docs/api.md', os.path.join(base, 'docs', 'api.md')),
    
    # Output images
    ('examples/output/lenia_timeline.png', os.path.join(base, 'examples', 'output', 'lenia_timeline.png')),
    ('examples/output/nca_final.png', os.path.join(base, 'examples', 'output', 'nca_final.png')),
    ('examples/output/pheromone_final.png', os.path.join(base, 'examples', 'output', 'pheromone_final.png')),
    ('examples/output/emergence_comparison.png', os.path.join(base, 'examples', 'output', 'emergence_comparison.png')),
    ('examples/output/lenia_sweep_results.json', os.path.join(base, 'examples', 'output', 'lenia_sweep_results.json')),
]

print(f"Uploading {len(files)} files to {username}/{repo}...")
success = 0
fail = 0
for filepath, local_path in files:
    if os.path.exists(local_path):
        if upload_file(filepath, local_path):
            success += 1
        else:
            fail += 1
    else:
        print(f"SKIP {filepath} (not found)")

print(f"\nDone: {success} OK, {fail} FAIL")
print(f"URL: https://github.com/{username}/{repo}")
