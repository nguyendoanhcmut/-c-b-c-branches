import os, json, sys
from build_volume_mindmap import parse_case, MISMATCHES_FILE, CASES_DIR

sys.stdout.reconfigure(encoding='utf-8')

def process_single_case(case_file, output_json):
    cpath = os.path.join(CASES_DIR, case_file) if not os.path.isabs(case_file) else case_file
    if not os.path.exists(cpath):
        print(f"Error: Case file {cpath} not found!")
        sys.exit(1)
        
    with open(MISMATCHES_FILE, 'r', encoding='utf-8') as f:
        mismatches_data = json.load(f)
    mismatches_map = {m['file']: m for m in mismatches_data.get('mismatches', [])}
    
    card = parse_case(cpath, mismatches_map)
    
    out_dir = os.path.dirname(output_json)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(card, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed {case_file} -> {output_json} (Verdict: {card['audit_verdict']})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_case_driller.py <case_file> <output_json>")
        sys.exit(1)
    process_single_case(sys.argv[1], sys.argv[2])
