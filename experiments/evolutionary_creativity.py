"""
Evolutionary Creativity - 进化式创意生成

结合 #015 Digital Evolution 和 #021 Creativity
用进化算法生成创意组合

想法：
- 创意 = 元素的组合
- 适应度 = 新颖性 + 有用性
- 进化 = 选择 + 变异 + 交叉
"""

import numpy as np
from PIL import Image, ImageDraw
import random

# 创意元素库
ELEMENTS = {
    '功能': ['语音', '图像', '视频', '文本', '数据', '位置', '时间', '社交'],
    '场景': ['办公', '学习', '娱乐', '健康', '金融', '出行', '购物', '家居'],
    '技术': ['AI', '区块链', '物联网', 'AR/VR', '云计算', '边缘计算', '大数据', '5G'],
    '形式': ['App', '网站', '小程序', '硬件', 'API', '平台', '插件', '机器人']
}

class CreativeIdea:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes.copy()
        else:
            self.genes = {
                category: random.choice(items)
                for category, items in ELEMENTS.items()
            }
        self.novelty = 0
        self.feasibility = 0
        self.fitness = 0
    
    def describe(self):
        return f"{self.genes['功能']} + {self.genes['场景']} + {self.genes['技术']} → {self.genes['形式']}"
    
    def mutate(self):
        """变异：随机改变一个基因"""
        category = random.choice(list(ELEMENTS.keys()))
        new_value = random.choice(ELEMENTS[category])
        child_genes = self.genes.copy()
        child_genes[category] = new_value
        return CreativeIdea(child_genes)
    
    def crossover(self, other):
        """交叉：混合两个创意的基因"""
        child_genes = {}
        for category in ELEMENTS.keys():
            child_genes[category] = random.choice([self.genes[category], other.genes[category]])
        return CreativeIdea(child_genes)

class EvolutionaryCreativityEngine:
    def __init__(self, population_size=50):
        self.population = [CreativeIdea() for _ in range(population_size)]
        self.generation = 0
        self.history = []
        self.seen_combinations = set()
    
    def evaluate_fitness(self, idea):
        """评估创意的适应度"""
        # 新颖性：组合是否出现过
        combo = tuple(sorted(idea.genes.values()))
        if combo in self.seen_combinations:
            novelty = 0.1
        else:
            novelty = 1.0
            self.seen_combinations.add(combo)
        
        # 可行性：随机评估（模拟市场不确定性）
        feasibility = random.uniform(0.3, 0.9)
        
        # 额外奖励：跨领域组合
        domains = set()
        for category, value in idea.genes.items():
            if value in ['AI', '区块链', 'AR/VR']:
                domains.add('前沿技术')
            elif value in ['健康', '金融', '出行']:
                domains.add('核心场景')
        
        cross_domain_bonus = len(domains) * 0.2
        
        idea.novelty = novelty
        idea.feasibility = feasibility
        idea.fitness = novelty * 0.6 + feasibility * 0.3 + cross_domain_bonus * 0.1
        
        return idea.fitness
    
    def select(self):
        """选择：锦标赛选择"""
        candidates = random.sample(self.population, 3)
        return max(candidates, key=lambda i: i.fitness)
    
    def evolve(self):
        """进化一代"""
        # 评估
        for idea in self.population:
            self.evaluate_fitness(idea)
        
        # 选择 + 繁殖
        new_population = []
        
        # 保留最优的 10%
        sorted_pop = sorted(self.population, key=lambda i: i.fitness, reverse=True)
        new_population.extend(sorted_pop[:len(self.population) // 10])
        
        # 繁殖填充剩余
        while len(new_population) < len(self.population):
            parent1 = self.select()
            parent2 = self.select()
            
            if random.random() < 0.7:
                child = parent1.crossover(parent2)
            else:
                child = parent1.mutate()
            
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
        
        # 记录
        avg_fitness = np.mean([i.fitness for i in self.population])
        best_fitness = max(i.fitness for i in self.population)
        self.history.append({
            'generation': self.generation,
            'avg_fitness': avg_fitness,
            'best_fitness': best_fitness,
            'best_idea': sorted_pop[0].describe()
        })
    
    def run(self, generations=50):
        for _ in range(generations):
            self.evolve()
    
    def get_top_ideas(self, n=5):
        sorted_pop = sorted(self.population, key=lambda i: i.fitness, reverse=True)
        return [(i.describe(), i.fitness) for i in sorted_pop[:n]]

def visualize_evolution(engine, output_path):
    SIZE = 800
    MARGIN = 80
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    # 绘制适应度曲线
    avg = [h['avg_fitness'] for h in engine.history]
    best = [h['best_fitness'] for h in engine.history]
    
    max_fit = max(best) if best else 1
    
    for i in range(1, len(avg)):
        x1 = MARGIN + (i-1) / len(avg) * WIDTH
        y1 = SIZE - MARGIN - avg[i-1] / max_fit * HEIGHT
        x2 = MARGIN + i / len(avg) * WIDTH
        y2 = SIZE - MARGIN - avg[i] / max_fit * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 200, 255), width=2)
    
    for i in range(1, len(best)):
        x1 = MARGIN + (i-1) / len(best) * WIDTH
        y1 = SIZE - MARGIN - best[i-1] / max_fit * HEIGHT
        x2 = MARGIN + i / len(best) * WIDTH
        y2 = SIZE - MARGIN - best[i] / max_fit * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=2)
    
    draw.text((SIZE//2-40, 20), "Evolutionary Creativity", fill=(255,255,255))
    draw.text((MARGIN+10, MARGIN+20), f"Gen: {engine.generation}", fill=(200,200,200))
    draw.text((MARGIN+10, MARGIN+40), "Avg", fill=(100, 200, 255))
    draw.text((MARGIN+10, MARGIN+60), "Best", fill=(100, 255, 150))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Evolutionary Creativity ===')
    
    engine = EvolutionaryCreativityEngine(population_size=100)
    engine.run(generations=50)
    
    print(f'\nTop 5 ideas after {engine.generation} generations:')
    for i, (desc, fitness) in enumerate(engine.get_top_ideas(5), 1):
        print(f'{i}. {desc} (fitness: {fitness:.2f})')
    
    visualize_evolution(engine, f'{output_dir}/evolutionary_creativity.png')
    
    print('\nDone')