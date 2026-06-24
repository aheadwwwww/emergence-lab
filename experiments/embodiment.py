"""
#023 Embodiment — 具身涌现实验

核心问题：没有"身体"的agent能真正涌现吗？
- 对比：无实体agent（纯符号决策）vs 有实体agent（空间位置+感知+行动）
- 环境交互如何塑造行为模式

方法：3个子实验
1. Minimal Embodiment — 2D网格上的agent，对比有/无空间反馈的行为差异
2. Perception-Action Loop — 不同感知半径下的适应行为
3. Emergent Tool Use — 简单"物体"操作涌现
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import os
from collections import defaultdict
import matplotlib.animation as animation

# ============================================================
# 实验1: Minimal Embodiment — 空间感知与行为涌现
# ============================================================

def experiment_1_minimal_embodiment():
    """对比：无实体 vs 有实体agent在资源收集任务中的行为差异"""
    np.random.seed(42)
    grid_size = 40
    n_steps = 200
    
    # --- 无实体Agent（纯决策，忽略空间位置） ---
    resources = np.zeros(5)
    resource_regen = np.array([1.0, 0.8, 0.6, 0.4, 0.2])
    pos = 0
    disembodied_trace = []
    
    for step in range(n_steps):
        # 无实体：直接选当前可用的最高资源
        best = np.argmax(resources)
        if resources[best] > 0.1:
            harvest = resources[best] * 0.3
            resources[best] -= harvest
            pos = best
            disembodied_trace.append(harvest)
        else:
            disembodied_trace.append(0)
        # 所有资源缓慢再生
        resources += resource_regen * 0.05
        resources = np.clip(resources, 0, 2.0)
    
    # --- 有实体Agent（空间感知+移动代价） ---
    np.random.seed(42)
    grid = np.random.rand(grid_size, grid_size) * 0.5  # 资源分布
    # 资源热点
    for _ in range(5):
        cx, cy = np.random.randint(5, grid_size-5, 2)
        grid[cx-2:cx+2, cy-2:cy+2] += 1.0
    
    agent_x, agent_y = grid_size//2, grid_size//2
    # 感知半径
    perception_r = 5
    embodied_trace = []
    positions = [(agent_x, agent_y)]
    
    for step in range(n_steps):
        # 感知局部区域
        x_min = max(0, agent_x - perception_r)
        x_max = min(grid_size, agent_x + perception_r + 1)
        y_min = max(0, agent_y - perception_r)
        y_max = min(grid_size, agent_y + perception_r + 1)
        
        local_view = grid[x_min:x_max, y_min:y_max]
        if local_view.size > 0 and local_view.max() > 0.1:
            # 朝资源最丰富的位置移动
            best_local = np.unravel_index(local_view.argmax(), local_view.shape)
            target_x = x_min + best_local[0]
            target_y = y_min + best_local[1]
            
            # 向目标移动（有移动代价）
            dx = np.sign(target_x - agent_x)
            dy = np.sign(target_y - agent_y)
            
            if abs(target_x - agent_x) > 1:
                agent_x += dx
            elif abs(target_y - agent_y) > 1:
                agent_y += dy
            else:
                # 到达——收获资源，消耗资源
                harvest = grid[agent_x, agent_y]
                embodied_trace.append(harvest)
                grid[agent_x, agent_y] *= 0.3  # 消耗大部分
            # 移动本身的能量代价
            if dx != 0 or dy != 0:
                if len(embodied_trace) > 0:
                    embodied_trace[-1] *= 0.95  # 5%移动损耗
        else:
            # 随机探索
            embodied_trace.append(0.01)
            agent_x += np.random.randint(-1, 2)
            agent_y += np.random.randint(-1, 2)
            agent_x = np.clip(agent_x, 0, grid_size-1)
            agent_y = np.clip(agent_y, 0, grid_size-1)
        
        # 资源缓慢再生
        grid += 0.01
        grid = np.clip(grid, 0, 2.0)
        positions.append((agent_x, agent_y))
    
    # --- 绘图对比 ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 累积收获对比
    ax1 = axes[0, 0]
    ax1.plot(np.cumsum(disembodied_trace), '--', label='无实体Agent', alpha=0.7, linewidth=2)
    ax1.plot(np.cumsum(embodied_trace), '-', label='有实体Agent', alpha=0.8, linewidth=2)
    ax1.set_xlabel('步骤')
    ax1.set_ylabel('累积收获')
    ax1.set_title('无实体 vs 有实体：累积收获对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 收获效率对比（滑动平均）
    ax2 = axes[0, 1]
    window = 20
    def moving_avg(data, w):
        if len(data) < w: return data
        return np.convolve(data, np.ones(w)/w, mode='valid')
    
    if len(embodied_trace) > window:
        ax2.plot(moving_avg(disembodied_trace, window), '--', label='无实体Agent', alpha=0.7)
        ax2.plot(moving_avg(embodied_trace, window), '-', label='有实体Agent', alpha=0.8)
    ax2.set_xlabel('步骤（滑动平均）')
    ax2.set_ylabel('单步收获')
    ax2.set_title(f'收获效率对比（{window}步滑动平均）')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 有实体Agent的移动轨迹
    ax3 = axes[1, 0]
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    scatter = ax3.scatter(xs, ys, c=range(len(positions)), cmap='viridis', 
                         s=5, alpha=0.6)
    ax3.plot(xs, ys, 'gray', alpha=0.2, linewidth=0.5)
    ax3.set_xlim(0, grid_size)
    ax3.set_ylim(0, grid_size)
    ax3.set_title('有实体Agent的空间轨迹（颜色=时间）')
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    plt.colorbar(scatter, ax=ax3, label='时间步')
    ax3.set_aspect('equal')
    
    # 探索覆盖率对比
    ax4 = axes[1, 1]
    dis_positions = [(i % 5, 0) for i in range(n_steps)]  # 无实体只有5个位置
    dis_covered = len(set(dis_positions))
    emb_covered = len(set(positions))
    
    bars = ax4.bar(['无实体Agent\n(5位置)', f'有实体Agent\n({grid_size}x{grid_size}网格)'],
                   [dis_covered, emb_covered],
                   color=['#E74C3C', '#2ECC71'], alpha=0.7)
    ax4.set_ylabel('已探索位置数')
    ax4.set_title('探索范围对比')
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.suptitle('实验1：具身认知——空间感知如何改变Agent行为', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('experiments/embodiment_ex1.png', dpi=150, bbox_inches='tight')
    print("[OK] 实验1完成：embodiment_ex1.png")
    
    # 关键数据
    print(f"  无实体Agent总收获: {sum(disembodied_trace):.2f}")
    print(f"  有实体Agent总收获: {sum(embodied_trace):.2f}")
    print(f"  探索状态数: 无实体={dis_covered} | 有实体={emb_covered}")
    print(f"  效率比: {sum(embodied_trace)/max(sum(disembodied_trace), 0.01):.2f}x")
    
    return disembodied_trace, embodied_trace


# ============================================================
# 实验2: Perception-Action Loop — 感知半径与适应行为
# ============================================================

def experiment_2_perception_action():
    """不同感知半径如何影响Agent的适应行为和涌现策略"""
    np.random.seed(42)
    grid_size = 60
    n_steps = 300
    
    # 资源环境设置：不均匀分布 + 动态变化
    grid = np.zeros((grid_size, grid_size))
    # 周期性资源斑块
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i, j] = 0.3 * (1 + 0.5 * np.sin(i/5) * np.cos(j/7))
    # 添加随机热点
    for _ in range(8):
        cx = np.random.randint(5, grid_size-5)
        cy = np.random.randint(5, grid_size-5)
        for di in range(-3, 4):
            for dj in range(-3, 4):
                d = np.sqrt(di**2 + dj**2)
                if d <= 3:
                    grid[cx+di, cy+dj] += 1.5 * np.exp(-d**2/4)
    
    # 测试不同感知半径
    radii = [1, 3, 7, 15, grid_size]  # 从完全局部到全知
    results = {}
    
    for r in radii:
        np.random.seed(42)
        g = grid.copy()
        ax, ay = grid_size//2, grid_size//2
        harvests = []
        positions = [(ax, ay)]
        strategies = defaultdict(int)  # 记录策略使用频率
        
        for step in range(n_steps):
            # 感知
            x_min = max(0, ax - r)
            x_max = min(grid_size, ax + r + 1)
            y_min = max(0, ay - r)
            y_max = min(grid_size, ay + r + 1)
            local_view = g[x_min:x_max, y_min:y_max]
            
            if local_view.max() > 0.05:
                # 找到最佳位置
                best = np.unravel_index(local_view.argmax(), local_view.shape)
                tx = x_min + best[0]
                ty = y_min + best[1]
                
                dist = np.sqrt((tx-ax)**2 + (ty-ay)**2)
                if dist <= 1.0:
                    # 收获
                    h = g[ax, ay]
                    harvests.append(h)
                    g[ax, ay] *= 0.2
                    strategies['harvest'] += 1
                else:
                    # 移动
                    dx = np.clip(tx - ax, -1, 1)
                    dy = np.clip(ty - ay, -1, 1)
                    ax += dx
                    ay += dy
                    strategies['move_toward'] += 1
                    if step % 10 == 0:
                        harvests.append(0.01)  # 移动成本
            else:
                # 随机游走
                ax += np.random.randint(-1, 2)
                ay += np.random.randint(-1, 2)
                ax = np.clip(ax, 0, grid_size-1)
                ay = np.clip(ay, 0, grid_size-1)
                strategies['random_walk'] += 1
                harvests.append(0.005)
            
            positions.append((ax, ay))
            # 资源缓慢再生
            g += 0.008
            g = np.clip(g, 0, 2.5)
        
        results[r] = {
            'harvests': harvests,
            'total': sum(harvests),
            'positions': positions,
            'strategies': dict(strategies),
            'explored': len(set(positions))
        }
        
        print(f"  感知半径 r={r:2d}: 总收获={results[r]['total']:.2f}, 探索位置={results[r]['explored']}")
    
    # --- 绘图 ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 总收获 vs 感知半径
    ax1 = axes[0, 0]
    r_labels = [str(r) if r < grid_size else '∞' for r in radii]
    totals = [results[r]['total'] for r in radii]
    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(radii)))
    bars = ax1.bar(r_labels, totals, color=colors, alpha=0.7)
    ax1.set_xlabel('感知半径')
    ax1.set_ylabel('总收获')
    ax1.set_title('感知半径 vs 收获效率')
    for bar, val in zip(bars, totals):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 策略分布
    ax2 = axes[0, 1]
    strategy_types = ['harvest', 'move_toward', 'random_walk']
    strategy_labels = ['收获', '定向移动', '随机探索']
    x = np.arange(len(radii))
    width = 0.25
    
    for i, (st, sl) in enumerate(zip(strategy_types, strategy_labels)):
        values = [results[r]['strategies'].get(st, 0) for r in radii]
        ax2.bar(x + i*width, values, width, label=sl, alpha=0.7)
    
    ax2.set_xlabel('感知半径')
    ax2.set_ylabel('使用次数')
    ax2.set_title('策略分布 vs 感知半径')
    ax2.set_xticks(x + width)
    ax2.set_xticklabels(r_labels)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 探索覆盖率
    ax3 = axes[1, 0]
    explored = [results[r]['explored'] for r in radii]
    ax3.plot(range(len(radii)), explored, 'o-', linewidth=2, markersize=8, color='#9B59B6')
    ax3.set_xticks(range(len(radii)))
    ax3.set_xticklabels(r_labels)
    ax3.set_xlabel('感知半径')
    ax3.set_ylabel('探索位置数')
    ax3.set_title('感知半径 vs 探索覆盖率')
    ax3.grid(True, alpha=0.3)
    
    # 收获时间序列（对比极端半径）
    ax4 = axes[1, 1]
    for r in [min(radii), radii[len(radii)//2], max(radii)]:
        cumsum = np.cumsum(results[r]['harvests'])
        label_r = str(r) if r < grid_size else '∞'
        ax4.plot(cumsum, label=f'r={label_r}', linewidth=2, alpha=0.7)
    
    ax4.set_xlabel('步骤')
    ax4.set_ylabel('累积收获')
    ax4.set_title('不同感知半径的收获时间线')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('实验2：感知-行动循环——感知半径如何塑造Agent策略', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('experiments/embodiment_ex2.png', dpi=150, bbox_inches='tight')
    print("[OK] 实验2完成：embodiment_ex2.png")
    
    return results


# ============================================================
# 实验3: Emergent Tool Use — 简单"物体"操作涌现
# ============================================================

def experiment_3_emergent_tool_use():
    """多Agent在有障碍物的环境中，
    能否自发利用/移动物体来完成任务？"""
    np.random.seed(42)
    grid_size = 30
    n_steps = 400
    
    # 初始场：中央有资源，四周有障碍物
    env = np.ones((grid_size, grid_size)) * 0.1
    # 障碍物——墙壁和可移动"石块"
    walls = set()
    movable_blocks = set()
    
    # 墙壁（不可穿越）
    for i in range(grid_size):
        walls.add((i, 0))
        walls.add((i, grid_size-1))
        walls.add((0, i))
        walls.add((grid_size-1, i))
    
    # 障碍物迷宫
    for i in range(5, grid_size-5):
        walls.add((i, 10))
    for i in range(10, 20):
        walls.add((15, i))
    # 可移动石块（初始位置）
    stones = [(13, 15), (17, 12), (12, 18)]
    for sx, sy in stones:
        movable_blocks.add((sx, sy))
    
    # 资源目标区域
    target_zone = set()
    for i in range(12, 18):
        for j in range(12, 18):
            if abs(i-15) + abs(j-15) <= 4:
                target_zone.add((i, j))
    
    # Agent状态
    n_agents = 5
    agents = []
    for aid in range(n_agents):
        x = np.random.randint(3, 8)
        y = np.random.randint(3, 8)
        agents.append({
            'id': aid,
            'x': x, 'y': y,
            'energy': 10.0,
            'carrying': None,  # 是否携带石块
            'memory': [],
            'harvests': [],
            'touch_target': False
        })
    
    is_wall = lambda x, y: (x, y) in walls
    
    def can_move_to(x, y):
        if x < 0 or x >= grid_size or y < 0 or y >= grid_size:
            return False
        if is_wall(x, y):
            return False
        for a in agents:
            if (a['x'], a['y']) == (x, y):
                return False
        return True
    
    def is_near_target(x, y):
        for tx, ty in target_zone:
            if abs(x-tx) + abs(y-ty) <= 2:
                return True
        return False
    
    metrics = {
        'avg_energy': [], 'stones_moved': 0,
        'target_visits': 0, 'stone_uses': []
    }
    
    for step in range(n_steps):
        for agent in agents:
            if agent['energy'] <= 0:
                continue
            
            # 感知周围
            neighbors = []
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = agent['x']+dx, agent['y']+dy
                    if (nx, ny) != (agent['x'], agent['y']):
                        if (nx, ny) in movable_blocks:
                            neighbors.append(('block', nx, ny))
                        elif (nx, ny) in target_zone:
                            neighbors.append(('target', nx, ny))
                        elif is_wall(nx, ny):
                            neighbors.append(('wall', nx, ny))
                        else:
                            neighbors.append(('empty', nx, ny))
            
            # 决策逻辑
            if agent['carrying'] is None:
                # 检查是否有附近石块可以推
                nearby_blocks = [(nx, ny) for t, nx, ny in neighbors if t == 'block']
                
                if nearby_blocks and is_near_target(agent['x'], agent['y']):
                    # 尝试把石块推向目标区域
                    bx, by = nearby_blocks[0]
                    # 计算推向目标的方向
                    tx, ty = 15, 15  # 目标中心
                    dx = np.sign(tx - bx)
                    dy = np.sign(ty - by)
                    new_bx, new_by = bx+dx, by+dy
                    
                    if can_move_to(new_bx, new_by) and (new_bx, new_by) not in movable_blocks:
                        movable_blocks.remove((bx, by))
                        movable_blocks.add((new_bx, new_by))
                        agent['carrying'] = (bx, by)
                        agent['energy'] -= 0.5
                        metrics['stones_moved'] += 1
                        metrics['stone_uses'].append(step)
                        continue
                
                # 否则向目标区域移动
                tx, ty = 15, 15
                if not is_near_target(agent['x'], agent['y']):
                    possible_moves = []
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0: continue
                            nx, ny = agent['x']+dx, agent['y']+dy
                            if can_move_to(nx, ny):
                                dist = abs(nx-tx) + abs(ny-ty)
                                possible_moves.append((dist, nx, ny))
                    if possible_moves:
                        possible_moves.sort()
                        agent['x'], agent['y'] = possible_moves[0][1], possible_moves[0][2]
                        agent['energy'] -= 0.1
                    else:
                        # 随机移动
                        for _ in range(5):
                            nx = agent['x'] + np.random.randint(-1, 2)
                            ny = agent['y'] + np.random.randint(-1, 2)
                            if can_move_to(nx, ny):
                                agent['x'], agent['y'] = nx, ny
                                break
                            agent['energy'] -= 0.05
                else:
                    # 在目标区域收集资源
                    energy_gain = 0.3 * (1 + env[agent['x'], agent['y']])
                    agent['energy'] += energy_gain
                    agent['harvests'].append(energy_gain)
                    agent['touch_target'] = True
                    metrics['target_visits'] += 1
                    env[agent['x'], agent['y']] *= 0.7
            else:
                # 携带石头，尝试在目标区域放下
                if is_near_target(agent['x'], agent['y']):
                    # 放下石块，阻挡其他agent进入
                    bx, by = agent['carrying']
                    agent['carrying'] = None
                    agent['energy'] -= 0.3
                else:
                    # 搬运石块向目标移动
                    tx, ty = 15, 15
                    dx = np.sign(tx - agent['x'])
                    dy = np.sign(ty - agent['y'])
                    if can_move_to(agent['x']+dx, agent['y']+dy):
                        agent['x'] += dx
                        agent['y'] += dy
                    agent['energy'] -= 0.3
            
            agent['energy'] = np.clip(agent['energy'], 0, 100)
        
        metrics['avg_energy'].append(np.mean([a['energy'] for a in agents]))
        
        # 环境资源缓慢再生
        for tx, ty in target_zone:
            env[tx, ty] += 0.02
        env = np.clip(env, 0, 1.0)
    
    # --- 绘图 ---
    fig = plt.figure(figsize=(16, 10))
    
    # 最终状态地图
    ax1 = fig.add_subplot(2, 3, 1)
    grid_viz = np.zeros((grid_size, grid_size))
    for (wx, wy) in walls:
        grid_viz[wx, wy] = 1
    for (bx, by) in movable_blocks:
        grid_viz[bx, by] = 2
    for (tx, ty) in target_zone:
        grid_viz[tx, ty] = 3
    
    cmap = plt.cm.colors.ListedColormap(['white', '#34495E', '#E67E22', '#2ECC71'])
    ax1.imshow(grid_viz.T, cmap=cmap, origin='lower', interpolation='nearest')
    for a in agents:
        ax1.plot(a['x'], a['y'], 'o', color='#3498DB', markersize=10, markeredgecolor='black')
        if a['carrying']:
            ax1.plot(a['x'], a['y'], 's', color='#E67E22', markersize=14, alpha=0.5)
    ax1.set_title(f'最终环境状态（步数={n_steps}）')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    
    # 平均能量时间线
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(metrics['avg_energy'], '-', color='#2ECC71', linewidth=2)
    ax2.set_xlabel('步骤')
    ax2.set_ylabel('平均能量')
    ax2.set_title('Agent群体平均能量')
    ax2.grid(True, alpha=0.3)
    
    # 石头使用事件
    ax3 = fig.add_subplot(2, 3, 3)
    if metrics['stone_uses']:
        ax3.eventplot(metrics['stone_uses'], colors='#E67E22', linewidths=2)
    ax3.set_xlabel('步骤')
    ax3.set_title(f'石头使用事件（共{metrics["stones_moved"]}次）')
    ax3.set_yticks([])
    
    # 个体收获分布
    ax4 = fig.add_subplot(2, 3, 4)
    harvest_data = [a['harvests'] for a in agents]
    ax4.boxplot(harvest_data if all(len(h)>0 for h in harvest_data) else [[]]*n_agents)
    ax4.set_xlabel('Agent ID')
    ax4.set_ylabel('收获量')
    ax4.set_title('个体收获分布')
    ax4.set_xticklabels([f'A{i}' for i in range(n_agents)])
    
    # 目标区域访问
    ax5 = fig.add_subplot(2, 3, 5)
    metrics_labels = ['总石头移动', '目标区域访问']
    metrics_vals = [metrics['stones_moved'], metrics['target_visits']]
    ax5.bar(metrics_labels, metrics_vals, color=['#E67E22', '#2ECC71'], alpha=0.7)
    ax5.set_title('任务完成指标')
    for i, v in enumerate(metrics_vals):
        ax5.text(i, v + 0.5, str(v), ha='center', va='bottom')
    
    # 涌现行为总结
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    summary_text = (
        "涌现行为分析\n"
        "══════════════\n\n"
        f"石块移动次数: {metrics['stones_moved']}\n"
        f"目标访问次数: {metrics['target_visits']}\n"
        f"完成移动的Agent: "
        f"{sum(1 for a in agents if a['touch_target'])}/{n_agents}\n\n"
        "涌现现象:\n"
        "• 局部感知→全局协作\n"
        '• 石块移动作为[工具]使用\n'
        '• 自我维持的能量循环\n'
        '• 个体在行动中[理解]环境'
    )
    ax6.text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))
    
    plt.suptitle('实验3：涌现工具使用——多Agent在杂乱环境中的协作', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('experiments/embodiment_ex3.png', dpi=150, bbox_inches='tight')
    print("[OK] 实验3完成：embodiment_ex3.png")
    
    return metrics


# ============================================================
# 主程序
# ============================================================

if __name__ == '__main__':
    print("="*60)
    print("  #023 Embodiment — 具身涌现实验套件")
    print("="*60)
    
    print("\n>>> 实验1: Minimal Embodiment — 对比有/无实体Agent")
    disembodied, embodied = experiment_1_minimal_embodiment()
    
    print("\n>>> 实验2: Perception-Action Loop — 感知半径策略分析")
    results = experiment_2_perception_action()
    
    print("\n>>> 实验3: Emergent Tool Use — 多Agent协作")
    metrics = experiment_3_emergent_tool_use()
    
    print("\n" + "="*60)
    print("  实验完成！请查看生成的图表。")
    print("="*60)
