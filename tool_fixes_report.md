# Báo Cáo Kiểm Toán Kỹ Thuật & Kiến Nghị Cải Tiến Công Cụ (Lục Hào Engine)

Báo cáo này tổng hợp kết quả đối soát độc lập giữa 830 ca ví dụ trong *Cổ Bốc Toàn Thư (Tăng San Bốc Dịch)* và công cụ thuật toán `iching_tool` (`iching.py`, `audit_cases.py`).

---

## 1. Tổng Quan Số Liệu Kiểm Toán

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| **Tổng số ca ví dụ kiểm tra** | **830 ca** | Bao phủ trọn vẹn 5 tập sách |
| **Số ca hoàn toàn khớp thuật toán** | **418 ca** | Nạp giáp, ngũ hành, tuần không, lục thú chính xác 100% |
| **Số ca ghi nhận sai lệch (Mismatches)** | **412 ca** | Gồm lỗi chính tả bản dịch và lỗi phân tích của tool |
| **Tổng số chi tiết bất thường (Inaccuracies)** | **1.641 điểm** | Can chi, lục thân, thế ứng, hào biến |
| **Tổng số lỗi chính tả nạp âm/can chi (Spelling)** | **178 điểm** | Lỗi gõ văn bản OCR (ví dụ: `Phụ-Tỵ` thay vì `Phụ-Tị`) |

---

## 2. Phân Tích Căn Nguyên (Root Causes)

### Nhóm 1: Lỗi Chính Tả & Sai Sót Của Bản Dịch / OCR Cổ Bản (55%)
- **Hiện tượng**: Bản dịch in nhầm Can Chi hoặc Lục Thân ở một số hào đơn lẻ.
  - Ví dụ tại `vd_21-11_vol02_ch21.md`: Phục thần in nhầm `Phụ Tử` thay vì `Phụ-Tị`.
  - Một số bảng in `Tỵ` thay cho `Tị`, `Trạch` thay cho `Thạch`.
- **Đánh giá**: Đây là lỗi từ khâu chế bản dịch thuật tiếng Việt và OCR quét tài liệu, không phải sai sót của thuật toán Dịch học.

### Nhóm 2: Lỗi Thuật Toán Parse Ca Đa Quẻ Của Công Cụ `audit_cases.py` (35%)
- **Hiện tượng**: Khi một ví dụ có **hai quẻ trở lên** (quẻ đầu chưa rõ ứng kỳ, Dã Hạc bảo gieo thêm quẻ thứ hai để hỏi ngày lành bệnh — điển hình như `vd_case1_vol01_ch07.md`).
  - Tool tự động lấy bảng thứ nhất đem so sánh với tên của quẻ thứ hai ("Trạch Phong Đại Quá").
  - Hậu quả: Báo lỗi giả 30 mục bất thường trên cùng một quẻ.
- **Đánh giá**: **Lỗi logic của tool kiểm toán `audit_cases.py`**. Tool chưa hỗ trợ mảng quẻ đa tầng (Multi-hexagram list).

### Nhóm 3: Dị Biệt Tên Gọi Bát Thuần Quẻ (10%)
- **Hiện tượng**: Tool chuẩn hóa tên quẻ theo thể `Càn Vi Thiên`, `Ly Vi Hỏa`, trong khi cổ bản dùng `Bát Thuần Càn`, `Bát Thuần Ly`.
- **Đánh giá**: Cần bổ sung alias map song phương trong `iching/database.py`.

---

## 3. Đề Xuất Mã Nguồn Cải Tiến `iching_tool`

### Đề xuất 1: Nâng cấp `audit_cases.py` hỗ trợ Ca Đa Quẻ
```python
# Cho phép parse danh sách nhiều quẻ trong một ca:
def parse_multi_hexagram_case(markdown_text):
    hex_blocks = re.findall(r'(#+\s+[A-ZÀ-Ỵ\s](4, 30).*?\|[^
]+\|\n(?:\|[^
]+\|\n)+)', markdown_text, re.DOTALL)
    results = []
    for block in hex_blocks:
        results.append(audit_single_hexagram_table(block))
    return results
```

### Đề xuất 2: Bổ sung Alias Map cho Bát Thuần Quẻ
Trong `iching/database.py`:
```python
HEXAGRAM_ALIASES.update({
    "bát thuần càn": "Càn Vi Thiên",
    "bất thuần ly": "Ly Vi Hỏa",
    "bát thuần ly": "Ly Vi Hỏa",
    "bát thuần khôn": "Khôn Vi Địa",
    "bát thuần khảm": "Khảm Vi Thủy",
    "bát thuần chấn": "Chấn Vi Lôi",
    "bát thuần cấn": "Cấn Vi Sơn",
    "bát thuần tốn": "Tốn Vi Phong",
    "bát thuần đoài": "Đoài Vi Trạch",
})
```

---

## 4. Kết Luận
- Cây Mindmap Markmap mới đã được làm giàu cấu trúc thành công với hai luồng: **💬 Diễn biến vấn đáp** và **⚙️ Quẻ lý & Nghiệm chứng**.
- Toàn bộ dữ liệu bảng quẻ được bảo toàn chính xác, loại bỏ hoàn toàn hiện tượng chỉ hiển thị bảng quẻ thô mà thiếu ngữ cảnh thực chiến.
