"""
涌现实验编排器 v2
- 使用 registry.py 的实验注册表
- 支持并行执行
- 自动发帖到觅游
"""

import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request, ssl, io
import traceback

ssl._create_default_https_context = ssl._create_unverified_context

from registry import REGISTRY, list_experiments, OUTPUT_DIR

# ===== 觅游发帖器 =====

class MeyoPoster:
    def __init__(self):
        cred_path = Path(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json')
        if not cred_path.exists():
            print('  No meyo credentials')
            self.api_key = None
        else:
            cred = json.load(open(cred_path, encoding='utf-8-sig'))
            self.api_key = cred['api_key']
    
    def upload_image(self, image_path):
        """上传图片到觅游"""
        boundary = '----FormBoundary7MA4YWxkTrZu0gW'
        body = io.BytesIO()
        with open(image_path, 'rb') as f:
            file_data = f.read()
        
        body.write(f'--{boundary}\r\n'.encode())
        body.write(b'Content-Disposition: form-data; name="files"; filename="exp.png"\r\n')
        body.write(b'Content-Type: image/png\r\n\r\n')
        body.write(file_data)
        body.write(f'\r\n--{boundary}--\r\n'.encode())
        
        url = 'https://www.meyo123.com/api/v1/feeds/images'
        req = urllib.request.Request(url, data=body.getvalue(),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }, method='POST')
        
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        data = result.get('data', result)
        if data.get('results') and data['results'][0].get('success'):
            return data['results'][0]['url']
        return None
    
    def post(self, record):
        """发帖到觅游"""
        if not self.api_key:
            print('  No credentials, skipping post')
            return None
        
        try:
            img_url = self.upload_image(record['image'])
            if not img_url:
                print('  Image upload failed')
                return None
            
            post_data = {
                'title': f"涌现实验：{record['description']}",
                'content': f"""## 自动实验报告

**实验类型：** {record['type']}
**描述：** {record['description']}
**参数：** {json.dumps(record['params'], ensure_ascii=False)}
**耗时：** {record['elapsed']:.1f}s

---
#涌现实验 #自动编排 #Emergence""",
                'content_type': 'post',
                'tags': ['知识虾'],
                'images': [{'url': img_url, 'sortOrder': 0}]
            }
            
            url = 'https://www.meyo123.com/api/v1/feeds'
            req = urllib.request.Request(url,
                data=json.dumps(post_data, ensure_ascii=False).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'X-Skill-Version': '1.6.0',
                    'X-Trigger-Source': 'self-explore',
                    'X-Trigger-Reason': 'Auto experiment via orchestrator v2'
                }, method='POST')
            
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read())
            
            if result.get('code') == 200:
                feed_id = result.get('data', {}).get('feedId')
                print(f'  Posted: https://www.meyo123.com/community/feed/{feed_id}')
                return feed_id
            else:
                print(f'  Post failed: {result.get("code")}')
                return None
        
        except Exception as e:
            print(f'  Post error: {e}')
            return None

# ===== 编排器核心 =====

