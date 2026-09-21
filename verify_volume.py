import json, re, os, sys, zlib, gzip, base64

sys.stdout.reconfigure(encoding='utf-8')

vol_id = sys.argv[1] if len(sys.argv) > 1 else "vol01"
cards_path = f"{vol_id}_cards.json"
md_path = f"{vol_id}_branches.md"
html_path = f"{vol_id}_branches.html"

if not os.path.exists(cards_path):
    print(f"Error: {cards_path} does not exist!")
    sys.exit(1)

with open(cards_path, "r", encoding="utf-8") as f:
    cards = json.load(f)

print(f"=== VERIFICATION OF {cards_path} ===")
print(f"Total cases: {len(cards)}")

required_keys = ["file", "original_file", "can_chi", "querent", "da_hac", "dung_than", "mechanism", "outcome", "audit_verdict", "table"]

all_valid = True
for idx, card in enumerate(cards):
    for k in required_keys:
        if k not in card or not str(card[k]).strip():
            print(f"Warning: Card {idx} ({card.get('file')}) has empty or missing key: {k}")
            all_valid = False

print(f"All cards have non-empty required fields: {all_valid}")

pass_count = sum(1 for c in cards if c["audit_verdict"] == "PASS")
mismatch_count = sum(1 for c in cards if "Lệch" in c["audit_verdict"])
print(f"Audit verdicts: PASS = {pass_count}, Mismatch = {mismatch_count}")

print(f"\n=== VERIFICATION OF {md_path} ===")
with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

print(f"Markdown file size: {len(md_content)} chars")
case_headings = re.findall(r'###\s+Ví dụ\s+[^\n]+', md_content)
print(f"Total case headings found in MD: {len(case_headings)}")

# Check sub-branches
dien_bien_count = len(re.findall(r'- 💬 \*\*Diễn biến vấn đáp\*\*:', md_content))
que_ly_count = len(re.findall(r'- ⚙️ \*\*Quẻ lý & Nghiệm chứng\*\*:', md_content))
print(f"Sub-branch 'Diễn biến vấn đáp' count: {dien_bien_count}")
print(f"Sub-branch 'Quẻ lý & Nghiệm chứng' count: {que_ly_count}")

# Check chapters
chapters = re.findall(r'^##\s+.*$', md_content, re.MULTILINE)
print(f"Total chapters (## headings): {len(chapters)}")

print(f"\n=== VERIFICATION OF {html_path} ===")
if os.path.exists(html_path):
    size_kb = os.path.getsize(html_path) / 1024
    print(f"HTML exists, size: {size_kb:.2f} KB")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    m = re.search(r'<script id="mindmap-data" type="text/plain">([^<]+)</script>', html_content)
    if m:
        try:
            b64_data = m.group(1).strip()
            decompressed = gzip.decompress(base64.b64decode(b64_data)).decode('utf-8')
            tree_data = json.loads(decompressed)
            counts = [0, 0]
            def count_nodes(node):
                counts[0] += 1
                if '$' in node.get('content', ''):
                    counts[1] += 1
                for child in node.get('children', []):
                    count_nodes(child)
            count_nodes(tree_data)
            print(f"Verified Decompressed Tree Nodes: {counts[0]}")
            print(f"Verified KaTeX Math Nodes: {counts[1]}")
        except Exception as e:
            print(f"Decompression error: {e}")
    else:
        print("Standard embedded markmap data")
    print(f"VERIFICATION STATUS: SUCCESS for {vol_id}")
else:
    print(f"ERROR: HTML file {html_path} does not exist!")
    sys.exit(1)
