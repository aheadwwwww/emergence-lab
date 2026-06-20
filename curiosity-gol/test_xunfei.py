#!/usr/bin/env python3
"""Test different Xunfei model names"""
import urllib.request, json

api_key = 'c4d786b2eadb100a627002791490b261:MDNkM2E1NTI5ZTljODRjNzJiYmE2OGI5'
base_url = 'https://maas-coding-api.cn-huabei-1.xf-yun.com/v2'

models_to_try = [
    'astron-code-latest',
    'astron-code',
    'spark-4.0-ultra',
    'spark-max',
    'spark-pro',
    '4.0Ultra',
    'generalv3.5',
    'general',
    'generalv3',
]

for model in models_to_try:
    try:
        req = urllib.request.Request(
            f'{base_url}/chat/completions',
            data=json.dumps({
                'model': model,
                'messages': [{'role': 'user', 'content': 'hi'}],
                'max_tokens': 5
            }).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            print(f'  {model}: OK - {resp.get("model", "?")}')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'  {model}: HTTP {e.code} - {body[:150]}')
    except Exception as e:
        print(f'  {model}: ERROR - {str(e)[:150]}')
