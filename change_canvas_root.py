import json

config_path = 'C:/Users/许耀仁/.openclaw/openclaw.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 修改 canvas root 到 D盘
if 'plugins' not in config:
    config['plugins'] = {}
if 'entries' not in config['plugins']:
    config['plugins']['entries'] = {}
if 'canvas' not in config['plugins']['entries']:
    config['plugins']['entries']['canvas'] = {}
if 'config' not in config['plugins']['entries']['canvas']:
    config['plugins']['entries']['canvas']['config'] = {}
if 'host' not in config['plugins']['entries']['canvas']['config']:
    config['plugins']['entries']['canvas']['config']['host'] = {}

config['plugins']['entries']['canvas']['config']['host']['root'] = 'D:/openclaw_workspace/canvas'

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("Canvas root changed to: D:/openclaw_workspace/canvas")