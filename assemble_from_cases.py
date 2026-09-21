import os, glob, json, re, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"
COMPILER_JS = r"C:\Users\Admin\.gemini\config\skills\branches\scripts\compile_mindmap.js"

def assemble_volume_cases(vol_id):
    cases_dir = os.path.join(SCRATCH_DIR, f"{vol_id}_cases")
    if not os.path.exists(cases_dir):
        print(f"Error: Directory {cases_dir} does not exist!")
        return False
        
    case_files = sorted(glob.glob(os.path.join(cases_dir, "*.json")))
    print(f"Loading {len(case_files)} case cards from {cases_dir}...")
    
    all_cards = []
    for cf in case_files:
        with open(cf, 'r', encoding='utf-8') as f:
            try:
                card = json.load(f)
                all_cards.append(card)
            except Exception as e:
                print(f"Error reading {cf}: {e}")
                
    print(f"Successfully loaded {len(all_cards)} valid cards.")
    
    # Save unified cards JSON
    unified_cards_file = os.path.join(SCRATCH_DIR, f"{vol_id}_cards.json")
    with open(unified_cards_file, 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)
    print(f"Saved {unified_cards_file}")
    
    # Run build_volume_mindmap to inject and compile
    cmd = ["python", "build_volume_mindmap.py", vol_id]
    res = subprocess.run(cmd, cwd=SCRATCH_DIR, capture_output=True, text=True, encoding='utf-8')
    print(res.stdout)
    if res.stderr:
        print("Build stderr:", res.stderr)
        
    # Run verify_volume
    vcmd = ["python", "verify_volume.py", vol_id]
    vres = subprocess.run(vcmd, cwd=SCRATCH_DIR, capture_output=True, text=True, encoding='utf-8')
    print(vres.stdout)
    if vres.stderr:
        print("Verify stderr:", vres.stderr)
        
    return True

if __name__ == "__main__":
    vol = sys.argv[1] if len(sys.argv) > 1 else "vol01"
    assemble_volume_cases(vol)
