"""
多Agent觅食宇宙 - 社会网络分析
"""
import sys
sys.path.insert(0, 'D:\\openclaw_workspace\\experiments')
import encoding_fix

import numpy as np
from test_multiagent import MultiAgentForaging

print("=== 社会网络分析 (10 Agents) ===\n")

# 运行一次，记录详细数据
universe = MultiAgentForaging(num_agents=15, num_states=50)
universe.run(5000)

alive = [a for a in universe.agents if a['alive']]
dead = [a for a in universe.agents if not a['alive']]

print(f"存活: {len(alive)}/{len(universe.agents)}")
print(f"最长存活: {max(a['age'] for a in universe.agents)}步")
print(f"最短存活: {min(a['age'] for a in universe.agents)}步")
print()

# 构建社会网络
print("社会网络：")
for a in universe.agents:
    friends = len(a['encounters'])
    food = a['food_found']
    survived = a['age']
    status = '存活' if a['alive'] else '死亡'
    print(f"  Agent {a['id']}: 存活{survived}步, 食物{food:.0f}, 认识{friends}个Agent [{status}]")

# 分析：有社会交互的Agent是否存活更久？
social_agents = [a for a in universe.agents if len(a['encounters']) > 3]
solitary_agents = [a for a in universe.agents if len(a['encounters']) <= 3]

if social_agents and solitary_agents:
    social_survival = np.mean([a['age'] for a in social_agents])
    solitary_survival = np.mean([a['age'] for a in solitary_agents])
    print(f"\n社交型Agent平均存活: {social_survival:.1f}步")
    print(f"独行型Agent平均存活: {solitary_survival:.1f}步")
    
    diff = social_survival - solitary_survival
    if diff > 5:
        print(f"差异 {diff:.1f}步 -> 社交带来生存优势")
    elif diff > 0:
        print(f"差异 {diff:.1f}步 -> 社交有轻微优势")
    else:
        print(f"差异 {diff:.1f}步 -> 独行更优")
