"""
Generate munger models CN HTML v2 with cases + related + progress bar
"""
import json

def make_model(mid, cat, title, core, desc, when, steps, case="", related=""):
    return {"id": mid, "cat": cat, "title": title, "core": core, "desc": desc, "when": when, "steps": steps, "case": case, "related": related}

models = [
    make_model("m1","决策","第一性原理","拆解到最基本事实，从零重建","把问题拆到不能再拆的基本元素，抛弃所有假设和惯例，从最底层重新构建解决方案。","当被告知不可能时；当行业惯例成为枷锁时；当需要突破性创新时","1.明确你要解决的问题是什么|2.拆解：这个问题由哪些基本元素构成|3.质疑：哪些是事实，哪些只是惯例|4.重建：从基本事实出发能有什么新方案","马斯克将火箭拆解为原材料成本，发现火箭材料仅占售价2%，于是自建SpaceX将成本降至十分之一。","m3,m4"),
    make_model("m2","决策","二阶思维","思考后果的后果","不只考虑直接结果，还要想然后呢。第一阶降价导致销量上升。第二阶竞品跟进导致利润都下降导致行业洗牌。","做战略决策时；评估政策影响时；投资判断时","1.列出决策的直接后果|2.对每个后果问会发生什么|3.重复至少两次|4.比较一阶和二阶的差异","亚马逊长期不盈利却持续投资物流和云服务，一阶看是亏损，二阶看是建立不可逾越的护城河。","m1,m3"),
    make_model("m3","决策","逆向思维","从失败倒推，避免错误","不问怎么成功，问怎么失败然后避免。芒格说告诉我我会死在哪，我永远不去那里。","风险评估；项目启动前；重大决策前","1.定义你想要的结果|2.反过来问怎样确保达不到|3.列出所有失败路径|4.逐一设计防范措施","巴菲特每年致股东信都先写过去一年犯的错误而非成就。先承认失败才能避免重蹈覆辙。","m1,m5"),
    make_model("m4","决策","思想实验","在脑子里做实验不花成本","在大脑中模拟场景探索假设和可能性。爱因斯坦用思想实验发现了相对论。不需要实验室只需要想象力。","无法做真实实验时；探索如果会怎样；测试假设","1.设定场景和假设条件|2.在脑中推演事件发展|3.观察矛盾点和意外发现|4.提炼可验证的结论","爱因斯坦16岁时想象追着一束光跑会看到什么，这个思想实验最终导向了狭义相对论。","m1,m5"),
    make_model("m5","决策","概率思维","用概率而非确定论看世界","未来不是确定的是一组概率分布。好的决策是选择胜率更高的选项而非保证赢的选项。","面对不确定性；评估风险；做预测","1.列出所有可能的结果|2.估算每种结果的概率|3.计算期望值|4.选择期望值最高的方案","德州扑克职业选手不追求每局都赢，而是追求正期望值决策。长期来看EV正的策略必然盈利。","m6,m11"),
    make_model("m6","决策","能力圈","知道边界在哪比圈子多大更重要","不在能力圈外做决策。圈的大小不重要知道边界在哪才重要。","做投资决策；接受新任务；给别人建议","1.问自己这件事我真的懂吗|2.区分知道和以为自己知道|3.在圈外时承认不懂找懂的人|4.持续扩大能力圈","巴菲特和盖茨同时写下对他们成功最重要的一个词，两人都写了专注。巴菲特一生不投资科技股因为不在他能力圈内。","m7,m11"),
    make_model("m7","决策","地图非领土","模型不等于现实","任何理论、模型、计划都只是现实的简化表示。地图再精确也不是领土本身。不要爱上自己的模型。","制定计划时；使用理论框架时；分析数据时","1.确认你用的是哪个地图|2.问这个地图忽略了什么|3.去领土上实地验证|4.根据现实反馈更新地图","二战前法国花十年建马奇诺防线，但德国绕过去了。法国的地图保护了上次战争却不适用于下次战争。","m1,m8"),
    make_model("m8","决策","奥卡姆剃刀","最简单的解释往往是对的","在多个解释中选择假设最少的那个。不是简单的一定对而是不必要的复杂通常是错的。","面对多个解释时；设计方案时；调试问题时","1.列出所有可能的解释|2.数每个解释需要多少假设|3.优先验证假设最少的|4.如果不够再逐步增加复杂度","哥白尼日心说替代托勒密地心说，不是因为它更准而是因为它更简单，不需要本轮均轮那套复杂体系。","m1,m28"),
    make_model("m9","决策","汉隆剃刀","能用愚蠢解释的不要归咎于恶意","别人做了让你不爽的事先假设他是疏忽或无知而不是故意害你。大多数恶意其实是笨拙。","被人冒犯时；解读竞争对手行为；处理冲突","1.暂停感受到被冒犯时先停下来|2.列出其他可能的解释|3.问有证据证明是恶意吗|4.没有证据就选最善意的解释","邮件没回大概率是对方忙或忘了而非故意冷落你。假设恶意会消耗大量情绪，假设疏忽则能快速翻篇。","m16,m18"),
    make_model("m10","经济学","复利","利滚利时间是最好的杠杆","收益产生收益形成指数增长。不光是钱，知识、技能、人际关系都遵循复利。关键是持续投入和时间。","投资理财；学习规划；职业发展","1.找到能产生复利的事|2.尽早开始让时间发挥作用|3.保持持续投入不要中断|4.耐心等待指数拐点","巴菲特90%的财富在65岁后获得。他从11岁开始投资，54年的复利积累证明复利需要极高的耐心。","m11,m12"),
    make_model("m11","经济学","机会成本","选择的真正代价是你放弃的东西","做一件事的成本不是花的时间和钱而是用同样的资源能做的最好的另一件事。","做选择时；分配资源时；评估时间投入","1.列出你正在放弃的选项|2.找出其中价值最高的|3.问选A放弃B值得吗|4.用放弃的最好选项来衡量成本","比尔盖茨退学创办微软，他放弃的不是学费而是哈佛学位的机会价值。但他用这个机会换来了更大的东西。","m6,m10"),
    make_model("m12","经济学","安全边际","留足缓冲应对意外","工程师造桥不造刚好承重的桥而是留几倍余量。投资、计划、承诺都应该留安全边际。","做预算；承诺截止日期；投资决策","1.估算最坏情况需要什么|2.在估算基础上加缓冲30%到100%|3.按加了缓冲的标准执行|4.永远不要刚好卡在极限上","本杰明格雷厄姆教导用远低于内在价值的价格买股票，差价就是安全边际。即使判断出错也不会亏太多。","m10,m17"),
    make_model("m13","经济学","供需关系","价格由供需决定不是由成本决定","东西值多少钱不取决于你花了多少成本，取决于有多少人想要、有多少人提供。理解供需就理解市场的底层逻辑。","定价；分析市场；理解价格波动","1.识别谁是供给方谁是需求方|2.分析供给和需求各自的弹性|3.预测什么因素会改变供给或需求|4.判断价格会往哪个方向走","疫情期间口罩需求暴增而供给不足，价格飙升。不是成本变了，是供需失衡。","m14,m29"),
    make_model("m14","经济学","稀缺性","有限的资源无限的需求","经济学的基本前提。因为稀缺所以需要选择，因为选择所以有机会成本。稀缺创造价值。","资源分配；优先级排序；理解价值","1.识别什么是真正稀缺的|2.区分稀缺和短暂短缺|3.问谁控制了稀缺资源|4.思考如何创造或获取稀缺资源","钻石本身并不稀有，但戴比尔斯控制全球钻石供应制造稀缺，成功让钻石价格远超实际价值。","m13,m15"),
    make_model("m15","经济学","激励","人会对激励做出反应","芒格说告诉我激励是什么我告诉你结果是什么。设计错误的激励会产生错误的行为。永远先看激励结构。","设计制度；管理团队；理解行为","1.找出系统中所有的激励|2.问这些激励会导致什么行为|3.检查有没有激励在鼓励坏行为|4.调整让激励和想要的结果对齐","苏联工厂按重量考核，导致生产出全世界最重的吊灯。目标设错了一切都错。","m13,m22"),
    make_model("m16","心理学","确认偏误","人只看到自己想看到的","我们倾向于寻找、注意、记住支持自己观点的证据，忽略反对的证据。这是最普遍也最危险的认知偏差。","做判断时；收集信息时；评估证据时","1.明确自己当前的信念是什么|2.主动寻找反对的证据|3.问如果我是错的会是什么原因|4.让持不同观点的人来挑战你","达尔文意识到确认偏误后，专门用一个笔记本来记录和理论矛盾的观察，强迫自己面对反面证据。","m17,m18"),
    make_model("m17","心理学","社会认同","别人怎么做我就怎么做","在不确定时人会参考他人的行为。这是为什么排队、从众、潮流会形成。也是为什么泡沫会膨胀。","看到大家都在做某事时；做独立判断时；分析趋势","1.意识到我是不是在跟风|2.问如果没人这么做我还会做吗|3.找反例有没有人不跟风也成功了|4.独立评估这件事本身的价值","郁金香泡沫、2000年互联网泡沫、比特币狂热——每次泡沫的驱动力都是因为看到别人在赚钱。","m16,m18"),
    make_model("m18","心理学","沉没成本","已经花掉的不应该影响未来决策","钱花出去了时间投入了但这些不应该影响要不要继续。决策只看未来不看过去。","考虑是否放弃时；评估项目时；投资决策","1.区分哪些是已经花掉的沉没成本|2.问如果今天从零开始我会做这个选择吗|3.只看未来的成本和收益|4.如果答案是不果断放弃","协和飞机项目英法两国明知会亏损仍继续投入已烧了几十亿，因为已经花了那么多。这就是被沉没成本绑架的典型。","m16,m21"),
    make_model("m19","心理学","锚定效应","第一个数字决定了你的判断范围","看到第一个价格后后续判断都会围绕它。标价1000打折到500你觉得便宜，但如果一开始标500呢？","谈判；定价；做估算","1.识别第一个出现的数字是什么|2.问如果没有这个锚我会怎么判断|3.主动设置自己的锚|4.在谈判中先出价","房地产中介先带你看一套又贵又差的房子，再带你看正常价格的房子，你会觉得后者性价比极高。","m20,m17"),
    make_model("m20","心理学","框架效应","怎么说比说什么更重要","同样的信息换个说法人的反应完全不同。存活率90%和死亡率10%是一回事但感受截然不同。","沟通；说服；做选择时","1.识别当前的表述框架|2.换个框架重新描述同一件事|3.问不同框架下我的判断会变吗|4.选择最能帮助理性决策的框架","医生告诉病人手术存活率90%时病人更愿意接受，告诉死亡率10%时则选择保守治疗。同一数据不同表述。","m19,m21"),
    make_model("m21","心理学","损失厌恶","失去的痛苦大于得到的快乐","失去100块的痛苦大约是得到100块快乐的两倍。这导致人过度保守不愿放弃不愿冒险。","做风险决策；考虑改变；评估投资","1.识别我是不是因为怕失去而在回避|2.量化失去和得到的实际价值|3.问如果这已经是失去的状态我会花多少挽回|4.用理性计算代替情绪反应","人们更愿意为保住已有的薪资而拖延辞职，即使新工作薪酬更高。失去现有的比得不到想要的心理冲击更大。","m18,m20"),
    make_model("m22","系统思维","反馈循环","输出反过来影响输入","正反馈A增加导致B增加导致A更增加。负反馈A增加导致B减少导致A被抑制。系统行为由反馈结构决定。","分析系统行为；设计流程；理解增长或衰退","1.画出系统的因果链条|2.找出所有反馈回路|3.判断每条回路是正反馈还是负反馈|4.问主导回路是什么它会把系统带向哪里","社交媒体算法：你多看某类内容，算法就多推送该类内容，你看到更多又继续看更多，形成正反馈信息茧房。","m23,m24"),
    make_model("m23","系统思维","涌现","整体大于部分之和","简单规则在大量交互后产生复杂行为。蚁群没有CEO但能建复杂的巢。意识从神经元中涌现。","理解复杂系统；设计规则；分析群体行为","1.识别系统的微观规则是什么|2.观察宏观层面出现了什么模式|3.问这个模式能从微观规则推导出来吗|4.如果不能这就是涌现","康威生命游戏三条简单规则产生滑翔机、振荡器甚至图灵完备的计算。微观简单宏观复杂。","m22,m25"),
    make_model("m24","系统思维","瓶颈","系统最慢的环节决定整体速度","一条流水线的速度由最慢的工位决定。优化非瓶颈环节是浪费。找到瓶颈解决它然后找下一个。","优化流程；提高效率；诊断问题","1.画出整个流程|2.找出最慢最堵的环节|3.集中资源解决这个环节|4.解决后新的瓶颈会出现重复此过程","丰田生产系统的核心理念就是持续识别和消除瓶颈，任何工人都可以拉停生产线来暴露瓶颈。","m25,m34"),
    make_model("m25","系统思维","杠杆点","小改变大影响","系统中有些点稍微用力就能产生巨大变化。找到这些点比盲目努力重要100倍。","推动变革；解决问题；提高效率","1.理解系统的结构|2.列出所有可以干预的点|3.评估每个点的杠杆效应|4.优先干预杠杆最大的点","阿基米德说过给我一个支点我能撬动地球。在组织中，改变绩效评估方式这一个点就能撬动所有人的行为。","m24,m26"),
    make_model("m26","系统思维","路径依赖","历史决定未来","一旦走上某条路就很难换。QWERTY键盘不是最优布局但所有人都习惯了。选择初始路径时要格外谨慎。","做初始选择；设计标准；理解行业格局","1.识别当前状态是哪些历史选择造成的|2.问如果重来我会选这条路吗|3.评估转换成本有多高|4.在起点时多花时间选对路","VHS战胜Betamax不是技术更优而是早期占有率更高。一旦形成正反馈就很难逆转。","m28,m22"),
    make_model("m27","系统思维","熵增","封闭系统必然走向无序","不持续输入能量或信息任何系统都会退化。这就是为什么维护比建设更难。","理解衰退；维护系统；组织管理","1.识别系统是封闭的还是开放的|2.测量无序度在增加吗|3.找到负熵源什么在对抗熵增|4.持续注入能量信息和秩序","任何不维护的软件系统都会腐化，代码库越来越乱。持续重构和文档更新就是对抗熵增。","m22,m24"),
    make_model("m28","生物学","演化","变异加选择加时间等于适应","不需要设计师不需要目标。随机变异环境选择适者生存。这是地球上最强大的优化算法。","理解变化；设计迭代流程；接受不确定性","1.创造变异尝试不同的方案|2.设置选择标准什么算好|3.保留好的淘汰差的|4.重复很多次","丰田的持续改善就是演化思维的商业应用。每天微小的改进在多年后积累成巨大的竞争优势。","m23,m31"),
    make_model("m29","生物学","生态位","找到你独有的位置","每个物种都有自己的生态位特定的环境食物生存方式。商业也一样找到别人做不了或不愿做的位置。","职业规划；商业定位；竞争策略","1.分析环境有什么未被满足的需求|2.评估自己有什么独特优势|3.匹配优势和需求的交集就是你的生态位|4.深耕在生态位里做到最好","彼得蒂尔说竞争是留给失败者的。垄断企业都在自己独特的生态位里做到了别人做不到的事。","m14,m30"),
    make_model("m30","生物学","合作","一起做比单干强","演化不只竞争合作同样重要。共生、互惠、协作自然界充满了合作的例子。","团队协作；商业合作；生态设计","1.识别谁和你有互补的能力|2.设计如何让合作双方都受益|3.建立信任从小合作开始|4.扩展成功的合作模式可以复制","蜜蜂和花是最经典的共生合作。蜜蜂获取花蜜，花获得传粉。双方都受益，谁也离不开谁。","m29,m31"),
    make_model("m31","生物学","自催化","产物加速自己的生产","化学反应中产物本身是催化剂。商业中用户越多产品越好导致产品越好用户越多。这是指数增长的底层机制。","理解增长；设计产品；分析网络效应","1.识别什么在加速自己的增长|2.问增长是自催化的还是外部驱动的|3.如果是自催化找到加速循环的关键环节|4.小心自催化也会加速崩溃","维基百科：内容越多吸引越多用户，用户越多贡献越多内容。这是典型的内容-用户双向自催化。","m22,m32"),
    make_model("m32","其他","临界质量","过了某个点变化不可逆","核反应需要足够的铀堆在一起才能链式反应。社会运动、技术采用、市场引爆都有临界质量。","推动变革；产品发布；理解趋势","1.定义什么状态算引爆|2.估算需要多少积累才能到临界点|3.集中资源推过临界点|4.过了临界点后系统会自我维持","Facebook最初只在哈佛校园推广，达到校内临界质量后才扩展到其他学校，每次都是先在局部达到引爆点。","m31,m33"),
    make_model("m33","其他","林迪效应","存在越久的东西未来存在越久","一本书卖了100年大概率还会再卖100年。时间是质量的过滤器。","选择学习内容；判断趋势；做长期决策","1.问这个东西存在多久了|2.存在越久未来预期寿命越长|3.优先选择经得起时间考验的东西|4.对新事物保持谨慎","几何原本已存在2300年仍被阅读。而去年畅销书排行榜上的大部分书十年后可能无人记得。","m10,m34"),
    make_model("m34","其他","帕累托法则","80%的结果来自20%的原因","80%的销售额来自20%的客户。80%的成果来自20%的努力。找到那20%把精力集中在那里。","优先级排序；资源分配；提高效率","1.列出所有投入和产出|2.找出贡献最大的20%|3.把80%精力放在这20%上|4.对剩下的80%减少投入或放弃","微软发现修复前20%的bug就能消除80%的崩溃和用户投诉。不是所有bug都值得修复。","m24,m25"),
    make_model("m35","心理学","幸存者偏差","只看到活下来的看不到死掉的","我们只听到成功者的故事而忽略了大量失败者。研究成功企业不如研究失败企业的共同死因更有价值。","分析成功案例时；做决策参考时；读传记时","1.问还有谁尝试过但失败了|2.找失败的共性而非成功的特性|3.从失败者身上学到的往往比成功者更多|4.警惕只讲成功不讲失败的故事","二战时军方想加固返回飞机的弹孔密集部位，但沃尔德指出应该加固没弹孔的地方因为那些位置中弹的飞机都没回来。","m16,m3"),
    make_model("m36","心理学","基本归因错误","别人犯错是人有问题自己犯错是环境问题","别人迟到是因为懒散，自己迟到是因为堵车。高估个人因素低估情境因素。","评价他人行为时；分析失败原因时；团队冲突时","1.当评判别人时先问如果是你会不会也这样|2.列出影响行为的外部因素|3.把自己犯同样错的经历列出来|4.用同样的标准看待自己和他人","斯坦福监狱实验揭示普通人穿上狱警制服后也会残忍地对待囚犯。不是人坏是情境塑造行为。","m16,m9"),
    make_model("m37","心理学","对比效应","判断取决于参照物","同一杯温水摸过冰水觉得烫摸过热水觉得凉。人对任何事物的感知取决于前后对比。","定价时；谈判时；做评价时","1.识别当前的参照点是什么|2.换一个参照点重新判断|3.问如果没有参照点我会怎么评价|4.警惕人为制造的对比陷阱","房产中介先带客户看又贵又差的房子再带看目标房源，客户会觉得目标房特别好。这就是对比效应的操纵。","m19,m20"),
    make_model("m38","心理学","承诺一致性","人一旦承诺就会保持一致","公开承诺后人们倾向于言行一致即使承诺是错的。先要小承诺再要大承诺就是登门槛效应。","谈判时；行为改变时；销售时","1.警惕被诱导做出小的承诺|2.问如果没做过之前的承诺我现在会怎么选|3.利用正向承诺帮助自己坚持好习惯|4.公开承诺比私下承诺更有约束力","健身房让顾客先填一张健康问卷（小承诺），再推销年卡（大承诺）成功率大幅提高。","m16,m18"),
    make_model("m39","心理学","可得性启发","容易想到的就被认为更重要","媒体报道飞机失事后人们觉得飞机很危险，其实开车更危险。记忆中容易提取的事件被高估概率。","风险评估时；做决策时；看新闻后","1.问这个风险的真实概率是多少而不是它多容易被想起|2.查实际数据而非依赖印象|3.最近发生的事不等于更可能发生|4.警惕媒体报道的放大效应","911后很多人选择开车代替坐飞机，结果在路上多死了1500人。恐惧的不是真实风险而是被放大的风险。","m5,m16"),
    make_model("m40","心理学","叙事本能","人需要把一切串成故事","纳西姆塔勒布提出。人类无法接受随机性必须给一切编故事。股市涨了就有解释股市跌了也有解释但其实很多时候就是随机波动。","分析事件时；解释过去时；做预测时","1.问这个故事是事后编的还是事前预测的|2.试试用相反的故事解释同一件事|3.承认有些事就是随机的|4.少解释多看数据","股市每天都有金融分析师解释为什么涨为什么跌，但第二天同样的分析师会给出截然相反的解释。故事是编的市场是随机的。","m16,m5"),
    make_model("m41","决策","多元思维模型","用多种模型交叉验证","芒格的核心主张。不要用单一学科的方法解决所有问题。用数学、心理学、生物学等多个透镜交叉审视同一个问题。","重大决策时；复杂问题时；需要创新时","1.列出3个以上不同学科的视角|2.用每个视角独立分析问题|3.找出各视角的共识和矛盾|4.综合形成更全面的判断","芒格和巴菲特用40多种模型评估一笔投资包括心理学、经济学、数学、生物学等绝不只用财务模型。","m1,m5"),
    make_model("m42","决策","反向思维","从目标倒推需要什么条件","设定了目标后问要达成这个目标必须先满足什么条件？然后逐一去创造这些条件。","设定宏大目标时；长期规划时；解决复杂问题时","1.明确最终目标|2.问要达成目标必须先满足什么|3.把必要条件列出来|4.从最近的条件开始满足","亚马逊创始人贝索斯想要万货商店，反向推导需要：无限货架、高效物流、用户评价系统、云计算基础设施然后逐一建立。","m1,m2"),
    make_model("m43","经济学","比较优势","做你最擅长的事交换别人擅长的事","即使你样样都比别人强也应该专注于相对优势最大的领域。大卫李嘉图的经典理论。","分工协作时；职业选择时；外包决策时","1.评估你在不同任务上的相对效率|2.找出你相对优势最大的领域|3.把其他任务交给相对优势更大的人|4.通过交换让双方都受益","程序员可能比设计师更懂设计但如果不擅长应该专注编程并雇人做设计。总产出更大。","m11,m29"),
    make_model("m44","系统思维","盖尔定律","复杂系统从简单系统演化而来","一个从头设计的复杂系统注定失败，它们也不会被修补成功。必须从一个可运行的简单系统开始逐步演化。","设计系统时；启动项目时；架构设计时","1.先做一个能跑的最简单版本|2.确保它能独立运行|3.在使用中逐步添加复杂度|4.永远不要从头设计完整系统再开发","互联网从简单的ARPANET四个节点开始演化了50年才成为今天的全球网络。如果1969年就设计今天的互联网架构一定失败。","m23,m26"),
    make_model("m45","生物学","红皇后效应","必须不停奔跑才能留在原地","在竞争环境中所有参与者都在进化你不进步就是退步。来自爱丽丝镜中奇缘中红皇后说的话。","竞争分析时；技术演进时；个人成长时","1.分析竞争对手在进化什么|2.评估自己不进化的后果|3.找到差异化进化的方向|4.不停迭代而非一次搞定","手机行业每隔一年芯片性能翻倍。如果你今年不更新产品线，去年旗舰机的性能就落后了。不进则退。","m28,m29"),
    make_model("m46","其他","幂律分布","少数赢家拿走大部分","不同于正态分布，幂律分布中少数极端值占绝对主导。互联网行业尤其明显赢家通吃。","分析行业格局时；投资时；理解不平等时","1.判断这个问题是正态分布还是幂律分布|2.如果是幂律做到前1%比做到前20%有价值100倍|3.识别幂律分布的临界点|4.在幂律领域押注头部","YouTube上前3%的视频获得了85%的播放量，大多数视频无人问津。互联网放大了幂律效应。","m34,m13"),
    make_model("m47","其他","熵增心理","心理也会熵增需要持续输入秩序","不学习不思考不锻炼，人的心理状态会自然滑向混乱。你必须持续输入高质量信息、锻炼身体、保持好习惯来对抗心理熵增。","感到混乱时；失去方向时；维持状态时","1.识别当前心理熵增的信号注意力分散情绪低落|2.找到负熵源读书运动写作冥想|3.每天固定时间注入负熵|4.熵增是常态对抗是日常","周末两天在家刷手机什么都不做，周一早上精神涣散注意力极差。这就是心理熵增。","m27,m18"),
    make_model("m48","其他","能力陷阱","擅长的事会限制你","你擅长的事让你成功但也让你停滞。因为太擅长了所以不愿尝试新方法。能力既是优势也是牢笼。","职业转型时；学习新技能时；打破瓶颈时","1.列出你擅长但可能限制你的事|2.问这些能力是否在阻碍新尝试|3.刻意做不擅长的事|4.区分核心能力和舒适区能力","柯达发明了数码相机但因为太擅长胶片业务而主动放弃了数码技术最终倒闭。能力变成了牢笼。","m6,m18"),
    make_model("m49","系统思维","延迟反馈","因和果之间有时间差","复杂系统中行动和结果之间往往有时间延迟。今天播的种子明年才结果。忽视延迟会导致过度反应或过早放弃。","评估效果时；制定计划时；理解系统行为时","1.识别系统中各环节的延迟时间|2.不要因为看不到即时结果就放弃|3.不要因为延迟而过度调整|4.在等待期保持耐心观察趋势而非结果","减肥第一周体重反而增加但坚持下去第二个月开始持续下降。如果第一周就放弃永远看不到结果。","m10,m22"),
    make_model("m50","决策","事前验尸","项目开始前先想象它已经死了","克莱因提出。在项目启动前召集团队想象项目已经失败然后分析是什么导致的。比事后复盘更有效因为没有沉没成本和面子问题。","项目启动前；战略规划时；风险评估时","1.召集团队宣布项目已经失败了完全破产|2.每个人独立写下失败原因|3.汇总归纳共同模式|4.逐一设计防范措施","投资决策前写下这笔投资可能归零的十个原因。写完后如果还觉得值得投资那才是真正的判断。","m3,m12"),
]

