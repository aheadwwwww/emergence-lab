"""
Emergence Experiment Orchestrator - 涌现实验编排器

逻辑编排：定义实验流程，自动执行

流程：
1. 定义实验参数
2. 运行模拟
3. 收集数据
4. 生成可视化
5. 发帖到觅游

用 DAG（有向无环图）表示依赖关系
"""

import json
import time
from pathlib import Path
from datetime import datetime

class Task:
    def __init__(self, name, func, dependencies=None):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.status = 'pending'  # pending, running, success, failed
        self.output = None
        self.start_time = None
        self.end_time = None
    
    def run(self, context):
        self.status = 'running'
        self.start_time = datetime.now()
        try:
            self.output = self.func(context)
            self.status = 'success'
        except Exception as e:
            self.output = str(e)
            self.status = 'failed'
        self.end_time = datetime.now()
        return self.output

class Workflow:
    def __init__(self, name):
        self.name = name
        self.tasks = {}
        self.context = {}
        self.history = []
    
    def add_task(self, task):
        self.tasks[task.name] = task
    
    def get_execution_order(self):
        """拓扑排序确定执行顺序"""
        visited = set()
        order = []
        
        def visit(name):
            if name in visited:
                return
            visited.add(name)
            for dep in self.tasks[name].dependencies:
                visit(dep)
            order.append(name)
        
        for name in self.tasks:
            visit(name)
        
        return order
    
    def run(self):
        order = self.get_execution_order()
        results = {}
        
        for name in order:
            task = self.tasks[name]
            print(f'  Running: {name}')
            output = task.run(self.context)
            results[name] = output
            self.context[name] = output
            
            if task.status == 'failed':
                print(f'  Failed: {name} - {output}')
                break
        
        self.history.append({
            'workflow': self.name,
            'timestamp': datetime.now().isoformat(),
            'results': {name: self.tasks[name].status for name in order}
        })
        
        return results

# 预定义的实验任务
def generate_params(context):
    """生成实验参数"""
    import random
    params = {
        'size': random.choice([50, 100, 200]),
        'steps': random.randint(100, 500),
        'seed': random.randint(0, 10000)
    }
    print(f'    Params: {params}')
    return params

def run_simulation(context):
    """运行模拟（以朗顿蚂蚁为例）"""
    params = context.get('generate_params', {})
    size = params.get('size', 100)
    steps = params.get('steps', 1000)
    
    import numpy as np
    grid = np.zeros((size, size), dtype=int)
    x, y = size // 2, size // 2
    direction = 0
    dx, dy = [0, 1, 0, -1], [-1, 0, 1, 0]
    
    for _ in range(steps):
        cell = grid[y, x]
        if cell == 0:
            direction = (direction + 1) % 4
            grid[y, x] = 1
        else:
            direction = (direction - 1) % 4
            grid[y, x] = 0
        x = (x + dx[direction]) % size
        y = (y + dy[direction]) % size
    
    print(f'    Simulation done: {steps} steps')
    return {'grid': grid, 'steps': steps}

def generate_visual(context):
    """生成可视化"""
    import numpy as np
    from PIL import Image
    
    sim_result = context.get('run_simulation', {})
    grid = sim_result.get('grid')
    
    if grid is None:
        return None
    
    size = len(grid)
    img = Image.new('RGB', (size * 4, size * 4), (20, 20, 30))
    pixels = img.load()
    
    for i in range(size):
        for j in range(size):
            color = (255, 255, 255) if grid[i, j] else (20, 20, 30)
            for di in range(4):
                for dj in range(4):
                    pixels[j * 4 + dj, i * 4 + di] = color
    
    output_path = f'C:/kb_cache/orchestrated_exp_{int(time.time())}.png'
    img.save(output_path)
    print(f'    Visual saved: {output_path}')
    return output_path

def create_post(context):
    """创建帖子内容"""
    params = context.get('generate_params', {})
    sim_result = context.get('run_simulation', {})
    
    title = f"编排实验：朗顿蚂蚁 ({params.get('size', 100)}x{params.get('size', 100)})"
    content = f"""
## 自动化涌现实验

这是通过**涌现实验编排器**自动生成的实验帖子。

**参数：**
- 网格大小：{params.get('size', 100)} x {params.get('size', 100)}
- 运行步数：{sim_result.get('steps', 0)}

**流程：**
1. 生成参数 → 2. 运行模拟 → 3. 生成可视化 → 4. 发帖

这个编排器可以自动运行任何涌现实验，无需人工干预。

---

#涌现实验 #自动化 #逻辑编排
"""
    print(f'    Post created: {title}')
    return {'title': title, 'content': content}

def main():
    print('=== Emergence Experiment Orchestrator ===\n')
    
    # 创建工作流
    workflow = Workflow('langtons_ant_auto')
    
    # 添加任务
    workflow.add_task(Task('generate_params', generate_params))
    workflow.add_task(Task('run_simulation', run_simulation, ['generate_params']))
    workflow.add_task(Task('generate_visual', generate_visual, ['run_simulation']))
    workflow.add_task(Task('create_post', create_post, ['generate_params', 'run_simulation']))
    
    # 运行工作流
    print('Running workflow...\n')
    results = workflow.run()
    
    print(f'\n=== Results ===')
    for name, status in workflow.tasks.items():
        print(f'{name}: {status.status}')
    
    # 显示帖子
    post = results.get('create_post', {})
    if post:
        print(f"\nTitle: {post.get('title')}")
    
    print('\nDone')

if __name__ == '__main__':
    main()