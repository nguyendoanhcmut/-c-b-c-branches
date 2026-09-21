import os, json, sys, math

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"

def prep_batches_for_volume(vol_id, max_batch_size=55):
    manifest_file = os.path.join(SCRATCH_DIR, f"{vol_id}_spawn_manifest.json")
    if not os.path.exists(manifest_file):
        print(f"Error: {manifest_file} not found!")
        return []
        
    with open(manifest_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
        
    cases_dir = os.path.join(SCRATCH_DIR, f"{vol_id}_cases")
    os.makedirs(cases_dir, exist_ok=True)
    
    total = len(items)
    num_batches = math.ceil(total / max_batch_size)
    batch_size = math.ceil(total / num_batches)
    
    batch_files = []
    for b_idx in range(num_batches):
        start = b_idx * batch_size
        end = min((b_idx + 1) * batch_size, total)
        batch_items = items[start:end]
        
        subagents = []
        for it in batch_items:
            cfile = it['case_file']
            out_json = it['output_json']
            subagents.append({
                "Model": "flash",
                "Role": f"Driller {cfile}",
                "TypeName": "case_driller",
                "Prompt": f'Process case {cfile}. Run: python run_case_driller.py "{cfile}" "{out_json}". Verify output JSON exists and satisfies ASD-STE100 technical card constraints with all required non-empty fields. Notify parent when finished.'
            })
            
        b_file = os.path.join(SCRATCH_DIR, f"subagents_{vol_id}_batch{b_idx + 1}.json")
        with open(b_file, 'w', encoding='utf-8') as f:
            json.dump(subagents, f, ensure_ascii=False, indent=2)
            
        batch_files.append((b_file, len(subagents)))
        print(f"Generated {b_file} ({len(subagents)} subagents, items {start+1} to {end})")
        
    print(f"Volume {vol_id}: Prepared {total} drillers across {num_batches} batches.")
    return batch_files

if __name__ == "__main__":
    vols = sys.argv[1:] if len(sys.argv) > 1 else ["vol02", "vol03", "vol04", "vol05"]
    for v in vols:
        prep_batches_for_volume(v)