cats = {}
for m in models:
    cats.setdefault(m["cat"], []).append(m)

total = len(models)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>芒格思维模型库 - {total}个核心模型</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:15px}}
.container{{max-width:1400px;margin:0 auto;background:white;border-radius:15px;box-shadow:0 15px 50px rgba(0,0,0,0.3);overflow:hidden}}
header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:25px;text-align:center}}
h1{{font-size:2em;margin-bottom:5px}}
.subtitle{{font-size:1em;opacity:0.9}}
.progress-bar{{margin:10px 20px;height:6px;background:#e9ecef;border-radius:3px;overflow:hidden}}
.progress-fill{{height:100%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:3px;transition:width .3s;width:0%}}
.stats{{display:flex;justify-content:space-around;padding:15px;background:#f8f9fa;border-bottom:1px solid #e9ecef}}
.stat{{text-align:center}}
.stat-number{{font-size:2em;font-weight:bold;color:#667eea}}
.stat-label{{color:#6c757d;margin-top:2px;font-size:0.85em}}
.main-content{{display:grid;grid-template-columns:220px 1fr;min-height:600px}}
.sidebar{{background:#f8f9fa;padding:10px;border-right:1px solid #e9ecef;overflow-y:auto;max-height:600px}}
.sidebar input{{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;margin-bottom:10px;font-size:0.85em}}
.cat-title{{font-weight:bold;color:#495057;padding:6px 8px;background:white;border-radius:4px;margin:8px 0 5px;cursor:pointer;font-size:0.85em;user-select:none}}
.cat-title:hover{{background:#667eea;color:white}}
.model-item{{padding:5px 8px;cursor:pointer;border-radius:3px;font-size:0.8em;color:#6c757d;margin-bottom:1px;display:flex;align-items:center;gap:4px}}
.model-item:hover{{background:#e9ecef;color:#495057}}
.model-item.active{{background:#667eea;color:white}}
.model-item .check{{color:#28a745;font-weight:bold;display:none;font-size:0.75em}}
.model-item.learned .check{{display:inline}}
.content{{padding:25px;overflow-y:auto;max-height:600px}}
.welcome{{text-align:center;padding:60px 20px}}
.welcome h2{{font-size:1.5em;color:#495057;margin-bottom:12px}}
.welcome p{{color:#6c757d;font-size:0.9em;line-height:1.6}}
.model-detail{{display:none}}
.model-detail.active{{display:block}}
.model-header{{margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid #e9ecef}}
.model-badge{{display:inline-block;background:#667eea;color:white;padding:3px 10px;border-radius:10px;font-weight:bold;margin-bottom:5px;font-size:0.85em}}
.model-title{{font-size:1.5em;color:#495057;margin-bottom:3px}}
.model-core{{font-size:1em;color:#667eea;margin-bottom:8px;font-style:italic}}
.section{{margin-bottom:18px}}
.section-title{{font-size:1em;color:#667eea;margin-bottom:8px;display:flex;align-items:center}}
.section-title::before{{content:'';display:inline-block;width:3px;height:14px;background:#667eea;margin-right:6px;border-radius:2px}}
.section-content{{color:#495057;line-height:1.7;padding-left:9px;font-size:0.9em}}
.steps-list{{list-style:none;padding-left:9px;counter-reset:step}}
.steps-list li{{padding:4px 0;color:#495057;font-size:0.9em;line-height:1.5;counter-increment:step}}
.steps-list li::before{{content:counter(step);display:inline-block;width:20px;height:20px;background:#667eea;color:white;border-radius:50%;text-align:center;line-height:20px;font-size:0.75em;margin-right:8px}}
.learn-btn{{display:inline-block;margin-top:15px;padding:8px 20px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer;font-size:0.9em}}
.learn-btn:hover{{background:#5a6fd6}}
.learn-btn.learned{{background:#28a745}}
.related-section{{margin-top:15px;padding-top:15px;border-top:1px dashed #e9ecef}}
.related-links{{display:flex;flex-wrap:wrap;gap:8px;padding-left:9px}}
.related-link{{padding:4px 12px;background:#f0f0ff;color:#667eea;border-radius:12px;cursor:pointer;font-size:0.85em;border:1px solid #e0e0ff}}
.related-link:hover{{background:#667eea;color:white}}
</style>
</head>
<body>
<div class="container">
<header>
<h1>芒格思维模型库</h1>
<p class="subtitle">查理芒格的多元思维模型 · {total}个核心模型 · 全中文 · 含案例与关联推荐</p>
</header>
<div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
<div class="stats">
<div class="stat"><div class="stat-number">{total}</div><div class="stat-label">思维模型</div></div>
<div class="stat"><div class="stat-number">6</div><div class="stat-label">分类</div></div>
<div class="stat"><div class="stat-number" id="learned-count">0</div><div class="stat-label">已学习</div></div>
</div>
<div class="main-content">
<div class="sidebar">
<input type="text" id="search" placeholder="搜索模型..." oninput="filterModels()">
'''

cat_order = ["决策","经济学","心理学","系统思维","生物学","其他"]
for cat in cat_order:
    ms = cats.get(cat, [])
    html += f'<div class="cat-title" onclick="toggleCat(this)">{cat} ({len(ms)})</div>'
    for m in ms:
        html += f'<div class="model-item" data-cat="{cat}" data-id="{m["id"]}" onclick="showModel(\'{m["id"]}\')"><span class="check">✓</span>{m["title"]}</div>'

html += '</div><div class="content" id="content-area">'
html += f'<div class="welcome" id="welcome"><h2>选择一个模型开始学习</h2><p>查理芒格说：手里只有锤子的人，看什么都像钉子。<br>掌握{total}个思维模型，用不同的透镜看世界。<br>每个模型配有经典案例和相关推荐，形成知识网络。</p></div>'

for m in models:
    steps = m["steps"].split("|")
    steps_html = "".join(f"<li>{s}</li>" for s in steps)
    case_html = f'<div class="section"><div class="section-title">经典案例</div><div class="section-content">{m["case"]}</div></div>' if m["case"] else ""
    related_html = ""
    if m["related"]:
        rids = m["related"].split(",")
        rlinks = ""
        for rid in rids:
            rid = rid.strip()
            rmodel = next((x for x in models if x["id"] == rid), None)
            if rmodel:
                rlinks += f'<span class="related-link" onclick="showModel(\'{rid}\')">{rmodel["title"]}</span>'
        related_html = f'<div class="related-section"><div class="section-title">相关模型</div><div class="related-links">{rlinks}</div></div>'

    html += f'''
<div class="model-detail" id="detail-{m["id"]}">
<div class="model-header">
<span class="model-badge">{m["cat"]}</span>
<h2 class="model-title">{m["title"]}</h2>
<p class="model-core">{m["core"]}</p>
</div>
<div class="section"><div class="section-title">描述</div><div class="section-content">{m["desc"]}</div></div>
<div class="section"><div class="section-title">何时使用</div><div class="section-content">{m["when"]}</div></div>
{case_html}
<div class="section"><div class="section-title">思考步骤</div><ol class="steps-list">{steps_html}</ol></div>
{related_html}
<button class="learn-btn" id="btn-{m["id"]}" onclick="toggleLearned('{m["id"]}')">标记为已学习</button>
</div>'''

html += f'''</div></div></div>
<script>
let learned=JSON.parse(localStorage.getItem("munger-v2")||"{{}}");
function showModel(id){{
document.querySelectorAll(".model-detail").forEach(d=>d.classList.remove("active"));
document.querySelectorAll(".model-item").forEach(i=>i.classList.remove("active"));
document.getElementById("detail-"+id).classList.add("active");
let item=document.querySelector('.model-item[data-id="'+id+'"]');
if(item)item.classList.add("active");
document.getElementById("welcome").style.display="none";
updateBtn(id);
}}
function toggleLearned(id){{
learned[id]=!learned[id];
localStorage.setItem("munger-v2",JSON.stringify(learned));
updateBtn(id);
updateCount();
updateProgress();
updateSidebar();
}}
function updateBtn(id){{
let btn=document.getElementById("btn-"+id);
if(learned[id]){{btn.textContent="已学习";btn.classList.add("learned");}}
else{{btn.textContent="标记为已学习";btn.classList.remove("learned");}}
}}
function updateCount(){{
document.getElementById("learned-count").textContent=Object.values(learned).filter(v=>v).length;
}}
function updateProgress(){{
let n=Object.values(learned).filter(v=>v).length;
document.getElementById("progress-fill").style.width=(n/{total}*100)+"%";
}}
function updateSidebar(){{
document.querySelectorAll(".model-item").forEach(item=>{{
let id=item.getAttribute("data-id");
if(learned[id])item.classList.add("learned");
else item.classList.remove("learned");
}});
}}
function filterModels(){{
let q=document.getElementById("search").value.toLowerCase();
document.querySelectorAll(".model-item").forEach(item=>{{
item.style.display=item.textContent.toLowerCase().includes(q)?"":"none";
}});
}}
function toggleCat(el){{
let items=el.parentElement.querySelectorAll(".model-item");
let hidden=items.length>0&&items[0].style.display!=="none";
items.forEach(i=>i.style.display=hidden?"none":"");
}}
updateCount();
updateProgress();
updateSidebar();
</script>
</body>
</html>'''

with open(r'D:\openclaw_workspace\canvas\munger-models-cn.html', 'w', encoding='utf-8') as f:
    f.write(html)

cn = sum(1 for c in html if '\u4e00' <= c <= '\u9fff')
print(f"Done! {len(html)} bytes, {total} models, {cn} Chinese chars")
print(f"Saved to: D:/openclaw_workspace/canvas/munger-models-cn.html")
