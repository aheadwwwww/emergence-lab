# 翻译第一批模型 (m01-m10)
# 使用PowerShell进行精确文本替换

$filePath = "D:\openclaw_workspace\canvas\munger-models-zh.html"
$content = Get-Content $filePath -Raw -Encoding UTF8

Write-Host "开始翻译第一批模型 (m01-m10)..."

# m01 描述翻译
$content = $content -replace [regex]::Escape("description: 'This mental model is based on the idea that any representation of reality—be it a physical map, a business plan, a scientific theory, or a data model—is inherently a simplification and not reality itself. These \""maps\"" are useful for navigation and understanding, but they are incomplete and can be misleading if we forget they are abstractions. Reality \(\""the territory\""\) is infinitely more complex and detailed than any model we can create.',"), "description: '这个思维模型基于这样一个理念：任何对现实的表征——无论是物理地图、商业计划、科学理论还是数据模型——本质上都是简化，而非现实本身。这些\""地图\""对于导航和理解是有用的，但如果我们忘记它们只是抽象，就会产生误导。现实（\""领土\""）比我们能创造的任何模型都更加复杂和详尽。',"

# m01 avoid 翻译
$content = $content -replace [regex]::Escape("avoid: '\(or Use with Caution\):\*\* - \*\*For Low-Stakes Decisions:\*\* When a decision is quick, low-impact, and easily reversible, a \""good enough\"" map is sufficient. Over-analyzing the territory can lead to decision paralysis when the cost of being wrong is low. - \*\*When the Map is Reliable:\*\* In highly predictable environments \(e\.g\., basic physics\), the map is extremely accurate. Questioning it without new evidence is inefficient.',"), "avoid: '（或谨慎使用）：** - **低风险决策时：** 当决策快速、影响小且容易逆转时，\""足够好\""的地图就足够了。在错误成本较低时过度分析实际情况会导致决策瘫痪。 - **地图可靠时：** 在高度可预测的环境（如基础物理学）中，地图极其准确。在没有新证据的情况下质疑它是不高效的。',"

# m01 keywords 翻译
$content = $content -replace [regex]::Escape('keywords: ["Strategic planning", "data analysis", "project management", "personal development", "financial forecasting", "scientific research."]'), 'keywords: ["战略规划", "数据分析", "项目管理", "个人发展", "财务预测", "科学研究。"]'

# 保存文件
Set-Content $filePath $content -Encoding UTF8 -NoNewline

Write-Host "第一批翻译完成！"
