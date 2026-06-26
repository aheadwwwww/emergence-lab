import os
import glob
import re

base_path = "repos/elllyers-mental-models/research-papers/Mental_Models"

categories = {
    "General": "Mental_Model_General",
    "Science": "Mental_Model_Science",
    "Mathematics": "Mental_Model_Math",
    "Economics": "Mental_Model_Economics",
    "Systems Thinking": "Mental_Model_SysThinking",
    "Human Nature": "Mental_Model_HumanNature",
    "Art": "Mental_Model_Art",
    "War": "Mental_Model_War"
}

models_data = {}

for cat_name, cat_dir in categories.items():
    dir_path = os.path.join(base_path, cat_dir)
    if not os.path.exists(dir_path):
        continue
    
    files = glob.glob(os.path.join(dir_path, "*.md"))
    for f in sorted(files):
        filename = os.path.basename(f)
        # 提取模型编号
        match = re.match(r'm(\d+)', filename)
        if not match:
            continue
        
        model_id = 'm' + match.group(1)
        
        # 读取文件内容
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 解析内容
        title = ""
        description = ""
        avoid = ""
        keywords = []
        steps = []
        coaching = []
        
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('**Category'):
                pass
            elif line.startswith('**Description:**'):
                description = line.replace('**Description:**', '').strip()
            elif line.startswith('**When to Avoid'):
                current_section = "avoid"
            elif line.startswith('**Keywords for Situations:**'):
                current_section = "keywords"
            elif line.startswith('**Thinking Steps:**'):
                current_section = "steps"
            elif line.startswith('**Coaching Questions:**'):
                current_section = "coaching"
            elif line.startswith('-') and current_section:
                content_part = line.lstrip('-').strip()
                if current_section == "avoid" and not avoid:
                    avoid = content_part
                elif current_section == "keywords":
                    keywords.append(content_part)
                elif current_section == "steps":
                    # 提取步骤内容
                    step_match = re.match(r'\d+\.\s*\*\*(.+?)\*\*:?\s*(.+)', content_part)
                    if step_match:
                        steps.append(f"{step_match.group(1)}: {step_match.group(2)}")
                    else:
                        steps.append(content_part)
                elif current_section == "coaching":
                    coaching.append(content_part)
        
        # 提取标题
        title_match = re.search(r'Mental Model = (.+)', content)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # 从文件名提取
            title = filename.replace('.md', '').replace('_', ' ')
            title = re.sub(r'm\d+\s*', '', title).strip()
        
        # 中文翻译映射
        title_zh = {
            'First-Principle Thinking': '第一性原理',
            'The Map Is Not the Territory': '地图非领土',
            'Circle of Competence': '能力圈',
            'Thought Experiment': '思想实验',
            'Second-Order Thinking': '二阶思维',
            'Probabilistic Thinking': '概率思维',
            'Inversion': '逆向思维',
            "Hanlon's Razor": '汉隆剃刀',
            "Occam's Razor": '奥卡姆剃刀',
            'Activation-Energy': '活化能',
            'Alloying': '合金化',
            'Catalysts': '催化剂',
            'Cooperation': '合作',
            'Ecosystems': '生态系统',
            'Evolution': '演化',
            'Friction and Viscosity': '摩擦与粘度',
            'Hierarchical Organization': '层级组织',
            'Incentives': '激励',
            'Inertia': '惯性',
            'Leverage': '杠杆',
            'Niches': '生态位',
            'Reciprocity': '互惠',
            'Relativity': '相对论',
            'Replication': '复制',
            'Self-Preservation': '自我保存',
            'Tendency to Minimize Energy Output': '能量最小化倾向',
            'Thermodynamics': '热力学',
            'Velocity': '速度'
        }
        
        display_title = title_zh.get(title, title)
        
        models_data[model_id] = {
            'id': model_id,
            'title': display_title,
            'title_en': title,
            'category': cat_name,
            'description': description[:200] if description else "暂无描述",
            'avoid': avoid[:150] if avoid else "暂无说明",
            'keywords': keywords[:5] if keywords else ["通用"],
            'steps': steps[:5] if steps else ["待补充"],
            'coaching': coaching[:5] if coaching else ["待补充"]
        }

# 输出JavaScript数据
print(f"Total models parsed: {len(models_data)}")
for mid in sorted(models_data.keys())[:10]:
    m = models_data[mid]
    print(f"{mid}: {m['title']} ({m['category']})")

# 保存为JSON
import json
with open('models_data.json', 'w', encoding='utf-8') as f:
    json.dump(models_data, f, ensure_ascii=False, indent=2)

print("\nSaved to models_data.json")