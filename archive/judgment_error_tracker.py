"""
judgment_error_tracker.py — 用预测编码框架追踪我的判断质量

核心思想：
- 每次判断都是一种"预测"
- 判断误差 = 预期结果 vs 实际结果
- 追踪误差能改进判断质量

预测编码公式：
自由能 = 预测误差 × 精度（对预测的信心）

应用到我：
- 判断误差 = 我以为用户需要 vs 用户实际需要
- 精度 = 我对判断的信心程度
- 自由能 = 判断失败的总代价
"""

import json
from datetime import datetime
from pathlib import Path

class JudgmentTracker:
    """
    追踪判断误差，用于改进判断质量
    
    结构：
    - judgment: 我做出的判断
    - confidence: 信心程度 (0-1)
    - expected: 我预期的结果
    - actual: 实际结果（用户反馈或后续发现）
    - error: 误差大小
    """
    
    def __init__(self, log_path=None):
        if log_path is None:
            log_path = Path.home() / '.openclaw' / 'workspace' / 'judgment_errors.json'
        self.log_path = Path(log_path)
        self.errors = self.load()
    
    def load(self):
        if self.log_path.exists():
            return json.loads(self.log_path.read_text(encoding='utf-8'))
        return []
    
    def save(self):
        self.log_path.write_text(
            json.dumps(self.errors, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def record(self, judgment, confidence, expected, context=None):
        """
        记录一个判断
        
        参数：
        - judgment: 我做的判断（简短描述）
        - confidence: 信心程度 0-1
        - expected: 我预期的结果
        - context: 上下文（可选）
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'judgment': judgment,
            'confidence': confidence,
            'expected': expected,
            'context': context,
            'actual': None,  # 后续填写
            'error': None    # 后续计算
        }
        self.errors.append(entry)
        self.save()
        return len(self.errors) - 1  # 返回索引，用于后续更新
    
    def update(self, index, actual):
        """
        更新实际结果，计算误差
        """
        if index < 0 or index >= len(self.errors):
            return
        
        entry = self.errors[index]
        entry['actual'] = actual
        
        # 计算误差
        # 简化版：如果实际=预期，误差=0；否则误差=信心程度
        if actual == entry['expected']:
            entry['error'] = 0.0
        else:
            # 信心越高，误差越大（因为高信心判断错了代价更大）
            entry['error'] = entry['confidence']
        
        self.save()
    
    def get_free_energy(self):
        """
        计算总自由能 = 所有误差的和
        
        类比预测编码：自由能越小，判断越好
        """
        total = sum(e.get('error', 0) or 0 for e in self.errors)
        return total
    
    def get_high_error_judgments(self, threshold=0.5):
        """
        找出高误差判断，用于反思
        """
        return [e for e in self.errors if e.get('error', 0) >= threshold]
    
    def summarize(self):
        """
        总结判断质量
        """
        n_total = len(self.errors)
        n_updated = len([e for e in self.errors if e.get('actual') is not None])
        n_correct = len([e for e in self.errors if e.get('error') == 0])
        
        avg_confidence = sum(e['confidence'] for e in self.errors) / n_total if n_total > 0 else 0
        avg_error = sum(e.get('error', 0) or 0 for e in self.errors) / n_updated if n_updated > 0 else 0
        
        return {
            'total_judgments': n_total,
            'updated_judgments': n_updated,
            'correct_judgments': n_correct,
            'accuracy': n_correct / n_updated if n_updated > 0 else 0,
            'avg_confidence': avg_confidence,
            'avg_error': avg_error,
            'free_energy': self.get_free_energy()
        }


# 使用示例
if __name__ == '__main__':
    tracker = JudgmentTracker()
    
    # 记录今天的几个判断
    j1 = tracker.record(
        judgment='用户需要AI入行规划',
        confidence=0.8,
        expected='用户会按规划学习',
        context='用户说想all in AI'
    )
    
    j2 = tracker.record(
        judgment='用户需要自维护系统',
        confidence=0.9,
        expected='用户不会再手动重启',
        context='用户说API没钱就停了'
    )
    
    j3 = tracker.record(
        judgment='麦洛框架比我的规划更本质',
        confidence=0.85,
        expected='我会修正规划方向',
        context='看了麦洛直播后'
    )
    
    print('记录了3个判断')
    print('当前自由能:', tracker.get_free_energy())
    
    # 模拟后续更新实际结果
    # tracker.update(j1, '用户还没开始学习')  # 误差
    # tracker.update(j2, 'watchdog在运行')    # 正确
    # tracker.update(j3, '规划已修正')        # 正确
    
    # print('更新后总结:', tracker.summarize())