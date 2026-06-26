import os
import glob

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

models = []
for cat_name, cat_dir in categories.items():
    dir_path = os.path.join(base_path, cat_dir)
    if os.path.exists(dir_path):
        files = glob.glob(os.path.join(dir_path, "*.md"))
        for f in sorted(files):
            name = os.path.basename(f).replace('.md', '').replace('_', ' ')
            # 提取模型编号
            num = name.split(' ')[0]
            title = name.replace(num + ' ', '').replace(num, '').strip()
            models.append({
                'category': cat_name,
                'number': num,
                'title': title,
                'file': f
            })

print(f"Total models: {len(models)}")
for m in models[:20]:
    print(f"{m['number']}: {m['title']} ({m['category']})")