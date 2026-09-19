# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm VNU RAG
**Thành viên:** Nguyễn Phúc Bảo - 2A202602925, Nguyễn Viết Dũng - 2A20262533, Nguyễn Văn Biển - 2A202602416
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân nộp trong `REPORT_CANHAN.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ dành cho sinh viên tại Đại học Quốc gia Hà Nội (ĐHQGHN).

**Tại sao nhóm chọn chủ đề này?**

Nhóm chọn các quy định/hướng dẫn đào tạo, học bổng và công tác sinh viên công khai. Corpus được crawler tải vào `data/vnu/` sau khi kiểm tra `robots.txt`; năm văn bản PDF công khai được trích bằng `pdftotext`, ba trang HTML được giữ làm nguồn bổ sung. Mỗi câu trả lời chuẩn chỉ dùng dữ kiện có mặt trong tài liệu đã tải.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---:|---|
| 1 | Quy định quản lý và sử dụng học bổng ĐHQGHN (PDF) | https://ussh.vnu.edu.vn/uploads/ussh/van-ban/qd4618cong-tac-qua-ly-va-su-dung-hoc-bong-tai-dhqghn.pdf | 2026-09-19 / 2024-10-07 | 22,548 | `audience=student`, `department=student-affairs`, `category=scholarship`, `language=vi` |
| 2 | Quy chế đào tạo đại học ĐHQGHN (PDF) | https://daotao.ulis.vnu.edu.vn/files/uploads/2023/02/3626_21.10.2022.-Quy-ch%E1%BA%BF-%C4%91%C3%A0o-t%E1%BA%A1o-%C4%91%E1%BA%A1i-h%E1%BB%8Dc-t%E1%BA%A1i-%C4%90HQGHN-%C3%A1p-d%E1%BB%A5ng-t%E1%BB%AB-kh%C3%B3a-QH2022.pdf | 2026-09-19 / 2022-10-21 | 104,070 | `audience=student`, `department=academic-affairs`, `category=regulation`, `language=vi` |
| 3 | Hướng dẫn quy chế đào tạo Tiến sĩ (PDF) | https://saudaihoc.ulis.vnu.edu.vn/files/uploads/2023/11/QD-1418-HD-thuc-hien-Quy-che-dao-tao-Tien-si-tu-khoa-QH2022.pdf | 2026-09-19 / 2023-11 | 24,347 | `audience=all`, `study_level=graduate`, `department=graduate-affairs`, `category=guidance`, `language=vi` |
| 4 | Hướng dẫn quy chế đào tạo Thạc sĩ (PDF) | https://saudaihoc.ulis.vnu.edu.vn/files/uploads/2023/11/QD-1419-HD-thuc-hien-Quy-che-dao-tao-Th%E1%BA%A1c-si-tu-khoa-QH2022-1.pdf | 2026-09-19 / 2023-11 | 21,343 | `audience=all`, `study_level=graduate`, `department=graduate-affairs`, `category=guidance`, `language=vi` |
| 5 | Quy chế đào tạo sau đại học theo QĐ 1555 (PDF) | https://saudaihoc.ulis.vnu.edu.vn/files/uploads/2016/12/QD-1555-Quy-che-dao-tao-SDH-o-DHQG-HN-ngay-25-05-2011-ap-dung-tu-nam-tuyen-sinh-2011.pdf | 2026-09-19 / 2011-05-25 | 187,466 | `audience=all`, `study_level=graduate`, `department=graduate-affairs`, `category=regulation`, `language=vi` |
| 6 | Danh mục quy định HUS-VNU (HTML) | https://hus.vnu.edu.vn/tai-lieu-bieu-mau/quy-dinh-quy-che | 2026-09-19 / not-stated | 1,720 | `audience=all`, `department=academic-affairs`, `category=regulations-directory`, `language=vi` |
| 7 | Quy chế công tác sinh viên (HTML) | https://sim.ussh.vnu.edu.vn/vi/download/Dao-tao-dai-hoc-Chung/Quy-che-Cong-tac-Hoc-sinh-Sinh-vien-cua-DHQGHN-2017.html | 2026-09-19 / 2017-01-05 | 1,874 | `audience=student`, `department=student-affairs`, `category=student-regulation`, `language=vi` |
| 8 | Danh mục hướng dẫn đào tạo đại học (HTML) | https://www.education.vnu.edu.vn/dao-tao/dao-tao-dai-hoc/van-ban-huong-dan-dao-tao-dai-hoc/ | 2026-09-19 / not-stated | 30,416 | `audience=student`, `department=academic-affairs`, `category=training-guidance`, `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu:**
- [x] Corpus chỉ có nguồn công khai; không có dữ liệu cá nhân, thông tin đăng nhập hay nội dung nội bộ.
- [x] Mỗi file có `source_url`, `retrieved_at`, `document_version` trong metadata; manifest ở `data/vnu/sources.csv`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| `doc_id` | string | `vnu-scholarship-regulation-2024` | Truy vết chunk về tài liệu nguồn. |
| `source_url` | URL | URL văn bản ĐHQGHN | Kiểm chứng gold answer. |
| `retrieved_at` | date | `2026-09-19` | Biết thời điểm lấy dữ liệu. |
| `document_version` | string/date | `2024-10-06` | Phân biệt phiên bản/ngày hiệu lực. |
| `audience` | enum | `student`, `faculty`, `staff`, `all` | Lọc tài liệu theo người dùng; chỉ dùng các giá trị rubric cho phép. |
| `study_level` | enum | `undergraduate`, `graduate` | Lọc riêng bậc đào tạo mà không làm sai enum `audience`. |
| `department`, `category` | string | `student-affairs`, `scholarship` | Giảm nhiễu theo dịch vụ/chủ đề. |
| `language` | string | `vi` | Hỗ trợ corpus đa ngôn ngữ sau này. |

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=250)` trên hai tài liệu đã crawl:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---:|---:|---|
| Quy định học bổng | Fixed size | 42 | 246.2 | Trung bình, có thể cắt nhãn/giá trị. |
| Quy định học bổng | Sentence | 2 | 4142.5 | Quá dài vì HTML ít dấu kết câu rõ. |
| Quy định học bổng | Recursive | 43 | 190.8 | Tốt hơn fixed ở ranh giới newline. |
| Hướng dẫn đào tạo | Fixed size | 152 | 249.8 | Nhiều chunk do trang dài. |
| Hướng dẫn đào tạo | Sentence | 13 | 2330.5 | Quá dài, không phù hợp retrieval. |
| Hướng dẫn đào tạo | Recursive | 153 | 193.2 | Có đoạn nhỏ hơn nhưng vẫn nhiễu menu HTML. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Phúc Bảo**
- **Loại chiến lược:** Chunk theo trang/heading + TF-IDF lexical retrieval.
- **Mô tả & lý do chọn cho chủ đề này:** Mỗi trang được xem như một section để không cắt rời metadata và thông tin định danh; phù hợp baseline trên 5 trang hiện tại.
- **Code snippet (nếu custom):** `chunk_by_heading()` trong `scripts/run_vinuni_benchmark.py`.

**Thành viên 2 — Nguyễn Viết Dũng**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=250, overlap=50)` + TF-IDF.
- **Mô tả & lý do chọn:** So sánh tác động của overlap khi tài liệu dài; 1,644 chunk trong lần chạy benchmark.
- **Code snippet (nếu custom):** Không áp dụng; dùng class có sẵn.

