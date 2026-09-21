import sys, os, json, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

CASES_DIR = r'C:\Users\Admin\Downloads\antgravity workplace\coboc_output\cases'
MISMATCHES_FILE = r'C:\Users\Admin\Downloads\antgravity workplace\coboc_output\tool_mismatches.json'
MANIFEST_FILE = r'C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches\vol01_manifest.json'
OUTPUT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\c-b-c-branches\vol01_workers'

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

def process_worker(worker_id):
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    worker_info = next((w for w in manifest if w['worker_id'] == worker_id), None)
    if not worker_info:
        print(f"Worker {worker_id} not found in manifest!")
        return False
        
    with open(MISMATCHES_FILE, 'r', encoding='utf-8') as f:
        mismatches_data = json.load(f)
    mismatch_by_file = {m['file']: m for m in mismatches_data.get('mismatches', [])}
    
    results = []
    for cfile in worker_info['cases']:
        cpath = os.path.join(CASES_DIR, cfile)
        with open(cpath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        can_chi = extract_can_chi(text)
        
        cm_text = ''
        m_cm = re.search(r'\ncase_meaning:\s*\n(.*)', text, re.DOTALL)
        if m_cm:
            cm_text = m_cm.group(1)
            
        # Dialogues
        author_q = []
        querent_r = []
        if 'author_questions:' in cm_text:
            author_part = cm_text.split('author_questions:')[1].split('querent_replies:')[0]
            author_q = [clean_ste(line.strip().lstrip('- ').strip(), 16) for line in author_part.split('\n') if line.strip().startswith('-') and clean_ste(line.strip().lstrip('- ').strip(), 16)]
        if 'querent_replies:' in cm_text:
            querent_part = cm_text.split('querent_replies:')[1].split('requires_dialog:')[0]
            querent_r = [clean_ste(line.strip().lstrip('- ').strip(), 16) for line in querent_part.split('\n') if line.strip().startswith('-') and clean_ste(line.strip().lstrip('- ').strip(), 16)]
            
        da_hac_lines = []
        for line in text.split('\n'):
            for prefix in ['Dã Hạc luận:', 'Dã Hạc nói:', 'Dã Hạc bảo:', 'Ta nói:']:
                if prefix in line:
                    da_hac_lines.append(line.split(prefix, 1)[1].strip())
        da_hac_summary = clean_ste(" ".join(da_hac_lines).strip(), 18)
        
        querent_str = " ".join(querent_r) if querent_r else "Thân chủ hỏi sự việc thực tế, lo lắng cầu cát hung."
        da_hac_str = " ".join(author_q) if author_q else (da_hac_summary or "Dã Hạc phân tích tương quan Thế Ứng và Dụng thần.")
        
        # Dung than
        m_dt = re.search(r'first_principles_invoked:\s*([^\n]+)', cm_text)
        dung_than = clean_ste(m_dt.group(1).strip(), 14) if m_dt else "Chọn hào trì Thế hoặc có hào động phát động"
        
        lessons = []
        for m in re.finditer(r'first_principle_axiom:\s*([^\n]+)', cm_text):
            cl = clean_ste(m.group(1).strip(), 16)
            if cl:
                lessons.append(cl)
        mechanism = lessons[0] if lessons else "Cát hung xác lập theo sinh khắc của hào động."
        
        outcome = ''
        m_qua = re.search(r'((?:Quả|Kết quả|Quả nhiên)\s+[^。\.\n]+[\.\n])', text)
        if m_qua:
            outcome = clean_ste(m_qua.group(1).strip(), 18)
        else:
            outcome = da_hac_summary or "Sự việc ứng nghiệm đúng theo quẻ báo."
            
        mismatch = mismatch_by_file.get(cfile)
        audit_verdict = "PASS" if not mismatch else f"Lệch {len(mismatch.get('inaccuracies', []))} điểm nạp giáp"
        
        results.append({
            'file': cfile,
            'can_chi': can_chi,
            'querent': querent_str,
            'da_hac': da_hac_str,
            'dung_than': dung_than,
            'mechanism': mechanism,
            'outcome': outcome,
            'audit_verdict': audit_verdict
        })
        
    out_file = os.path.join(OUTPUT_DIR, f"{worker_id}.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Worker {worker_id} processed {len(results)} cases -> {out_file}")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        wid = sys.argv[1]
        process_worker(wid)
    else:
        print("Usage: python run_worker.py <worker_id>")
