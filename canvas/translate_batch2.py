#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芒格思维模型翻译脚本 - 第二批 (m11-m20)
继续翻译description, avoid, keywords字段
"""

dst = r'D:\openclaw_workspace\canvas\munger-models-zh.html'

with open(dst, 'r', encoding='utf-8') as f:
    content = f.read()

print("继续翻译 m11-m20...")

# m11 合金化
replacements = []

replacements.append(("description: 'Alloying is the process of combining different elements to create a new material with enhanced properties that are superior to the individual components. This concept extends beyond metallurgy to teams, skills, and ideas, where a strategic mix of diverse components can create a stronger, more resilient, and more valuable whole.'", "description: '合金化是将不同元素组合以创造具有增强特性的新材料的过程，这些特性优于各单独成分。这个概念超越了冶金学，延伸到团队、技能和想法，战略性混合多样化成分可以创造更强大、更有韧性、更有价值的整体。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Purity is the Goal:** In situations that require specialization or a single, pure skill set (e.g., a highly technical, isolated task), adding other elements can be a distraction. - **Incompatible Combinations:** Not all elements or skills mix well. Forcing a combination of conflicting personalities, skills, or ideas can create a \"brittle\" or dysfunctional outcome.'", "avoid: '（或谨慎使用）：** - **追求纯净时：** 在需要专业化或单一纯技能组合的情况下（如高度技术性、孤立的任务），添加其他元素可能分散注意力。 - **不兼容组合：** 并非所有元素或技能都能良好混合。强制组合冲突的性格、技能或想法可能产生\"脆弱\"或功能失调的结果。'"))

replacements.append(('keywords: ["Team building", "skill development", "innovation", "product design", "strategic partnerships", "personal growth."]', 'keywords: ["团队建设", "技能发展", "创新", "产品设计", "战略合作伙伴", "个人成长。"]'))

# m12 催化剂
replacements.append(("description: 'A catalyst is a substance or agent that accelerates a chemical reaction without being consumed by it. In broader terms, a catalyst is a person, event, or technology that precipitates significant change or action without necessarily being a major part of the final outcome. They lower the activation energy required for a change to occur, making it faster, more likely, or even possible in the first place.'", "description: '催化剂是一种加速化学反应而不被消耗的物质或剂。更广泛地说，催化剂是一个人、事件或技术，它促成重大变化或行动，而不必是最终结果的主要部分。它们降低发生变化所需的活化能，使其更快、更可能或甚至首次成为可能。'"))

replacements.append(("avoid: '(or Use with Caution):** - **Unintended Consequences:** Introducing a catalyst can have unforeseen side effects. The change might be accelerated in an undesirable direction. - **Creating Dependency:** Relying on a specific catalyst (e.g., one charismatic leader) can make a system fragile. When the catalyst is removed, the process may grind to a halt.'", "avoid: '（或谨慎使用）：** - **意外后果：** 引入催化剂可能产生不可预见的副作用。变化可能在不良方向上加速。 - **制造依赖：** 依赖特定催化剂（如一个魅力型领导者）可能使系统脆弱。当催化剂移除时，过程可能停滞。'"))

replacements.append(('keywords: ["Leadership", "innovation", "social change", "personal development", "process improvement", "mentorship."]', 'keywords: ["领导力", "创新", "社会变革", "个人发展", "流程改进", "导师指导。"]'))

# m13 合作
replacements.append(("description: 'Cooperation is the principle that entities can often achieve greater success by working together than by competing. It is a strategy for non-zero-sum games, where the total gains are not fixed and can be expanded through collaboration. From symbiotic relationships in biology to alliances in human society, cooperation allows for the pooling of resources, knowledge, and capabilities to achieve outcomes that would be impossible for individuals alone.'", "description: '合作是这样一种原则：实体通过协作往往能比竞争获得更大成功。它是非零和博弈的策略，总收益不是固定的，可以通过协作扩展。从生物学中的共生关系到人类社会中的联盟，合作允许汇集资源、知识和能力，实现个人无法单独达成的结果。'"))

replacements.append(("avoid: '(or Use with Caution):** - **In Zero-Sum Games:** In situations where one party\\'s gain is directly another\\'s loss (e.g., a single promotion, a competitive sport), cooperation with a direct competitor is counterproductive. - **With Untrustworthy Actors:** Cooperation requires a degree of trust. Engaging with parties who have a history of cheating or acting in bad faith is risky and likely to be exploited.'", "avoid: '（或谨慎使用）：** - **零和博弈中：** 在一方收益直接是另一方损失的情况下（如单个晋升名额、竞技运动），与直接竞争者合作是适得其反的。 - **与不可信行为者：** 合作需要一定程度的信任。与有欺骗或不良行为历史的方合作是有风险的，很可能被利用。'"))

replacements.append(('keywords: ["Teamwork", "negotiation", "partnerships", "community building", "organizational design", "conflict resolution."]', 'keywords: ["团队合作", "谈判", "伙伴关系", "社区建设", "组织设计", "冲突解决。"]'))

# m14 生态系统
replacements.append(("description: 'An ecosystem is a complex network of interconnected and interdependent parts. No single component exists in isolation; the actions of one element can have cascading, often unpredictable, effects on the entire system. This model emphasizes understanding the relationships, feedback loops, and emergent behaviors within a system, rather than just analyzing its individual components.'", "description: '生态系统是相互连接和相互依赖部分的复杂网络。没有任何单一成分孤立存在；一个元素的行动可以对整个系统产生连锁的、往往是不可预测的影响。这个模型强调理解系统内的关系、反馈循环和涌现行为，而非仅分析其单个成分。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Simple, Linear Problems:** When dealing with a straightforward, isolated problem with clear cause and effect, an ecosystem analysis can be overkill and lead to unnecessary complexity. - **When Immediate Action is Required:** A full ecosystem analysis takes time. In a crisis that demands a rapid, tactical response, you may need to act first and analyze the broader system later.'", "avoid: '（或谨慎使用）：** - **简单线性问题：** 当处理有明确因果关系的直接、孤立问题时，生态系统分析可能过度并导致不必要的复杂性。 - **需要立即行动时：** 完整的生态系统分析需要时间。在需要快速战术响应的危机中，可能需要先行动后再分析更广泛的系统。'"))

replacements.append(('keywords: ["Business strategy", "market analysis", "policy making", "organizational change", "environmental management", "supply chain logistics."]', 'keywords: ["商业战略", "市场分析", "政策制定", "组织变革", "环境管理", "供应链物流。"]'))

# m15 进化（自然选择与灭绝）
replacements.append(("description: 'Evolution is a process of change over time driven by natural selection. Organisms or systems with traits best suited to their environment (the \"fittest\") are more likely to survive, reproduce, and pass on those traits. Those that are poorly adapted (the \"unfit\") are eliminated (extinction). This model applies not just to biology, but also to businesses, technologies, ideas, and skills, which all compete and adapt in a changing environment.'", "description: '进化是自然选择驱动的时间变化过程。最适应其环境特性的生物或系统（\"最适应者\")更有可能生存、繁殖并传递这些特性。适应性差的（\"不适应者\")被淘汰（灭绝）。这个模型不仅适用于生物学，也适用于企业、技术、想法和技能，它们都在变化环境中竞争和适应。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Short-Term Planning:** Evolution is a long-term process. Relying on it for immediate, short-term results is inappropriate. It describes a long-term trend, not a quick fix. - **As a Justification for Ruthlessness:** Applying this model too literally to social or organizational management can foster a toxic, cutthroat culture that destroys psychological safety and cooperation.'", "avoid: '（或谨慎使用）：** - **短期规划：** 进化是长期过程。依赖它获得即时短期结果是不适当的。它描述长期趋势，而非快速解决方案。 - **作为无情行为的正当理由：** 将这个模型过于字面地应用于社会或组织管理可能培养有毒、竞争激烈的文化，破坏心理安全和合作。'"))

replacements.append(('keywords: ["Business strategy", "market competition", "innovation", "product development", "career planning", "skill adaptation."]', 'keywords: ["商业战略", "市场竞争", "创新", "产品开发", "职业规划", "技能适应。"]'))

# m16 进化（适应与红皇后效应）
replacements.append(("description: 'The Red Queen Effect, named after a character in Lewis Carroll\\'s *Through the Looking-Glass*, is the idea that in a competitive, evolving system, you must constantly adapt and improve just to maintain your current position relative to your competitors. Standing still is equivalent to falling behind. Continuous improvement is not just for getting ahead, but for survival.'", "description: '红皇后效应，以路易斯·卡罗尔的《镜中世界》中角色命名，是指在竞争、进化的系统中，你必须不断适应和改进才能维持相对于竞争对手的当前位置。停滞等同于落后。持续改进不只是为了领先，而是为了生存。'"))

replacements.append(("avoid: '(or Use with Caution):** - **In Stable, Non-Competitive Environments:** If the environment is truly static and there are no competitive pressures, constant change can be a waste of resources.  - **When it Leads to Mindless Change:** The Red Queen Effect should not be an excuse for change for the sake of change. Adaptations should be strategic and intelligent, not just a frantic reaction to competitors\\' moves.'", "avoid: '（或谨慎使用）：** - **稳定非竞争环境：** 如果环境真正静止且没有竞争压力，持续变化可能是资源浪费。 - **导致无意义变化时：** 红皇后效应不应成为为变化而变化的借口。适应应该是战略性和智能的，而非对竞争对手行动的慌乱反应。'"))

replacements.append(('keywords: ["Competitive strategy", "arms races", "innovation", "business", "technology", "career development"]', 'keywords: ["竞争战略", "军备竞赛", "创新", "商业", "技术", "职业发展"]'))

# m17-m20 已有中文标题，需要翻译其他字段
# m17 摩擦与粘度 - description已部分翻译，需要补全
# m18 层级组织 - description已部分翻译，需要补全
# m19 激励 - description已部分翻译，需要补全
# m20 惯性 - description已部分翻译，需要补全

# 执行替换
success = 0
fail = 0

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        success += 1
    else:
        fail += 1

# 保存
with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"第二批翻译完成！成功: {success}, 失败: {fail}")