**Thành viên 3 — Nguyễn Văn Biển**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=250)` + TF-IDF.
- **Mô tả & lý do chọn:** Ưu tiên paragraph/newline; 214 chunk trong lần chạy benchmark.
- **Code snippet (nếu custom):** Không áp dụng; dùng class có sẵn.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| Nguyễn Phúc Bảo | Heading/section | 8 / 10 | 59 chunk, 5/5 tài liệu nguồn liên quan trong Top-3. | Câu #2 chưa lấy đúng điều khoản ở Top-3. |
| Nguyễn Viết Dũng | Fixed + overlap | 6 / 10 | Có overlap, bảo toàn ranh giới cắt nhỏ. | 1,644 chunk; câu #2 và #4 mất tài liệu nguồn trong Top-3. |
| Nguyễn Văn Biển | Recursive | 8 / 10 | 2,070 chunk; 5/5 tài liệu nguồn liên quan trong Top-3. | Độ phân mảnh cao và nhiều kết quả chưa chứa đúng câu trả lời. |

**Chiến lược tốt nhất:** heading/section là lựa chọn dễ giải thích nhất trên corpus hiện tại. Với HTML/PDF đã làm sạch, fixed hoặc recursive có thể cho precision top-1 tốt hơn; cần xác nhận lại qua demo của từng thành viên.

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi chung (nguyên văn) | Metadata filter | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|---|
| 1 | Văn bản quy định quản lý và sử dụng học bổng tại ĐHQGHN có số kí hiệu nào? | `{"audience":"student"}` | `4618/QĐ-ĐHQGHN` | `vnu-scholarship-regulation-2024` |
| 2 | Theo quy chế đào tạo ĐHQGHN, sinh viên được rút bớt học phần trong bao lâu kể từ đầu học kỳ chính và học kỳ phụ? | Không | `2 tuần` / `1 tuần` | `vnu-student-training-handbook` |
| 3 | Quyết định 1418/QĐ-ĐHNN ban hành ngày nào? | `{"study_level":"graduate"}` | `22/07/2023` | `vnu-doctoral-training-guidance-1418` |
| 4 | Hướng dẫn thực hiện Quy chế đào tạo Thạc sĩ tại Trường Đại học Ngoại ngữ thay thế quyết định số nào? | `{"study_level":"graduate"}` | `191/QĐ-ĐHNN`, `10/01/2023` | `vnu-masters-training-guidance-1419` |
| 5 | Quy chế đào tạo sau đại học theo Quyết định 1555 áp dụng cho những trình độ đào tạo nào? | `{"study_level":"graduate"}` | `Thạc sĩ và tiến sĩ` | `vnu-graduate-training-regulation-1555` |

### Tổng hợp chất lượng truy xuất của nhóm

> Baseline chạy heading/section trên 5 PDF đã clean, tạo 59 chunk. Ba HTML vẫn lưu trong corpus/manifest để truy vết nhưng không tính vào benchmark vì menu và danh mục làm nhiễu kết quả. Bản semantic OpenAI chưa chạy lại được vì API key hiện trả `401 token_invalidated`; nhóm không dùng số liệu cũ hoặc tự điền kết quả. Theo rubric: 2 điểm/câu khi top-3 có evidence và agent trả lời đúng; 1 điểm khi evidence liên quan nhưng câu trả lời thiếu/không ở top-1; 0 điểm nếu không có evidence trong top-3.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|---|
| 1 | Văn bản quy định quản lý và sử dụng học bổng tại ĐHQGHN có số kí hiệu nào? | Heading/section + filter | Có | Baseline TF-IDF: đúng tài liệu ở top-1, score 0.7662. |
| 2 | Theo quy chế đào tạo ĐHQGHN, sinh viên được rút bớt học phần trong bao lâu kể từ đầu học kỳ chính và học kỳ phụ? | Heading/section | Có | Baseline TF-IDF: đúng tài liệu ở top-1, score 0.7396. |
| 3 | Quyết định 1418/QĐ-ĐHNN ban hành ngày nào? | Heading/section + filter | Có | Tài liệu Tiến sĩ ở top-1, score 0.3166; câu trích chứa ngày 22/07/2023. |
| 4 | Hướng dẫn thực hiện Quy chế đào tạo Thạc sĩ tại Trường Đại học Ngoại ngữ thay thế quyết định số nào? | Heading/section + filter | Có | Đúng tài liệu ở rank 3, agent extractive nêu được đáp án. |
| 5 | Quy chế đào tạo sau đại học theo Quyết định 1555 áp dụng cho những trình độ đào tạo nào? | Heading/section + filter | Có | Đúng tài liệu ở top-1, score 0.6548. |

**Metadata filtering:** Câu 1 dùng `audience=student`, loại tài liệu `audience=all` trước khi xếp hạng. Filter làm giảm nhiễu, nhưng cần gán metadata chính xác để không làm mất evidence.

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> Demo `python3 scripts/run_vnu_benchmark.py --chunking heading`, hiển thị `source_url`, filter `audience`/`study_level` và top-3. So sánh cho thấy fixed/recursive tạo rất nhiều chunk và mất evidence ở một số câu, còn heading dễ truy vết nguồn.

**Bài học rút ra khi so sánh trong nhóm:**
> Heading/section dễ truy vết nguồn; corpus nay có năm PDF sạch nên giảm đáng kể menu/breadcrumb. Baseline TF-IDF lấy được cả năm tài liệu nguồn trong Top-3, nhưng câu #2 chưa đưa đúng điều khoản vào context nên vẫn cần semantic embedding hoặc reranking sau khi key API hợp lệ.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Đã tải PDF đính kèm được phép và chuyển thành Markdown sạch. Lần tiếp theo nhóm sẽ thay key API hợp lệ, chạy semantic benchmark lại và so sánh heading với sentence-based (gợi ý từ phân tích corpus).

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
