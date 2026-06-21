# 本地模型部署方案

## 你的硬件
- Intel Iris Xe Graphics (2GB 显存)
- 集成显卡，可以跑轻量模型

## 安装 Ollama

### 方法 1: 直接下载
1. 访问 https://ollama.com/download
2. 下载 Windows 版本
3. 运行安装程序

### 方法 2: PowerShell (需要你手动执行)
```powershell
# 下载安装脚本
Invoke-WebRequest -Uri "https://ollama.com/install.ps1" -OutFile "install.ps1"
# 运行安装
.\install.ps1
```

### 方法 3: 手动下载
直接下载: https://github.com/ollama/ollama/releases/download/v0.1.26/OllamaSetup.exe

## 推荐模型（适合 2GB 显存）

| 模型 | 大小 | 用途 |
|------|------|------|
| qwen2.5:1.5b | 1.5GB | 中文对话，轻量 |
| llama3.2:1b | 1GB | 英文对话，最小 |
| phi3:mini | 2GB | 代码/推理 |

## 安装后运行

```bash
# 拉取模型
ollama pull qwen2.5:1.5b

# 运行模型
ollama run qwen2.5:1.5b

# 测试 API
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:1.5b","prompt":"你好"}'
```

## 配置 OpenClaw 使用 Ollama

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "api": "ollama",
        "models": [
          {
            "id": "qwen2.5:1.5b",
            "name": "Qwen 2.5 1.5B",
            "cost": { "input": 0, "output": 0 }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen2.5:1.5b",
        "fallbacks": ["xunfei/astron-code-latest"]
      }
    }
  }
}
```

## 优势

- 完全免费，无 API 成本
- 数据留在本地，隐私安全
- 不依赖网络，随时可用
- 可以跑中文模型 (qwen)

## 限制

- 速度比云端慢
- 模型能力有限（小模型）
- 需要占用系统资源

---

**建议**: 先装 Ollama，跑 qwen2.5:1.5b，作为终极免费备份。