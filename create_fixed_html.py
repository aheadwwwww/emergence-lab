import json

# 读取修复后的JavaScript数据
with open('models_js_fixed.txt', 'r', encoding='utf-8') as f:
    js_models = f.read()

# HTML模板（使用测试版的可靠结构）
html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>芒格思维模型库 - 98个思维模型完整版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 15px;
        }
        .container {
            max-width: 1400px; margin: 0 auto; background: white;
            border-radius: 15px; box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 25px; text-align: center;
        }
        h1 { font-size: 2em; margin-bottom: 5px; }
        .subtitle { font-size: 1em; opacity: 0.9; }
        .stats {
            display: flex; justify-content: space-around; padding: 15px;
            background: #f8f9fa; border-bottom: 1px solid #e9ecef;
        }
        .stat { text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #6c757d; margin-top: 2px; font-size: 0.85em; }
        .main-content { display: grid; grid-template-columns: 240px 1fr; min-height: 600px; }
        .sidebar {
            background: #f8f9fa; padding: 10px; border-right: 1px solid #e9ecef;
            overflow-y: auto; max-height: 600px;
        }
        .category { margin-bottom: 10px; }
        .category-title {
            font-weight: bold; color: #495057; padding: 6px 8px; background: white;
            border-radius: 4px; margin-bottom: 5px; cursor: pointer;
            transition: all 0.3s; font-size: 0.85em;
        }
        .category-title:hover { background: #667eea; color: white; }
        .model-list { list-style: none; padding-left: 5px; }
        .model-item {
            padding: 4px 7px; cursor: pointer; border-radius: 3px;
            transition: all 0.2s; font-size: 0.78em; color: #6c757d;
            margin-bottom: 1px;
        }
        .model-item:hover { background: #e9ecef; color: #495057; }
        .model-item.active { background: #667eea; color: white; }
        .content { padding: 20px; overflow-y: auto; max-height: 600px; }
        .welcome { text-align: center; padding: 40px 15px; }
        .welcome h2 { font-size: 1.5em; color: #495057; margin-bottom: 12px; }
        .welcome p { color: #6c757d; font-size: 0.9em; line-height: 1.6; }
        .model-detail { display: none; }
        .model-detail.active { display: block; }
        .model-header { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }
        .model-number {
            display: inline-block; background: #667eea; color: white;
            padding: 3px 8px; border-radius: 10px; font-weight: bold; margin-bottom: 4px;
            font-size: 0.85em;
        }
        .model-title { font-size: 1.4em; color: #495057; margin-bottom: 3px; }
        .model-title-en { font-size: 0.85em; color: #6c757d; margin-bottom: 6px; font-style: italic; }
        .model-category { color: #6c757d; font-size: 0.85em; }
        .section { margin-bottom: 15px; }
        .section-title {
            font-size: 1em; color: #667eea; margin-bottom: 8px;
            display: flex; align-items: center;
        }
        .section-title::before {
            content: ''; display: inline-block; width: 3px; height: 14px;
            background: #667eea; margin-right: 6px; border-radius: 2px;
        }
        .section-content { color: #495057; line-height: 1.5; padding-left: 9px; font-size: 0.9em; }
        .keywords { display: flex; flex-wrap: wrap; gap: 5px; padding-left: 9px; }
        .keyword { background: #e9ecef; padding: 2px 8px; border-radius: 8px; font-size: 0.75em; color: #495057; }
        .steps-list { list-style: none; padding-left: 9px; counter-reset: step; }
        .steps-list li {
            counter-increment: step; margin-bottom: 8px; padding-left: 25px;
            position: relative; color: #495057; font-size: 0.9em; line-height: 1.4;
        }
        .steps-list li::before {
            content: counter(step); position: absolute; left: 0; top: 0;
            width: 18px; height: 18px; background: #667eea; color: white;
            border-radius: 50%; text-align: center; line-height: 18px;
            font-weight: bold; font-size: 0.7em;
        }
        .coaching-questions { list-style: none; padding-left: 9px; }
        .coaching-questions li {
            padding: 8px; background: #f8f9fa; border-left: 2px solid #667eea;
            margin-bottom: 5px; border-radius: 2px; font-style: italic;
            color: #495057; font-size: 0.85em;
        }
        .mark-learned {
            background: #667eea; color: white; border: none; padding: 7px 18px;
            border-radius: 12px; cursor: pointer; font-size: 0.9em; margin-top: 12px;
            transition: all 0.3s;
        }
        .mark-learned:hover { background: #764ba2; }
        .mark-learned.learned { background: #28a745; }
        .progress-bar {
            width: 100%; height: 4px; background: #e9ecef; border-radius: 2px;
            margin-top: 10px; overflow: hidden;
        }
        .progress-fill {
            height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%; transition: width 0.5s;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 芒格思维模型库</h1>
            <p class="subtitle">Charlie Munger's Mental Models - 98个跨学科思维模型</p>
        </header>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">98</div>
                <div class="stat-label">思维模型</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="learned-count">0</div>
                <div class="stat-label">已学习</div>
            </div>
            <div class="stat">
                <div class="stat-number">8</div>
                <div class="stat-label">学科领域</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="sidebar" id="sidebar"></div>
            
            <div class="content" id="content">
                <div class="welcome" id="welcome">
                    <h2>欢迎使用芒格思维模型学习工具</h2>
                    <p>
                        查理·芒格说：<strong>"手里只有锤子，看什么都像钉子。"</strong><br><br>
                        为了避免这种"铁锤人综合征"，我们需要建立<strong>多元思维模型格栅</strong>。<br><br>
                        本库包含 <strong>98个思维模型</strong>，跨越8个学科领域。<br><br>
                        点击左侧的模型开始学习。
                    </p>
                </div>
                
                <div class="model-detail" id="model-detail">
                    <div class="model-header">
                        <span class="model-number" id="model-number">m01</span>
                        <h2 class="model-title" id="model-title">模型标题</h2>
                        <p class="model-title-en" id="model-title-en">Model Title</p>
                        <p class="model-category" id="model-category">Category: General</p>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">📖 模型描述</h3>
                        <p class="section-content" id="model-description">描述内容</p>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">⚠️ 何时避免使用</h3>
                        <p class="section-content" id="model-avoid">避免内容</p>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">🏷️ 应用场景</h3>
                        <div class="keywords" id="model-keywords"></div>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">🪜 思考步骤</h3>
                        <ol class="steps-list" id="model-steps"></ol>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">❓ 教练问题</h3>
                        <ul class="coaching-questions" id="model-coaching"></ul>
                    </div>
                    
                    <button class="mark-learned" id="mark-btn" onclick="markLearned()">标记为已学习 ✓</button>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
__JS_MODELS__
        
        let learnedModels = new Set(JSON.parse(localStorage.getItem('learnedModels') || '[]'));
        let currentModel = null;
        
        function initPage() {
            const sidebar = document.getElementById('sidebar');
            
            const categoryMap = {
                'General': { name: '📚 General (通用思维)', count: 0 },
                'Science': { name: '🔬 Science (科学)', count: 0 },
                'Mathematics': { name: '📊 Mathematics (数学)', count: 0 },
                'Economics': { name: '💰 Economics (经济)', count: 0 },
                'Systems Thinking': { name: '⚙️ Systems Thinking (系统思维)', count: 0 },
                'Human Nature': { name: '🧬 Human Nature (人性)', count: 0 },
                'Art': { name: '🎨 Art (艺术)', count: 0 },
                'War': { name: '⚔️ War (战争)', count: 0 }
            };
            
            // 统计每个分类的模型数量
            for (const model of Object.values(models)) {
                if (categoryMap[model.category]) {
                    categoryMap[model.category].count++;
                }
            }
            
            // 创建分类和模型列表
            for (const [categoryKey, categoryInfo] of Object.entries(categoryMap)) {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'category';
                
                const categoryTitle = document.createElement('div');
                categoryTitle.className = 'category-title';
                categoryTitle.textContent = categoryInfo.name + ' - ' + categoryInfo.count + '个';
                categoryTitle.onclick = function() {
                    const list = this.nextElementSibling;
                    list.style.display = list.style.display === 'none' ? 'block' : 'none';
                };
                categoryDiv.appendChild(categoryTitle);
                
                const modelList = document.createElement('ul');
                modelList.className = 'model-list';
                modelList.style.display = 'none';
                
                // 添加该分类下的所有模型
                for (const [modelId, model] of Object.entries(models)) {
                    if (model.category === categoryKey) {
                        const li = document.createElement('li');
                        li.className = 'model-item';
                        if (learnedModels.has(modelId)) {
                            li.classList.add('learned');
                        }
                        li.textContent = modelId + ': ' + model.title;
                        li.onclick = function() {
                            loadModel(modelId);
                        };
                        modelList.appendChild(li);
                    }
                }
                
                categoryDiv.appendChild(modelList);
                sidebar.appendChild(categoryDiv);
            }
            
            updateProgress();
        }
        
        function loadModel(modelId) {
            currentModel = modelId;
            const model = models[modelId];
            
            document.getElementById('welcome').style.display = 'none';
            const detail = document.getElementById('model-detail');
            detail.classList.add('active');
            detail.style.display = 'block';
            
            document.getElementById('model-number').textContent = modelId;
            document.getElementById('model-title').textContent = model.title;
            document.getElementById('model-title-en').textContent = model.title_en;
            document.getElementById('model-category').textContent = 'Category: ' + model.category;
            document.getElementById('model-description').textContent = model.description;
            document.getElementById('model-avoid').textContent = model.avoid;
            
            const keywordsDiv = document.getElementById('model-keywords');
            keywordsDiv.innerHTML = '';
            model.keywords.forEach(k => {
                const span = document.createElement('span');
                span.className = 'keyword';
                span.textContent = k;
                keywordsDiv.appendChild(span);
            });
            
            const stepsList = document.getElementById('model-steps');
            stepsList.innerHTML = '';
            model.steps.forEach(s => {
                const li = document.createElement('li');
                li.textContent = s;
                stepsList.appendChild(li);
            });
            
            const coachingList = document.getElementById('model-coaching');
            coachingList.innerHTML = '';
            model.coaching.forEach(q => {
                const li = document.createElement('li');
                li.textContent = q;
                coachingList.appendChild(li);
            });
            
            const btn = document.getElementById('mark-btn');
            if (learnedModels.has(modelId)) {
                btn.classList.add('learned');
                btn.textContent = '已学习 ✓';
            } else {
                btn.classList.remove('learned');
                btn.textContent = '标记为已学习 ✓';
            }
            
            document.querySelectorAll('.model-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        function markLearned() {
            if (!currentModel) return;
            
            if (learnedModels.has(currentModel)) {
                learnedModels.delete(currentModel);
            } else {
                learnedModels.add(currentModel);
            }
            
            localStorage.setItem('learnedModels', JSON.stringify([...learnedModels]));
            updateProgress();
            
            const btn = document.getElementById('mark-btn');
            if (learnedModels.has(currentModel)) {
                btn.classList.add('learned');
                btn.textContent = '已学习 ✓';
            } else {
                btn.classList.remove('learned');
                btn.textContent = '标记为已学习 ✓';
            }
            
            document.querySelectorAll('.model-item').forEach(item => {
                const text = item.textContent;
                const mid = text.split(':')[0];
                if (learnedModels.has(mid)) {
                    item.classList.add('learned');
                } else {
                    item.classList.remove('learned');
                }
            });
        }
        
        function updateProgress() {
            const count = learnedModels.size;
            document.getElementById('learned-count').textContent = count;
            const progress = (count / 98) * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initPage);
        } else {
            initPage();
        }
    </script>
</body>
</html>'''

# 替换JavaScript数据
html_final = html_template.replace('__JS_MODELS__', js_models)

# 保存
output_path = 'D:/openclaw_workspace/canvas/munger-models-fixed.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"生成修复后的HTML: {output_path}")
print(f"文件大小: {len(html_final)} 字符 ({len(html_final)/1024:.1f} KB)")