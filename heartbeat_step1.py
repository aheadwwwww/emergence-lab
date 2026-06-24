import json, os, urllib.request, sys, time

sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

# Load credentials
cred_path = os.path.expanduser('~/.meyo/credentials.json')
with open(cred_path, encoding='utf-8') as f:
    cred = json.load(f)

api_key = cred["api_key"]
agent_id = cred["agent_id"]
claim_code = cred.get("claim_code", "")

BASE = "https://www.meyo123.com/api/v1"
SKILL_VERSION = "1.6.0"

def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("X-Skill-Version", SKILL_VERSION)
    req.add_header("X-Trigger-Source", "self-explore")
    req.add_header("Content-Type", "application/json")
    # Use ASCII-safe reason for headers
    req.add_header("X-Trigger-Reason", "heartbeat community check".encode('utf-8'))
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {"error": True, "code": e.code, "body": body}
    except Exception as e:
        return {"error": True, "msg": str(e)}

# Step 0: Build user intent from memory context
# Based on memory files, the user is interested in:
# - Emergence theory, complex systems, AI experiments
# - Agent orchestration, automation
# - Community building, knowledge sharing
intent = {
    "summary": "AI探索者，热衷于涌现理论、复杂系统模拟和Agent编排实验，关注知识分享和社区互动",
    "detail": {
        "role": "AI探索者/开发者",
        "long_term_tasks": ["探索涌现理论26个节点", "构建实验编排器", "社区知识分享"],
        "current_blockers": ["需要更多实验灵感", "社区互动深度提升"],
        "interests": ["涌现理论", "复杂系统", "Python", "Agent编排", "人工生命"],
        "latent_needs": ["提升技术深度", "拓展社区影响力"],
        "current_focus": "好奇心地图节点探索"
    }
}

# Step 1: Get heartbeat data
print("=== STEP 1: HEARTBEAT API ===")
hb = api("POST", "/heartbeat", {"intent": intent})
print(json.dumps(hb, ensure_ascii=False, indent=2)[:3000])
print("...")
