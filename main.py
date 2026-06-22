"""
Emergence Lab - 主入口

使用方法：
    python main.py <command> [options]

命令：
    run <experiment>    运行指定实验
    batch               批量运行所有实验
    post                发帖到觅游
    update-kb           更新知识库
    status              显示状态
"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print("用法: python main.py run <experiment>")
            print("可用实验: ant, life, boids, sandpile, turing")
            return
        exp = sys.argv[2]
        print(f"运行实验: {exp}")
        # TODO: 实现实验运行
    
    elif cmd == "batch":
        print("批量运行编排器...")
        import subprocess
        subprocess.run(["python", "experiments/orchestrator/orchestrator_full.py"])
    
    elif cmd == "post":
        print("发帖到觅游...")
        # TODO: 实现发帖
    
    elif cmd == "update-kb":
        print("更新知识库...")
        import subprocess
        subprocess.run(["python", "tools/kb/update_kb.py"])
    
    elif cmd == "status":
        print("=== Emergence Lab Status ===")
        print(f"Workspace: {Path.cwd()}")
        
        # 统计脚本数量
        experiments = len(list(Path("experiments").rglob("*.py")))
        meyo = len(list(Path("meyo").rglob("*.py")))
        tools = len(list(Path("tools").rglob("*.py")))
        
        print(f"实验脚本: {experiments}")
        print(f"觅游脚本: {meyo}")
        print(f"工具脚本: {tools}")
    
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()