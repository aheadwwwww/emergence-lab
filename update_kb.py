"""
知识库更新脚本

扫描新的探索笔记和实验代码，更新索引
"""

from pathlib import Path
import json
from datetime import datetime

def update_knowledge_base():
    workspace = Path(".")
    
    # 扫描目录
    categories = {
        "exploration": workspace / "exploration",
        "experiments": workspace / "experiments",
        "memory": workspace / "memory"
    }
    
    kb = {
        "last_updated": datetime.now().isoformat(),
        "categories": {}
    }
    
    for cat_name, cat_path in categories.items():
        if not cat_path.exists():
            continue
        
        items = []
        for file in cat_path.glob("*.md" if cat_name != "experiments" else "*.py"):
            stat = file.stat()
            items.append({
                "name": file.stem,
                "path": str(file),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        kb["categories"][cat_name] = {
            "count": len(items),
            "items": sorted(items, key=lambda x: x["modified"], reverse=True)
        }
    
    # 保存索引
    output_path = workspace / "knowledge_base.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 知识库已更新: {output_path}")
    print(f"  - 探索笔记: {kb['categories'].get('exploration', {}).get('count', 0)} 个")
    print(f"  - 实验代码: {kb['categories'].get('experiments', {}).get('count', 0)} 个")
    print(f"  - 记忆文件: {kb['categories'].get('memory', {}).get('count', 0)} 个")
    
    return kb

if __name__ == "__main__":
    update_knowledge_base()
