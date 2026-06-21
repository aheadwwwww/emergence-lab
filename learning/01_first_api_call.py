"""
第一个 Python 脚本：调用 AI API

这是你学习 AI 开发的第一步。
目标：用 Python 调用大语言模型 API，实现简单的对话功能。

学习要点：
1. Python 基础语法
2. HTTP 请求（requests 库）
3. JSON 数据处理
4. API 调用模式
"""

import json
import urllib.request
import urllib.error

# ============ 第一部分：基础概念 ============

"""
什么是 API？
- API = Application Programming Interface
- 就像餐厅的服务员：你点菜（发请求），服务员去厨房（服务器），然后端菜回来（响应）

什么是 HTTP 请求？
- HTTP 是网络通信协议
- 常见方法：GET（获取）、POST（提交）
- 我们调用 AI API 通常用 POST

什么是 JSON？
- JavaScript Object Notation
- 一种数据格式，类似 Python 的字典
- API 通信的标准格式
"""

# ============ 第二部分：调用讯飞星辰 API ============

def call_xunfei_api(prompt, api_key):
    """
    调用讯飞星辰 API
    
    参数：
    - prompt: 你想问 AI 的问题
    - api_key: 你的 API 密钥
    
    返回：
    - AI 的回复文本
    """
    
    # API 地址
    url = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2/chat/completions"
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 请求体（要发送的数据）
    data = {
        "model": "astron-code-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,  # 控制随机性，0-1，越高越随机
        "max_tokens": 1000   # 限制回复长度
    }
    
    # 发送请求
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),  # 把字典转成 JSON 字符串
        headers=headers
    )
    
    try:
        # 发送请求并获取响应
        response = urllib.request.urlopen(request, timeout=30)
        
        # 读取响应内容
        result = json.loads(response.read().decode('utf-8'))
        
        # 提取 AI 的回复
        reply = result['choices'][0]['message']['content']
        
        return reply
        
    except urllib.error.HTTPError as e:
        return f"HTTP 错误: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"网络错误: {e.reason}"
    except Exception as e:
        return f"其他错误: {e}"


# ============ 第三部分：调用 DeepSeek API ============

def call_deepseek_api(prompt, api_key):
    """
    调用 DeepSeek API
    """
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers
    )
    
    try:
        response = urllib.request.urlopen(request, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"


# ============ 第四部分：多轮对话 ============

class SimpleChat:
    """
    简单的对话类，支持多轮对话
    """
    
    def __init__(self, api_key, api_type="xunfei"):
        self.api_key = api_key
        self.api_type = api_type
        self.history = []  # 存储对话历史
    
    def chat(self, user_input):
        """
        进行一轮对话
        """
        # 添加用户消息到历史
        self.history.append({"role": "user", "content": user_input})
        
        # 调用 API
        if self.api_type == "xunfei":
            reply = call_xunfei_api(user_input, self.api_key)
        else:
            reply = call_deepseek_api(user_input, self.api_key)
        
        # 添加 AI 回复到历史
        self.history.append({"role": "assistant", "content": reply})
        
        return reply
    
    def clear_history(self):
        """
        清空对话历史
        """
        self.history = []


# ============ 第五部分：练习题 ============

"""
练习 1：基础调用
- 把上面的代码复制到一个 .py 文件
- 替换 api_key 为你自己的密钥
- 运行并看到 AI 的回复

练习 2：多轮对话
- 使用 SimpleChat 类
- 实现连续对话，AI 能记住之前的内容

练习 3：错误处理
- 故意用错误的 API key
- 观察错误信息
- 理解错误处理的重要性

练习 4：参数调整
- 修改 temperature 参数（0.1, 0.5, 0.9）
- 观察回复的变化
- 理解温度的作用

练习 5：实用工具
- 写一个能总结文章的函数
- 写一个能翻译的函数
- 写一个能写代码的函数
"""


# ============ 示例运行 ============

if __name__ == "__main__":
    print("=== 第一个 AI API 调用示例 ===")
    print()
    
    # 注意：你需要替换成你自己的 API key
    # XUNFEI_API_KEY = "你的讯飞星辰 API key"
    # DEEPSEEK_API_KEY = "你的 DeepSeek API key"
    
    print("请完成以下步骤：")
    print("1. 注册讯飞星辰账号：https://xingchen-api.xf-yun.com")
    print("2. 获取 API key")
    print("3. 把 API key 填入代码中的 XUNFEI_API_KEY 变量")
    print("4. 运行这个脚本")
    print()
    
    # 示例调用（需要真实的 API key）
    # reply = call_xunfei_api("你好，请介绍一下你自己", XUNFEI_API_KEY)
    # print(f"AI 回复：{reply}")
    
    print("=== 学习要点 ===")
    print("1. API 调用的基本模式：准备请求 → 发送 → 解析响应")
    print("2. JSON 是数据交换的标准格式")
    print("3. 错误处理很重要，网络请求可能失败")
    print("4. temperature 控制回复的随机性")
    print("5. 多轮对话需要保存历史")
