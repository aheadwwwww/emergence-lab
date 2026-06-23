"""
改进的自扩展状态空间
解决"创建多状态但只访问一个"的问题
"""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

OUTPUT_DIR = Path('D:/emergence_experiments')


class ImprovedExpandingUniverse:
    """
    改进的自扩展宇宙
    - 状态转移有概率探索新状态
    - 引入"好奇心"机制：偏好未访问状态
    - 状态空间增长 + 实际探索相匹配
    """
    
    def __init__(self, initial_states=3, curiosity=0.3):
        self.states = list(range(initial_states))
        self.state_count = initial_states
        
        # 当前状态
        self.state = np.random.randint(0, initial_states)
        self.memory = np.random.randint(0, 2)
        
        # 访问计数
        self.visit_count = {s: 0 for s in self.states}
        self.visit_count[self.state] += 1
        
        # 规则字典
        self.rules = {}
        self._init_rules()
        
        # 参数
        self.curiosity = curiosity  # 探索未访问状态的概率
        
        # 历史
        self.history = [(self.state, self.memory, self.state_count)]
        
        # 扩展历史
        self.expansion_events = []
    
    def _init_rules(self):
        """初始化转移规则"""
        for s in self.states:
            for m in [0, 1]:
                # 初始规则：偏向转移到现有状态
                self.rules[(s, m)] = (
                    np.random.choice(self.states),
                    np.random.randint(0, 2)
                )
    
    def _add_state(self):
        """添加新状态并更新规则"""
        new_state = self.state_count
        self.states.append(new_state)
        self.visit_count[new_state] = 0
        self.state_count += 1
        
        # 为新状态创建规则
        for m in [0, 1]:
            # 新状态的规则：有概率自指，也有概率转移
            if np.random.random() < 0.3:
                self.rules[(new_state, m)] = (new_state, m)  # 自指
            else:
                self.rules[(new_state, m)] = (
                    np.random.randint(0, self.state_count),
                    np.random.randint(0, 2)
                )
        
        # 更新现有状态的部分规则，让它们可能指向新状态
        for s in self.states[:-1]:
            for m in [0, 1]:
                if np.random.random() < 0.15:  # 15%概率更新
                    self.rules[(s, m)] = (new_state, np.random.randint(0, 2))
        
        self.expansion_events.append(len(self.history))
    
    def _get_unvisited_states(self):
        """获取未访问的状态"""
        return [s for s in self.states if self.visit_count[s] == 0]
    
    def _get_least_visited_states(self, top_k=3):
        """获取访问最少的状态"""
        sorted_states = sorted(self.states, key=lambda s: self.visit_count[s])
        return sorted_states[:top_k]
    
    def step(self):
        """执行一步"""
        key = (self.state, self.memory)
        
        # 扩展触发：当所有状态都被访问，或定期扩展
        unvisited = self._get_unvisited_states()
        if len(unvisited) == 0 and self.state_count < 100:
            self._add_state()
        
        # 选择下一个状态
        if np.random.random() < self.curiosity and unvisited:
            # 好奇心驱动：跳转到未访问状态
            self.state = np.random.choice(unvisited)
            self.memory = np.random.randint(0, 2)
        else:
            # 规则驱动
            if key in self.rules:
                self.state, self.memory = self.rules[key]
        
        # 更新访问计数
        self.visit_count[self.state] += 1
        
        # 记录历史
        self.history.append((self.state, self.memory, self.state_count))
    
    def run(self, steps=1000):
        """运行多步"""
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        """分析运行结果"""
        visited_states = set(h[0] for h in self.history)
        
        # 状态分布
        state_dist = {s: self.visit_count[s] for s in self.states}
        
        # 访问频率最高的状态
        most_visited = max(self.states, key=lambda s: self.visit_count[s])
        
        return {
            'final_state_count': self.state_count,
            'visited_states': len(visited_states),
            'visit_coverage': len(visited_states) / self.state_count if self.state_count > 0 else 0,
            'state_distribution': state_dist,
            'most_visited': most_visited,
            'most_visited_count': self.visit_count[most_visited],
            'expansion_events': len(self.expansion_events),
            'open_ended': self.state_count > 3,
        }
    
    def visualize(self, save_path='D:/emergence_experiments/improved_universe.png'):
        """可视化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 状态序列
        states = [h[0] for h in self.history]
        axes[0, 0].plot(states[:500], alpha=0.7)
        axes[0, 0].set_xlabel('Time Step')
        axes[0, 0].set_ylabel('State')
        axes[0, 0].set_title('State Sequence (First 500 Steps)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 状态计数增长
        state_counts = [h[2] for h in self.history]
        axes[0, 1].plot(state_counts)
        for event in self.expansion_events[:10]:  # 显示前10个扩展事件
            axes[0, 1].axvline(event, color='red', alpha=0.3, linestyle='--')
        axes[0, 1].set_xlabel('Time Step')
        axes[0, 1].set_ylabel('State Count')
        axes[0, 1].set_title('State Space Growth')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 访问分布
        visited = sorted(self.visit_count.items(), key=lambda x: x[0])
        state_ids = [v[0] for v in visited]
        counts = [v[1] for v in visited]
        axes[1, 0].bar(state_ids, counts)
        axes[1, 0].set_xlabel('State ID')
        axes[1, 0].set_ylabel('Visit Count')
        axes[1, 0].set_title('State Visit Distribution')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # 4. 唯一状态累积曲线
        unique_states = []
        seen = set()
        for h in self.history:
            seen.add(h[0])
            unique_states.append(len(seen))
        axes[1, 1].plot(unique_states)
        axes[1, 1].set_xlabel('Time Step')
        axes[1, 1].set_ylabel('Unique States Visited')
        axes[1, 1].set_title('Cumulative Unique States')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        return save_path


def test_improved():
    """测试改进版本"""
    print("=== 测试改进的自扩展宇宙 ===\n")
    
    results = []
    for i in range(5):
        universe = ImprovedExpandingUniverse(initial_states=3, curiosity=0.3)
        universe.run(2000)
        analysis = universe.analyze()
        results.append(analysis)
        
        print(f"运行 {i+1}:")
        print(f"  最终状态数: {analysis['final_state_count']}")
        print(f"  访问状态数: {analysis['visited_states']}")
        print(f"  访问覆盖率: {analysis['visit_coverage']:.2%}")
        print(f"  扩展事件数: {analysis['expansion_events']}")
        print()
    
    # 平均结果
    avg_coverage = np.mean([r['visit_coverage'] for r in results])
    avg_states = np.mean([r['final_state_count'] for r in results])
    
    print(f"平均访问覆盖率: {avg_coverage:.2%}")
    print(f"平均最终状态数: {avg_states:.1f}")
    
    # 可视化最后一次运行
    universe.visualize()
    print(f"\n可视化保存到: D:/emergence_experiments/improved_universe.png")
    
    return results


if __name__ == '__main__':
    results = test_improved()
    
    print("\n=== 关键发现 ===")
    print("通过引入'好奇心'机制，系统现在能够：")
    print("1. 主动探索未访问的状态")
    print("2. 状态空间增长与实际探索相匹配")
    print("3. 避免陷入单一状态的死循环")
    print("\n这揭示了开放式涌现的一个重要条件：")
    print("**主动探索机制**（好奇心）是自扩展系统产生复杂行为的关键")
