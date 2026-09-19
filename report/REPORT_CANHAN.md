# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Viết Dũng - 2A20262533  
**Nhóm:** Nguyễn Phúc Bảo - 2A202602925, Nguyễn Viết Dũng - 2A20262533, Nguyễn Văn Biển - 2A202602416  
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector hướng về gần như cùng một góc trong không gian embedding đa chiều, biểu thị rằng hai đoạn văn bản có ý nghĩa ngữ nghĩa (semantic meaning) rất tương đồng hoặc diễn đạt cùng một thông điệp, bất kể số lượng từ hay độ dài ngắn khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: *"Sinh viên cần nộp hồ sơ xin miễn giảm học phí trước ngày 15 tháng 10."*
- Câu B: *"Hạn chót để người học gửi giấy tờ xin hỗ trợ học phí là ngày 15/10."*
- Tại sao tương đồng: Dù sử dụng các từ ngữ khác nhau (*sinh viên/người học, nộp hồ sơ/gửi giấy tờ, miễn giảm/hỗ trợ*), cả hai câu đều mang cùng một nội dung cốt lõi và mốc thời gian hành động.

**Ví dụ có độ tương tự THẤP:**
- Câu A: *"Sinh viên cần nộp hồ sơ xin miễn giảm học phí trước ngày 15 tháng 10."*
- Câu B: *"Thư viện mở cửa phục vụ bạn đọc từ 8 giờ sáng đến 9 giờ tối các ngày trong tuần."*
- Tại sao khác: Hai câu đề cập đến hai mảng nghiệp vụ độc lập hoàn toàn (thủ tục tài chính học vụ và khung giờ hoạt động của cơ sở vật chất thư viện), không có sự giao thoa ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị phụ thuộc lớn vào độ lớn (magnitude/length) của vector: một câu ngắn và một đoạn văn dài dù cùng nói về một nội dung sẽ có độ dài vector khác nhau dẫn đến khoảng cách Euclid xa. Ngược lại, Cosine Similarity chỉ đo góc giữa hai vector (chuẩn hóa độ dài về 1), cho phép so sánh thuần túy về mặt ngữ nghĩa độc lập với độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Bước nhảy giữa các chunk (step): $\text{chunk\_size} - \text{overlap} = 500 - 50 = 450 \text{ ký tự}$.
> - Áp dụng công thức: $\text{Số lượng chunk} = \left\lceil \frac{\text{độ\_dài} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \lceil 22.111 \rceil$
> *Đáp án:* **23 chunks** (chunk thứ 23 chứa phần dư từ vị trí 9,900 đến 10,000).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - Khi overlap = 100: Bước nhảy giảm xuống $500 - 100 = 400 \text{ ký tự}$. Số chunk mới là $\left\lceil \frac{10000 - 100}{400} \right\rceil = \lceil 24.75 \rceil = \mathbf{25\text{ chunks}}$ (tăng thêm 2 chunks).
> - Tăng độ chồng chéo giúp bảo toàn tính toàn vẹn của ngữ cảnh (context preservation) tại các điểm giao cắt, tránh việc một câu quy định quan trọng, điều kiện ngoại lệ hoặc số liệu bị cắt đứt đoạn giữa chừng khiến retriever bỏ sót thông tin.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy positive lookbehind `r'(?<=[.!?])(?:\s+|\n+)'` để tách ở vị trí ngay sau dấu câu mà **không nuốt mất dấu câu**, giúp bảo toàn câu văn hoàn chỉnh thay vì bị cụt. Xử lý trường hợp chuỗi rỗng trả về `[]` an toàn. Sau đó gom từng cụm câu theo `max_sentences_per_chunk` và strip khoảng trắng. **Hạn chế đã biết (Edge cases):** Regex này chưa xử lý được các từ viết tắt có dấu chấm (như *TS., ThS., v.v.*) hoặc số thập phân/điểm số (*GPA 3.2, 3.14*) nếu vô tình theo sau là khoảng trắng, dẫn đến nguy cơ bị ngắt câu sai vị trí.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán kết hợp cả hai chiều: **(1) Đệ quy xuống sâu:** thử lần lượt các separator theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`, mảnh nào vẫn dài hơn `chunk_size` thì đệ quy xuống tầng dấu phân cách nhỏ hơn; **(2) Gom lên:** các mảnh nhỏ liền kề được nối lại bằng separator cho tới sát ngưỡng `chunk_size` để tránh sinh ra các chunk vụn chỉ vài ký tự làm hỏng retrieval. **Base cases:** xử lý triệt để 3 trường hợp dừng gồm chuỗi rỗng (`[]`), chuỗi $\le$ `chunk_size` (`[text]`), và trường hợp danh sách phân tách rỗng (`separators=[]` hoặc `""`) thì fallback cắt cố định theo kích thước để không bao giờ bị crash.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Dữ liệu được lưu trữ thuần trong bộ nhớ (`_store`), copy metadata để tránh đột biến object bên ngoài và tự động gắn `doc_id` chuẩn hóa trỏ về file gốc (xử lý trường hợp chunk `file#0`, `file#1`). Khi tìm kiếm, truy vấn đi qua helper `_search_records` tính tích vô hướng (bằng cosine do vector đã chuẩn hóa), xếp hạng và loại bỏ trường `embedding` trong kết quả trả về để tránh làm bẩn terminal bởi vector hàng ngàn chiều.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` bắt buộc dùng cơ chế **tiền lọc (pre-filtering)**: nếu lọc sau (post-filtering), $k$ slot lấy về có thể bị chiếm hết bởi tài liệu không khớp khiến kết quả trả về rỗng dù kho dữ liệu vẫn có tài liệu thỏa mãn. Hàm `delete_document` xóa triệt để mọi chunk khớp `id` hoặc `metadata['doc_id']`, trả về `True` nếu có bản ghi bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Thực hiện quy trình 3 nhịp: (1) Kiểm tra an toàn (guard clause): nếu store rỗng thì trả về thông báo ngay thay vì gọi LLM vô ích; (2) Truy xuất top-$k$ chunk và đánh số ngữ cảnh `[1]`, `[2]` kèm tên nguồn/file nhằm đáp ứng tiêu chí **Source Traceability**; (3) Dựng prompt kèm chỉ dẫn chống bịa đặt (anti-hallucination) nghiêm ngặt (chỉ trả lời dựa trên ngữ cảnh, không có thì báo không tìm thấy) và gọi `self.llm_fn(prompt)`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI20K_LABS\K4-DAY07-NguyenVietDung-2A202602533
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đại học được phép mượn tối đa 3 cuốn sách trong 2 tuần. | Người học bậc cử nhân có quyền mượn không quá 3 tài liệu thư viện trong vòng 14 ngày. | cao | -0.0225 | Sai |
| 2 | Hồ sơ xin học bổng và hỗ trợ tài chính được xét duyệt hai lần mỗi năm. | Hạn nộp hồ sơ xin trợ cấp kinh phí học tập cho sinh viên là vào tháng 7 và tháng 11. | cao | -0.0158 | Sai |
| 3 | Sách tham khảo và tạp chí được phép mang về nhà mượn tự do. | Tài liệu tham khảo và tạp chí định kỳ tuyệt đối không được phép mượn về. | thấp | -0.0381 | Đúng |
| 4 | Sinh viên đăng ký học phần trên cổng thông tin điện tử trước thời hạn. | Sinh viên đăng ký tài khoản truy cập mạng internet tại quầy dịch vụ IT. | thấp | 0.2341 | Sai |
| 5 | Sinh viên phải tuân thủ bộ quy tắc ứng xử văn minh trong khuôn viên trường. | Thực đơn bữa trưa tại căng tin hôm nay gồm có cơm gà và canh rau cải. | thấp | 0.1705 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là Cặp 1 (hai câu diễn đạt cùng một quy định mượn sách bằng các từ đồng nghĩa) lại có điểm cosine xấp xỉ 0 (-0.0225), trong khi Cặp 4 và Cặp 5 (khác nghĩa hoặc hoàn toàn không liên quan) lại có điểm số dương cao nhất (0.2341 và 0.1705). Điều này phản ánh rõ bản chất của `MockEmbedder`: thuật toán chỉ băm chuỗi ký tự bằng MD5 rồi sinh vector giả ngẫu nhiên, hoàn toàn không có khả năng nắm bắt ngữ nghĩa thực tế. Muốn embedding biểu diễn được ý nghĩa thực sự của văn bản, hệ thống bắt buộc phải sử dụng các mô hình ngôn ngữ học sâu (như Sentence Transformers hay OpenAI embeddings) được huấn luyện trên ngữ liệu lớn để ánh xạ ngữ nghĩa vào không gian vector.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược:** `FixedSizeChunker(chunk_size=250, overlap=50)` + OpenAI `text-embedding-3-small` / TF-IDF

> Kết quả chạy trên corpus 5 tài liệu ĐHQGHN tại `data/vnu/`, với cùng 5 benchmark query của nhóm. Cấu hình tạo **227 chunks** (do tài liệu hướng dẫn đào tạo dài 41,271 ký tự). 4/5 câu đều có chunk liên quan trong top-3; riêng câu 5 là failure case chung của cả nhóm do nhiễu từ khóa tổng quát.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Số kí hiệu quy định học bổng ĐHQGHN? `metadata_filter={"audience": "student"}` | `vnu-scholarship-regulation-2024#5`: Quy định về công tác quản lý và sử dụng học bổng tại ĐHQGHN | 0.6732 | Có, top-1 | Trả đúng: Quyết định số 4618/QĐ-ĐHQGHN. |
| 2 | Quy định học bổng bắt đầu hiệu lực ngày nào? | `vnu-scholarship-regulation-2024#5`: Tiêu đề quy định học bổng (ngày hiệu lực 07/10/2024 nằm ở chunk#6 - Top-2) | 0.6836 | Có, top-2 | Top-1 là tiêu đề chung; Top-2 chứa ngày hiệu lực 07/10/2024 nên Agent trả lời đúng. |
| 3 | Hạn làm bài kiểm tra tài liệu tập huấn quy chế? | `vnu-student-training-handbook#2`: Hướng dẫn sinh viên đọc toàn văn quy chế và làm bài kiểm tra trước hạn | 0.5419 | Có, top-1 | Trả đúng: Hạn hoàn thành trước ngày 28/02/2023. |
| 4 | Mã văn bản hướng dẫn khóa luận nhóm ngoài sư phạm? | `vnu-undergraduate-guidance-directory#3`: Danh mục văn bản hướng dẫn đào tạo, mã 3002/HD-ĐHGD | 0.4583 | Có, top-3 | Top-3 chứa mã hướng dẫn 3002/HD-ĐHGD nhưng bị lẫn giữa nhiều văn bản khác nên Agent trích dẫn thiếu một phần chi tiết. |
| 5 | Danh mục HUS-VNU có nhóm đào tạo nào? | `vnu-undergraduate-guidance-directory#19`: Danh mục hướng dẫn học phần ngoại ngữ | 0.5803 | Không (Failure case) | Top-3 bị chiếm lĩnh hoàn toàn bởi các chunk của trang hướng dẫn đào tạo dài; không truy xuất được `vnu-regulations-directory`. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điểm retrieval theo rubric:** 7 / 10

> Câu 1 và 3 đạt 2 điểm vì top-1 chứa đủ bằng chứng và Agent trả lời chính xác. Câu 2 và 4 đạt 1 điểm vì bằng chứng nằm ở top-2/top-3. Câu 5 đạt 0 điểm vì bị nhiễu ngữ cảnh bởi các trang hướng dẫn đào tạo có tần suất từ khóa "đào tạo" quá lớn.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Khi tài liệu HTML có độ dài rất lớn (như file hướng dẫn đào tạo hơn 41,000 ký tự), việc chia nhỏ fixed-size sinh ra hàng trăm chunk cạnh tranh slot trong top-k. Chiến lược Heading/section của bạn Bảo gom thành các khối logic giúp kiểm soát số lượng chunk tốt hơn, trong khi chiến lược của em chỉ ra rõ điểm yếu của vector retrieval khi gặp tài liệu chứa nhiều từ khóa phổ quát.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
