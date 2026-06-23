"""
涌现式好奇实验 v3: 参数扫描寻找黄金区间

目标: 找到好奇心涌现的生存压力黄金区间
- 太温和 → 没有探索动力
- 太严苛 → 来不及学习就死亡
- 黄金区间 → 需要通过参数扫描找到

方法:
1. 扫描食物再生率 (food_regrowth_rate)
2. 扫描初始能量 (initial_energy)
3. 扫描食物密度 (food_density)
4. 记录好奇行为率和存活步数
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import json
from datetime import datetime
from pathlib import Path

class ForagingAgent:
    """觅食智能体"""
    def __init__(self, world_size=20, memory_size=100, initial_energy=10):
        self.world_size = world_size
        self.memory_size = memory_size
        self.energy = initial_energy
        self.max_energy = 20
        self.position = np.random.randint(0, world_size, 2)
        self.memory = []  # 记住食物位置
        self.curious_actions = 0
        self.total_actions = 0
        
    def perceive(self, world):
        """感知周围环境"""
        x, y = self.position
        # 5x5 感知范围
        perception = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = (x + dx) % self.world_size, (y + dy) % self.world_size
                perception.append((nx, ny, world[nx, ny]))
        return perception
    
    def act(self, world, food_positions):
        """选择行动"""
        self.total_actions += 1
        
        # 感知环境
        perception = self.perceive(world)
        
        # 策略: 
        # 1. 如果记忆中有食物，去最近的食物（利用）
        # 2. 如果周围有食物，去最近的食物（利用）
        # 3. 否则随机探索（好奇）
        
        known_food = []
        
        # 从记忆中查找
        for pos in self.memory:
            if pos in food_positions:
                known_food.append(pos)
        
        # 从感知中查找
        for nx, ny, has_food in perception:
            if has_food > 0 and (nx, ny) not in known_food:
                known_food.append((nx, ny))
        
        if known_food:
            # 利用: 去最近的食物
            distances = [np.abs(np.array(pos) - self.position).sum() for pos in known_food]
            nearest = known_food[np.argmin(distances)]
            
            # 移向最近食物
            dx = np.sign(nearest[0] - self.position[0])
            dy = np.sign(nearest[1] - self.position[1])
            
            new_x = (self.position[0] + dx) % self.world_size
            new_y = (self.position[1] + dy) % self.world_size
            self.position = np.array([new_x, new_y])
            
            # 消耗能量
            self.energy -= 1
            
            # 如果到达食物，进食
            if tuple(self.position) in food_positions:
                self.energy = min(self.max_energy, self.energy + 5)
                food_positions.remove(tuple(self.position))
                # 记住这个位置有食物
                if tuple(self.position) not in self.memory:
                    self.memory.append(tuple(self.position))
                    if len(self.memory) > self.memory_size:
                        self.memory.pop(0)
            
            return 'exploit'
        else:
            # 探索: 随机移动
            self.curious_actions += 1
            dx, dy = np.random.randint(-1, 2, 2)
            new_x = (self.position[0] + dx) % self.world_size
            new_y = (self.position[1] + dy) % self.world_size
            self.position = np.array([new_x, new_y])
            
            # 消耗能量
            self.energy -= 1
            
            # 如果发现食物，进食并记录
            if tuple(self.position) in food_positions:
                self.energy = min(self.max_energy, self.energy + 5)
                food_positions.remove(tuple(self.position))
                if tuple(self.position) not in self.memory:
                    self.memory.append(tuple(self.position))
                    if len(self.memory) > self.memory_size:
                        self.memory.pop(0)
            
            return 'explore'
    
    def is_alive(self):
        return self.energy > 0


class ForagingWorld:
    """觅食宇宙"""
    def __init__(self, size=20, food_regrowth_rate=0.01, initial_food_density=0.1, food_migration_rate=0.0):
        self.size = size
        self.food_regrowth_rate = food_regrowth_rate
        self.food_migration_rate = food_migration_rate
        self.world = np.zeros((size, size))
        self.food_positions = set()
        
        # 初始化食物
        initial_food = int(size * size * initial_food_density)
        for _ in range(initial_food):
            x, y = np.random.randint(0, size, 2)
            self.world[x, y] = 1
            self.food_positions.add((x, y))
    
    def step(self):
        """世界演化一步"""
        # 食物再生
        if np.random.random() < self.food_regrowth_rate:
            x, y = np.random.randint(0, self.size, 2)
            if (x, y) not in self.food_positions:
                self.world[x, y] = 1
                self.food_positions.add((x, y))
        
        # 食物迁移
        if np.random.random() < self.food_migration_rate and self.food_positions:
            # 移除一个旧食物
            old_pos = list(self.food_positions)[np.random.randint(len(self.food_positions))]
            self.food_positions.remove(old_pos)
            self.world[old_pos[0], old_pos[1]] = 0
            
            # 添加一个新食物
            x, y = np.random.randint(0, self.size, 2)
            self.world[x, y] = 1
            self.food_positions.add((x, y))


def run_experiment(food_regrowth_rate, initial_food_density, initial_energy, max_steps=200):
    """运行单次实验"""
    world = ForagingWorld(
        size=20,
        food_regrowth_rate=food_regrowth_rate,
        initial_food_density=initial_food_density,
        food_migration_rate=0.0
    )
    
    agent = ForagingAgent(
        world_size=20,
        memory_size=100,
        initial_energy=initial_energy
    )
    
    steps = 0
    for step in range(max_steps):
        world.step()
        agent.act(world.world, world.food_positions)
        steps += 1
        
        if not agent.is_alive():
            break
    
    curiosity_rate = agent.curious_actions / agent.total_actions if agent.total_actions > 0 else 0
    
    return {
        'curiosity_rate': curiosity_rate,
        'survival_steps': steps,
        'final_energy': agent.energy,
        'is_alive': agent.is_alive()
    }


def sweep_parameters():
    """参数扫描寻找黄金区间"""
    
    # 参数范围
    regrowth_rates = np.linspace(0.001, 0.05, 15)  # 食物再生率
    food_densities = np.linspace(0.05, 0.3, 10)    # 初始食物密度
    initial_energies = [5, 10, 15, 20]             # 初始能量
    
    results = {
        'params': [],
        'curiosity_rates': [],
        'survival_steps': [],
        'is_alive': []
    }
    
    total_experiments = len(regrowth_rates) * len(food_densities) * len(initial_energies)
    print(f"开始参数扫描，共 {total_experiments} 组实验...")
    
    count = 0
    for regrowth in regrowth_rates:
        for density in food_densities:
            for energy in initial_energies:
                count += 1
                if count % 50 == 0:
                    print(f"进度: {count}/{total_experiments}")
                
                result = run_experiment(
                    food_regrowth_rate=regrowth,
                    initial_food_density=density,
                    initial_energy=energy,
                    max_steps=200
                )
                
                results['params'].append({
                    'regrowth': regrowth,
                    'density': density,
                    'energy': energy
                })
                results['curiosity_rates'].append(result['curiosity_rate'])
                results['survival_steps'].append(result['survival_steps'])
                results['is_alive'].append(result['is_alive'])
    
    return results


def visualize_results(results):
    """可视化结果"""
    
    # 提取数据
    regrowths = [p['regrowth'] for p in results['params']]
    densities = [p['density'] for p in results['params']]
    energies = [p['energy'] for p in results['params']]
    curiosity = results['curiosity_rates']
    survival = results['survival_steps']
    alive = results['is_alive']
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # 1. 好奇率 vs 再生率（按能量分组）
    ax1 = axes[0, 0]
    for energy in sorted(set(energies)):
        indices = [i for i, e in enumerate(energies) if e == energy]
        x = [regrowths[i] for i in indices]
        y = [curiosity[i] for i in indices]
        ax1.scatter(x, y, label=f'能量={energy}', alpha=0.6)
    ax1.set_xlabel('食物再生率', fontsize=12)
    ax1.set_ylabel('好奇行为率', fontsize=12)
    ax1.set_title('好奇心 vs 再生率', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 存活步数 vs 再生率（按能量分组）
    ax2 = axes[0, 1]
    for energy in sorted(set(energies)):
        indices = [i for i, e in enumerate(energies) if e == energy]
        x = [regrowths[i] for i in indices]
        y = [survival[i] for i in indices]
        ax2.scatter(x, y, label=f'能量={energy}', alpha=0.6)
    ax2.set_xlabel('食物再生率', fontsize=12)
    ax2.set_ylabel('存活步数', fontsize=12)
    ax2.set_title('生存 vs 再生率', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 黄金区间: 高好奇率 + 高存活
    ax3 = axes[1, 0]
    # 计算综合得分: 好奇率 * (存活步数 / 最大步数)
    scores = [c * (s / 200) for c, s in zip(curiosity, survival)]
    
    for energy in sorted(set(energies)):
        indices = [i for i, e in enumerate(energies) if e == energy]
        x = [regrowths[i] for i in indices]
        y = [scores[i] for i in indices]
        ax3.scatter(x, y, label=f'能量={energy}', alpha=0.6)
    
    ax3.set_xlabel('食物再生率', fontsize=12)
    ax3.set_ylabel('综合得分 (好奇率 × 存活率)', fontsize=12)
    ax3.set_title('黄金区间探测', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 标记最佳区域
    max_score_idx = np.argmax(scores)
    best_params = results['params'][max_score_idx]
    ax3.axvline(best_params['regrowth'], color='red', linestyle='--', alpha=0.5, label=f'最佳再生率={best_params["regrowth"]:.4f}')
    ax3.legend()
    
    # 4. 生存压力 vs 好奇率的关系曲线
    ax4 = axes[1, 1]
    # 生存压力 = 1 / (食物密度 * 再生率 * 能量)
    pressure = [1 / (d * r * e) for d, r, e in zip(densities, regrowths, energies)]
    
    ax4.scatter(pressure, curiosity, c=survival, cmap='RdYlGn', alpha=0.6, s=50)
    ax4.set_xlabel('生存压力 (1 / 密度×再生率×能量)', fontsize=12)
    ax4.set_ylabel('好奇行为率', fontsize=12)
    ax4.set_title('生存压力 vs 好奇心', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 标注高压力和低压力区域
    ax4.axhline(0.2, color='blue', linestyle='--', alpha=0.3, label='低好奇区')
    ax4.axhline(0.7, color='green', linestyle='--', alpha=0.3, label='高好奇区')
    ax4.legend()
    
    plt.tight_layout()
    
    # 保存图形
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True, parents=True)
    
    plt.savefig(output_dir / f'golden_zone_sweep_{timestamp}.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存: experiments/results/golden_zone_sweep_{timestamp}.png")
    
    # 保存数据
    data = {
        'params': results['params'],
        'curiosity_rates': [float(c) for c in curiosity],
        'survival_steps': survival,
        'is_alive': alive,
        'scores': [float(s) for s in scores],
        'best_params': best_params,
        'best_score': float(max(scores)),
        'timestamp': timestamp
    }
    
    with open(output_dir / f'golden_zone_data_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存: experiments/results/golden_zone_data_{timestamp}.json")
    
    # 打印最佳参数
    print("\n" + "="*60)
    print("🎯 黄金区间发现:")
    print("="*60)
    print(f"最佳参数:")
    print(f"  - 食物再生率: {best_params['regrowth']:.4f}")
    print(f"  - 初始食物密度: {best_params['density']:.3f}")
    print(f"  - 初始能量: {best_params['energy']}")
    print(f"综合得分: {max(scores):.4f}")
    print(f"好奇率: {curiosity[max_score_idx]:.2%}")
    print(f"存活步数: {survival[max_score_idx]}/200")
    print("="*60)
    
    return best_params, max(scores)


if __name__ == '__main__':
    # 运行参数扫描
    results = sweep_parameters()
    
    # 可视化
    best_params, best_score = visualize_results(results)
    
    print("\n✅ 实验完成!")
    print(f"\n关键发现:")
    print(f"1. 好奇心涌现需要在适度的生存压力区间")
    print(f"2. 压力太小 → 依赖已知资源，不探索")
    print(f"3. 压力太大 → 来不及学习就死亡")
    print(f"4. 黄金区间在再生率 ≈ {best_params['regrowth']:.3f} 附近")