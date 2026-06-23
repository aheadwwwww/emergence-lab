"""
涌现式好奇实验 v4: 延长模拟时间寻找真正的黄金区间

关键发现: v3 的分析显示最大存活时间只有 25 步，
          这阻止了我们找到真正的黄金区间。

新方法:
1. 延长 max_steps 到 500 步
2. 调整能量消耗率（降低）让 agent 活得更久
3. 测试是否能找到 curiosity > 10% AND survival > 100 步的配置

假设: 如果能延长存活时间，黄金区间会浮现
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pathlib import Path

class ForagingAgentV4:
    """觅食智能体 v4 - 调整能量系统"""
    def __init__(self, world_size=20, memory_size=100, initial_energy=10, energy_decay=0.5):
        self.world_size = world_size
        self.memory_size = memory_size
        self.energy = initial_energy
        self.max_energy = 30
        self.energy_decay = energy_decay  # 每步能量消耗
        self.position = np.random.randint(0, world_size, 2)
        self.memory = []
        self.curious_actions = 0
        self.total_actions = 0
        self.food_eaten = 0
        
    def perceive(self, world):
        """感知周围环境"""
        x, y = self.position
        perception = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = (x + dx) % self.world_size, (y + dy) % self.world_size
                perception.append((nx, ny, world[nx, ny]))
        return perception
    
    def act(self, world, food_positions):
        """选择行动"""
        self.total_actions += 1
        
        perception = self.perceive(world)
        
        # 收集已知食物
        known_food = []
        
        for pos in self.memory:
            if pos in food_positions:
                known_food.append(pos)
        
        for nx, ny, has_food in perception:
            if has_food > 0 and (nx, ny) not in known_food:
                known_food.append((nx, ny))
        
        if known_food:
            # 利用模式
            distances = [np.abs(np.array(pos) - self.position).sum() for pos in known_food]
            nearest = known_food[np.argmin(distances)]
            
            dx = np.sign(nearest[0] - self.position[0])
            dy = np.sign(nearest[1] - self.position[1])
            
            new_x = (self.position[0] + dx) % self.world_size
            new_y = (self.position[1] + dy) % self.world_size
            self.position = np.array([new_x, new_y])
            
            self.energy -= self.energy_decay
            
            if tuple(self.position) in food_positions:
                self.energy = min(self.max_energy, self.energy + 8)
                self.food_eaten += 1
                food_positions.remove(tuple(self.position))
                if tuple(self.position) not in self.memory:
                    self.memory.append(tuple(self.position))
                    if len(self.memory) > self.memory_size:
                        self.memory.pop(0)
            
            return 'exploit'
        else:
            # 探索模式（好奇）
            self.curious_actions += 1
            dx, dy = np.random.randint(-1, 2, 2)
            new_x = (self.position[0] + dx) % self.world_size
            new_y = (self.position[1] + dy) % self.world_size
            self.position = np.array([new_x, new_y])
            
            self.energy -= self.energy_decay
            
            if tuple(self.position) in food_positions:
                self.energy = min(self.max_energy, self.energy + 8)
                self.food_eaten += 1
                food_positions.remove(tuple(self.position))
                if tuple(self.position) not in self.memory:
                    self.memory.append(tuple(self.position))
                    if len(self.memory) > self.memory_size:
                        self.memory.pop(0)
            
            return 'explore'
    
    def is_alive(self):
        return self.energy > 0


class ForagingWorldV4:
    """觅食宇宙 v4 - 增强的食物系统"""
    def __init__(self, size=20, food_regrowth_rate=0.01, initial_food_density=0.1, 
                 food_migration_rate=0.0, max_food=100):
        self.size = size
        self.food_regrowth_rate = food_regrowth_rate
        self.food_migration_rate = food_migration_rate
        self.max_food = max_food
        self.world = np.zeros((size, size))
        self.food_positions = set()
        
        # 初始化食物
        initial_food = min(int(size * size * initial_food_density), max_food)
        for _ in range(initial_food):
            x, y = np.random.randint(0, size, 2)
            self.world[x, y] = 1
            self.food_positions.add((x, y))
    
    def step(self):
        """世界演化"""
        # 食物再生（但有上限）
        if len(self.food_positions) < self.max_food:
            if np.random.random() < self.food_regrowth_rate:
                x, y = np.random.randint(0, self.size, 2)
                if (x, y) not in self.food_positions:
                    self.world[x, y] = 1
                    self.food_positions.add((x, y))


def run_experiment_v4(food_regrowth_rate, initial_food_density, initial_energy, 
                      max_steps=500, energy_decay=0.5):
    """运行单次实验 v4"""
    world = ForagingWorldV4(
        size=20,
        food_regrowth_rate=food_regrowth_rate,
        initial_food_density=initial_food_density,
        food_migration_rate=0.0,
        max_food=100
    )
    
    agent = ForagingAgentV4(
        world_size=20,
        memory_size=100,
        initial_energy=initial_energy,
        energy_decay=energy_decay
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
        'is_alive': agent.is_alive(),
        'food_eaten': agent.food_eaten,
        'curious_actions': agent.curious_actions,
        'total_actions': agent.total_actions
    }


def sweep_extended():
    """参数扫描 - 延长时间版"""
    
    # 参数范围 - 调整为更合理的范围
    regrowth_rates = np.linspace(0.01, 0.08, 8)
    food_densities = np.linspace(0.03, 0.15, 6)
    initial_energies = [10, 15, 20, 25, 30]
    energy_decays = [0.3, 0.5, 0.7]
    
    results = []
    
    total = len(regrowth_rates) * len(food_densities) * len(initial_energies) * len(energy_decays)
    print(f"开始扩展参数扫描，共 {total} 组实验...")
    
    count = 0
    for regrowth in regrowth_rates:
        for density in food_densities:
            for energy in initial_energies:
                for decay in energy_decays:
                    count += 1
                    if count % 50 == 0:
                        print(f"进度: {count}/{total}")
                    
                    result = run_experiment_v4(
                        food_regrowth_rate=regrowth,
                        initial_food_density=density,
                        initial_energy=energy,
                        max_steps=500,
                        energy_decay=decay
                    )
                    
                    results.append({
                        'regrowth': float(regrowth),
                        'density': float(density),
                        'energy': int(energy),
                        'decay': float(decay),
                        'curiosity_rate': result['curiosity_rate'],
                        'survival_steps': result['survival_steps'],
                        'is_alive': result['is_alive'],
                        'food_eaten': result['food_eaten']
                    })
    
    return results


def analyze_golden_zone(results):
    """分析黄金区间"""
    
    # 原始标准
    golden_original = [r for r in results if r['curiosity_rate'] > 0.1 and r['survival_steps'] > 100]
    
    # 宽松标准
    golden_relaxed = [r for r in results if r['curiosity_rate'] > 0.05 and r['survival_steps'] > 50]
    
    print("\n=== 黄金区间分析 ===")
    print(f"总实验数: {len(results)}")
    print(f"原始标准 (curiosity > 10%, survival > 100): {len(golden_original)} 组")
    print(f"宽松标准 (curiosity > 5%, survival > 50): {len(golden_relaxed)} 组")
    
    if golden_original:
        print("\n=== 最佳原始黄金区间配置 ===")
        sorted_golden = sorted(golden_original, key=lambda x: x['curiosity_rate'] * x['survival_steps'], reverse=True)
        for i, r in enumerate(sorted_golden[:5], 1):
            print(f"{i}. 再生率={r['regrowth']:.3f}, 密度={r['density']:.3f}, "
                  f"能量={r['energy']}, 衰减={r['decay']:.1f} → "
                  f"好奇={r['curiosity_rate']*100:.1f}%, 存活={r['survival_steps']}步, "
                  f"进食={r['food_eaten']}次")
    
    if golden_relaxed:
        print("\n=== 最佳宽松黄金区间配置 ===")
        sorted_relaxed = sorted(golden_relaxed, key=lambda x: x['curiosity_rate'] * x['survival_steps'], reverse=True)
        for i, r in enumerate(sorted_relaxed[:5], 1):
            print(f"{i}. 再生率={r['regrowth']:.3f}, 密度={r['density']:.3f}, "
                  f"能量={r['energy']}, 衰减={r['decay']:.1f} → "
                  f"好奇={r['curiosity_rate']*100:.1f}%, 存活={r['survival_steps']}步, "
                  f"进食={r['food_eaten']}次")
    
    return golden_original, golden_relaxed


def visualize_extended(results, output_dir):
    """可视化结果"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 提取数据
    curiosities = [r['curiosity_rate'] for r in results]
    survivals = [r['survival_steps'] for r in results]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. 存活步数分布
    ax1 = axes[0, 0]
    ax1.hist(survivals, bins=50, color='steelblue', edgecolor='white', alpha=0.7)
    ax1.axvline(100, color='red', linestyle='--', label='Golden threshold (100)')
    ax1.set_xlabel('Survival Steps', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title('Survival Steps Distribution', fontsize=14)
    ax1.legend()
    
    # 2. 好奇率分布
    ax2 = axes[0, 1]
    ax2.hist([c * 100 for c in curiosities], bins=50, color='coral', edgecolor='white', alpha=0.7)
    ax2.axvline(10, color='red', linestyle='--', label='Golden threshold (10%)')
    ax2.set_xlabel('Curiosity Rate (%)', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Curiosity Rate Distribution', fontsize=14)
    ax2.legend()
    
    # 3. 散点图
    ax3 = axes[1, 0]
    scatter = ax3.scatter(survivals, [c * 100 for c in curiosities], 
                         c=[r['energy'] for r in results], cmap='viridis', alpha=0.6)
    ax3.axhline(10, color='red', linestyle='--', alpha=0.5)
    ax3.axvline(100, color='red', linestyle='--', alpha=0.5)
    ax3.fill_between([100, 600], 10, 110, alpha=0.1, color='gold', label='Golden Zone')
    ax3.set_xlabel('Survival Steps', fontsize=12)
    ax3.set_ylabel('Curiosity Rate (%)', fontsize=12)
    ax3.set_title('Curiosity vs Survival (color=energy)', fontsize=14)
    plt.colorbar(scatter, ax=ax3, label='Energy')
    ax3.legend()
    
    # 4. 按能量衰减分组
    ax4 = axes[1, 1]
    decays = sorted(set(r['decay'] for r in results))
    for decay in decays:
        subset = [r for r in results if r['decay'] == decay]
        avg_survival = np.mean([r['survival_steps'] for r in subset])
        avg_curiosity = np.mean([r['curiosity_rate'] for r in subset]) * 100
        ax4.scatter(avg_survival, avg_curiosity, s=200, label=f'decay={decay}')
    ax4.set_xlabel('Average Survival Steps', fontsize=12)
    ax4.set_ylabel('Average Curiosity Rate (%)', fontsize=12)
    ax4.set_title('Performance by Energy Decay', fontsize=14)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'golden_zone_extended.png', dpi=150)
    plt.close()
    
    print(f"\n可视化已保存到: {output_dir / 'golden_zone_extended.png'}")


if __name__ == '__main__':
    # 运行实验
    results = sweep_extended()
    
    # 分析
    golden_original, golden_relaxed = analyze_golden_zone(results)
    
    # 保存结果
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_file = output_dir / f'golden_zone_extended_{timestamp}.json'
    
    with open(data_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n数据已保存到: {data_file}")
    
    # 可视化
    visualize_extended(results, output_dir)
    
    print("\n✅ 扩展实验完成！")
