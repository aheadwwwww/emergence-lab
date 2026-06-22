import urllib.request, json, ssl, re
ssl._create_default_https_context = ssl._create_unverified_context

# 从 openclaw.json 读取 feishu 配置
with open(r'C:\Users\许耀仁\.openclaw\openclaw.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

feishu_cfg = config.get('channels', {}).get('feishu', {})
app_id = feishu_cfg.get('appId')
app_secret = feishu_cfg.get('appSecret')

print(f'appId: {app_id}')

# 获取 tenant_access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
token_data = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode()
token_req = urllib.request.Request(token_url, data=token_data, headers={'Content-Type': 'application/json'}, method='POST')
token_resp = urllib.request.urlopen(token_req, timeout=10)
token_result = json.loads(token_resp.read())
token = token_result.get('tenant_access_token')
print(f'token: {token[:20]}...')

# 尝试删除聊天会话 (p2p chat)
# 飞书 API: DELETE /open-apis/im/v1/chats/:chat_id
chat_id = 'user:ou_a7ad011af470024c0bebded3a1453686'

del_url = f'https://open.feishu.cn/open-apis/im/v1/chats/{urllib.request.quote(chat_id, safe="")}'
del_req = urllib.request.Request(del_url, method='DELETE', headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
})

try:
    del_resp = urllib.request.urlopen(del_req, timeout=10)
    del_result = json.loads(del_resp.read())
    print(f'Delete result: {json.dumps(del_result, ensure_ascii=False, indent=2)}')
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f'HTTP {e.code}: {error_body[:500]}')
