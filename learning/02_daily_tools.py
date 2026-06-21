"""
第二课：构建个人工具 - 自动化日常任务

这个脚本帮你自动化一些日常任务：
1. 检查 API 额度
2. 清理临时文件
3. 生成每日报告

学习要点：
1. 文件操作
2. 定时任务
3. 数据处理
4. 实用工具开发
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# ============ 第一部分：文件操作 ============

def clean_temp_files(directory, days_old=7):
    """
    清理指定目录中超过 N 天的临时文件
    
    参数：
    - directory: 要清理的目录路径
    - days_old: 文件保留天数
    
    返回：
    - 删除的文件数量
    """
    
    deleted_count = 0
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            # 检查文件修改时间
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()  # 删除文件
                    deleted_count += 1
                    print(f"已删除: {file_path.name}")
                except Exception as e:
                    print(f"删除失败 {file_path.name}: {e}")
    
    return deleted_count


def get_directory_size(directory):
    """
    计算目录大小（MB）
    """
    
    total_size = 0
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    
    return total_size / (1024 * 1024)  # 转换为 MB


# ============ 第二部分：配置管理 ============

class ConfigManager:
    """
    简单的配置管理类
    """
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self.load()
    
    def load(self):
        """
        加载配置文件
        """
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    
    def save(self):
        """
        保存配置文件
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """
        获取配置项
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        设置配置项
        """
        self.config[key] = value
        self.save()


# ============ 第三部分：日志和报告 ============

def generate_daily_report(workspace_path):
    """
    生成每日工作报告
    """
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "stats": {}
    }
    
    workspace = Path(workspace_path)
    
    # 统计文件数量
    files = list(workspace.rglob('*'))
    report["stats"]["total_files"] = len([f for f in files if f.is_file()])
    
    # 统计目录大小
    report["stats"]["workspace_size_mb"] = round(get_directory_size(workspace), 2)
    
    # 统计 git 状态
    git_dir = workspace / ".git"
    if git_dir.exists():
        report["stats"]["git_initialized"] = True
    else:
        report["stats"]["git_initialized"] = False
    
    # 统计 memory 文件
    memory_dir = workspace / "memory"
    if memory_dir.exists():
        memory_files = list(memory_dir.glob("*.md"))
        report["stats"]["memory_files"] = len(memory_files)
    
    return report


def save_report(report, output_path):
    """
    保存报告到文件
    """
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 每日报告 - {report['date']}\n\n")
        f.write(f"生成时间: {report['time']}\n\n")
        f.write("## 统计数据\n\n")
        for key, value in report["stats"].items():
            f.write(f"- {key}: {value}\n")
    
    print(f"报告已保存到: {output_file}")


# ============ 第四部分：主程序 ============

def main():
    """
    主程序：执行日常维护任务
    """
    
    print("=== 日常维护任务 ===")
    print()
    
    # 工作区路径
    workspace = Path.home() / ".openclaw" / "workspace"
    
    # 1. 清理临时文件
    print("1. 清理临时文件...")
    temp_dir = workspace / "temp"
    if temp_dir.exists():
        deleted = clean_temp_files(temp_dir, days_old=7)
        print(f"   删除了 {deleted} 个临时文件")
    else:
        print("   没有临时文件目录")
    
    # 2. 生成报告
    print("\n2. 生成每日报告...")
    report = generate_daily_report(workspace)
    
    # 打印报告
    print(f"   日期: {report['date']}")
    print(f"   文件数: {report['stats']['total_files']}")
    print(f"   大小: {report['stats']['workspace_size_mb']} MB")
    
    # 保存报告
    report_path = workspace / "reports" / f"daily_{report['date']}.md"
    save_report(report, report_path)
    
    print("\n=== 任务完成 ===")


# ============ 练习题 ============

"""
练习 1：文件清理
- 修改 clean_temp_files 函数
- 添加文件扩展名过滤（只删除 .tmp 文件）

练习 2：配置管理
- 创建一个配置文件
- 用 ConfigManager 读写配置

练习 3：报告生成
- 添加更多统计信息
- 比如：代码行数、最近修改的文件等

练习 4：定时执行
- 使用 Windows 任务计划程序
- 让这个脚本每天自动运行

练习 5：通知
- 添加飞书通知
- 报告生成后自动发送
"""


if __name__ == "__main__":
    main()
