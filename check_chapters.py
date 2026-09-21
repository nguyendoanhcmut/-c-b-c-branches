import os, glob, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
cases_dir = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases"
vol01_cases = glob.glob(os.path.join(cases_dir, "*vol01*.md"))
print(f"Total Vol 1 cases: {len(vol01_cases)}")

orig_files = []
for c in vol01_cases:
    with open(c, 'r', encoding='utf-8') as f:
        content = f.read(600)
    m = re.search(r'original_file:\s*"?([^"\n]+)"?', content)
    if m:
        orig_files.append(m.group(1))
    else:
        orig_files.append("UNKNOWN")

counts = Counter(orig_files)
for k, v in sorted(counts.items()):
    print(f"{k} -> {v} cases")
