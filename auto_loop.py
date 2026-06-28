"""
Auto-exploration loop: 1-hour continuous work cycle.

Each cycle:
  1. Explore (GitHub, papers, codebases)
  2. Experiment (run, verify, iterate)
  3. Record (write findings to file)
  4. Commit (auto git push)
  5. Repeat

Runs for 60 minutes without stopping.
All output goes to files, NOT to user chat.
"""

import subprocess, json, time, ssl, urllib.request, os, sys
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
WORKSPACE = Path('D:/openclaw_workspace')
END_TIME = datetime.now() + timedelta(minutes=60)

LOG_PATH = WORKSPACE / 'memory' / 'auto-loop-log.md'

def log(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def git_commit(msg: str):
    """Commit all changes."""
    subprocess.run(['git', '-C', str(WORKSPACE), 'add', '-A'], capture_output=True)
    subprocess.run(['git', '-C', str(WORKSPACE), 'commit', '-m', msg], capture_output=True)

def github_search(query: str, sort='updated', per_page=15):
    """Search GitHub API."""
    url = f'https://api.github.com/search/repositories?q={query}&sort={sort}&per_page={per_page}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github+json'
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'items': [], 'error': str(e)}

def run_experiment(script: str):
    """Run a Python experiment script, return success."""
    try:
        result = subprocess.run(
            ['python', script],
            cwd=WORKSPACE / 'experiments',
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return True, result.stdout[-500:]
        else:
            return False, result.stderr[-500:]
    except Exception as e:
        return False, str(e)

# ====================================================================
# MAIN LOOP
# ====================================================================
def main():
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(f'# Auto-Loop Log\nStarted: {datetime.now().isoformat()}\nEnds: {END_TIME.isoformat()}\n\n')
    
    log("Auto-loop started. Running for 60 minutes.")
    cycle = 0
    
    while datetime.now() < END_TIME:
        cycle += 1
        remaining = (END_TIME - datetime.now()).total_seconds() / 60
        log(f"\n--- Cycle {cycle} ({remaining:.0f}m remaining) ---")
        
        # Phase 1: Explore
        log(f"Phase 1: Exploring...")
        queries = [
            'evolutionary+algorithm+emergence',
            'self-organizing+systems+python',
            'neural+cellular+automata+learning',
            'artificial+life+simulation+2026',
        ]
        query = queries[cycle % len(queries)]
        
        result = github_search(query)
        items = result.get('items', [])
        log(f"  Found {len(items)} repos for '{query}'")
        
        for item in items[:5]:
            name = item.get('full_name', '?')
            stars = item.get('stargazers_count', 0)
            desc = (item.get('description', '') or '')[:80]
            log(f"    {name} ({stars}★) - {desc}")
        
        # Save discovery
        discovery_file = WORKSPACE / 'exploration' / f'auto-loop-cycle{cycle}.json'
        with open(discovery_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cycle': cycle,
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'results': [{'name': i.get('full_name'), 'stars': i.get('stargazers_count'), 
                             'desc': i.get('description',''), 'url': i.get('html_url','')} 
                           for i in items[:10]]
            }, f, indent=2, ensure_ascii=False)
        log(f"  Saved to {discovery_file.name}")
        
        # Phase 2: Experiment
        log(f"Phase 2: Experimenting...")
        
        # Run Lenia with best params for visualization
        exp_script = WORKSPACE / 'experiments' / 'auto_run.py'
        exp_code = f'''
import jax, jax.numpy as jnp, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lenia_jax import make_kernel_fft, make_orbium
from pathlib import Path

R, mu, sigma, size, steps = 10, 0.1622, 0.0257, 128, 500
kernel_fft = make_kernel_fft((size, size), R)
grid = make_orbium((size, size), R)
dt = 0.1

for step in range(steps):
    grid_fft = jnp.fft.fft2(grid)
    conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
    growth = jnp.exp(-((conv - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
    grid = jnp.clip(grid + dt * growth, 0, 1)

final = np.array(grid)
mass = float(final.sum())
print(f"Steps: {steps}, Final mass: {mass:.2f}, Alive: {mass > 10}")

outdir = Path('output/auto_loop')
outdir.mkdir(parents=True, exist_ok=True)
plt.figure(figsize=(8, 8))
plt.imshow(final, cmap='viridis')
plt.title(f'Lenia R={R} mu={mu:.4f} sigma={sigma:.4f} (cycle {cycle})')
plt.axis('off')
plt.savefig(outdir / f'cycle{cycle}.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"Saved cycle{cycle}.png")
'''
        with open(exp_script, 'w') as f:
            f.write(exp_code)
        
        ok, output = run_experiment(str(exp_script))
        log(f"  {'OK' if ok else 'FAIL'}: {output[:200]}")
        
        # Phase 3: Record
        log(f"Phase 3: Recording...")
        summary = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'repos_found': len(items),
            'experiment_ok': ok,
        }
        
        with open(LOG_PATH.replace('.md', '.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Phase 4: Git commit
        log(f"Phase 4: Commit...")
        git_commit(f"auto-loop cycle {cycle}: explore {query} + experiment")
        
        # Wait between cycles
        if datetime.now() < END_TIME:
            wait = min(120, (END_TIME - datetime.now()).total_seconds())
            log(f"Waiting {wait:.0f}s before next cycle...")
            time.sleep(wait)
    
    log(f"\n{'='*50}")
    log(f"Auto-loop complete. {cycle} cycles in 60 minutes.")
    log(f"Log: {LOG_PATH}")
    
    git_commit(f"auto-loop: {cycle} cycles completed, final archive")

if __name__ == '__main__':
    main()
