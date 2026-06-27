#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芒格思维模型翻译脚本 - 补充m17-m30
继续翻译description, keywords字段
"""

dst = r'D:\openclaw_workspace\canvas\munger-models-zh.html'

with open(dst, 'r', encoding='utf-8') as f:
    content = f.read()

print("补充翻译 m17-m30...")

replacements = []

# m17 摩擦与粘度
replacements.append(("description: 'Friction and viscosity are forces that resist motion. Friction opposes the sliding of surfaces against each other, while viscosity is the internal resistance of a fluid to flow. In any system, these forces represent the costs, drags, and inefficiencies that slow down progress. Reducing friction is often a more effective strategy for improvement than simply applying more force.'", "description: '摩擦和粘度是抵抗运动的力。摩擦反对表面彼此滑动，而粘度是流体流动的内部阻力。在任何系统中，这些力代表减慢进度成本、拖累和低效。减少摩擦往往是比简单施加更多力更有效的改进策略。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Friction is Necessary (Traction):** Not all friction is bad. It provides the grip needed to walk, for brakes to work, or for a team to gain traction on a project. Removing all friction can lead to chaos and lack of control. - **When Reducing Friction is Too Costly:** The effort to eliminate a minor point of friction might outweigh the benefit gained from its removal.'", "avoid: '（或谨慎使用）：** - **摩擦必要时（牵引力）：** 并非所有摩擦都是坏的。它提供走路所需的抓地力、刹车工作所需，或团队在项目上获得牵引力所需。移除所有摩擦可能导致混乱和缺乏控制。 - **减少摩擦成本过高时：** 消除小摩擦点的努力可能超过其移除带来的好处。'"))

replacements.append(('keywords: ["Process improvement", "user experience (UX) design", "habit formation", "organizational efficiency", "sales funnels", "project management."]', 'keywords: ["流程改进", "用户体验设计", "习惯养成", "组织效率", "销售漏斗", "项目管理。"]'))

# m18 层级组织
replacements.append(("description: 'Hierarchy is the invisible scaffolding that organizes the living world. It\\'s the organizing principle that allows scale from the microscopic to the magnificent. Hierarchies in biology aren\\'t just about structure but about function—they allow for specialization and division of labor, enabling the emergence of complex behaviors from simple rules. In the hierarchy of an ant colony, the queen, workers, and soldiers all play their roles, their interactions giving rise to the sophisticated operation of the colony as a whole. But hierarchy isn\\'t rigid or fixed; it\\'s fluid and dynamic, with levels constantly interacting and influencing one another. A change at one level can ripple across the entire hierarchy, transforming the system unexpectedly.'", "description: '层级是组织生命世界的无形支架。它是允许从微观到宏伟规模的组织原则。生物学中的层级不只是关于结构而是功能——它们允许专业化和劳动分工，使复杂行为从简单规则中涌现。在蚂蚁群体的层级中，蚁后、工蚁和兵蚁都扮演各自角色，它们的互动产生整个群体的复杂运作。但层级不是刚性固定的；它是流动动态的，层级不断互动相互影响。一个层级的变化可以涟漪整个层级，意外地转变系统。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Creating Excessive Layers:** Too much hierarchy leads to unrest, instability, and inefficiency. Over-hierarchical systems become bureaucratic and slow to respond. - **When Emphasizing Status Over Function:** Most organizations promote cultures that emphasize an individual\\'s status, power, and place rather than functional effectiveness, which tears apart the organization as fighting for position takes precedence over success. - **In Highly Dynamic Environments:** Rigid hierarchies can be too slow to adapt in rapidly changing situations where flat, agile structures perform better.'", "avoid: '（或谨慎使用）：** - **创建过多层级时：** 过多层级导致动荡、不稳定和低效。过度层级化系统变得官僚化且响应缓慢。 - **强调地位而非功能时：** 大多数组织提倡强调个人地位、权力和位置而非功能效能的文化，这撕裂组织，争夺位置优先于成功。 - **高度动态环境中：** 刚性层级在快速变化情况下可能太慢无法适应，扁平敏捷结构表现更好。'"))

replacements.append(('keywords: ["Organizational design", "team structure", "complexity management", "systems thinking", "leadership", "delegation"]', 'keywords: ["组织设计", "团队结构", "复杂性管理", "系统思维", "领导力", "授权"]'))

# m19 激励
replacements.append(("description: 'Incentives are the hidden engines that drive behavior. They are the unseen forces, both explicit (like a sales bonus) and subtle (like social approval), that shape our choices by tapping into our fundamental wiring to seek reward and avoid punishment. When incentives are aligned with desired goals, systems thrive. When they are misaligned, they create struggle and inefficiency. The core principle is that if you understand the incentive, you can often predict the outcome.'", "description: '激励是驱动行为的隐藏引擎。它们是无形力量，既明确（如销售奖金）又微妙（如社会认可），通过接入我们寻求奖励避免惩罚的基本线路来塑造选择。当激励与期望目标一致时，系统繁荣。当它们不一致时，它们制造挣扎和低效。核心原则是如果你理解激励，你往往可以预测结果。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When They Are Poorly Designed:** Poorly designed incentives can backfire, encouraging short-term thinking, unethical behavior, or other unintended consequences (e.g., rewarding code quantity over quality). - **When Short-Term and Long-Term Incentives Conflict:** Many systems reward immediate gratification (pleasure of immediate gains) at the expense of long-term success (being healthy as you age). This misalignment is a primary source of failure. - **When They Crowd Out Intrinsic Motivation:** Relying solely on external rewards can diminish a person\\'s natural interest or enjoyment in a task.'", "avoid: '（或谨慎使用）：** - **设计不善时：** 设计不善的激励可能适得其反，鼓励短期思维、不道德行为或其他意外后果（如奖励代码数量而非质量）。 - **短期与长期激励冲突时：** 许多系统奖励即时满足（即时收益的快乐）以牺牲长期成功（随着年龄增长健康）为代价。这种不一致是失败的主要来源。 - **挤出内在动机时：** 仅依赖外部奖励可能减弱一个人对任务的自然兴趣或享受。'"))

replacements.append(('keywords: ["Performance management", "motivation", "behavioral economics", "game theory", "policy design", "habit formation"]', 'keywords: ["绩效管理", "动机", "行为经济学", "博弈论", "政策设计", "习惯养成"]'))

# m20 惯性
replacements.append(("description: 'Inertia is the resistance to change. Objects (and systems) at rest stay at rest, and those in motion stay in motion. It\\'s a fundamental property of mass, but it\\'s also a powerful metaphor for understanding resistance to change in habits, organizations, and beliefs. The more \"mass\" a habit or institution has (e.g., the longer it\\'s existed), the more force is required to change its direction.'", "description: '惯性是抵抗变化的属性。静止物体（和系统）保持静止，运动物体保持运动。这是质量的基本属性，但也是理解习惯、组织和信念中变化抵抗的强大隐喻。习惯或机构有越多\"质量\"（如存在时间越长），改变其方向需要越多力。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Facing Disruption:** Relying on past momentum can be disastrous when the environment changes. Successful companies can fail if their inertia prevents them from adapting to new technologies or market shifts. - **When Bad Habits are Entrenched:** Personal and organizational inertia can keep destructive habits in place. The \"we\\'ve always done it this way\" mentality is a classic sign of dangerous inertia. - **When Agility is Required:** In dynamic environments, inertia is a liability. Startups often succeed because their lack of inertia allows them to pivot and adapt quickly, while larger incumbents are slowed by their own momentum.'", "avoid: '（或谨慎使用）：** - **面对颠覆时：** 当环境变化时依赖过去动量可能是灾难性的。成功公司可能因惯性阻止适应新技术或市场转变而失败。 - **坏习惯根深蒂固时：** 个人和组织惯性可能将破坏性习惯保持在位。\"我们一直这样做\"心态是危险惯性的经典标志。 - **需要敏捷时：** 在动态环境中，惯性是负债。初创企业往往成功因为缺乏惯性允许它们快速转向适应，而更大现有企业被自己动量拖慢。'"))

replacements.append(('keywords: ["Habit formation", "change management", "organizational resistance", "status quo", "process improvement", "innovation"]', 'keywords: ["习惯养成", "变革管理", "组织抵抗", "现状", "流程改进", "创新"]'))

# 执行替换
success = 0
fail = 0

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        success += 1
    else:
        fail += 1

with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"补充翻译完成！成功: {success}, 失败: {fail}")