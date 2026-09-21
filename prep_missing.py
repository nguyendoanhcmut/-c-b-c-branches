import json, os

items = json.load(open('vol01_spawn_manifest.json', encoding='utf-8'))
missing = [it for it in items if not os.path.exists(it['output_json'])]
subagents = []
for it in missing:
    cf = it['case_file']
    out_json = it['output_json']
    subagents.append({
        'Model': 'flash',
        'Role': f'Driller {cf}',
        'TypeName': 'case_driller',
        'Prompt': f'Process case {cf}. Run: python run_case_driller.py "{cf}" "{out_json}". Verify output JSON exists and satisfies ASD-STE100 technical card constraints with all required non-empty fields. Notify parent when finished.'
    })
with open('missing_subagents.json', 'w', encoding='utf-8') as f:
    json.dump(subagents, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(subagents)} subagents to missing_subagents.json")
