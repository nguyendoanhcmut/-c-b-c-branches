import os, glob, re, sys

sys.stdout.reconfigure(encoding='utf-8')
cases_dir = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases"

for vol in ['vol01', 'vol02', 'vol03', 'vol04', 'vol05']:
    cases = glob.glob(os.path.join(cases_dir, f"*{vol}*.md"))
    chapters = set()
    for c in cases:
        content = open(c, 'r', encoding='utf-8').read(600)
        m = re.search(r'original_file:\s*"?([^"\n]+)"?', content)
        if m:
            chapters.add(m.group(1))
    print(f"=== {vol}: {len(cases)} cases across {len(chapters)} chapter files ===")
    for ch in sorted(list(chapters))[:3]:
        print("  Sample:", ch)
