"""
Resilience - 韧性

系统承受扰动后恢复的能力
例：生态恢复、网络鲁棒性

本实验模拟网络韧性
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class ResilientNetwork:
    def __init__(self, n_nodes=100, edge_prob=0.08):
        self.n = n_nodes
        self.edges = {i: set() for i in range(n_nodes)}
        
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if random.random() < edge_prob:
                    self.edges[i].add(j)
                    self.edges[j].add(i)
        
        self.active = set(range(n_nodes))
    
    def remove_nodes(self, nodes):
        """移除节点（攻击/故障）"""
        for node in nodes:
            self.active.discard(node)
            for neighbor in self.edges[node]:
                self.edges[neighbor].discard(node)
    
    def largest_component_size(self):
        """计算最大连通分量"""
        if not self.active:
            return 0
        
        visited = set()
        max_size = 0
        
        for start in self.active:
            if start in visited:
                continue
            
            # BFS
            component = set()
            queue = [start]
            
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                
                for neighbor in self.edges[node]:
                    if neighbor in self.active and neighbor not in visited:
                        queue.append(neighbor)
            
            max_size = max(max_size, len(component))
        
        return max_size
    
    def resilience_test(self, attack_mode='random'):
        """韧性测试：逐步移除节点"""
        results = []
        nodes_to_remove = list(range(self.n))
        
        if attack_mode == 'targeted':
            # 针对性攻击：优先移除高度节点
            nodes_to_remove.sort(key=lambda n: len(self.edges[n]), reverse=True)
        else:
            random.shuffle(nodes_to_remove)
        
        for i in range(0, self.n, 5):
            self.remove_nodes(nodes_to_remove[i:i+5])
            size = self.largest_component_size()
            results.append({
                'removed': i + 5,
                'largest_component': size,
                'active_nodes': len(self.active)
            })
        
        return results

def visualize_resilience(results, output_path):
    """可视化韧性"""
    SIZE = 700
    MARGIN = 80
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    removed = [r['removed'] for r in results]
    component = [r['largest_component'] for r in results]
    
    max_nodes = results[0]['active_nodes'] if results else 100
    
    for i in range(1, len(results)):
        x1 = MARGIN + (i-1) / len(results) * WIDTH
        y1 = SIZE - MARGIN - component[i-1] / max_nodes * HEIGHT
        x2 = MARGIN + i / len(results) * WIDTH
        y2 = SIZE - MARGIN - component[i] / max_nodes * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=2)
    
    draw.text((SIZE//2-30, 20), "Resilience", fill=(255,255,255))
    draw.text((MARGIN+10, MARGIN+20), "Largest Component", fill=(100,255,150))
    draw.text((MARGIN+10, SIZE-40), "Nodes Removed", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Resilience ===')
    
    # 随机故障
    net1 = ResilientNetwork(n_nodes=100, edge_prob=0.1)
    results1 = net1.resilience_test('random')
    
    print(f'Random failure: {results1[-1]["largest_component"]} nodes remain')
    
    visualize_resilience(results1, f'{output_dir}/resilience.png')
    
    print('Done')