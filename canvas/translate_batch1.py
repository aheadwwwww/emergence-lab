#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芒格思维模型批量翻译脚本 - 第一批 (m01-m10)
只翻译description, avoid, keywords字段
steps和coaching字段转义复杂，需要单独处理
"""

import os
import shutil

src = r'D:\openclaw_workspace\canvas\munger-models-fixed.html'
dst = r'D:\openclaw_workspace\canvas\munger-models-zh.html'

# 读取文件
with open(dst, 'r', encoding='utf-8') as f:
    content = f.read()

print("开始翻译 m01-m10 的description, avoid, keywords字段...")

# 定义翻译映射
replacements = []

# m01
replacements.append(("description: 'This mental model is based on the idea that any representation of reality—be it a physical map, a business plan, a scientific theory, or a data model—is inherently a simplification and not reality itself. These \"maps\" are useful for navigation and understanding, but they are incomplete and can be misleading if we forget they are abstractions. Reality (\"the territory\") is infinitely more complex and detailed than any model we can create.'", "description: '这个思维模型基于这样一个理念：任何对现实的表征——无论是物理地图、商业计划、科学理论还是数据模型——本质上都是简化，而非现实本身。这些\"地图\"对于导航和理解是有用的，但如果我们忘记它们只是抽象，就会产生误导。现实（\"领土\"）比我们能创造的任何模型都更加复杂和详尽。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Low-Stakes Decisions:** When a decision is quick, low-impact, and easily reversible, a \"good enough\" map is sufficient. Over-analyzing the territory can lead to decision paralysis when the cost of being wrong is low. - **When the Map is Reliable:** In highly predictable environments (e.g., basic physics), the map is extremely accurate. Questioning it without new evidence is inefficient.'", "avoid: '（或谨慎使用）：** - **低风险决策时：** 当决策快速、影响小且容易逆转时，\"足够好\"的地图就足够了。在错误成本较低时过度分析实际情况会导致决策瘫痪。 - **地图可靠时：** 在高度可预测的环境（如基础物理学）中，地图极其准确。在没有新证据的情况下质疑它是不高效的。'"))

replacements.append(('keywords: ["Strategic planning", "data analysis", "project management", "personal development", "financial forecasting", "scientific research."]', 'keywords: ["战略规划", "数据分析", "项目管理", "个人发展", "财务预测", "科学研究。"]'))

# m02
replacements.append(("description: 'This model, famously advocated by Warren Buffett, emphasizes the importance of knowing the boundaries of your own knowledge and skills. It's about being brutally honest about what you understand deeply and what you don't. Making critical decisions outside your circle of competence is a recipe for disaster, as you risk operating on flawed assumptions and partial knowledge.'", "description: '这个模型由沃伦·巴菲特著名倡导，强调了解自己知识和技能边界的重要性。它要求对自己深刻理解什么、不理解什么保持极度诚实。在能力圈之外做关键决策是灾难的配方，因为你可能基于错误假设和不完整知识进行操作。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Exploring New Domains:** The model should not be used as an excuse to avoid learning. Deliberately stepping outside your circle is a prerequisite for growth and innovation. - **In Collaborative Teams:** In a team setting, the focus should be on the collective circle of competence. Deferring to others' expertise is more important than staying within your own individual circle.'", "avoid: '（或谨慎使用）：** - **探索新领域时：** 这个模型不应成为逃避学习的借口。有意走出能力圈是成长和创新的前提。 - **团队协作中：** 在团队环境中，重点应该是集体的能力圈。尊重他人的专业比停留在自己的个人能力圈更重要。'"))

replacements.append(('keywords: ["Investing", "career choices", "business strategy", "decision-making", "giving advice."]', 'keywords: ["投资", "职业选择", "商业战略", "决策制定", "提供建议。"]'))

# m03
replacements.append(("description: 'First-principles thinking is the act of deconstructing a problem or idea down to its most fundamental, foundational truths—the things you know are true beyond any doubt. From there, you reason up from scratch, challenging all assumptions and conventions. It's the opposite of reasoning by analogy (i.e., \"we do it this way because that's how it's always been done\").'", "description: '第一性原理思维是将问题或想法分解到最基本、最基础的真理——那些你毫无疑问知道是真实的东西。然后从零开始推理，挑战所有假设和惯例。这是类比推理的对立面（即\"我们这样做是因为一直都是这样做的\"）。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Incremental Improvements:** When a system is already working well and only needs minor optimization, reasoning from first principles is often too slow and unnecessary. Analogy and precedent are more efficient here. - **Under Severe Time Constraints:** Deconstructing a problem to its core takes time. When a rapid decision is required, relying on established best practices is often the only viable option.'", "avoid: '（或谨慎使用）：** - **增量改进时：** 当系统已经运行良好只需要微调优化时，从第一原理推理通常太慢且不必要。类比和先例在这里更高效。 - **严重时间限制下：** 将问题分解到核心需要时间。当需要快速决策时，依赖既定的最佳实践往往是唯一可行的选择。'"))

replacements.append(('keywords: ["Innovation", "problem-solving", "product development", "process improvement", "business model creation."]', 'keywords: ["创新", "问题解决", "产品开发", "流程改进", "商业模式创建。"]'))

# m04
replacements.append(("description: 'A thought experiment is a mental simulation used to explore the potential consequences of an idea or action without having to enact it in reality. It's a way of thinking through possibilities, testing hypotheses, and uncovering implications in the \"laboratory of the mind.\"'", "description: '思想实验是一种心理模拟，用于探索想法或行动的潜在后果，而无需在现实中实际执行。这是一种在\"心灵实验室\"中思考可能性、测试假设和揭示含义的方式。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Direct Experimentation is Cheap:** If you can easily test a hypothesis in the real world, do that instead. A thought experiment is a substitute for, not a superior alternative to, real-world data. - **If You Lack Foundational Knowledge:** A thought experiment is only as good as the user's understanding of the variables. If the user is ignorant of the basic principles of a system, the simulation will be flawed and its conclusions unreliable.'", "avoid: '（或谨慎使用）：** - **直接实验成本低时：** 如果可以容易地在现实世界中测试假设，那就那样做。思想实验是替代品，而非真实世界数据的优越替代。 - **缺乏基础知识时：** 思想实验的质量取决于用户对变量的理解。如果用户对系统的基本原理无知，模拟将会有缺陷，其结论不可靠。'"))

replacements.append(('keywords: ["Major life decisions", "strategic planning", "ethical dilemmas", "scientific theorizing", "creative problem-solving."]', 'keywords: ["重大人生决策", "战略规划", "伦理困境", "科学理论化", "创造性问题解决。"]'))

# m05
replacements.append(("description: 'This is the practice of thinking beyond the immediate consequences of a decision and considering the longer-term, \"and then what?\" effects. First-order thinking is fast and easy, focusing on the direct result. Second-order thinking is more deliberate and complex, as it explores the ripple effects and unintended consequences that unfold over time.'", "description: '这是超越决策即时后果的实践，考虑更长期的\"然后呢？\"效应。一阶思维快速且简单，关注直接结果。二阶思维更深思熟虑且复杂，因为它探索随时间展开的涟漪效应和意外后果。'"))

replacements.append(("avoid: '(or Use with Caution):** - **In True Emergencies:** During a crisis that requires an immediate response (e.g., a server is down), the priority is the first-order effect of fixing the problem. Second-order analysis can wait until after the imminent threat is neutralized. - **On Trivial Matters:** Applying deep, long-term thinking to insignificant decisions (e.g., what to eat for lunch) is a waste of cognitive resources.'", "avoid: '（或谨慎使用）：** - **真正紧急情况中：** 在需要即时响应的危机中（如服务器宕机），优先级是解决问题的一阶效应。二阶分析可以在即时威胁消除后进行。 - **琐碎事项上：** 对无关紧要的决策（如午餐吃什么）应用深度、长期的思考是对认知资源的浪费。'"))

replacements.append(('keywords: ["Policy making", "business strategy", "personal finance", "environmental planning", "long-term decisions."]', 'keywords: ["政策制定", "商业战略", "个人理财", "环境规划", "长期决策。"]'))

# m06
replacements.append(("description: 'Probabilistic thinking involves using statistical and logical reasoning to estimate the likelihood of different outcomes. Instead of seeing the world in black-and-white certainties (\"this will happen\"), you see it in shades of gray, assigning probabilities to possibilities. This helps you make better decisions in the face of uncertainty.'", "description: '概率思维涉及使用统计和逻辑推理来估计不同结果的可能性。你不以黑白分明的方式看待世界（\"这会发生\"），而是以灰色阴影的方式，给可能性分配概率。这帮助你在面对不确定性时做出更好的决策。'"))

replacements.append(("avoid: '(or Use with Caution):** - **In High-Stakes, Fat-Tailed Domains:** In domains where a single, low-probability event can have catastrophic consequences (e.g., nuclear safety), one cannot rely on probability alone. The magnitude of the worst-case scenario is more important than its likelihood. - **When Data is Misleading:** Probabilities are only as good as the data they are based on. If the data is biased, incomplete, or from a different context, the resulting probabilities will be dangerously inaccurate.'", "avoid: '（或谨慎使用）：** - **高风险、肥尾领域：** 在单个低概率事件可能造成灾难性后果的领域（如核安全），不能仅依赖概率。最坏情况的严重性比其可能性更重要。 - **数据误导时：** 概率的质量取决于其基于的数据。如果数据有偏见、不完整或来自不同语境，得出的概率将危险地不准确。'"))

replacements.append(('keywords: ["Investing", "medical diagnoses", "gambling (poker)", "strategic bets", "risk management", "weather forecasting."]', 'keywords: ["投资", "医疗诊断", "赌博（扑克）", "战略性押注", "风险管理", "天气预报。"]'))

# m07
replacements.append(("description: 'Inversion is a powerful thinking tool that involves approaching a problem or goal backward. Instead of asking, \"How can I achieve success?\" you ask, \"What could cause me to fail?\" By identifying and then systematically avoiding all the potential pitfalls, you dramatically increase your chances of reaching your desired outcome.'", "description: '逆向思维是一个强大的思考工具，涉及从后向前处理问题或目标。与其问\"我如何实现成功？\"你问\"什么可能导致我失败？\"通过识别然后系统地避免所有潜在陷阱，你大幅增加达到预期结果的机会。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Simple, Direct Problems:** If the path to success is straightforward and well-understood, inversion adds unnecessary complexity. It is most useful for complex, ambiguous, or high-stakes problems. - **When It Leads to Excessive Pessimism:** While useful for risk management, focusing exclusively on failure can stifle creativity and risk-taking. It should be balanced with a forward-looking vision of success.'", "avoid: '（或谨慎使用）：** - **简单直接问题时：** 如果通往成功的道路直接且明确，逆向思维增加不必要的复杂性。它最适用于复杂、模糊或高风险问题。 - **导致过度悲观时：** 虽然对风险管理有用，但专注于失败会扼杀创造力和冒险精神。应该与前瞻性的成功愿景平衡。'"))

replacements.append(('keywords: ["Goal setting", "project planning", "risk management", "personal improvement", "system design."]', 'keywords: ["目标设定", "项目规划", "风险管理", "个人改进", "系统设计。"]'))

# m08
replacements.append(("description: 'Hanlon\\'s Razor is a mental model that advises: \"Never attribute to malice that which is adequately explained by stupidity\" (or incompetence, ignorance, or neglect). It suggests that when something goes wrong or someone acts in a way that negatively affects you, it\\'s far more likely to be the result of a mistake or oversight than a deliberate attempt to cause you harm.'", "description: '汉隆剃刀是一个思维模型，建议：\"永远不要把可以用愚蠢解释的事情归咎于恶意\"（或无能、无知或疏忽）。它建议当事情出错或某人以对你负面影响的方式行动时，这更可能是错误或疏忽的结果，而非故意伤害你的企图。'"))

replacements.append(("avoid: '(or Use with Caution):** - **When Faced with Repeated Negative Behavior:** If a person or system repeatedly causes the same negative outcome, it is no longer a random mistake. The cause may be systemic incompetence or, in some cases, malice. Don\\'t let the razor justify inaction in the face of patterns. - **In Adversarial Contexts:** In situations that are explicitly competitive or adversarial (e.g., a zero-sum negotiation, warfare), assuming your opponent is not acting maliciously is naive and dangerous.'", "avoid: '（或谨慎使用）：** - **面对重复负面行为时：** 如果某人或系统反复造成同样的负面结果，这不再是随机错误。原因可能是系统性无能，或某些情况下的恶意。不要让剃刀为面对模式时的不行动辩护。 - **对抗性语境中：** 在明确竞争或对抗的情况下（如零和谈判、战争），假设对手不是恶意行动是天真的危险。'"))

# m08 keywords - 注意转义
replacements.append(('keywords: ["Interpersonal conflicts", "workplace communication", "customer service issues", "interpreting others\' actions."]', 'keywords: ["人际冲突", "职场沟通", "客户服务问题", "解读他人行动。"]'))

# m09
replacements.append(("description: 'Occam\\'s Razor is a problem-solving principle that states when you are presented with multiple competing explanations for a phenomenon, the simplest one—the one with the fewest assumptions—is the most likely to be correct. It\\'s a mental razor that \"shaves away\" unnecessary complexity.'", "description: '奥卡姆剃刀是一个问题解决原则，当面对多个竞争解释时，最简单的那个——假设最少的那一个——最可能是正确的。这是一个心理剃刀，\"剃掉\"不必要的复杂性。'"))

replacements.append(("avoid: '(or Use with Caution):** - **Inherently Complex Systems:** Do not apply rigidly to fields like biology, economics, or social dynamics, where outcomes often result from many interacting variables and the simplest explanation can be misleading. - **When Evidence Points to Complexity:** If the simplest explanation is tested and fails to account for the evidence, it must be discarded in favor of a more complex one that fits the facts. - **Insufficient Data:** Be cautious when evidence is scarce. The \"simplest\" explanation may just be the most obvious, not the most correct.'", "avoid: '（或谨慎使用）：** - **固有复杂系统：** 不要严格应用于生物学、经济学或社会动力学等领域，那里结果往往来自许多交互变量，最简单的解释可能有误导性。 - **证据指向复杂性时：** 如果最简单的解释经过测试无法解释证据，必须放弃它，转向更复杂但符合事实的解释。 - **数据不足时：** 证据稀少时要谨慎。\"最简单\"的解释可能只是最明显的，而非最正确的。'"))

replacements.append(('keywords: ["Troubleshooting", "scientific theorizing", "medical diagnosis", "debugging code", "investigations."]', 'keywords: ["故障排查", "科学理论化", "医疗诊断", "调试代码", "调查。"]'))

# m10
replacements.append(("description: 'Activation energy is the initial spark of effort required to start a process or reaction. Just as a chemical reaction needs a certain amount of energy to begin, many tasks, projects, and habits require an upfront investment of energy to overcome inertia and get started. Once this initial barrier is overcome, the process can often continue with much less effort, driven by its own momentum.'", "description: '活化能是启动过程或反应所需的初始努力火花。就像化学反应需要一定能量才能开始，许多任务、项目和习惯需要前置能量投入来克服惰性并开始。一旦这个初始障碍被克服，过程通常可以以更少努力继续，由其自身动力驱动。'"))

replacements.append(("avoid: '(or Use with Caution):** - **For Unsustainable goals:** Applying a massive burst of activation energy to a goal that is fundamentally unsustainable or poorly planned can lead to quick burnout and failure. - **When the task is impossible:** No amount of activation energy can make an impossible task possible. It\\'s crucial to distinguish between a high barrier to entry and a literal dead end.'", "avoid: '（或谨慎使用）：** - **不可持续目标：** 对根本不可持续或计划不善的目标投入大量活化能可能导致快速倦怠和失败。 - **任务不可能时：** 无论多少活化能都无法使不可能的任务变为可能。区分高进入门槛和真正死胡同至关重要。'"))

replacements.append(('keywords: ["Procrastination", "habit formation", "project initiation", "innovation", "change management", "starting a new venture."]', 'keywords: ["拖延", "习惯形成", "项目启动", "创新", "变革管理", "创业。"]'))

# 执行替换
success = 0
fail = 0

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        success += 1
    else:
        fail += 1
        # 尝试打印更详细的错误信息
        print(f"未找到: {old[:80]}...")

# 保存
with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n翻译完成！成功: {success}, 失败: {fail}")
print("m01-m10的description, avoid, keywords字段已翻译")