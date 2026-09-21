import os, re, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"
COMPILER_JS = r"C:\Users\Admin\.gemini\config\skills\branches\scripts\compile_mindmap.js"

master_title = "# Cổ Bốc Toàn Thư (Tăng San Bốc Dịch) - Toàn Tập 5 Quyển (830 Ví Dụ Thực Nghiệm)\n\n"
content = master_title

vols = [
    ("vol01", "Tập 1: Thông Luận Cơ Sở & Nhập Môn (Ch.I–XX)"),
    ("vol02", "Tập 2: Dịch Lý Thiên – Phần 1 (Ch.XXI–XXVII)"),
    ("vol03", "Tập 3: Dịch Lý Thiên – Phần 2 (Ch.XXVIII–XXXIV)"),
    ("vol04", "Tập 4: Tiến Giai Thiên (Ch.XXXV–XL + Giảng Nghĩa)"),
    ("vol05", "Tập 5: Chi Tiết Thiên (Ch.XLI–LVII)")
]

for vol_id, vol_heading in vols:
    md_file = os.path.join(SCRATCH_DIR, f"{vol_id}_branches.md")
    with open(md_file, 'r', encoding='utf-8') as f:
        vol_content = f.read()

    # Shift headings down by 1 level so master is #, volumes are ##, chapters are ###
    lines = vol_content.split('\n')
    processed_lines = []
    first_h1_skipped = False
    for line in lines:
        if line.startswith('# ') and not first_h1_skipped:
            processed_lines.append(f"## {vol_heading}")
            first_h1_skipped = True
        elif line.startswith('#'):
            processed_lines.append('#' + line)
        else:
            processed_lines.append(line)

    content += "\n".join(processed_lines) + "\n\n"

master_md = os.path.join(SCRATCH_DIR, "coboc_toan_thu_branches.md")
with open(master_md, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Đã cập nhật Master MD: {master_md} ({len(content)} bytes)")

master_html = os.path.join(SCRATCH_DIR, "coboc_toan_thu_branches.html")
print(f"Biên dịch Master HTML: {master_html}...")
cmd = ["node", COMPILER_JS, master_md, master_html]
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print(res.stdout)
if res.stderr:
    print("Compiler stderr:", res.stderr)

if os.path.exists(master_html):
    sz = os.path.getsize(master_html) / 1024
    print(f"HOÀN THÀNH Master HTML: {master_html} ({sz:.1f} KB)")
