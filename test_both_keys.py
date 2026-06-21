import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 两个key都试试
keys = [
    'AQ.Ab8…JVpQ',  # 第一个
]

for key in keys:
    print(f"测试 key: ...{key[-4:]}")
    url = "https://generativelanguage.googleapis.com/v1beta/models?key=***" + key
    
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode('utf-8'))
        print("  有效！")
        return key
    except Exception as e:
        print(f"  无效: {e}")

print("\n两个key都无效。页面显示的可能不是完整的key。")
print("请点击key旁边的'复制'按钮或'显示'按钮获取完整key。")