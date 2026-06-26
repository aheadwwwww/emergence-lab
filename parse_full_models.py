import os
import glob
import json
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

models_full = {}

for cat_name, cat_dir in categories.items():
    dir_path = os.path.join(base_path, cat_dir)
    if not os.path.exists(dir_path):
        continue
    
    files = glob.glob(os.path.join(dir_path, "*.md"))
    for f in sorted(files):
        filename = os.path.basename(f)
        match = re.match(r'm(\d+)', filename)
        if not match:
            continue
        
        model_id = 'm' + match.group(1)
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 解析各个部分
        def extract_section(content, start_marker, end_markers):
            """提取指定部分的内容"""
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return ""
            
            start_idx += len(start_marker)
            
            # 找到下一个section的开始
            end_idx = len(content)
            for marker in end_markers:
                idx = content.find(marker, start_idx)
                if idx != -1 and idx < end_idx:
                    end_idx = idx
            
            return content[start_idx:end_idx].strip()
        
        # 提取Title
        title_match = re.search(r'Mental Model = (.+)', content)
        title_en = title_match.group(1).strip() if title_match else "Unknown"
        
        # 提取Description
        desc = extract_section(content, '**Description:**', ['**When to Avoid', '**Keywords'])
        
        # 提取When to Avoid
        avoid = extract_section(content, '**When to Avoid', ['**Keywords', '**Thinking Steps'])
        
        # 提取Keywords
        keywords_text = extract_section(content, '**Keywords for Situations:**', ['**Thinking Steps', '**Coaching'])
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        if not keywords:
            keywords = ["通用"]
        
        # 提取Thinking Steps
        steps_text = extract_section(content, '**Thinking Steps:**', ['**Coaching Questions:**'])
        steps = []
        for line in steps_text.split('\n'):
            line = line.strip()
            if re.match(r'\d+\.', line):
                # 清理markdown格式
                step = re.sub(r'\d+\.\s*\*\*(.+?)\*\*:?\s*', r'\1: ', line)
                step = re.sub(r'\*\*(.+?)\*\*', r'\1', step)
                steps.append(step)
        
        # 提取Coaching Questions
        coaching_text = extract_section(content, '**Coaching Questions:**', [])
        coaching = []
        for line in coaching_text.split('\n'):
            line = line.strip()
            if line.startswith('-') and line != '-':
                q = line.lstrip('-').strip()
                coaching.append(q)
        
        # 中文标题映射
        title_zh_map = {
            'The Map Is Not the Territory': '地图非领土',
            'Circle of Competence': '能力圈',
            'First-Principle Thinking': '第一性原理',
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
        
        # 尝试匹配中文标题
        title_zh = title_zh_map.get(title_en, title_en)
        
        models_full[model_id] = {
            'id': model_id,
            'title': title_zh,
            'title_en': title_en,
            'category': cat_name,
            'description': desc,
            'avoid': avoid,
            'keywords': keywords[:6],  # 最多6个关键词
            'steps': steps,
            'coaching': coaching[:7]  # 最多7个教练问题
        }

print(f"Total models parsed: {len(models_full)}")

# 保存为JSON
with open('models_full_data.json', 'w', encoding='utf-8') as f:
    json.dump(models_full, f, ensure_ascii=False, indent=2)

print("Saved to models_full_data.json")

# 显示前3个模型的标题
for mid in sorted(models_full.keys())[:5]:
    m = models_full[mid]
    print(f"\n{mid}: {m['title']}")
    print(f"  Description length: {len(m['description'])} chars")
    print(f"  Steps: {len(m['steps'])}")
    print(f"  Coaching: {len(m['coaching'])}")