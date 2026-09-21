import json

with open('vol01_spawn_manifest.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

subagents_batch1 = []
for item in items[:54]:
    case_file = item['case_file']
    out_json = item['output_json']
    subagents_batch1.append({
        'Model': 'flash',
        'Role': f'Driller {case_file}',
        'TypeName': 'case_driller',
        'Prompt': f'Process case {case_file}. Run: python run_case_driller.py "{case_file}" "{out_json}". Verify output JSON exists and satisfies ASD-STE100 technical card constraints with all required non-empty fields. Notify parent when finished.'
    })

with open('subagents_batch1.json', 'w', encoding='utf-8') as f:
    json.dump(subagents_batch1, f, ensure_ascii=False, indent=2)

subagents_batch2 = []
for item in items[54:]:
    case_file = item['case_file']
    out_json = item['output_json']
    subagents_batch2.append({
        'Model': 'flash',
        'Role': f'Driller {case_file}',
        'TypeName': 'case_driller',
        'Prompt': f'Process case {case_file}. Run: python run_case_driller.py "{case_file}" "{out_json}". Verify output JSON exists and satisfies ASD-STE100 technical card constraints with all required non-empty fields. Notify parent when finished.'
    })

with open('subagents_batch2.json', 'w', encoding='utf-8') as f:
    json.dump(subagents_batch2, f, ensure_ascii=False, indent=2)

print(f"Batch 1: {len(subagents_batch1)}, Batch 2: {len(subagents_batch2)}")
