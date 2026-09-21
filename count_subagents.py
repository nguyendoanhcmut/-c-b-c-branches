import json, sys

sys.stdout.reconfigure(encoding='utf-8')
log_path = r"C:\Users\Admin\.gemini\antigravity\brain\d873f6ef-8044-4aaf-bd06-e2a06ee682d8\.system_generated\logs\transcript.jsonl"

subagents = []
with open(log_path, 'r', encoding='utf-8') as f:
    for line_no, line in enumerate(f):
        data = json.loads(line)
        tool_calls = data.get('tool_calls', [])
        for tc in tool_calls:
            if tc.get('name') == 'invoke_subagent':
                args = tc.get('args', {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                sub_list = args.get('Subagents', [])
                if isinstance(sub_list, str):
                    try:
                        sub_list = json.loads(sub_list)
                    except Exception:
                        pass
                for s in sub_list:
                    if isinstance(s, dict):
                        subagents.append(s)

print(f"Tổng số subagent đã invoke trong phiên này: {len(subagents)}")
roles = {}
types = {}
for s in subagents:
    r = s.get('Role', 'Unknown')
    t = s.get('TypeName', 'Unknown')
    roles[r] = roles.get(r, 0) + 1
    types[t] = types.get(t, 0) + 1

print("\nPhân loại theo TypeName:")
for t, c in types.items():
    print(f"  - {t}: {c}")

print("\nDanh sách chi tiết theo Role:")
for r, c in sorted(roles.items()):
    print(f"  - {r}: {c}")
