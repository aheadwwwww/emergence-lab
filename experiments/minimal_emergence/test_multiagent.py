"""
多Agent觅食宇宙
多个好奇Agent在同一个环境中觅食
竞争、协作、社会结构是否会自发涌现？
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class MultiAgentForaging:
    """多Agent觅食宇宙"""
    
    def __init__(self, num_agents=5, num_states=50):
        self.num_states = num_states
        self.num_agents = num_agents
        self.day = 0
        
        # 食物（所有Agent共享）
        self.food = np.zeros(num_states, dtype=float)
        for _ in range(8):
            self._spawn_food()
        
        # Agent
        self.agents = []
        for i in range(num_agents):
            agent = {
                'id': i,
                'state': np.random.randint(0, num_states),
                'energy': 15,
                'max_energy': 30,
                'alive': True,
                'memory': np.full(num_states, 2.0),
                'forget_rate': 0.97,
                'exploration_weight': 0.3,
                'age': 0,
                'food_found': 0,
                'encounters': {}  # 遇到其他Agent的记录
            }
            self.agents.append(agent)
        
        # 共享信息（如果Agent们"交流"）
        self.shared_memory = np.full(num_states, 2.0)
        
        self.history = []
    
    def _spawn_food(self):
        state = np.random.randint(0, self.num_states)
        self.food[state] += np.random.randint(3, 10)
    
    def _agent_step(self, agent):
        """一个Agent走一步"""
        if not agent['alive']:
            return
        
        agent['age'] += 1
        
        # 决策
        # 如果能量低 -> 利用记忆
        # 如果能量高 -> 好奇探索
        # 如果遇到其他Agent -> 可能跟随
        if agent['energy'] < 5:
            # 快饿死了 -> 去记忆中最好的地方
            chosen = np.argmax(agent['memory'])
        elif np.random.random() < 0.3 and len(agent['encounters']) > 0:
            # 有时跟随其他Agent的位置
            # 如果另一个Agent之前在那里找到了食物
            other_positions = []
            for other_id, data in agent['encounters'].items():
                if data.get('food_found', 0) > 0:
                    other_positions.append(data['last_seen_at'])
            if other_positions:
                chosen = np.random.choice(other_positions)
            else:
                chosen = self._explore(agent)
        else:
            chosen = self._explore(agent)
        
        agent['state'] = chosen
        
        # 吃食物
        food_here = self.food[chosen]
        eaten = min(food_here, 3.0)
        self.food[chosen] -= eaten
        agent['energy'] = min(agent['max_energy'], agent['energy'] + eaten)
        if eaten > 0:
            agent['food_found'] += eaten
        
        # 更新记忆
        if food_here > 0:
            agent['memory'][chosen] += 0.3
        else:
            agent['memory'][chosen] *= 0.95
        
        # 遗忘
        agent['memory'] *= agent['forget_rate']
        agent['memory'] = np.clip(agent['memory'], 0.1, 10)
        
        # 基础代谢
        agent['energy'] -= 1
        
        # 死亡检查
        if agent['energy'] <= 0:
            agent['alive'] = False
    
    def _explore(self, agent):
        """好奇探索策略"""
        uncertainty = 1.0 / (agent['memory'] + 0.5)
        # 混合已知好的位置和未知位置
        known_good = agent['memory'] / 10.0
        blend = 0.3 * known_good + 0.7 * uncertainty
        blend = blend / blend.sum()
        return np.random.choice(self.num_states, p=blend)
    
    def step(self):
        self.day += 1
        
        # 1. 所有Agent轮流行动
        np.random.shuffle(self.agents)
        for agent in self.agents:
            self._agent_step(agent)
        
        # 2. Agent间相遇检测
        alive_agents = [a for a in self.agents if a['alive']]
        for i, a1 in enumerate(alive_agents):
            for a2 in alive_agents[i+1:]:
                if a1['state'] == a2['state']:
                    # 相遇：记录对方位置和食物情况
                    a1['encounters'][a2['id']] = {
                        'last_seen_at': a2['state'],
                        'food_found': a2['food_found']
                    }
                    a2['encounters'][a1['id']] = {
                        'last_seen_at': a1['state'],
                        'food_found': a1['food_found']
                    }
        
        # 3. 食物迁移
        if self.day % 15 == 0:
            depletion = np.random.randint(0, self.num_states)
            self.food[depletion] = 0
            self._spawn_food()
        
        self.history.append({
            'day': self.day,
            'alive_count': sum(1 for a in self.agents if a['alive']),
            'total_food': self.food.sum()
        })
    
    def run(self, max_steps=10000):
        for _ in range(max_steps):
            self.step()
            alive = sum(1 for a in self.agents if a['alive'])
            if alive == 0:
                break
        return self.history
    
    def analyze(self):
        survivals = [a['age'] for a in self.agents]
        visits_per_agent = [len(set([a['state']])) for a in self.agents]
        
        # 计算好奇行为
        curious_total = 0
        for a in self.agents:
            if hasattr(a, '_curious_moves'):
                curious_total += a['_curious_moves']
        
        return {
            'days': self.day,
            'agents_alive': sum(1 for a in self.agents if a['alive']),
            'avg_survival': np.mean(survivals),
            'max_survival': max(survivals),
            'avg_visits': np.mean(visits_per_agent),
            'encounters_total': sum(len(a['encounters']) for a in self.agents),
        }


if __name__ == '__main__':
    print("=== 多Agent觅食宇宙 ===\n")
    
    for num_agents in [2, 5, 10, 20]:
        print(f"\n--- {num_agents} 个Agent ---")
        results = []
        for trial in range(10):
            universe = MultiAgentForaging(num_agents=num_agents, num_states=50)
            universe.run(5000)
            result = universe.analyze()
            results.append(result)
        
        avg_survival = np.mean([r['avg_survival'] for r in results])
        max_survival = np.mean([r['max_survival'] for r in results])
        avg_encounters = np.mean([r['encounters_total'] for r in results])
        
        print(f"平均存活: {avg_survival:.1f}步")
        print(f"最长存活: {max_survival:.1f}步")
        print(f"平均相遇次数: {avg_encounters:.0f}")
        
        # 判断社会结构是否涌现
        if avg_encounters > 20:
            print(f"  -> 高频相遇：社会交互涌现")
        elif avg_encounters > 5:
            print(f"  -> 中等相遇：有一定社会交互")
        else:
            print(f"  -> 低频相遇：各自生存")
    
    print("\n\n结论：社会交互是否从生存压力中涌现？")
    print("关键因素：Agent数量 vs 资源密度")
    print("过多Agent -> 竞争激烈 -> 存活下降")
    print("过少Agent -> 没有社会交互")
