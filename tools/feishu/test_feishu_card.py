"""
尝试发送飞书消息卡片
"""

import json, urllib.request, ssl, os
ssl._create_default_https_context = ssl._create_unverified_context

# 读取配置获取 access token
config_path = r'C:\Users\许耀仁\.openclaw\config\config.json5'
with open(config_path, 'r', encoding='utf-8') as f:
    import json5
    config = json5.load(f)

# 获取飞书配置
feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {})
default_account = feishu_config.get('defaultAccount', 'default')
account = accounts.get(default_account, {})

app_id = account.get('appId')
app_secret = account.get('appSecret')

print(f'App ID: {app_id}')

# 获取 tenant_access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
token_data = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode('utf-8')
token_req = urllib.request.Request(token_url, data=token_data, headers={'Content-Type': 'application/json'}, method='POST')
token_resp = urllib.request.urlopen(token_req, timeout=30)
token_result = json.loads(token_resp.read())
tenant_token = token_result.get('tenant_access_token')
print(f'Token: {tenant_token[:20]}...')

# 发送消息卡片到当前用户
# 接收者的 open_id
receive_id = 'ou_a7ad011af470024c0bebded3a1453686'

# 卡片内容
card_content = {
    "type": "template",
    "data": {
        "template_id": "AAqk8RIAAA",  # 这是一个示例模板ID，需要真实模板
        "template_variable": {
            "title": "测试卡片",
            "content": "这是一个消息卡片测试"
        }
    }
}

# 或者使用自定义卡片
custom_card = {
    "config": {
        "wide_screen_mode": True
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**这是一个测试卡片**\n支持 Markdown 格式"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "点击我"
                    },
                    "type": "primary"
                }
            ]
        }
    ]
}

# 发送
send_url = f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
send_data = {
    'receive_id': receive_id,
    'msg_type': 'interactive',  # 卡片类型
    'content': json.dumps(custom_card)
}

send_req = urllib.request.Request(
    send_url,
    data=json.dumps(send_data).encode('utf-8'),
    headers={
        'Authorization': f'Bearer {tenant_token}',
        'Content-Type': 'application/json'
    },
    method='POST'
)

try:
    send_resp = urllib.request.urlopen(send_req, timeout=30)
    send_result = json.loads(send_resp.read())
    print(f'Result: {json.dumps(send_result, ensure_ascii=False, indent=2)[:500]}')
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f'Error: {error_body[:500]}')