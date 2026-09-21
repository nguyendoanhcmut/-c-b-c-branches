import os, glob, json, re, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"
CASES_DIR = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases"
COMPILER_JS = r"C:\Users\Admin\.gemini\config\skills\branches\scripts\compile_mindmap.js"

CHAPTER_MAP = [
    ("ch01", "Chương I: Nghiên cứu Dịch đều có tâm thành chính xác", "Chương I"),
    ("ch07", "Chương VII: Đường tắt nhanh chóng để cao trình độ dự đoán", "Chương VII"),
    ("ch08", "Chương VIII: Trình tự đoán quẻ hoàn chỉnh", "Chương VIII"),
    ("ch09", "Chương IX: Dự đoán quẻ cần phân tích hai phương diện lý luận khác nhau", "Chương IX"),
    ("ch11", "Chương XI: Xác định và lựa chọn Dụng thần", "Chương XI"),
    ("ch12", "Chương XII: Dụng thần trong quẻ tĩnh thời", "Chương XII"),
    ("ch13", "Chương XIII: Bốn nhân tố có thể ảnh hưởng vượng suy của một hào", "Chương XIII"),
    ("ch14", "Chương XIV: Ảnh hưởng của tổ hợp nhật nguyệt tới với hào trong quẻ", "Chương XIV"),
    ("ch15", "Chương XV: Tổ hợp động biến", "Chương XV"),
    ("ch16", "Chương XVI: Phân rõ hào động hữu dụng", "Chương XVI"),
    ("ch17", "Chương XVII: Nguyên tắc động phân hợp", "Chương XVII"),
    ("ch18", "Chương XVIII: Tác dụng trọng yếu của Dụng thần và Hào Thế trong quẻ động", "Chương XVIII"),
    ("ch19", "Chương XIX: Ý niệm khi ra xem và thay mặt xem", "Chương XIX"),
    ("ch20", "Chương XX: Quan hệ giữa ý niệm và tin tức trong quẻ tượng", "Chương XX"),
    ("ch23", "Chương XXIII: Chư thần bản giảng nghĩa", "Chương XXIII")
]

def extract_table_from_case(cfile):
    cpath = os.path.join(CASES_DIR, cfile)
    if not os.path.exists(cpath):
        return ""
    with open(cpath, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    table_lines = []
    in_table = False
    for line in lines:
        if '|' in line:
            in_table = True
            table_lines.append(line)
        elif in_table:
            break
    return "\n".join(table_lines)

def build_case_node(card):
    cfile = card.get('file', '')
    can_chi = card.get('can_chi', 'Chưa rõ can chi')
    querent = card.get('querent', 'Thân chủ hỏi sự việc thực tế, lo lắng cầu cát hung.')
    da_hac = card.get('da_hac', 'Dã Hạc phân tích tương quan Thế Ứng và Dụng thần.')
    dung_than = card.get('dung_than', 'Dụng thần định vị.')
    mechanism = card.get('mechanism', 'Luận quẻ theo Dụng thần và tương tác nhật nguyệt động biến.')
    outcome = card.get('outcome', 'Sự việc ứng nghiệm đúng theo quẻ báo.')
    verdict = card.get('audit_verdict', 'PASS')
    
    table = extract_table_from_case(cfile)
    title = cfile.replace('.md', '').replace('vd_', 'Ví dụ ').replace('_', ' ')
    
    node = f"### {title}: {can_chi}\n\n"
    node += f"- 💬 **Diễn biến vấn đáp**:\n"
    node += f"  - **Thân chủ**: {querent}\n"
    node += f"  - **Dã Hạc**: {da_hac}\n"
    node += f"- ⚙️ **Quẻ lý & Nghiệm chứng**:\n"
    if table:
        indented_table = "\n".join(["    " + l for l in table.split('\n')])
        node += f"  - **Bảng quẻ**:\n{indented_table}\n"
    node += f"  - **Dụng thần**: {dung_than}\n"
    node += f"  - **Cơ chế luận**: {mechanism}\n"
    node += f"  - **Nghiệm chứng**: {outcome}\n"
    node += f"  - **Kiểm toán nạp giáp**: {verdict}\n\n"
    return node

def assemble_vol01():
    print("Reading backup/original vol01_branches.md...")
    md_path = os.path.join(SCRATCH_DIR, "vol01_branches.md")
    
    # Check if git has clean original
    res = subprocess.run(["git", "checkout", "vol01_branches.md"], cwd=SCRATCH_DIR, capture_output=True, text=True)
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Load cards
    worker_files = sorted(glob.glob(os.path.join(SCRATCH_DIR, "vol01_workers", "*.json")))
    all_cards = []
    for wf in worker_files:
        with open(wf, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            all_cards.extend(cards)
    print(f"Total cards loaded: {len(all_cards)}")
    
    # Map cards to ch_key
    cards_by_ch = {}
    for card in all_cards:
        cfile = card.get('file', '')
        m = re.search(r'ch_?(\d+)', cfile)
        if m:
            num = int(m.group(1))
            ch_key = f"ch{num:02d}"
        else:
            ch_key = "ch_other"
        cards_by_ch.setdefault(ch_key, []).append(card)
        
    for ch_key, full_title, roman_key in CHAPTER_MAP:
        ch_cards = cards_by_ch.get(ch_key, [])
        if not ch_cards:
            continue
        print(f"Processing {ch_key}: {len(ch_cards)} cases...")
        
        # Build text for examples
        ex_text = f"\n### 📚 Các ca ví dụ thực tế nghiệm chứng ({len(ch_cards)} ca)\n\n"
        for card in ch_cards:
            ex_text += build_case_node(card)
            
        # Check if chapter heading exists in content
        # Pattern matches ## Chương VII... or ## Chương 7...
        m = re.search(rf'##\s+{re.escape(roman_key)}[^\n]*\n', content)
        if m:
            # Find the start of next ## heading or end of file
            start_pos = m.end()
            next_heading = re.search(r'\n##\s+', content[start_pos:])
            if next_heading:
                insert_pos = start_pos + next_heading.start()
                content = content[:insert_pos] + "\n" + ex_text + content[insert_pos:]
            else:
                content = content + "\n" + ex_text
        else:
            # Chapter heading doesn't exist, append new chapter
            new_section = f"\n## {full_title}\n\n" + ex_text
            content = content + "\n" + new_section
            
    # Write updated vol01_branches.md
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {md_path} ({len(content)} bytes)")
    
    # Compile HTML
    html_path = os.path.join(SCRATCH_DIR, "vol01_branches.html")
    print(f"Compiling {html_path}...")
    cmd = ["node", COMPILER_JS, md_path, html_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    print("Compiler stdout:", res.stdout)
    if res.stderr:
        print("Compiler stderr:", res.stderr)
        
    if os.path.exists(html_path):
        size_kb = os.path.getsize(html_path) / 1024
        print(f"Successfully compiled {html_path} ({size_kb:.1f} KB)")
        return True
    return False

if __name__ == "__main__":
    assemble_vol01()
