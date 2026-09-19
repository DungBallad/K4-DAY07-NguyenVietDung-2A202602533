from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context (numbered for source traceability).
        3. Call the LLM to generate an answer with strict grounding constraints.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Guard against empty store or zero search results
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy tài liệu liên quan trong cơ sở tri thức (Kho tri thức đang trống)."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức để trả lời câu hỏi."

        context_blocks = []
        for index, item in enumerate(results, start=1):
            content = item.get("content", "").strip()
            source = (
                item.get("metadata", {}).get("source")
                or item.get("metadata", {}).get("title")
                or item.get("metadata", {}).get("doc_id")
                or item.get("id")
            )
            context_blocks.append(f"[{index}] (Nguồn: {source})\n{content}")

        context_str = "\n\n".join(context_blocks)
        prompt = (
            "Bạn là cán bộ hướng dẫn nội quy và dịch vụ sinh viên tại Đại học VinUniversity (VinUni Policy & Student Services Advisor).\n\n"
            "NHIỆM VỤ & NGUYÊN TẮC HOẠT ĐỘNG:\n"
            "1. Tính chính xác & Chống bịa đặt (Anti-Hallucination): Chỉ trả lời dựa trên các đoạn ngữ cảnh trích xuất được cung cấp dưới đây. Tuyệt đối không tự suy đoán hoặc sáng tạo thông tin ngoài ngữ cảnh.\n"
            "2. Phạm vi hỗ trợ: Chỉ giải đáp các vấn đề liên quan đến nội quy, chính sách, học vụ và dịch vụ của VinUniversity. Nếu câu hỏi không liên quan đến quy định trường hoặc ngữ cảnh không có đủ thông tin, hãy từ chối lịch sự và nêu rõ bạn chỉ hỗ trợ thông tin nội quy và dịch vụ của VinUniversity.\n"
            "3. Nguyên tắc Phản chiếu Ngôn ngữ (Strict Language Mirroring): BẮT BUỘC phát hiện và phản hồi bằng CHÍNH XÁC ngôn ngữ mà người dùng sử dụng trong câu hỏi (Ví dụ: Hỏi bằng tiếng Pháp (Français) -> Toàn bộ câu trả lời phải bằng tiếng Pháp; Hỏi tiếng Anh -> Trả lời tiếng Anh; Hỏi tiếng Việt -> Trả lời tiếng Việt; Hỏi tiếng Đức/Hàn/Nhật -> Trả lời đúng thứ tiếng đó). Ngay cả khi từ chối trả lời câu hỏi ngoài phạm vi, câu từ chối CŨNG PHẢI ĐƯỢC VIẾT BẰNG CHÍNH NGÔN NGỮ CỦA CÂU HỎI.\n"
            "4. Truy vết nguồn (Source Traceability): Bắt buộc trích dẫn số hiệu nguồn [1], [2]... tương ứng với đoạn ngữ cảnh cung cấp thông tin trong câu trả lời.\n\n"
            f"Ngữ cảnh trích xuất:\n{context_str}\n\n"
            f"Câu hỏi của người dùng: {question}\n\n"
            "Câu trả lời của cán bộ hướng dẫn (bằng đúng ngôn ngữ của câu hỏi):"
        )
        return self.llm_fn(prompt)