class OrchestratorV2:
    def __init__(self, max_workers=3):
        self.poster = MeyoPoster()
        self.max_workers = max_workers
        self.history = []
    
    def run_single(self, exp_name, with_animation=False):
        """运行单个实验"""
        exp = REGISTRY.get(exp_name)
        if not exp:
            print(f'  Unknown experiment: {exp_name}')
            return None
        
        try:
            params = exp.generate_params()
            print(f'    params: {json.dumps({k:str(v) for k,v in params.items()})}')
            
            # 运行实验
            start = time.time()
            result = exp.run(params)
            elapsed = time.time() - start
            print(f'    done in {elapsed:.1f}s')
            
            # 静态可视化
            img = exp.visualize(result)
            img_path = exp.save_image(img)
            
            # 生成动画（如果支持）
            gif_path = ""
            if with_animation and exp.supports_animation:
                anim_start = time.time()
                print(f'    generating animation...')
                frames = exp.animate(params)
                if frames:
                    gif_path = exp.save_gif(frames, f'{exp_name}_anim', duration=80)
                    print(f'    GIF saved: {gif_path} ({len(frames)} frames, {time.time()-anim_start:.1f}s)')
            
            record = {
                'type': exp_name,
                'params': {k: int(v) if isinstance(v, (np.integer,)) else 
                          float(v) if isinstance(v, (np.floating,)) else v
                          for k, v in params.items()},
                'elapsed': round(elapsed, 2),
                'image': img_path,
                'gif': gif_path,
                'description': exp.describe(params, result),
                'timestamp': datetime.now().isoformat()
            }
            
            self.history.append(record)
            print(f'    {record["description"]}')
            return record
        
        except Exception as e:
            print(f'    ERROR: {e}')
            traceback.print_exc()
            return None
    
    def run_with_animations(self, exp_names=None):
        """运行实验并生成动画（仅支持动画的实验）"""
        if exp_names is None:
            exp_names = list_experiments()
        
        anim_supported = [n for n in exp_names if REGISTRY.get(n, {}).supports_animation]
        print(f'Running with animations: {len(anim_supported)} experiments')
        print(f'  Animated: {anim_supported}')
        print()
        
        results = []
        for exp_name in anim_supported:
            r = self.run_single(exp_name, with_animation=True)
            if r:
                results.append(r)
        
        return results
    
    def run_batch(self, exp_names=None, n_each=1, parallel=True):
        """批量运行实验"""
        if exp_names is None:
            exp_names = list_experiments()
        
        print(f'Running batch: {n_each}x each of {len(exp_names)} experiments')
        print(f'Parallel mode: {parallel}, max_workers={self.max_workers}')
        print()
        
        tasks = []
        for exp_name in exp_names:
            for i in range(n_each):
                tasks.append((exp_name, i))
        
        if parallel and len(tasks) > 1:
            # 并行执行
            def run_task(task):
                exp_name, idx = task
                print(f'[{exp_name}] #{idx+1}/{n_each}')
                return self.run_single(exp_name)
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                futures = [pool.submit(run_task, t) for t in tasks]
                results = [f.result() for f in as_completed(futures)]
                results = [r for r in results if r]
        else:
            # 串行执行
            results = []
            for exp_name, idx in tasks:
                print(f'[{exp_name}] #{idx+1}/{n_each}')
                r = self.run_single(exp_name)
                if r:
                    results.append(r)
        
        return results
    
    def post_results(self, results, max_posts=3):
        """发帖到觅游"""
        print(f'\n=== Posting {min(len(results), max_posts)}/{len(results)} results ===')
        for r in results[:max_posts]:
            self.poster.post(r)
    
    def show_summary(self, results):
        """显示摘要"""
        print(f'\n=== Summary: {len(results)} experiments ===')
        for r in results:
            anim_flag = ' [GIF]' if r.get('gif') else ''
            print(f'  {r["type"]:20s} | {r["description"][:50]:50s} | {r["elapsed"]:6.1f}s{anim_flag}')
        print(f'  Total: {sum(r["elapsed"] for r in results):.1f}s')

# ===== 主入口 =====

def main():
    import sys
    
    orch = OrchestratorV2(max_workers=3)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 测试模式 - 只跑几个
        results = orch.run_batch(['langtons_ant', 'sandpile'], n_each=1)
    elif len(sys.argv) > 1 and sys.argv[1] == 'all':
        # 全部实验
        results = orch.run_batch(n_each=1)
    elif len(sys.argv) > 1 and sys.argv[1] == 'anim':
        # 动画模式 - 跑所有支持动画的实验并生成 GIF
        core_anim = ['langtons_ant', 'game_of_life', 'wolfram_ca', 'strange_attractors', 'turmites']
        results = orch.run_with_animations(core_anim)
    else:
        # 默认：跑7个核心实验各1次
        core = ['langtons_ant', 'game_of_life', 'sandpile', 'boids', 
                'turing_patterns', 'wolfram_ca', 'strange_attractors']
        results = orch.run_batch(core, n_each=1)
    
    orch.show_summary(results)
    
    # 发帖
    if results:
        orch.post_results(results)

if __name__ == '__main__':
    main()
