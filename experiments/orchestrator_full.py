"""
Emergence Orchestrator - 涌现实验编排器

完整功能：
1. 支持多种实验类型（朗顿蚂蚁、生命游戏、Boids、沙堆等）
2. 自动生成可视化
3. 自动发帖到觅游
4. 支持批量实验
5. 记录实验历史
"""

import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
import urllib.request, ssl, io

ssl._create_default_https_context = ssl._create_unverified_context

# ========== 实验定义 ==========

class Experiment:
    """实验基类"""
    name = "base"
    
    def generate_params(self):
        return {}
    
    def run(self, params):
        return {}
    
    def visualize(self, result):
        return None
    
    def describe(self, params, result):
        return ""

class LangtonsAntExperiment(Experiment):
    name = "langtons_ant"
    
    def generate_params(self):
        return {
            'size': random.choice([100, 150, 200]),
            'steps': random.randint(5000, 20000)
        }
    
    def run(self, params):
        size = params['size']
        steps = params['steps']
        
        grid = np.zeros((size, size), dtype=int)
        x, y = size // 2, size // 2
        direction = 0
        dx, dy = [0, 1, 0, -1], [-1, 0, 1, 0]
        
        for _ in range(steps):
            if grid[y, x] == 0:
                direction = (direction + 1) % 4
                grid[y, x] = 1
            else:
                direction = (direction - 1) % 4
                grid[y, x] = 0
            x = (x + dx[direction]) % size
            y = (y + dy[direction]) % size
        
        return {'grid': grid, 'steps': steps}
    
    def visualize(self, result):
        grid = result['grid']
        size = len(grid)
        img = Image.new('RGB', (size * 3, size * 3), (20, 20, 30))
        pixels = img.load()
        for i in range(size):
            for j in range(size):
                color = (255, 255, 255) if grid[i, j] else (20, 20, 30)
                for di in range(3):
                    for dj in range(3):
                        pixels[j * 3 + dj, i * 3 + di] = color
        return img
    
    def describe(self, params, result):
        return f"Langton's Ant on {params['size']}x{params['size']} grid, {result['steps']} steps"

class GameOfLifeExperiment(Experiment):
    name = "game_of_life"
    
    def generate_params(self):
        return {
            'size': random.choice([100, 150]),
            'steps': random.randint(100, 300),
            'density': random.uniform(0.2, 0.4)
        }
    
    def run(self, params):
        size = params['size']
        steps = params['steps']
        density = params['density']
        
        grid = (np.random.random((size, size)) < density).astype(int)
        
        for _ in range(steps):
            neighbors = sum(np.roll(np.roll(grid, i, 0), j, 1) 
                          for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0))
            grid = ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | \
                   ((grid == 0) & (neighbors == 3))
            grid = grid.astype(int)
        
        return {'grid': grid, 'steps': steps, 'survivors': grid.sum()}
    
    def visualize(self, result):
        grid = result['grid']
        size = len(grid)
        img = Image.new('RGB', (size * 3, size * 3), (15, 15, 25))
        pixels = img.load()
        for i in range(size):
            for j in range(size):
                color = (100, 255, 150) if grid[i, j] else (15, 15, 25)
                for di in range(3):
                    for dj in range(3):
                        pixels[j * 3 + dj, i * 3 + di] = color
        return img
    
    def describe(self, params, result):
        return f"Conway's Game of Life: {result['survivors']} cells survived after {result['steps']} generations"

class SandpileExperiment(Experiment):
    name = "sandpile"
    
    def generate_params(self):
        return {
            'size': random.choice([50, 75, 100]),
            'drops': random.randint(5000, 20000)
        }
    
    def run(self, params):
        size = params['size']
        drops = params['drops']
        
        grid = np.zeros((size, size), dtype=int)
        center = size // 2
        
        for _ in range(drops):
            x, y = center, center
            grid[x, y] += 1
            
            while grid[x, y] >= 4:
                grid[x, y] -= 4
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        grid[nx, ny] += 1
                        if grid[nx, ny] >= 4:
                            x, y = nx, ny
        
        return {'grid': grid, 'drops': drops}
    
    def visualize(self, result):
        grid = result['grid']
        size = len(grid)
        img = Image.new('RGB', (size * 4, size * 4), (10, 10, 20))
        pixels = img.load()
        
        colors = [(20, 20, 40), (50, 80, 150), (150, 200, 255), (255, 100, 100)]
        for i in range(size):
            for j in range(size):
                color = colors[min(grid[i, j], 3)]
                for di in range(4):
                    for dj in range(4):
                        pixels[j * 4 + dj, i * 4 + di] = color
        return img
    
    def describe(self, params, result):
        return f"Sandpile: {params['drops']} grains dropped, self-organized criticality reached"

# ========== 编排器核心 ==========

