# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 2A (K4-L3A)
**Thành viên:** Nguyễn Phúc Bảo - 2A202602925, Nguyễn Viết Dũng - 2A20262533, Nguyễn Văn Biển - 2A202602416
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân nộp trong `REPORT_CANHAN.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ dành cho sinh viên tại Đại học Quốc gia Hà Nội (ĐHQGHN).

**Tại sao nhóm chọn chủ đề này?**

Nhóm chọn các trang quy định/hướng dẫn đào tạo, học bổng và công tác sinh viên công khai. Corpus được crawler tải vào `data/vnu/` sau khi kiểm tra `robots.txt`; mỗi câu trả lời chuẩn bên dưới chỉ dùng dữ kiện có mặt trong HTML đã tải, không suy diễn nội dung PDF đính kèm.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---:|---|
| 1 | Danh mục quy định và quy chế HUS-VNU | https://hus.vnu.edu.vn/tai-lieu-bieu-mau/quy-dinh-quy-che | 2026-09-19 / not-stated | 2,261 | `audience=all`, `department=academic-affairs`, `category=regulations-directory`, `language=vi` |
| 2 | Quy định quản lý và sử dụng học bổng ĐHQGHN | https://ussh.vnu.edu.vn/vi/van-ban/detail/Quy-dinh-ve-cong-tac-quan-ly-va-su-dung-hoc-bong-tai-Dai-hoc-Quoc-gia-Ha-Noi-19468/ | 2026-09-19 / 2024-10-06 | 10,561 | `audience=student`, `department=student-affairs`, `category=scholarship`, `language=vi` |
| 3 | Quy chế công tác sinh viên ĐHQGHN | https://sim.ussh.vnu.edu.vn/vi/download/Dao-tao-dai-hoc-Chung/Quy-che-Cong-tac-Hoc-sinh-Sinh-vien-cua-DHQGHN-2017.html | 2026-09-19 / 2017-01-05 | 2,204 | `audience=student`, `department=student-affairs`, `category=student-regulation`, `language=vi` |
| 4 | Tài liệu tập huấn quy chế đào tạo | https://student.ulis.vnu.edu.vn/tai-lieu-tap-huan-quy-che-dao-tao-dai-hoc-tai-dhqghn-danh-cho-sinh-vien-2/ | 2026-09-19 / not-stated | 2,650 | `audience=student`, `department=academic-affairs`, `category=student-guidance`, `language=vi` |
| 5 | Văn bản hướng dẫn đào tạo đại học | https://www.education.vnu.edu.vn/dao-tao/dao-tao-dai-hoc/van-ban-huong-dan-dao-tao-dai-hoc/ | 2026-09-19 / not-stated | 41,271 | `audience=student`, `department=academic-affairs`, `category=training-guidance`, `language=vi` |

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
| `audience` | enum | `student`, `all` | Lọc tài liệu theo người dùng. |
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
- **Mô tả & lý do chọn:** So sánh tác động của overlap khi trang HTML dài; 215 chunk trong lần chạy benchmark.
- **Code snippet (nếu custom):** Không áp dụng; dùng class có sẵn.

**Thành viên 3 — Nguyễn Văn Biển**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=250)` + TF-IDF.
- **Mô tả & lý do chọn:** Ưu tiên paragraph/newline; 214 chunk trong lần chạy benchmark.
- **Code snippet (nếu custom):** Không áp dụng; dùng class có sẵn.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| Nguyễn Phúc Bảo | Heading/section | 7 / 10 | Ít chunk, dễ truy vết nguồn. | Trang danh mục có thể nhiễu lexical. |
| Nguyễn Viết Dũng | Fixed + overlap | 7 / 10 | Tìm được đoạn nhỏ trong trang dài. | HTML menu tạo nhiều chunk không liên quan. |
| Nguyễn Văn Biển | Recursive | 6 / 10 | Tôn trọng newline/paragraph. | Chưa xử lý được HTML thô. |

**Chiến lược tốt nhất:** heading/section là lựa chọn dễ giải thích nhất trên corpus hiện tại. Với HTML/PDF đã làm sạch, fixed hoặc recursive có thể cho precision top-1 tốt hơn; cần xác nhận lại qua demo của từng thành viên.

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| 1 | Số kí hiệu quy định học bổng ĐHQGHN? `metadata_filter={"audience":"student"}` | `4618/QĐ-ĐHQGHN` | `vnu-scholarship-regulation-2024` |
| 2 | Quy định học bổng bắt đầu hiệu lực ngày nào? | `07/10/2024` | `vnu-scholarship-regulation-2024` |
| 3 | Hạn làm bài kiểm tra tài liệu tập huấn quy chế? | `28/02/2023` | `vnu-student-training-handbook` |
| 4 | Mã văn bản hướng dẫn khóa luận nhóm ngoài sư phạm? | `3002/HD-ĐHGD` | `vnu-undergraduate-guidance-directory` |
| 5 | Danh mục HUS-VNU có nhóm đào tạo nào? | `Đào tạo`, gồm `Đại học` và `Sau đại học` | `vnu-regulations-directory` |

### Tổng hợp chất lượng truy xuất của nhóm

> Lần chạy semantic dùng `text-embedding-3-small` qua OpenAI, heading/section có giới hạn 6,000 ký tự để không vượt context window. Corpus tạo 11 chunk từ 5 tài liệu. Theo rubric: 2 điểm/câu khi top-3 có evidence và agent trả lời đúng; 1 điểm khi evidence liên quan nhưng câu trả lời thiếu/không ở top-1; 0 điểm nếu không có evidence trong top-3.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|---|
| 1 | Số kí hiệu quy định học bổng | Heading/section + filter | Có, top-1 | `vnu-scholarship-regulation-2024`, score 0.4963. |
| 2 | Ngày hiệu lực quy định học bổng | Heading/section | Có, rank 2 | Văn bản học bổng ở rank 2, score top-1 0.4848. |
| 3 | Hạn làm bài kiểm tra | Heading/section | Có, top-1 | `vnu-student-training-handbook`, score 0.6042. |
| 4 | Mã văn bản khóa luận | Heading/section | Có, top-3 | Hai chunk đầu thuộc trang hướng dẫn, score top-1 0.5047. |
| 5 | Nhóm đào tạo HUS-VNU | Heading/section | Không | Failure case: top-3 bị nhiễu bởi trang hướng dẫn HTML, score top-1 0.6179. |

**Metadata filtering:** Câu 1 dùng `audience=student`, loại tài liệu `audience=all` trước khi xếp hạng. Filter làm giảm nhiễu, nhưng cần gán metadata chính xác để không làm mất evidence.

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> Demo `python3 scripts/run_vnu_benchmark.py --chunking heading`, hiển thị `source_url`, filter `audience` và top-3. Failure case câu 5 cho thấy lexical retrieval bị nhiễu bởi từ chung như “ĐHQGHN” và “đào tạo”.

**Bài học rút ra khi so sánh trong nhóm:**
> Heading/section dễ truy vết nguồn trên corpus hiện tại, nhưng semantic embedding vẫn thất bại ở câu 5 vì HTML menu/breadcrumb và trang danh mục không có nội dung đủ sạch. Fixed và recursive sẽ còn tạo nhiều chunk nhiễu hơn nếu chưa làm sạch HTML.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Tải PDF đính kèm được phép, chuyển thành Markdown sạch rồi benchmark lại; không dùng tóm tắt AI thay cho nội dung nguồn.

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **37 / 40** |
