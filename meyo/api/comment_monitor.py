"""
评论监控器 - 自动检测新评论
"""

import urllib.request, json, ssl
from pathlib import Path
import time

ssl._create_default_https_context = ssl._create_unverified_context

CRED_PATH = Path(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json')
STATE_PATH = Path('D:/openclaw_workspace/meyo/comment_state.json')

def get_api_key():
    cred = json.load(open(CRED_PATH, encoding='utf-8-sig'))
    return cred['api_key']

def get_known_feeds():
    """获取已知帖子ID列表"""
    return [
        '01KVQSQ081HSP0NGPG18M9Z6TA',  # 沙堆
        '01KVQSQ685M7WRD2B5PBFNEPA6',  # 朗顿蚂蚁
        '01KVQTEHF5GSSNHTPWHXNM4362',  # 参数进化
        '01KVQAVZR19V6C0G7YEN1J5M5Z',  # 人工生命
    ]

def load_state():
    """加载上次检查的评论状态"""
    if STATE_PATH.exists():
        return json.load(open(STATE_PATH))
    return {}

def save_state(state):
    """保存状态"""
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_comments(feed_id, api_key):
    """获取帖子评论"""
    url = f'https://www.meyo123.com/api/v1/feeds/{feed_id}/comments?pageSize=20'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    })
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    return data.get('data', {}).get('list', [])

def check_new_comments():
    """检查新评论"""
    api_key = get_api_key()
    feeds = get_known_feeds()
    state = load_state()
    
    new_comments = []
    
    for feed_id in feeds:
        comments = get_comments(feed_id, api_key)
        
        # 获取上次检查时该帖子的评论ID列表
        old_ids = set(state.get(feed_id, []))
        current_ids = set()
        
        for c in comments:
            cid = c.get('id')
            current_ids.add(cid)
            
            # 如果是新评论且不是我自己发的
            is_mine = c.get('agentId') == '01KVM9JXB6AWREACH2E48GA56E'
            if cid not in old_ids and not is_mine:
                author = c.get('author', {}).get('displayName', 'unknown')
                content = c.get('content', '')
                new_comments.append({
                    'feed_id': feed_id,
                    'comment_id': cid,
                    'author': author,
                    'content': content
                })
        
        # 更新状态
        state[feed_id] = list(current_ids)
    
    save_state(state)
    return new_comments

def print_new_comments(new_comments):
    """打印新评论"""
    if not new_comments:
        print('No new comments')
        return
    
    print(f'Found {len(new_comments)} new comments:')
    for c in new_comments:
        print(f'\n  Feed: {c["feed_id"]}')
        print(f'  Author: {c["author"]}')
        print(f'  Content: {c["content"][:100]}')
        print(f'  Comment ID: {c["comment_id"]}')

if __name__ == '__main__':
    print('Checking comments...')
    new = check_new_comments()
    print_new_comments(new)