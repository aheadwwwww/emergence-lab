import json

models_raw = [
    ["m1","决策","第一性原理","拆解到最基本事实，从零重建","把问题拆到不能再拆的基本元素，抛弃所有假设和惯例，从最底层重新构建解决方案。马斯克用这个方法把火箭成本降到1/10。","当被告知不可能时；当行业惯例成为枷锁时；当需要突破性创新时","1. 明确你要解决的问题是什么|2. 拆解：这个问题由哪些基本元素构成？|3. 质疑：哪些是事实，哪些只是惯例？|4. 重建：从基本事实出发，能有什么新方案？"],
    ["m2","决策","二阶思维","思考后果的后果","不只考虑直接结果，还要想'然后呢？'。第一阶：降价导致销量上升。第二阶：竞品跟进导致利润都下降导致行业洗牌。","做战略决策时；评估政策影响时；投资判断时","1. 列出决策的直接后果|2. 对每个后果问会发生什么|3. 重复至少两次|4. 比较一阶和二阶的差异"],
    ["m3","决策","逆向思维","从失败倒推","不问怎么成功，问怎么失败然后避免。芒格说：告诉我我会死在哪，我永远不去那里。","风险评估；项目启动前；重大决策前","1. 定义你想要的结果|2. 反过来问：怎样确保达不到？|3. 列出所有失败路径|4. 逐一设计防范措施"],
    ["m4","决策","思想实验","在脑子里做实验","在大脑中模拟场景，探索假设和可能性。爱因斯坦用思想实验发现了相对论。","无法做真实实验时；探索如果会怎样；测试假设","1. 设定场景和假设条件|2. 在脑中推演事件发展|3. 观察矛盾点和意外发现|4. 提炼可验证的结论"],
    ["m5","决策","概率思维","用概率而非确定论看世界","未来不是确定的，是一组概率分布。好的决策是选择胜率更高的选项，而非保证赢的选项。","面对不确定性；评估风险；做预测","1. 列出所有可能的结果|2. 估算每种结果的概率|3. 计算期望值|4. 选择期望值最高的方案"],
    ["m6","决策","能力圈","知道边界在哪比圈子多大更重要","巴菲特和芒格的核心原则。不在能力圈外做决策。圈的大小不重要，知道边界在哪才重要。","做投资决策；接受新任务；给别人建议","1. 问自己：这件事我真的懂吗？|2. 区分知道和以为自己知道|3. 在圈外时承认不懂找懂的人|4. 持续扩大能力圈"],
    ["m7","决策","地图非领土","模型不等于现实","任何理论、模型、计划都只是现实的简化表示。地图再精确也不是领土本身。不要爱上自己的模型。","制定计划时；使用理论框架时；分析数据时","1. 确认你用的是哪个地图|2. 问：这个地图忽略了什么？|3. 去领土上实地验证|4. 根据现实反馈更新地图"],
    ["m8","决策","奥卡姆剃刀","最简单的解释往往是对的","在多个解释中，选择假设最少的那个。不是简单的一定对，而是不必要的复杂通常是错的。","面对多个解释时；设计方案时；调试问题时","1. 列出所有可能的解释|2. 数每个解释需要多少假设|3. 优先验证假设最少的|4. 如果不够再逐步增加复杂度"],
    ["m9","决策","汉隆剃刀","能用愚蠢解释的，不要归咎于恶意","别人做了让你不爽的事，先假设他是疏忽或无知，而不是故意害你。大多数恶意其实是笨拙。","被人冒犯时；解读竞争对手行为；处理冲突","1. 暂停：感受到被冒犯时先停下来|2. 列出其他可能的解释|3. 问：有证据证明是恶意吗？|4. 没有证据就选最善意的解释"],
    ["m10","经济学","复利","利滚利，时间是最好的杠杆","收益产生收益，形成指数增长。不只是钱，知识、技能、人际关系都遵循复利。关键是持续投入和时间。","投资理财；学习规划；职业发展","1. 找到能产生复利的事|2. 尽早开始让时间发挥作用|3. 保持持续投入不要中断|4. 耐心等待指数拐点"],
    ["m11","经济学","机会成本","选择的真正代价是你放弃的东西","做一件事的成本不是花的时间和钱，而是用同样的资源能做的最好的另一件事。","做选择时；分配资源时；评估时间投入","1. 列出你正在放弃的选项|2. 找出其中价值最高的|3. 问：选A放弃B值得吗？|4. 用放弃的最好选项来衡量成本"],
    ["m12","经济学","安全边际","留足缓冲应对意外","工程师造桥不造刚好承重的桥，而是留几倍余量。投资、计划、承诺都应该留安全边际。","做预算；承诺截止日期；投资决策","1. 估算最坏情况需要什么|2. 在估算基础上加缓冲30%到100%|3. 按加了缓冲的标准执行|4. 永远不要刚好卡在极限上"],
    ["m13","经济学","供需关系","价格由供需决定不是由成本决定","东西值多少钱不取决于你花了多少成本，取决于有多少人想要、有多少人提供。","定价；分析市场；理解价格波动","1. 识别谁是供给方谁是需求方|2. 分析供给和需求各自的弹性|3. 预测什么因素会改变供给或需求|4. 判断价格会往哪个方向走"],
    ["m14","经济学","稀缺性","有限的资源无限的需求","经济学的基本前提。因为稀缺所以需要选择，因为选择所以有机会成本。稀缺创造价值。","资源分配；优先级排序；理解价值","1. 识别什么是真正稀缺的|2. 区分稀缺和短暂短缺|3. 问：谁控制了稀缺资源？|4. 思考如何创造或获取稀缺资源"],
    ["m15","经济学","激励","人会对激励做出反应","芒格说：告诉我激励是什么，我告诉你结果是什么。设计错误的激励会产生错误的行为。永远先看激励结构。","设计制度；管理团队；理解行为","1. 找出系统中所有的激励|2. 问这些激励会导致什么行为|3. 检查有没有激励在鼓励坏行为|4. 调整让激励和想要的结果对齐"],
    ["m16","心理学","确认偏误","人只看到自己想看到的","我们倾向于寻找、注意、记住支持自己观点的证据，忽略反对的证据。这是最普遍也最危险的认知偏差。","做判断时；收集信息时；评估证据时","1. 明确自己当前的信念是什么|2. 主动寻找反对的证据|3. 问如果我是错的会是什么原因|4. 让持不同观点的人来挑战你"],
    ["m17","心理学","社会认同","别人怎么做我就怎么做","在不确定时人会参考他人的行为。这是为什么排队、从众、潮流会形成。也是为什么泡沫会膨胀。","看到大家都在做某事时；做独立判断时；分析趋势","1. 意识到我是不是在跟风|2. 问如果没人这么做我还会做吗|3. 找反例有没有人不跟风也成功了|4. 独立评估这件事本身的价值"],
    ["m18","心理学","沉没成本","已经花掉的不应该影响未来决策","钱花出去了时间投入了，但这些不应该影响要不要继续。决策只看未来不看过去。","考虑是否放弃时；评估项目时；投资决策","1. 区分哪些是已经花掉的沉没成本|2. 问如果今天从零开始我会做这个选择吗|3. 只看未来的成本和收益|4. 如果答案是不果断放弃"],
    ["m19","心理学","锚定效应","第一个数字决定了你的判断范围","看到第一个价格后后续判断都会围绕它。标价1000打折到500你觉得便宜，但如果一开始标500呢？","谈判；定价；做估算","1. 识别第一个出现的数字是什么|2. 问如果没有这个锚我会怎么判断|3. 主动设置自己的锚|4. 在谈判中先出价"],
    ["m20","心理学","框架效应","怎么说比说什么更重要","同样的信息换个说法人的反应完全不同。存活率90%和死亡率10%是一回事但感受截然不同。","沟通；说服；做选择时","1. 识别当前的表述框架|2. 换个框架重新描述同一件事|3. 问不同框架下我的判断会变吗|4. 选择最能帮助理性决策的框架"],
    ["m21","心理学","损失厌恶","失去的痛苦大于得到的快乐","失去100块的痛苦大约是得到100块快乐的两倍。这导致人过度保守不愿放弃不愿冒险。","做风险决策；考虑改变；评估投资","1. 识别我是不是因为怕失去而在回避|2. 量化失去和得到的实际价值|3. 问如果这已经是失去的状态我会花多少挽回|4. 用理性计算代替情绪反应"],
    ["m22","系统思维","反馈循环","输出反过来影响输入","正反馈：A增加导致B增加导致A更增加。负反馈：A增加导致B减少导致A被抑制。系统行为由反馈结构决定。","分析系统行为；设计流程；理解增长或衰退","1. 画出系统的因果链条|2. 找出所有反馈回路|3. 判断每条回路是正反馈还是负反馈|4. 问主导回路是什么它会把系统带向哪里"],
    ["m23","系统思维","涌现","整体大于部分之和","简单规则在大量交互后产生复杂行为。蚁群没有CEO但能建复杂的巢。意识从神经元中涌现。","理解复杂系统；设计规则；分析群体行为","1. 识别系统的微观规则是什么|2. 观察宏观层面出现了什么模式|3. 问这个模式能从微观规则推导出来吗|4. 如果不能这就是涌现"],
    ["m24","系统思维","瓶颈","系统最慢的环节决定整体速度","一条流水线的速度由最慢的工位决定。优化非瓶颈环节是浪费。找到瓶颈解决它然后找下一个。","优化流程；提高效率；诊断问题","1. 画出整个流程|2. 找出最慢最堵的环节|3. 集中资源解决这个环节|4. 解决后新的瓶颈会出现重复此过程"],
    ["m25","系统思维","杠杆点","小改变大影响","系统中有些点稍微用力就能产生巨大变化。找到这些点比盲目努力重要100倍。","推动变革；解决问题；提高效率","1. 理解系统的结构|2. 列出所有可以干预的点|3. 评估每个点的杠杆效应|4. 优先干预杠杆最大的点"],
    ["m26","系统思维","路径依赖","历史决定未来","一旦走上某条路就很难换。QWERTY键盘不是最优布局但所有人都习惯了。选择初始路径时要格外谨慎。","做初始选择；设计标准；理解行业格局","1. 识别当前状态是哪些历史选择造成的|2. 问如果重来我会选这条路吗|3. 评估转换成本有多高|4. 在起点时多花时间选对路"],
    ["m27","系统思维","熵增","封闭系统必然走向无序","热力学第二定律。不持续输入能量或信息任何系统都会退化。这就是为什么维护比建设更难。","理解衰退；维护系统；组织管理","1. 识别系统是封闭的还是开放的|2. 测量无序度在增加吗|3. 找到负熵源什么在对抗熵增|4. 持续注入能量信息和秩序"],
    ["m28","生物学","演化","变异加选择加时间等于适应","不需要设计师不需要目标。随机变异环境选择适者生存。这是地球上最强大的优化算法。","理解变化；设计迭代流程；接受不确定性","1. 创造变异尝试不同的方案|2. 设置选择标准什么算好|3. 保留好的淘汰差的|4. 重复很多次"],
    ["m29","生物学","生态位","找到你独有的位置","每个物种都有自己的生态位。商业也一样找到别人做不了或不愿做的位置。","职业规划；商业定位；竞争策略","1. 分析环境有什么未被满足的需求|2. 评估自己有什么独特优势|3. 匹配优势和需求的交集就是你的生态位|4. 深耕在生态位里做到最好"],
    ["m30","生物学","合作","一起做比单干强","演化不只是竞争合作同样重要。共生、互惠、协作自然界充满了合作的例子。","团队协作；商业合作；生态设计","1. 识别谁和你有互补的能力|2. 设计如何让合作双方都受益|3. 建立信任从小合作开始|4. 扩展成功的合作模式可以复制"],
    ["m31","生物学","自催化","产物加速自己的生产","化学反应中产物本身是催化剂。商业中用户越多产品越好导致产品越好用户越多。这是指数增长的底层机制。","理解增长；设计产品；分析网络效应","1. 识别什么在加速自己的增长|2. 问增长是自催化的还是外部驱动的|3. 如果是自催化找到加速循环的关键环节|4. 小心自催化也会加速崩溃"],
    ["m32","其他","临界质量","过了某个点变化不可逆","核反应需要足够的铀堆在一起才能链式反应。社会运动、技术采用、市场引爆都有临界质量。","推动变革；产品发布；理解趋势","1. 定义什么状态算引爆|2. 估算需要多少积累才能到临界点|3. 集中资源推过临界点|4. 过了临界点后系统会自我维持"],
    ["m33","其他","林迪效应","存在越久的东西未来存在越久","一本书卖了100年大概率还会再卖100年。时间是质量的过滤器。","选择学习内容；判断趋势；做长期决策","1. 问这个东西存在多久了|2. 存在越久未来预期寿命越长|3. 优先选择经得起时间考验的东西|4. 对新事物保持谨慎"],
    ["m34","其他","帕累托法则","80%的结果来自20%的原因","80%的销售额来自20%的客户。80%的成果来自20%的努力。找到那20%把精力集中在那里。","优先级排序；资源分配；提高效率","1. 列出所有投入和产出|2. 找出贡献最大的20%|3. 把80%精力放在这20%上|4. 对剩下的80%减少投入或放弃"],
]

