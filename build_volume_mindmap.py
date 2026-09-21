import os, glob, json, re, sys, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches"
CASES_DIR = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases"
VOLUMES_DIR = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\volumes"
MISMATCHES_FILE = r"C:\Users\Admin\Downloads\antgravity workplace\coboc_output\tool_mismatches.json"
COMPILER_JS = r"C:\Users\Admin\.gemini\config\skills\branches\scripts\compile_mindmap.js"

def clean_ste(text, max_words=18):
    if not text:
        return ""
    t = re.sub(r'\s*\([A-Za-z\s,_\-]+\)', '', text)
    t = t.replace('**', '').replace('__', '').strip()
    t = re.sub(r'\s+', ' ', t)
    words = t.split()
    if len(words) > max_words:
        t = " ".join(words[:max_words]) + "..."
    t = t.strip()
    while t and t[-1] in ',;:':
        t = t[:-1].strip()
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t

def extract_can_chi(text):
    m = re.search(r'Can chi\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if m:
        return clean_ste(m.group(1).strip(), 12)
    m = re.search(r'(Ngày\s+[^\n,\(]+(?:\s*\([^\)]+\))?)', text, re.IGNORECASE)
    if m:
        return clean_ste(m.group(1).strip(), 12)
    m = re.search(r'(?:Can chi|Ngày)[^:\n]*:?\s*([^\n\(]+(?:\([^\)]+\))?)', text, re.IGNORECASE)
    if m:
        return clean_ste(m.group(1).strip(), 12)
    return "Chưa rõ nhật nguyệt"

def extract_table(text):
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

def parse_case(cpath, mismatches_map):
    cfile = os.path.basename(cpath)
    with open(cpath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Frontmatter
    orig_file = ""
    m_orig = re.search(r'original_file:\s*"?([^"\n]+)"?', text)
    if m_orig:
        orig_file = m_orig.group(1).strip().replace('\\\\', '\\')

    can_chi = extract_can_chi(text)

    # Dialogue
    cm_text = ''
    m_cm = re.search(r'\ncase_meaning:\s*\n(.*)', text, re.DOTALL)
    if m_cm:
        cm_text = m_cm.group(1)

    querent_lines = []
    if 'querent_replies:' in cm_text:
        part = cm_text.split('querent_replies:')[1].split('requires_dialog:')[0]
        for l in part.split('\n'):
            if l.strip().startswith('-'):
                cl = clean_ste(l.strip().lstrip('- ').strip(), 16)
                if cl and not re.search(r'\b(the|client|diviner|inquiry|context)\b', cl, re.I):
                    querent_lines.append(cl)
    if not querent_lines:
        for prefix in ['Hỏi:', 'Chiếm:', 'Xem:', 'Vấn:', 'xem ', 'hỏi ']:
            for line in text.split('\n'):
                if prefix in line and not line.startswith('#'):
                    m_val = line.split(prefix, 1)[1].strip()
                    # Clean up trailing punctuation / hexagram name
                    m_val = re.split(r'[,;\.\?]|\s+được quẻ', m_val)[0].strip()
                    if m_val:
                        querent_lines.append(clean_ste(m_val, 16))
                        break
            if querent_lines:
                break
    querent_summary = querent_lines[0] if querent_lines else "Thân chủ hỏi sự việc thực tế, cầu cát hung."

    da_hac_lines = []
    lines_list = text.split('\n')
    prefixes_dh = ['Dã Hạc luận:', 'Dã Hạc nói:', 'Dã Hạc bảo:', 'Ta nói:', 'Dã Hạc:']
    for idx, line in enumerate(lines_list):
        clean_l = line.replace('*', '').replace('#', '').strip()
        for prefix in prefixes_dh:
            if prefix.lower() in clean_l.lower():
                m_pos = re.search(re.escape(prefix), clean_l, re.IGNORECASE)
                if m_pos:
                    rest = clean_l[m_pos.end():].strip()
                    if rest:
                        da_hac_lines.append(rest)
                    else:
                        for nxt_idx in range(idx + 1, min(idx + 6, len(lines_list))):
                            nxt = lines_list[nxt_idx].strip()
                            if nxt and not nxt.startswith('#') and not nxt.startswith('---') and not nxt.startswith('|'):
                                da_hac_lines.append(nxt)
                                break
                break
        if da_hac_lines:
            break
    da_hac_summary = clean_ste(" ".join(da_hac_lines).strip(), 18)
    if not da_hac_summary:
        da_hac_summary = "Dã Hạc phân tích tương quan Thế Ứng và Dụng thần."

    # Dung Than
    dung_than = "Dụng thần theo sự việc"
    for prefix in ['Dụng Thần:', 'Dụng thần:', 'Chọn Dụng thần:', 'Lấy làm Dụng thần:']:
        for line in text.split('\n'):
            if prefix in line:
                dt = line.split(prefix, 1)[1].strip()
                if dt:
                    dung_than = clean_ste(dt, 12)
                    break
        if dung_than != "Dụng thần theo sự việc":
            break
    if not dung_than:
        dung_than = "Dụng thần theo sự việc"

    # Mechanism
    mechanism = "Hào động tác dụng trực tiếp đến Dụng thần và Thế hào."
    for prefix in ['Cơ chế:', 'Nguyên lý:', 'Lý giải:', 'Đoán rằng:']:
        for line in text.split('\n'):
            if prefix in line:
                val = line.split(prefix, 1)[1].strip()
                if val:
                    mechanism = clean_ste(val, 18)
                    break
        if mechanism != "Hào động tác dụng trực tiếp đến Dụng thần và Thế hào.":
            break
    if not mechanism:
        mechanism = "Hào động tác dụng trực tiếp đến Dụng thần và Thế hào."

    # Outcome
    outcome = "Sự việc ứng nghiệm đúng theo quẻ báo."
    for prefix in ['Nghiệm chứng:', 'Quả nhiên:', 'Ứng nghiệm:', 'Kết quả:']:
        for line in text.split('\n'):
            if prefix in line:
                res = line.split(prefix, 1)[1].strip()
                if res:
                    outcome = clean_ste(res, 18)
                    break
        if outcome != "Sự việc ứng nghiệm đúng theo quẻ báo.":
            break
    if not outcome:
        outcome = "Sự việc ứng nghiệm đúng theo quẻ báo."

    # Audit verdict
    mismatch = mismatches_map.get(cfile)
    if mismatch:
        count = mismatch.get('mismatch_count', 1)
        audit_verdict = f"Lệch {count} điểm nạp giáp"
    else:
        audit_verdict = "PASS"

    table = extract_table(text)
    if not table:
        table = "(Dẫn chứng lý thuyết nguyên tắc - không lập bảng lục hào)"

    return {
        "file": cfile,
        "original_file": orig_file,
        "can_chi": can_chi,
        "querent": querent_summary,
        "da_hac": da_hac_summary,
        "dung_than": dung_than,
        "mechanism": mechanism,
        "outcome": outcome,
        "audit_verdict": audit_verdict,
        "table": table
    }

def get_chapter_title(orig_file):
    if not orig_file:
        return "Chương bổ sung"
    full_path = os.path.join(VOLUMES_DIR, orig_file)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                l = line.strip()
                if l.startswith('# '):
                    return l.lstrip('# ').strip()
    # Fallback to filename
    base = os.path.basename(orig_file).replace('.md', '').replace('_', ' ')
    return base

def build_case_node(card):
    cfile = card['file']
    can_chi = card['can_chi']
    title = cfile.replace('.md', '').replace('vd_', 'Ví dụ ').replace('_', ' ')
    
    node = f"### {title}: {can_chi}\n\n"
    node += f"- 💬 **Diễn biến vấn đáp**:\n"
    node += f"  - **Thân chủ**: {card['querent']}\n"
    node += f"  - **Dã Hạc**: {card['da_hac']}\n"
    node += f"- ⚙️ **Quẻ lý & Nghiệm chứng**:\n"
    if card.get('table'):
        if '|' in card['table']:
            indented = "\n".join(["    " + l for l in card['table'].split('\n')])
            node += f"  - **Bảng quẻ**:\n{indented}\n"
        else:
            node += f"  - **Bảng quẻ**: {card['table']}\n"
    node += f"  - **Dụng thần**: {card['dung_than']}\n"
    node += f"  - **Cơ chế luận**: {card['mechanism']}\n"
    node += f"  - **Nghiệm chứng**: {card['outcome']}\n"
    node += f"  - **Kiểm toán nạp giáp**: {card['audit_verdict']}\n\n"
    return node

def process_volume(vol_id):
    print(f"=== BẮT ĐẦU XỬ LÝ {vol_id.upper()} ===")
    
    # 1. Load mismatches
    with open(MISMATCHES_FILE, 'r', encoding='utf-8') as f:
        mismatches_data = json.load(f)
    mismatches_map = {m['file']: m for m in mismatches_data.get('mismatches', [])}

    # 2. Collect case files
    case_files = sorted(glob.glob(os.path.join(CASES_DIR, f"*{vol_id}*.md")))
    print(f"Tìm thấy {len(case_files)} ca ví dụ cho {vol_id}.")

    # 3. Parse all cases
    cards = []
    cards_by_orig = {}
    for cp in case_files:
        card = parse_case(cp, mismatches_map)
        cards.append(card)
        cards_by_orig.setdefault(card['original_file'], []).append(card)

    pass_count = sum(1 for c in cards if c['audit_verdict'] == 'PASS')
    mismatch_count = len(cards) - pass_count
    print(f"Đối soát: {pass_count} PASS, {mismatch_count} Lệch điểm nạp giáp.")

    # Save cards JSON
    cards_file = os.path.join(SCRATCH_DIR, f"{vol_id}_cards.json")
    with open(cards_file, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu thẻ kỹ thuật tại: {cards_file}")

    # 4. Inject into branches md
    md_file = os.path.join(SCRATCH_DIR, f"{vol_id}_branches.md")
    if not os.path.exists(md_file):
        print(f"Lỗi: Không tìm thấy {md_file}")
        return False

    # Read base md (strip any previous injection if re-running)
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # If already injected, strip out previous injected sections
    clean_lines = []
    skipping = False
    for line in content.split('\n'):
        if '### 📚 Các ca ví dụ thực tế nghiệm chứng' in line:
            skipping = True
            continue
        if skipping and (line.startswith('## ') or line.startswith('# ')):
            skipping = False
        if not skipping:
            clean_lines.append(line)
    content = "\n".join(clean_lines)

    # Normalize missing chapter landmarks if needed for vol02
    if vol_id == 'vol02':
        # Remove any trailing orphan chapter headings at EOF
        content = re.sub(r'\n+## Chương XXII\b[^\n]*', '', content)
        content = re.sub(r'\n+## Chương XXVII\b[^\n]*\s*$', '', content)
        if not re.search(r'##\s+Chương\s+XXII\b', content):
            content = content.replace('### 1. Định nghĩa và Bản chất của Âm động', '## Chương XXII: Lý luận về Âm động trong Lục hào\n\n### 1. Định nghĩa và Bản chất của Âm động')
        if not re.search(r'##\s+Chương\s+XXVII\b', content):
            content = content.replace('### 1. Định nghĩa và đặc điểm của Nhật kiến', '## Chương XXVII: Công năng tác dụng của Nhật kiến\n\n### 1. Định nghĩa và đặc điểm của Nhật kiến')

    # Normalize missing chapter landmarks if needed for vol03
    if vol_id == 'vol03':
        for num in ['XXIX', 'XXX', 'XXXI', 'XXXIII', 'XXXIV']:
            content = re.sub(rf'\n+## Chương {num}\b[^\n]*', '', content)
        if not re.search(r'##\s+Chương\s+XXIX\b', content):
            content = content.replace('### I. Khái niệm cơ bản và Bản chất của Lục xung', '## Chương XXIX: Lý luận về Lục xung\n\n### I. Khái niệm cơ bản và Bản chất của Lục xung')
        if not re.search(r'##\s+Chương\s+XXX\b', content):
            content = content.replace('### Khái luận về Lục hợp và vấn đề Hợp hóa', '## Chương XXX: Lý luận về Lục hợp\n\n### Khái luận về Lục hợp và vấn đề Hợp hóa')
        if not re.search(r'##\s+Chương\s+XXXI\b', content):
            content = content.replace('### 1. Bản chất và phân loại Lục xung, Lục hợp hóa lẫn nhau', '## Chương XXXI: Lục xung, Lục hợp hóa lẫn nhau\n\n### 1. Bản chất và phân loại Lục xung, Lục hợp hóa lẫn nhau')
        if not re.search(r'##\s+Chương\s+XXXIII\b', content):
            content = content.replace('### I. Định nghĩa thực dụng của 12 cung Trường sinh', '## Chương XXXIII: Lý luận 12 cung Trường sinh\n\n### I. Định nghĩa thực dụng của 12 cung Trường sinh')
        if not re.search(r'##\s+Chương\s+XXXIV\b', content):
            content = content.replace('### Khái luận về Hóa tiến, Hóa thoái', '## Chương XXXIV: Lý luận về Hóa tiến, Hóa thoái\n\n### Khái luận về Hóa tiến, Hóa thoái')

    # Normalize missing chapter landmarks if needed for vol04
    if vol_id == 'vol04':
        for num in ['XXXVII', 'XXXVIII', 'XXXIX', 'XL', '37', '38', '39', '40']:
            content = re.sub(rf'\n+## Chương {num}\b[^\n]*', '', content)
        if not re.search(r'##\s+Chương\s+(?:XXXVII|37)\b', content):
            content = content.replace('### 1. Khái niệm và Bản chất của Phản ngâm', '## Chương XXXVII: Phản ngâm ứng dụng lý luận\n\n### 1. Khái niệm và Bản chất của Phản ngâm')
        if not re.search(r'##\s+Chương\s+(?:XXXVIII|38)\b', content):
            content = content.replace('### 1. Định nghĩa và bản chất của Phục ngâm', '## Chương XXXVIII: Phục ngâm lý luận ứng dụng\n\n### 1. Định nghĩa và bản chất của Phục ngâm')
        if not re.search(r'##\s+Chương\s+(?:XXXIX|39)\b', content):
            content = content.replace('### 1. Khái niệm cơ bản về Hào phục và Tàng hào', '## Chương XXXIX: Tàng phục lý luận ứng dụng\n\n### 1. Khái niệm cơ bản về Hào phục và Tàng hào')
        if not re.search(r'##\s+Chương\s+(?:XL|40)\b', content):
            content = content.replace('### I. Khái quát về Ứng kỳ trong Hệ thống Cổ Phệ', '## Chương XL: Công thức quy nạp ứng kỳ lý luận\n\n### I. Khái quát về Ứng kỳ trong Hệ thống Cổ Phệ')

    # Roman to Arabic and Arabic to Roman conversion tables
    ROMAN_MAP = {
        '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V', '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X',
        '11': 'XI', '12': 'XII', '13': 'XIII', '14': 'XIV', '15': 'XV', '16': 'XVI', '17': 'XVII', '18': 'XVIII', '19': 'XIX', '20': 'XX',
        '21': 'XXI', '22': 'XXII', '23': 'XXIII', '24': 'XXIV', '25': 'XXV', '26': 'XXVI', '27': 'XXVII', '28': 'XXVIII', '29': 'XXIX', '30': 'XXX',
        '31': 'XXXI', '32': 'XXXII', '33': 'XXXIII', '34': 'XXXIV', '35': 'XXXV', '36': 'XXXVI', '37': 'XXXVII', '38': 'XXXVIII', '39': 'XXXIX', '40': 'XL',
        '41': 'XLI', '42': 'XLII', '43': 'XLIII', '44': 'XLIV', '45': 'XLV', '46': 'XLVI', '47': 'XLVII', '48': 'XLVIII', '49': 'XLIX', '50': 'L',
        '51': 'LI', '52': 'LII', '53': 'LIII', '54': 'LIV', '55': 'LV', '56': 'LVI', '57': 'LVII'
    }
    REV_ROMAN = {v: k for k, v in ROMAN_MAP.items()}

    # Group and inject by chapter
    for orig_file, ch_cards in cards_by_orig.items():
        ch_title = get_chapter_title(orig_file)
        
        # Build text
        ex_text = f"\n### 📚 Các ca ví dụ thực tế nghiệm chứng ({len(ch_cards)} ca)\n\n"
        for card in ch_cards:
            ex_text += build_case_node(card)

        # Match chapter title or roman/arabic numeral in content
        m_num = re.search(r'chuong_([a-z0-9]+)', orig_file, re.IGNORECASE)
        heading_found = False
        if m_num:
            raw_str = m_num.group(1).upper()
            patterns_to_try = [raw_str]
            if raw_str in ROMAN_MAP:
                patterns_to_try.append(ROMAN_MAP[raw_str])
            if raw_str in REV_ROMAN:
                patterns_to_try.append(REV_ROMAN[raw_str])
            
            pattern_regex = '|'.join(patterns_to_try)
            pattern = rf'##\s+[^\n]*Chương\s+(?:{pattern_regex})\b[^\n]*\n'
            m = re.search(pattern, content, re.IGNORECASE)
            if m:
                pos = m.end()
                next_h = re.search(r'\n##\s+', content[pos:])
                insert_pos = pos + next_h.start() if next_h else len(content)
                content = content[:insert_pos] + "\n" + ex_text + content[insert_pos:]
                heading_found = True

        if not heading_found:
            # Check for Chu Thần Bân
            if 'chu_than' in orig_file.lower():
                m_ctb = re.search(r'##\s+Chu\s+Thần\s+B[aâ]n[^\n]*\n', content, re.IGNORECASE)
                if m_ctb:
                    pos = m_ctb.end()
                    next_h = re.search(r'\n##\s+', content[pos:])
                    insert_pos = pos + next_h.start() if next_h else len(content)
                    content = content[:insert_pos] + "\n" + ex_text + content[insert_pos:]
                    heading_found = True

        if not heading_found:
            # Append new chapter section
            new_section = f"\n## {ch_title}\n\n" + ex_text
            content = content + "\n" + new_section

    # Write updated markdown
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Đã cập nhật {md_file} ({len(content)} bytes).")

    # 5. Compile mindmap HTML
    html_file = os.path.join(SCRATCH_DIR, f"{vol_id}_branches.html")
    print(f"Biên dịch {html_file} bằng {COMPILER_JS}...")
    cmd = ["node", COMPILER_JS, md_file, html_file]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    print(res.stdout)
    if res.stderr:
        print("Compile stderr:", res.stderr)

    if os.path.exists(html_file):
        sz = os.path.getsize(html_file) / 1024
        print(f"HOÀN THÀNH: {html_file} ({sz:.1f} KB)")
        return {
            "volume": vol_id,
            "total_cases": len(cards),
            "pass_count": pass_count,
            "mismatch_count": mismatch_count,
            "md_bytes": len(content),
            "html_kb": sz,
            "success": True
        }
    return {"volume": vol_id, "success": False}

if __name__ == "__main__":
    vol = sys.argv[1] if len(sys.argv) > 1 else "vol01"
    process_volume(vol)
