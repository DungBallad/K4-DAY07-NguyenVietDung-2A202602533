from __future__ import annotations

from typing import Any, Callable

import sys
from pathlib import Path

try:
    from .chunking import _dot
    from .embeddings import _mock_embed
    from .models import Document
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.chunking import _dot
    from src.embeddings import _mock_embed
    from src.models import Document


class EmbeddingStore:
    """
    An in-memory vector store for text chunks.

    The embedding_fn parameter allows injection of mock embeddings for tests
    or real embedding models.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._collection_name = collection_name
        self._embedding_fn = embedding_fn or _mock_embed
        self._store: list[dict[str, Any]] = []

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Normalize a Document into an in-memory record.

        Copies metadata to avoid mutating external state and ensures
        a 'doc_id' key is always present for clean chunk management.
        """
        embedding = self._embedding_fn(doc.content)
        metadata = dict(doc.metadata) if doc.metadata else {}
        if "doc_id" not in metadata:
            metadata["doc_id"] = doc.id.split("#")[0] if "#" in doc.id else doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """
        Run similarity search over candidate records.

        Returns only the needed fields (omitting the large embedding vector
        to keep terminal output and memory clean).
        """
        if not records or top_k <= 0:
            return []
        query_emb = self._embedding_fn(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for r in records:
            score = _dot(query_emb, r["embedding"])
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[dict[str, Any]] = []
        for score, r in scored[:top_k]:
            results.append(
                {
                    "id": r["id"],
                    "content": r["content"],
                    "metadata": r.get("metadata", {}),
                    "score": float(score),
                }
            )
        return results

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it in-memory.
        1 Document input = 1 stored record (chunking is handled externally).
        """
        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query among all stored records.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict | None = None
    ) -> list[dict[str, Any]]:
        """
        Search with pre-filtering on metadata before running similarity search.
        Pre-filtering prevents relevant candidates from being displaced by non-matching docs.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        filtered_records = [
            r
            for r in self._store
            if all(r.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
        ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document (by id or parent doc_id).

        Returns True if any chunks were removed, False otherwise.
        """
        before_len = len(self._store)
        self._store = [
            r
            for r in self._store
            if r.get("id") != doc_id
            and r.get("metadata", {}).get("doc_id") != doc_id
            and not r.get("id", "").startswith(f"{doc_id}#")
        ]
        return len(self._store) < before_len


if __name__ == "__main__":
    import sys

    # UTF-8 encoding support for Windows console
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 65)
    print("DEMO CHẠY THỬ NGHIỆM IN-MEMORY EMBEDDING STORE")
    print("=" * 65)

    # 1. Khởi tạo store
    store = EmbeddingStore(collection_name="demo_store")

    # 2. Tạo dữ liệu mẫu
    sample_docs = [
        Document(
            id="doc1#0",
            content="Quy định học bổng khuyến khích học tập tại ĐHQGHN có số hiệu 4618/QĐ-ĐHQGHN.",
            metadata={"doc_id": "doc1", "audience": "student", "department": "student-affairs"},
        ),
        Document(
            id="doc1#1",
            content="Quy định học bổng bắt đầu có hiệu lực kể từ ngày 07/10/2024.",
            metadata={"doc_id": "doc1", "audience": "student", "department": "student-affairs"},
        ),
        Document(
            id="doc2#0",
            content="Danh mục quy chế và biểu mẫu của trường đại học dành cho toàn thể cán bộ và sinh viên.",
            metadata={"doc_id": "doc2", "audience": "all", "department": "academic-affairs"},
        ),
    ]

    print(f"-> Đang nạp {len(sample_docs)} documents vào store...")
    store.add_documents(sample_docs)
    print(f"-> Kích thước store hiện tại (get_collection_size): {store.get_collection_size()} records")

    # 3. Tìm kiếm không lọc (Search)
    query = "Học bổng ĐHQGHN"
    print(f"\n1. Tìm kiếm với query: '{query}' (top_k=2):")
    results = store.search(query, top_k=2)
    for i, r in enumerate(results, 1):
        print(f"   [{i}] ID={r['id']} | score={r['score']:.4f}")
        print(f"       Content: {r['content']}")

    # 4. Tìm kiếm có tiền lọc (Pre-filtering)
    print(f"\n2. Tìm kiếm có lọc metadata_filter={{'audience': 'student'}}:")
    filtered_results = store.search_with_filter(query, top_k=2, metadata_filter={"audience": "student"})
    for i, r in enumerate(filtered_results, 1):
        print(f"   [{i}] ID={r['id']} | audience={r['metadata'].get('audience')} | score={r['score']:.4f}")
        print(f"       Content: {r['content']}")

    print("\n" + "=" * 65)
    print("STORE HOẠT ĐỘNG HOÀN TOÀN BÌNH THƯỜNG TRÊN IN-MEMORY (RAM)!")
    print("=" * 65)