# Build HTML
cats_map = {}
for m in models_raw:
    cats_map.setdefault(m[1], []).append(m)

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>芒格思维模型库 - 34个核心模型</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:15px}
.container{max-width:1400px;margin:0 auto;background:white;border-radius:15px;box-shadow:0 15px 50px rgba(0,0,0,0.3);overflow:hidden}
header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:25px;text-align:center}
h1{font-size:2em;margin-bottom:5px}
.subtitle{font-size:1em;opacity:0.9}
.stats{display:flex;justify-content:space-around;padding:15px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.stat{text-align:center}
.stat-number{font-size:2em;font-weight:bold;color:#667eea}
.stat-label{color:#6c757d;margin-top:2px;font-size:0.85em}
.main-content{display:grid;grid-template-columns:200px 1fr;min-height:600px}
.sidebar{background:#f8f9fa;padding:10px;border-right:1px solid #e9ecef;overflow-y:auto;max-height:600px}
.sidebar input{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;margin-bottom:10px;font-size:0.85em}
.cat-title{font-weight:bold;color:#495057;padding:6px 8px;background:white;border-radius:4px;margin:8px 0 5px;cursor:pointer;font-size:0.85em}
.cat-title:hover{background:#667eea;color:white}
.model-item{padding:5px 8px;cursor:pointer;border-radius:3px;font-size:0.8em;color:#6c757d;margin-bottom:1px}
.model-item:hover{background:#e9ecef;color:#495057}
.model-item.active{background:#667eea;color:white}
.content{padding:25px;overflow-y:auto;max-height:600px}
.welcome{text-align:center;padding:60px 20px}
.welcome h2{font-size:1.5em;color:#495057;margin-bottom:12px}
.welcome p{color:#6c757d;font-size:0.9em;line-height:1.6}
.model-detail{display:none}
.model-detail.active{display:block}
.model-header{margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid #e9ecef}
.model-badge{display:inline-block;background:#667eea;color:white;padding:3px 10px;border-radius:10px;font-weight:bold;margin-bottom:5px;font-size:0.85em}
.model-title{font-size:1.5em;color:#495057;margin-bottom:3px}
.model-core{font-size:1em;color:#667eea;margin-bottom:8px;font-style:italic}
.section{margin-bottom:18px}
.section-title{font-size:1em;color:#667eea;margin-bottom:8px;display:flex;align-items:center}
.section-title::before{content:'';display:inline-block;width:3px;height:14px;background:#667eea;margin-right:6px;border-radius:2px}
.section-content{color:#495057;line-height:1.7;padding-left:9px;font-size:0.9em}
.steps-list{list-style:none;padding-left:9px;counter-reset:step}
.steps-list li{padding:4px 0;color:#495057;font-size:0.9em;line-height:1.5;counter-increment:step}
.steps-list li::before{content:counter(step);display:inline-block;width:20px;height:20px;background:#667eea;color:white;border-radius:50%;text-align:center;line-height:20px;font-size:0.75em;margin-right:8px}
.learn-btn{display:inline-block;margin-top:15px;padding:8px 20px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer;font-size:0.9em}
.learn-btn:hover{background:#5a6fd6}
.learn-btn.learned{background:#28a745}
</style>
</head>
<body>
<div class="container">
<header>
<h1>芒格思维模型库</h1>
<p class="subtitle">查理芒格的多元思维模型 -- 34个核心模型 | 全中文</p>
</header>
<div class="stats">
<div class="stat"><div class="stat-number">34</div><div class="stat-label">思维模型</div></div>
<div class="stat"><div class="stat-number">6</div><div class="stat-label">分类</div></div>
<div class="stat"><div class="stat-number" id="learned-count">0</div><div class="stat-label">已学习</div></div>
</div>
<div class="main-content">
<div class="sidebar">
<input type="text" id="search" placeholder="搜索模型..." oninput="filterModels()">
''')

cat_order = ["决策","经济学","心理学","系统思维","生物学","其他"]
for cat in cat_order:
    models_in_cat = cats_map.get(cat, [])
    html_parts.append(f'<div class="cat-title" onclick="toggleCat(this)">{cat} ({len(models_in_cat)})</div>')
    for m in models_in_cat:
        mid, cat2, title, core, desc, when, steps_str = m
        html_parts.append(f'<div class="model-item" data-cat="{cat}" data-id="{mid}" onclick="showModel(\'{mid}\')">{title}</div>')

html_parts.append('</div><div class="content" id="content-area">')
html_parts.append('<div class="welcome" id="welcome"><h2>选择一个模型开始学习</h2><p>查理芒格说：手里只有锤子的人，看什么都像钉子。<br>掌握多元思维模型，用不同的透镜看世界。</p></div>')

for m in models_raw:
    mid, cat, title, core, desc, when, steps_str = m
    steps = steps_str.split('|')
    steps_html = ''.join(f'<li>{s}</li>' for s in steps)
    html_parts.append(f'''
<div class="model-detail" id="detail-{mid}">
<div class="model-header">
<span class="model-badge">{cat}</span>
<h2 class="model-title">{title}</h2>
<p class="model-core">{core}</p>
</div>
<div class="section"><div class="section-title">描述</div><div class="section-content">{desc}</div></div>
<div class="section"><div class="section-title">何时使用</div><div class="section-content">{when}</div></div>
<div class="section"><div class="section-title">思考步骤</div><ol class="steps-list">{steps_html}</ol></div>
<button class="learn-btn" id="btn-{mid}" onclick="toggleLearned('{mid}')">标记为已学习</button>
</div>''')

html_parts.append('''</div></div></div>
<script>
let learned=JSON.parse(localStorage.getItem("munger-learned")||"{}");
function showModel(id){
document.querySelectorAll(".model-detail").forEach(d=>d.classList.remove("active"));
document.querySelectorAll(".model-item").forEach(i=>i.classList.remove("active"));
document.getElementById("detail-"+id).classList.add("active");
let item=document.querySelector('.model-item[data-id="'+id+'"]');
if(item)item.classList.add("active");
document.getElementById("welcome").style.display="none";
updateBtn(id);
}
function toggleLearned(id){
learned[id]=!learned[id];
localStorage.setItem("munger-learned",JSON.stringify(learned));
updateBtn(id);
updateCount();
}
function updateBtn(id){
let btn=document.getElementById("btn-"+id);
if(learned[id]){btn.textContent="已学习";btn.classList.add("learned");}
else{btn.textContent="标记为已学习";btn.classList.remove("learned");}
}
function updateCount(){
document.getElementById("learned-count").textContent=Object.values(learned).filter(v=>v).length;
}
function filterModels(){
let q=document.getElementById("search").value.toLowerCase();
document.querySelectorAll(".model-item").forEach(item=>{
item.style.display=item.textContent.toLowerCase().includes(q)?"":"none";
});
}
function toggleCat(el){
let items=el.parentElement.querySelectorAll(".model-item");
let hidden=items.length>0&&items[0].style.display!=="none";
items.forEach(i=>i.style.display=hidden?"none":"");
}
updateCount();
</script>
</body>
</html>''')

html_output = ''.join(html_parts)
with open(r'D:\openclaw_workspace\canvas\munger-models-cn.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print(f'Done! {len(html_output)} bytes, 34 models, all Chinese')
