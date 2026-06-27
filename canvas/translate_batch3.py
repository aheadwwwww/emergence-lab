#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芒格思维模型翻译脚本 - 第三批 (m21-m30)
"""

dst = r'D:\openclaw_workspace\canvas\munger-models-zh.html'

with open(dst, 'r', encoding='utf-8') as f:
    content = f.read()

print("继续翻译 m21-m30...")

replacements = []

# m21 杠杆
replacements.append(("description: 'Leverage is the principle of getting a disproportionate output from a given input. It\\'s a force multiplier that allows a small, strategic effort to produce massive results. While its roots are in physics (like using a lever to lift a heavy object), the concept applies to nearly every area of life, from technology and finance to personal productivity. It\\'s the engine behind nonlinear outcomes, where one decision, skill, or action can create an outsized impact.'", "description: '杠杆是从给定输入获得不成比例输出的原则。它是一个力量倍增器，允许小的战略性努力产生巨大结果。虽然其根源在物理学（如用杠杆举起重物），这个概念几乎适用于生活的每个领域，从技术和金融到个人生产力。它是非线性结果的引擎，一个决策、技能或行动可以创造巨大影响。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When the Downside is Unacceptable:** Leverage magnifies both gains and losses. Using financial leverage (debt) can lead to ruin if the investment fails. Be cautious when the potential negative consequences are catastrophic. - **When It Leads to Exploitation:** Using leverage to extract maximum value from people can backfire, creating resentment, disloyalty, and long-term instability. Sustainable leverage respects the system and its participants. - **Without Understanding the System:** Applying leverage without understanding the full context and potential second- and third-order effects is reckless. A small push in the wrong place can destabilize an entire system.'", "avoid: '（或谨慎使用）：** - **负面后果不可接受时：** 杠杆放大收益和损失。使用财务杠杆（债务）可能因投资失败导致毁灭。当潜在负面后果灾难性时要谨慎。 - **导致剥削时：** 用杠杆从人中榨取最大价值可能适得其反，制造怨恨、不忠和长期不稳定。可持续杠杆尊重系统和参与者。 - **不了解系统时：** 在不了解完整语境和潜在二阶三阶效应的情况下应用杠杆是鲁莽的。在错误位置的小推力可能 destabilize 整个系统。'"))

replacements.append(('keywords: ["Force multiplier", "productivity", "efficiency", "strategic planning", "investment", "habit formation"]', 'keywords: ["力量倍增器", "生产力", "效率", "战略规划", "投资", "习惯养成"]'))

# m22 生态位
replacements.append(("description: 'A niche is a specialized corner of an environment where a particular organism, company, or individual can thrive. It\\'s a position that is uniquely suited to a specific set of strengths and capabilities, allowing one to avoid direct, resource-intensive competition with larger, more generalized players. By focusing on a niche, you don\\'t have to be the best at everything; you just have to be the best at serving the unique needs of that specific space.'", "description: '生态位是环境中一个专门的角落，特定生物、公司或个人可以在这里茁壮成长。它是独特适合一组特定优势和能力的位置，允许避免与更大、更泛化的参与者进行直接、资源密集的竞争。专注于生态位，你不必在所有方面最好；只需在服务那个特定空间的独特需求方面最好。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When the Niche is Too Small:** A niche strategy can limit growth potential if the market is too narrow to sustain a viable business. - **When the Niche Disappears:** Niches can be fragile. If the specific needs or conditions of the niche change or disappear, the specialized player can be left with no viable alternatives. - **In Markets That Reward Scale:** In some markets, being big and broad is the winning strategy. Trying to find a niche in a market dominated by economies of scale can be a losing battle.'", "avoid: '（或谨慎使用）：** - **生态位太小时：** 如果市场太窄无法维持可行业务，生态位策略可能限制增长潜力。 - **生态位消失时：** 生态位可能脆弱。如果生态位的特定需求或条件改变或消失，专门化参与者可能没有可行替代方案。 - **奖励规模的市场中：** 在某些市场，大而广是获胜策略。在规模经济主导的市场中寻找生态位可能是失败的战斗。'"))

replacements.append(('keywords: ["Business strategy", "market positioning", "career specialization", "competitive advantage", "product differentiation", "personal branding."]', 'keywords: ["商业战略", "市场定位", "职业专业化", "竞争优势", "产品差异化", "个人品牌。"]'))

# m23 互惠
replacements.append(("description: 'Reciprocity is the social norm of responding to a positive action with another positive action, rewarding kind actions. It\\'s a deeply ingrained human tendency that forms the basis of much of human cooperation and social interaction. When someone does something for you, you feel a psychological obligation to return the favor, creating a cycle of mutual benefit.',", "description: '互惠是用另一个积极行动回应积极行动的社会规范，奖励善意行动。这是深深根植的人类倾向，形成人类合作和社会互动的基础。当某人为你做某事，你感到心理义务回报恩惠，创造互利循环。',"))

replacements.append(("avoid: '(or Use with Caution):** - **When It Creates Manipulation:** Reciprocity can be weaponized. If someone gives you something with the specific intent of extracting a larger return, it becomes a manipulation tactic rather than a genuine social bond. - **In Transactional Relationships:** Over-reliance on reciprocity can make relationships feel purely transactional, devoid of genuine care or altruism.'", "avoid: '（或谨慎使用）：** - **制造操纵时：** 互惠可以被武器化。如果某人给你某物专门意图榨取更大回报，它变成操纵战术而非真实社会纽带。 - **交易性关系中：** 过度依赖互惠可能使关系感觉纯粹交易性，缺乏真正的关怀或利他主义。'"))

replacements.append(('keywords: ["Relationship building", "negotiation", "sales", "leadership", "social psychology", "team dynamics."]', 'keywords: ["关系建设", "谈判", "销售", "领导力", "社会心理学", "团队动力学。"]'))

# m24 相对论
replacements.append(("description: 'Relativity is the principle that our perception and judgment are not absolute but are shaped by our unique point of view and frame of reference. Two people can witness the same event and have vastly different interpretations because their context, experiences, and values are different. Understanding this subjectivity is crucial for empathy, communication, and making more robust judgments. It\\'s recognizing that we all have blind spots and that our view is not the complete picture.'", "description: '相对论是我们的感知和判断不是绝对而是由我们独特视角和参照框架塑造的原则。两个人可以目睹同一事件并有截然不同的解释，因为他们的语境、经验和价值观不同。理解这种主观性对共情、沟通和做出更稳健判断至关重要。它认识到我们都有盲点，我们的视角不是完整画面。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Confused with Relativism:** Relativity should not be mistaken for the idea that all perspectives are equally valid or true (relativism). Recognizing that perspectives differ doesn\\'t mean abandoning critical judgment or the pursuit of objective facts. - **As an Excuse for Inaction:** Using relativity to argue that \"everyone has their own truth\" can be a cop-out that prevents making necessary judgments or taking a moral stance.'", "avoid: '（或谨慎使用）：** - **混淆相对主义时：** 相对论不应被误认为所有视角同样有效或真实的观念（相对主义）。认识到视角不同不意味着放弃批判判断或追求客观事实。 - **作为不行动借口：** 用相对论争论\"每个人都有自己的真理\"可能是逃避做出必要判断或采取道德立场的借口。'"))

replacements.append(('keywords: ["Perspective taking", "empathy", "communication", "conflict resolution", "bias detection", "decision-making"]', 'keywords: ["视角采纳", "共情", "沟通", "冲突解决", "偏见检测", "决策制定"]'))

# m25-m30 继续添加...

# m25 自我保护
replacements.append(("description: 'Self-preservation is the fundamental instinct to protect oneself from harm, danger, or death. It\\'s the most basic drive that underlies much of human behavior and decision-making. While essential for survival, this instinct can sometimes lead to short-term, self-centered thinking that neglects long-term well-being or the needs of others.'", "description: '自我保护是保护自己免受伤害、危险或死亡的基本本能。它是人类行为和决策基础的最基本驱动。虽然对生存至关重要，这个本能有时可能导致短期、以自我为中心的思维，忽视长期福祉或他人需求。'"))

# m26 生存
replacements.append(("description: 'Survival is the state of continuing to live or exist, especially in spite of difficult conditions. It\\'s the most fundamental goal of any organism or organization. Understanding survival mechanics helps us identify what is truly essential and what can be sacrificed when resources are scarce or threats are imminent.'", "description: '生存是在困难条件下继续生活或存在的状态。它是任何生物或组织最基本的目标。理解生存机制帮助我们识别什么真正本质，什么可以在资源稀缺或威胁迫近时牺牲。'"))

# m27 竞争
replacements.append(("description: 'Competition is the rivalry between entities for limited resources, status, or other advantages. It drives innovation and efficiency but can also lead to destructive behaviors when not properly bounded. Understanding when to compete and when to cooperate is a key strategic skill.'", "description: '竞争是实体间争夺有限资源、地位或其他优势的对抗。它驱动创新和效率，但在没有适当边界时也可能导致破坏性行为。理解何时竞争何时合作是关键战略技能。'"))

# m28 适应
replacements.append(("description: 'Adaptation is the process of adjusting to new conditions or environments. It\\'s a fundamental survival mechanism that allows organisms and organizations to persist through change. Successful adaptation requires flexibility, learning, and the ability to modify behavior or structure in response to feedback.'", "description: '适应是调整到新条件或环境的过程。它是允许生物和组织在变化中持续的基本生存机制。成功适应需要灵活性、学习能力和根据反馈修改行为或结构的能力。'"))

# m29 合作进化
replacements.append(("description: 'Co-evolution is the process where two or more species or systems reciprocally affect each other\\'s evolution. Changes in one trigger changes in the other, creating a dynamic interdependence. This model helps understand how partnerships, ecosystems, and competitive dynamics evolve together over time.'", "description: '合作进化是两个或更多物种或系统相互影响对方进化的过程。一个的变化触发另一个的变化，创造动态相互依赖。这个模型帮助理解伙伴关系、生态系统和竞争动力学如何随时间共同演进。'"))

# m30 规模效应
replacements.append(("description: 'Scale effects refer to the advantages (or disadvantages) that come from increasing size or volume. As things get bigger, costs per unit often decrease (economies of scale), but complexity and coordination challenges often increase. Understanding scale helps in deciding when to grow and when to stay small.'", "description: '规模效应指来自增加大小或体积的优势（或劣势）。随着事物变大，单位成本通常下降（规模经济），但复杂性和协调挑战通常增加。理解规模帮助决定何时增长何时保持小规模。'"))

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

print(f"第三批翻译完成！成功: {success}, 失败: {fail}")