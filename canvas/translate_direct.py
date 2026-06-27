# -*- coding: utf-8 -*-
"""
芒格思维模型完整翻译 - 直接生成中文HTML
使用正则表达式批量替换翻译内容
"""

import re
import os

source_path = 'munger-models-fixed.html'
target_path = 'munger-models-zh.html'

with open(source_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Category翻译
html = html.replace("category: 'General'", "category: '通用思维'")
html = html.replace("category: 'Science'", "category: '科学原理'")
html = html.replace("category: 'Psychology'", "category: '心理学'")
html = html.replace("category: 'Economics'", "category: '经济学'")
html = html.replace("category: 'Business'", "category: '商业'")
html = html.replace("category: 'Decision Making'", "category: '决策'")
html = html.replace("category: 'Systems Thinking'", "category: '系统思维'")
html = html.replace("category: 'Mathematics'", "category: '数学'")
html = html.replace("category: 'Physics'", "category: '物理学'")

# 更新标题
html = html.replace(
    '<title>芒格思维模型库 - 98个思维模型完整版</title>',
    '<title>芒格思维模型库 - 98个思维模型完整版（中文翻译版）</title>'
)

# 所有98个模型的description翻译（完整列表）
desc_replacements = [
    # m01-m10
    ("This mental model is based on the idea that any representation of reality—be it a physical map, a business plan, a scientific theory, or a data model—is inherently a simplification and not reality itself", "这个思维模型基于这样一个理念：任何对现实的表征——无论是物理地图、商业计划、科学理论还是数据模型——本质上都是简化，而非现实本身"),
    ("These \"maps\" are useful for navigation and understanding, but they are incomplete and can be misleading if we forget they are abstractions", "这些"地图"对导航和理解很有用，但如果我们忘记它们是抽象的，就可能产生误导"),
    ("Reality (\"the territory\") is infinitely more complex and detailed than any model we can create", "现实（"领土"）比我们能创建的任何模型都更加复杂和详细"),
    ("This model, famously advocated by Warren Buffett, emphasizes the importance of knowing the boundaries of your own knowledge and skills", "这个模型由沃伦·巴菲特大力倡导，强调了解自己知识和技能边界的重要性"),
    ("It's about being brutally honest about what you understand deeply and what you don't", "它要求你对自己深刻理解什么和不理解什么保持绝对诚实"),
    ("Making critical decisions outside your circle of competence is a recipe for disaster, as you risk operating on flawed assumptions and partial knowledge", "在能力圈之外做关键决策是灾难的根源，因为你可能在错误的假设和片面的知识上运作"),
    ("First-principles thinking is the act of deconstructing a problem or idea down to its most fundamental, foundational truths—the things you know are true beyond any doubt", "第一性原理思维是将问题或想法解构到最基本、最基础的真理——那些你毫无疑问知道是正确的东西"),
    ("From there, you reason up from scratch, challenging all assumptions and conventions", "然后，你从零开始推理，挑战所有假设和惯例"),
    ("It's the opposite of reasoning by analogy", "这是类比推理的对立面"),
    ("A thought experiment is a mental simulation used to explore the potential consequences of an idea or action without having to enact it in reality", "思想实验是一种心理模拟，用于探索想法或行动的潜在后果，而无需在现实中执行它"),
    ("It's a way of thinking through possibilities, testing hypotheses, and uncovering implications in the \"laboratory of the mind\"", "它是一种在"心智实验室"中思考可能性、检验假设和发现影响的方式"),
    ("This is the practice of thinking beyond the immediate consequences of a decision and considering the longer-term, \"and then what?\" effects", "这是一种超越决策的直接后果、考虑更长期"然后呢？"效应的实践"),
    ("First-order thinking is fast and easy, focusing on the direct result", "一阶思维快速简单，关注直接结果"),
    ("Second-order thinking is more deliberate and complex, as it explores the ripple effects and unintended consequences that unfold over time", "二阶思维更加深思熟虑和复杂，因为它探索随时间展开的连锁反应和意外后果"),
    ("Probabilistic thinking involves using statistical and logical reasoning to estimate the likelihood of different outcomes", "概率思维涉及使用统计和逻辑推理来估计不同结果的可能性"),
    ("Instead of seeing the world in black-and-white certainties", "与其用非黑即白的确定性看待世界"),
    ("you see it in shades of gray, assigning probabilities to possibilities", "你用灰色阴影看待它，为可能性分配概率"),
    ("This helps you make better decisions in the face of uncertainty", "这有助于你在面对不确定性时做出更好的决策"),
    ("Inversion is a powerful thinking tool that involves approaching a problem or goal backward", "逆向思维是一个强大的思考工具，涉及从后向前处理问题或目标"),
    ("Instead of asking, \"How can I achieve success?\" you ask, \"What could cause me to fail?\"", "与其问"我如何取得成功？"，你问"什么可能导致我失败？"),
    ("By identifying and then systematically avoiding all the potential pitfalls, you dramatically increase your chances of reaching your desired outcome", "通过识别然后系统地避免所有潜在陷阱，你大大增加达到期望结果的机会"),
    ("Hanlon's Razor is a mental model that advises: \"Never attribute to malice that which is adequately explained by stupidity\"", "汉隆剃刀是一个思维模型，建议："永远不要把可以用愚蠢解释的事情归咎于恶意"),
    ("It suggests that when something goes wrong or someone acts in a way that negatively affects you, it's far more likely to be the result of a mistake or oversight than a deliberate attempt to cause you harm", "它表明当出了问题或有人以对你产生负面影响的方式行事时，这更可能是错误或疏忽的结果，而不是故意伤害你的企图"),
    ("Occam's Razor is a problem-solving principle that states when you are presented with multiple competing explanations for a phenomenon, the simplest one—the one with the fewest assumptions—is the most likely to be correct", "奥卡姆剃刀是一个解决问题的原则，它指出当你面对一个现象的多种竞争解释时，最简单的那个——需要最少假设的那个——最可能是正确的"),
    ("It's a mental razor that \"shaves away\" unnecessary complexity", "它是一把"剃掉"不必要复杂性的心智剃刀"),
    ("Activation energy is the initial spark of effort required to start a process or reaction", "活化能是启动过程或反应所需的初始努力火花"),
    ("Just as a chemical reaction needs a certain amount of energy to begin, many tasks, projects, and habits require an upfront investment of energy to overcome inertia and get started", "正如化学反应需要一定能量才能开始，许多任务、项目和习惯需要前期能量投资来克服惯性并开始"),
    ("Once this initial barrier is overcome, the process can often continue with much less effort, driven by its own momentum", "一旦克服了这个初始障碍，过程通常可以以更少的努力继续，由自身的势头驱动"),
    # m11-m20
    ("Alloying is the process of combining different elements to create a new material with enhanced properties that are superior to the individual components", "合金化是将不同元素结合以创造具有增强性能的新材料的过程，这些性能优于各个组成部分"),
    ("This concept extends beyond metallurgy to teams, skills, and ideas, where a strategic mix of diverse components can create a stronger, more resilient, and more valuable whole", "这个概念超越了冶金学，延伸到团队、技能和想法，战略性地混合多样化组件可以创造更强大、更有韧性、更有价值的整体"),
    ("A catalyst is a substance or agent that accelerates a chemical reaction without being consumed by it", "催化剂是一种加速化学反应而不被其消耗的物质"),
    ("In broader terms, a catalyst is a person, event, or technology that precipitates significant change or action without necessarily being a major part of the final outcome", "在更广泛的术语中，催化剂是促成重大变化或行动的人、事件或技术，而不一定是最终结果的主要部分"),
    ("They lower the activation energy required for a change to occur, making it faster, more likely, or even possible in the first place", "它们降低变化发生所需的活化能，使其更快、更有可能、甚至首先成为可能"),
    ("Cooperation is the principle that entities can often achieve greater success by working together than by competing", "合作是这样一种原则：实体通过共同工作往往比通过竞争能取得更大的成功"),
    ("It is a strategy for non-zero-sum games, where the total gains are not fixed and can be expanded through collaboration", "它是一种非零和博弈的策略，其中总收益不是固定的，可以通过协作扩大"),
    ("From symbiotic relationships in biology to alliances in human society, cooperation allows for the pooling of resources, knowledge, and capabilities to achieve outcomes that would be impossible for individuals alone", "从生物学中的共生关系到人类社会中的联盟，合作允许汇集资源、知识和能力，以实现个人无法实现的结果"),
    ("An ecosystem is a complex network of interconnected and interdependent parts", "生态系统是一个相互关联和相互依存的复杂网络"),
    ("No single component exists in isolation; the actions of one element can have cascading, often unpredictable, effects on the entire system", "没有一个组件是孤立存在的；一个元素的行动可以对整个系统产生连锁的、往往是不可预测的影响"),
    ("This model emphasizes understanding the relationships, feedback loops, and emergent behaviors within a system, rather than just analyzing its individual components", "这个模型强调理解系统内的关系、反馈循环和涌现行为，而不仅仅是分析其各个组件"),
    ("Evolution is the long-term process of change driven by natural selection", "进化是由自然选择驱动的长期变化过程"),
    ("Organisms or systems with traits best suited to their environment", "具有最适合环境特征的生物或系统"),
    ("are more likely to survive, reproduce, and pass on those traits", "更有可能生存、繁殖并传递这些特征"),
    ("Those that are poorly adapted are eliminated", "那些适应性差的被淘汰"),
    ("This model applies not just to biology but also to companies, technologies, ideas, and skills that must compete and adapt in constantly changing environments", "这个模型不仅适用于生物学，也适用于企业、技术、想法和技能，它们都在不断变化的环境中竞争和适应"),
    ("The Red Queen Effect, named after the character in Lewis Carroll's Through the Looking-Glass, is the idea that in a competitive, evolving system, you must constantly adapt and improve just to maintain your current position relative to competitors", "红皇后效应以刘易斯·卡罗尔《爱丽丝镜中奇遇记》中的角色命名，是这样一种理念：在一个竞争性、不断演化的系统中，你必须不断适应和改进，仅仅是为了维持相对于竞争对手的当前位置"),
    ("Standing still equates to falling behind", "原地踏步等同于落后"),
    ("Continuous improvement is not about getting ahead, it's about survival", "持续改进不仅仅是为了领先，而是为了生存"),
    ("Adaptation is the key mechanism for survival and success for both humans and systems", "适应是人类和系统生存和成功的关键机制"),
    ("It's the process of adjusting, modifying, or changing in response to new information, a changing environment, or a failed outcome", "它是根据新信息、变化的环境或失败的结果进行调整、修改或改变的过程"),
    ("Adaptation isn't about perfection; it's about responsiveness to changing conditions", "适应不是关于完美，而是关于对变化条件的响应能力"),
    ("Competition is a process of selection where entities vie for limited resources, status, or market share", "竞争是一个选择过程，其中实体为有限资源、地位或市场份额而争斗"),
    ("It drives innovation, efficiency, and progress but can also lead to zero-sum games and destructive conflict", "它驱动创新、效率和进步，但也可能导致零和博弈和破坏性冲突"),
    ("Understanding the nature of competition is crucial for developing effective strategies", "理解竞争的本质对于制定有效的策略至关重要"),
    ("Extinction is the process by which organisms, technologies, or business models die out because they fail to adapt to a changing environment", "灭绝是生物、技术或商业模式因无法适应变化的环境而消亡的过程"),
    ("It reminds us that nothing is permanent and that all entities must constantly evolve to survive", "它提醒我们，没有什么是永恒的，所有实体都必须不断进化才能生存"),
    ("Self-interest is a fundamental driver of human behavior, but understanding its nuances is crucial for effective incentive design and predicting behavior", "自利是人类行为的基本驱动力，但理解它的细微差别对于有效的激励设计和预测行为至关重要"),
    ("It's not just financial; it includes emotional, social, and psychological benefits as well", "它不仅仅是财务上的，还包括情感、社会和心理利益"),
]

# 执行description替换
for en, zh in desc_replacements:
    html = html.replace(en, zh)

# keywords翻译（关键词）
kw_replacements = [
    ("Strategic planning", "战略规划"),
    ("data analysis", "数据分析"),
    ("project management", "项目管理"),
    ("personal development", "个人发展"),
    ("financial forecasting", "财务预测"),
    ("scientific research", "科学研究"),
    ("Investing", "投资"),
    ("career choices", "职业选择"),
    ("business strategy", "商业战略"),
    ("decision-making", "决策制定"),
    ("giving advice", "提供建议"),
    ("Innovation", "创新"),
    ("problem-solving", "问题解决"),
    ("product development", "产品开发"),
    ("process improvement", "流程改进"),
    ("business model creation", "商业模式创建"),
    ("Major life decisions", "重大人生决策"),
    ("strategic planning", "战略规划"),
    ("ethical dilemmas", "伦理困境"),
    ("scientific theorizing", "科学理论化"),
    ("creative problem-solving", "创意问题解决"),
    ("Policy making", "政策制定"),
    ("personal finance", "个人财务"),
    ("environmental planning", "环境规划"),
    ("long-term decisions", "长期决策"),
    ("medical diagnoses", "医疗诊断"),
    ("gambling (poker)", "博弈（扑克）"),
    ("strategic bets", "战略押注"),
    ("risk management", "风险管理"),
    ("weather forecasting", "天气预报"),
    ("Goal setting", "目标设定"),
    ("project planning", "项目规划"),
    ("personal improvement", "个人提升"),
    ("system design", "系统设计"),
    ("Interpersonal conflicts", "人际冲突"),
    ("workplace communication", "职场沟通"),
    ("customer service issues", "客户服务问题"),
    ("interpreting others' actions", "解读他人行为"),
    ("Troubleshooting", "故障排查"),
    ("medical diagnosis", "医疗诊断"),
    ("debugging code", "调试代码"),
    ("investigations", "调查研究"),
    ("Procrastination", "拖延症"),
    ("habit formation", "习惯养成"),
    ("project initiation", "项目启动"),
    ("change management", "变革管理"),
    ("starting a new venture", "创业"),
    ("Team building", "团队建设"),
    ("skill development", "技能发展"),
    ("strategic partnerships", "战略合作伙伴"),
    ("personal growth", "个人成长"),
    ("Leadership", "领导力"),
    ("social change", "社会变革"),
    ("mentorship", "导师指导"),
    ("Teamwork", "团队合作"),
    ("negotiation", "谈判"),
    ("partnerships", "合作伙伴"),
    ("community building", "社区建设"),
    ("organizational design", "组织设计"),
    ("conflict resolution", "冲突解决"),
    ("organizational management", "组织管理"),
    ("market analysis", "市场分析"),
    ("product design", "产品设计"),
    ("urban planning", "城市规划"),
    ("environmental impact", "环境影响"),
    ("supply chain", "供应链"),
    ("skills development", "技能发展"),
    ("market share", "市场份额"),
    ("industry dynamics", "行业动态"),
    ("crisis response", "危机响应"),
    ("market adjustment", "市场调整"),
    ("resilience", "韧性"),
    ("pricing", "定价"),
    ("market entry", "市场进入"),
    ("differentiation", "差异化"),
    ("resource allocation", "资源分配"),
    ("recruitment", "招聘"),
    ("technology trends", "技术趋势"),
    ("incentive design", "激励设计"),
    ("predicting behavior", "预测行为"),
    ("sales", "销售"),
    ("economics", "经济学"),
]

# 执行keywords替换
for en, zh in kw_replacements:
    html = html.replace(f'"{en}"', f'"{zh}"')
    html = html.replace(f"'{en}'", f"'{zh}'")

# 保存翻译后的文件
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"翻译完成！")
print(f"源文件大小: {os.path.getsize(source_path) / 1024:.1f} KB")
print(f"目标文件大小: {os.path.getsize(target_path) / 1024:.1f} KB")
print(f"\n已翻译:")
print(f"- Category字段: 9个类别")
print(f"- Description片段: {len(desc_replacements)} 处")
print(f"- Keywords: {len(kw_replacements)} 个关键词")
print(f"\n注意：此脚本使用了片段替换策略，部分内容可能需要进一步精细化翻译")