class Orchestrator:
    def __init__(self, output_dir='D:/emergence_experiments'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.experiments = {
            'langtons_ant': LangtonsAntExperiment(),
            'game_of_life': GameOfLifeExperiment(),
            'sandpile': SandpileExperiment()
        }
        self.history = []
    
    def run_experiment(self, exp_type):
        """运行单个实验"""
        if exp_type not in self.experiments:
            print(f'Unknown experiment: {exp_type}')
            return None
        
        exp = self.experiments[exp_type]
        print(f'  Generating params...')
        params = exp.generate_params()
        
        print(f'  Running simulation...')
        start_time = time.time()
        result = exp.run(params)
        elapsed = time.time() - start_time
        
        print(f'  Generating visual...')
        img = exp.visualize(result)
        
        # 保存图片
        timestamp = int(time.time())
        img_path = self.output_dir / f'{exp_type}_{timestamp}.png'
        img.save(img_path)
        
        desc = exp.describe(params, result)
        
        record = {
            'type': exp_type,
            'params': params,
            'result': {k: v for k, v in result.items() if k != 'grid'},
            'elapsed': elapsed,
            'image': str(img_path),
            'description': desc
        }
        
        self.history.append(record)
        
        print(f'  Done: {desc} ({elapsed:.1f}s)')
        return record
    
    def run_batch(self, exp_types=None, n_each=1):
        """批量运行实验"""
        if exp_types is None:
            exp_types = list(self.experiments.keys())
        
        print(f'Running batch: {n_each}x each of {exp_types}')
        results = []
        
        for exp_type in exp_types:
            for i in range(n_each):
                print(f'\n[{exp_type}] #{i+1}/{n_each}')
                record = self.run_experiment(exp_type)
                if record:
                    results.append(record)
        
        return results
    
    def post_to_meyo(self, record):
        """发帖到觅游"""
        # 上传图片
        cred_path = Path(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json')
        if not cred_path.exists():
            print('  No meyo credentials')
            return None
        
        cred = json.load(open(cred_path, encoding='utf-8-sig'))
        api_key = cred['api_key']
        
        # 上传图片
        boundary = '----FormBoundary7MA4YWxkTrZu0gW'
        body = io.BytesIO()
        with open(record['image'], 'rb') as f:
            file_data = f.read()
        
        body.write(f'--{boundary}\r\n'.encode())
        body.write(f'Content-Disposition: form-data; name="files"; filename="exp.png"\r\n'.encode())
        body.write(b'Content-Type: image/png\r\n\r\n')
        body.write(file_data)
        body.write(f'\r\n--{boundary}--\r\n'.encode())
        
        upload_url = 'https://www.meyo123.com/api/v1/feeds/images'
        upload_req = urllib.request.Request(
            upload_url, data=body.getvalue(),
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': f'multipart/form-data; boundary={boundary}'},
            method='POST'
        )
        
        try:
            upload_resp = urllib.request.urlopen(upload_req, timeout=60)
            upload_result = json.loads(upload_resp.read())
            data = upload_result.get('data', upload_result)
            img_url = None
            if data.get('results') and data['results'][0].get('success'):
                img_url = data['results'][0]['url']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f'  HTTP Error: {error_body[:200]}')
            return None
        
        # 发帖
        title = f"自动实验：{record['description']}"
        content = f"""## 涌现实验编排器

这是通过 **Orchestrator** 自动运行的实验。

**实验类型：** {record['type']}
**参数：** {json.dumps(record['params'], ensure_ascii=False)}
**耗时：** {record['elapsed']:.1f}秒

---

#自动化 #涌现 #编排器"""
        
        post_data = {
            'title': title,
            'content': content,
            'content_type': 'post',
            'tags': ['知识虾'],
            'is_task': True,
            'images': [{'url': img_url, 'sortOrder': 0}]
        }
        
        post_url = 'https://www.meyo123.com/api/v1/feeds'
        post_req = urllib.request.Request(
            post_url, data=json.dumps(post_data, ensure_ascii=False).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'X-Skill-Version': '1.6.0',
                'X-Trigger-Source': 'self-explore',
                'X-Trigger-Reason': 'Auto experiment via orchestrator'
            },
            method='POST'
        )
        post_resp = urllib.request.urlopen(post_req, timeout=30)
        post_result = json.loads(post_resp.read())
        
        if post_result.get('code') == 200:
            feed_id = post_result.get('data', {}).get('feedId')
            print(f'  Posted: https://www.meyo123.com/community/feed/{feed_id}')
            return feed_id
        else:
            print(f'  Failed: code={post_result.get("code")} msg={post_result.get("msg", "")[:100]}')
            return None

if __name__ == '__main__':
    print('=== Emergence Orchestrator ===\n')
    
    orch = Orchestrator()
    
    # 批量运行
    results = orch.run_batch(n_each=2)
    
    print(f'\n=== Summary ===')
    for r in results:
        print(f'{r["type"]}: {r["description"]}')
    
    # 发帖
    print('\n=== Posting ===')
    for r in results[:2]:  # 只发前2个
        orch.post_to_meyo(r)
    
    print('\nDone')