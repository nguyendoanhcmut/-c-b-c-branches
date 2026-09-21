import os, glob, json, sys

sys.stdout.reconfigure(encoding='utf-8')

CASES_DIR = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases"
SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"

def create_spawn_manifest(vol_id):
    cases = sorted(glob.glob(os.path.join(CASES_DIR, f"*{vol_id}*.md")))
    manifest = []
    for idx, cpath in enumerate(cases):
        cfile = os.path.basename(cpath)
        base = os.path.splitext(cfile)[0]
        manifest.append({
            "index": idx + 1,
            "case_file": cfile,
            "case_path": cpath,
            "output_json": os.path.join(SCRATCH_DIR, f"{vol_id}_cases", f"{base}.json")
        })
    
    out_file = os.path.join(SCRATCH_DIR, f"{vol_id}_spawn_manifest.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"Created spawn manifest: {out_file} ({len(manifest)} cases)")
    return manifest

if __name__ == "__main__":
    vol = sys.argv[1] if len(sys.argv) > 1 else "vol01"
    create_spawn_manifest(vol)
