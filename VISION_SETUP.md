# 如何让AI看图片

## 当前状态

讯飞星辰（当前使用的模型）**不支持图片理解**。

OpenClaw 的 `media-understanding` 功能需要配置 vision-capable 模型。

## 解决方案

### 方案1：配置 Google Gemini（推荐，有免费额度）

1. 获取 Gemini API key：
   - 访问 https://aistudio.google.com/apikey
   - 创建 API key

2. 编辑 `~/.openclaw/openclaw.json`，添加：

```json
{
  "models": {
    "providers": {
      "google": {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
        "api": "google",
        "apiKey": "你的API_KEY",
        "models": [
          {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "input": ["text", "image"],
            "cost": {"input": 0, "output": 0},
            "contextWindow": 1000000
          }
        ]
      }
    }
  }
}
```

3. 重启 gateway：`openclaw gateway restart`

### 方案2：配置 OpenRouter

OpenRouter 可以访问多种模型，包括 vision 模型。

1. 获取 OpenRouter API key：https://openrouter.ai/keys

2. 编辑配置，添加 OpenRouter provider

### 方案3：用飞书的图片转文字功能

如果用户在飞书发送图片时，先使用飞书自带的"识别文字"功能，然后把文字发给我。

## 状态记录

**判断**：我应该能看图片
**信心**：0.6
**预期**：找到方法OCR图片内容
**实际**：发现需要配置vision模型，当前模型不支持
**误差**：0.6（需要用户配置API key）

## 下一步

需要用户：
1. 选择一个vision模型提供商（推荐Gemini）
2. 获取API key
3. 配置到openclaw.json
4. 重启gateway

之后我就能看图片了。