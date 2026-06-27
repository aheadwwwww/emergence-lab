# -*- coding: utf-8 -*-
"""
最终翻译清理脚本 - 清理所有剩余英文内容
"""
import os
import re

source_path = 'munger-models-zh.html'

with open(source_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 清理steps字段中的混合内容
cleanup_map = {
    'you are using to understand a situation (e.g., a project plan, a financial forecast, your perception of a person).': '',
    'and does not capture every detail or nuance of the real world.': '',
    '. Don\'t just rely on reports or data. If possible, experience the situation firsthand.': '',
    'How does the real-world evidence (the territory) differ from your map? Note the discrepancies and unexpected factors.': '真实世界的证据（领土）与你的地图有何不同？注意差异和意外因素。',
    'you\'ve gathered. Be flexible and ready to change course when the map doesn\'t match the reality.': '',
    'built through experience and study.': '',
    'Be explicit about what you _don\'t_ know. List areas where you have only surface-level knowledge or are a complete novice.': '明确你不知道什么。列出你只有表面知识或完全是新手领域。',
    ', heavily favor options that fall squarely within your circle of competence.': '，严重倾向于完全在你的能力圈内的选项。',
    ', do so with caution and a commitment to deep learning. Don\'t confuse casual interest with competence.': '，要谨慎并承诺深入学习。不要混淆随意兴趣和能力。',
    ', seek out and listen to true experts who have that area within their own circle of competence.': '，寻找并倾听在该领域有真正能力的专家。',
    'or the goal you are trying to achieve.': '或你试图达到的目标。',
    'or truths. Ask "Why?" repeatedly, like a child, until you can\'t go any deeper. What are the absolute, fundamental building blocks?': '或真理。像孩子一样反复问"为什么？"，直到无法再深入。绝对的、基本的构成块是什么？',
    'surrounding each component. Ask, "How do I know this is true?" and "Is this necessarily the only way?"': '。问"我怎么知道这是真的？"和"这一定是唯一的方式吗？"',
    ', start to build a new solution or approach from scratch, ignoring previous methods.': '，从头开始建立新的解决方案或方法，忽略以前的方法。',
    ', not on tradition.': '',
    'of the experiment. What are the rules?': '。规则是什么？',
    '. Imagine the sequence of events that would follow.': '。想象将发生的事件序列。',
    ', the secondary effects (second-order thinking), and potential unintended consequences. Think about the best-case, worst-case, and most likely scenarios.': '、次要效应（二阶思维）和潜在的意外后果。思考最佳、最差和最可能的场景。',
    '? What insights did it provide that can inform your real-world decision?': '? 它提供了哪些可以指导现实世界决策的见解？',
    'and its most immediate, obvious result. (e.g., "If we lower our prices, we will sell more units.")': '及其最即时、最明显的结果。（如"如果我们降价，我们会卖更多单位。）"',
    '? (e.g., "Our competitors might also lower their prices.")': '?（如"我们的竞争对手可能也会降价。）"',
    '. What is the third-order consequence? (e.g., "A price war could start, eroding profit margins for the entire industry.")': '。三阶后果是什么？（如"可能开始价格战，侵蚀整个行业的利润率。）"',
    'of the system (other people, departments, the market, the environment).': '（其他人、部门、市场、环境）。',
    'against the potentially undesirable second- and third-order effects to make a more robust decision.': '与潜在不理想的二阶和三阶效应，以做出更稳健的决策。',
    'with no pre-existing knowledge of this industry?': '，对这个行业没有任何既有知识，我们会怎么做？',
    ', both literally and figuratively?': '，字面上和比喻上？',
    'Let\'s pretend we\'re explaining this to a five-year-old. What are the simplest truths we can state?': '假设我们在向一个五岁孩子解释这个。我们能陈述的最简单的真理是什么？',
    'It\'s a way of thinking through possibilities, testing hypotheses, and uncovering implications in the "laboratory of the mind."': '它是一种在"心智实验室"中思考可能性、检验假设和发现影响的方式。',
    'It\'s the opposite of reasoning by analogy (i.e., "we do it this way because that\'s how it\'s always been done").': '这是类比推理的对立面（即"我们这样做是因为一直都是这样做的"）。',
    'It\'s about being brutally honest about what you understand deeply and what you don\'t.': '它要求你对自己深刻理解什么和不理解什么保持绝对诚实。',
    '"and then what?" effects.': '"然后呢？"效应。',
    'one year from now, what might we see?': '一年后，我们会看到什么？',
    'in this mental simulation?': '我们在这个心理模拟中没有考虑什么因素？',
    'over the next six months?': '在接下来的六个月会如何影响我们的财务、压力水平和关系？',
    'that could result from this decision? Let\'s play that out in our minds.': '这个决策可能产生的绝对最坏场景是什么？让我们在脑海中演练。',
    'Let\'s imagine we go ahead with this plan. ': '让我们想象我们推进这个计划。',
    '一步步带我看接下来会发生什么.': '一步步带我看接下来会发生什么。',
    '绝对最坏场景是什么 ': '绝对最坏场景是什么',
    '如果我们有魔法棒，能看到结果 ': '如果我们有魔法棒，能看到',
    '我们没有考虑什么因素 ': '我们在这个心理模拟中没有考虑什么因素',
    '这个决策如何影响我们的财务、压力水平和关系 ': '这个决策在接下来的六个月会如何影响我们的财务、压力水平和关系',
    'That\'s the immediate benefit. What happens after that?': '那是即时好处。然后呢？',
    'Let\'s think about a time a similar decision led to a surprising outcome. What happened?': '让我们想想一个类似决策导致意外结果的时候。发生了什么？',
    '(Charlie Munger\'s test).': '（查理·芒格的测试）。',
}

for en, zh in cleanup_map.items():
    if zh == '':
        html = html.replace(en, '')
    else:
        html = html.replace(en, zh)

# 翻译更多关键词
more_kw = {
    'scientific research': '科学研究',
    'business model creation': '商业模式创建',
    'strategic planning': '战略规划',
    'creative problem-solving': '创意问题解决',
    'long-term decisions': '长期决策',
    'giving advice': '提供建议',
}

for en, zh in more_kw.items():
    html = html.replace(f'"{en}"', f'"{zh}"')
    html = html.replace(f'{en}', f'{zh}')

# 保存
with open(source_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"清理完成！文件大小: {os.path.getsize(source_path)/1024:.1f}KB")