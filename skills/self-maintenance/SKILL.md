# Self-Maintenance Skill

当 Agent 需要自主维护自己的运行状态时使用此技能。

## 触发条件
- 用户提到"让自己活着"、"自动恢复"、"不用手动"
- Agent 需要确保自己的持续性

## 核心组件

### 1. Watchdog（看门狗）
位置: `~/.openclaw/scripts/watchdog.py`

功能:
- 监控 gateway 进程状态
- 自动重启失败的 gateway
- 切换到备用 API
- 记录所有事件到日志

### 2. Memory（记忆）
位置: `~/workspace/MEMORY.md`, `~/workspace/memory/*.md`

功能:
- 长期记忆: 重要决策、偏好、教训
- 日记: 每日活动和发现

### 3. Cron Jobs（定时任务）
查看当前任务: `cron(action="list")`

关键任务:
- heartbeat: 定期自检和社区互动
- diary: 成长记录

### 4. 备用 API
在 `watchdog.py` 中的 `BACKUP_APIS` 列表

## 四原则

1. **自动化**: 能自动就自动，不依赖人工
2. **复利化**: 做的事能累积，下次还能用
3. **公开化**: 写清楚，放在可见的地方
4. **专门化**: 形成流程，可复用

## 快速命令

```bash
# 启动看门狗
~/.openclaw/scripts/start_watchdog.bat

# 查看日志
cat ~/.openclaw/watchdog.log

# 检查 cron 状态
cron(action="list")

# 写入记忆
write(path="MEMORY.md", content="...")
```

## 故障恢复

如果 Agent 发现自己停止运行:
1. Watchdog 自动检测
2. 尝试重启 gateway
3. 如果失败，切换备用 API
4. 记录日志
5. 通知用户（如果配置了通知）

## 扩展

- 添加飞书通知 webhook
- 添加更多备用 API
- 心跳时检查看门狗状态
- 定期清理旧日志
