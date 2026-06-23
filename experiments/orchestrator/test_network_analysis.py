"""
测试 NetworkX 分析模块与编排器的集成

运行选定的实验，然后用图论分析揭示隐藏结构。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from registry import get_experiment
from network_analysis import get_network_report
import time


def run_and_analyze(exp_name: str):
    """运行实验并返回网络分析报告"""
    exp = get_experiment(exp_name)
    if not exp:
        return None

    print(f"\n{'='*60}")
    print(f"  [{exp_name}] {exp.description}")
    print(f"{'='*60}")

    params = exp.generate_params()
    print(f"  Params: {params}")

    t0 = time.time()
    result = exp.run(params)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.2f}s: {exp.describe(params, result)}")

    report = get_network_report(exp_name, result, params)
    print(f"\n  Network Analysis:")
    for k, v in report.items():
        if isinstance(v, dict):
            print(f"  ├ {k}:")
            for sk, sv in v.items():
                print(f"  │  └ {sk}: {sv}")
        elif isinstance(v, list):
            print(f"  ├ {k}: {v[:6]}{'...' if len(v) > 6 else ''}")
        else:
            print(f"  ├ {k}: {v}")

    return report


if __name__ == '__main__':
    reports = {}
    for name in ['phase_transitions', 'game_of_life', 'sandpile', 'boids', 'gray_scott']:
        r = run_and_analyze(name)
        if r:
            reports[name] = r

    print(f"\n\n{'='*60}")
    print(f"  SUMMARY: {len(reports)} experiments analyzed via graph theory")
    print(f"{'='*60}")
    for name, r in reports.items():
        n_domains = r.get('n_domains', r.get('n_components', r.get('n_agents', '?')))
        leaders = r.get('leader_count', None)
        leaders_str = f", {leaders} leaders" if leaders is not None else ""
        print(f"  {name}: {n_domains} components{leaders_str}")
