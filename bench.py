#!/usr/bin/env python3
"""Benchmark script for Lab 7 (K4-L3A - VinUniversity).

Individual Strategy: FixedSizeChunker(chunk_size=250, overlap=50)
Student: Nguyễn Việt Dũng (2A202602533)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv(override=True)

# Add repo root to sys.path
REPO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from src.chunking import FixedSizeChunker
from src.embeddings import MockEmbedder, OpenAIEmbedder
from src.models import Document
from src.store import EmbeddingStore


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter and extract body text."""
    parts = content.split("---")
    metadata: dict[str, str] = {}
    if len(parts) >= 3:
        front_matter_raw = parts[1].strip()
        for line in front_matter_raw.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                val_clean = val.split("#")[0].strip().strip("\"' ")
                metadata[key.strip()] = val_clean
        body = "---".join(parts[2:]).strip()
    else:
        body = content.strip()
    return metadata, body


def get_data_dir() -> Path:
    """Find data directory for university corpus."""
    for candidate in [REPO_ROOT / "data" / "vnu", REPO_ROOT / "data" / "vinuni", REPO_ROOT / "data" / "university"]:
        if candidate.exists() and list(candidate.glob("*.md")):
            return candidate
    raise FileNotFoundError("Cannot find university data directory!")


def main() -> None:
    data_dir = get_data_dir()
    md_files = sorted(data_dir.glob("*.md"))

    print("=" * 70)
    print("BENCHMARK RETRIEVAL - LAB 07 (K4-L3A: VinUniversity)")
    print(f"Thư mục dữ liệu: {data_dir.relative_to(REPO_ROOT)}")
    print(f"Số lượng tài liệu: {len(md_files)}")
    print("Chiến lược chunking cá nhân: FixedSizeChunker(chunk_size=250, overlap=50)")
    print("=" * 70)

    # 1 & 2. Đọc file, tách frontmatter, chunk phần thân và gán metadata
    chunker = FixedSizeChunker(chunk_size=250, overlap=50)
    all_chunks: list[Document] = []

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        doc_id = frontmatter.get("doc_id", path.stem)

        chunks = chunker.chunk(body)
        for i, c in enumerate(chunks):
            # doc_id trỏ về file gốc, id là chunk id
            doc = Document(
                id=f"{path.stem}#{i}",
                content=c,
                metadata={
                    **frontmatter,
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "source_file": path.name,
                },
            )
            all_chunks.append(doc)

    print(f"-> Đã nạp và chia nhỏ thành tổng cộng: {len(all_chunks)} chunks.")

    # 3. Khởi tạo Embedder & EmbeddingStore
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    embedder = None

    if provider == "openai" and api_key and not api_key.startswith("your-") and not api_key.startswith("sk-placeholder"):
        try:
            test_embedder = OpenAIEmbedder(model_name="text-embedding-3-small")
            test_embedder("smoke test")
            embedder = test_embedder
            print("-> Sử dụng Embedding Backend: OpenAI text-embedding-3-small (1536 chiều)")
        except Exception as e:
            print(f"-> Không thể gọi OpenAI API ({e}), chuyển sang MockEmbedder")
            embedder = MockEmbedder()
    else:
        print("-> Sử dụng Embedding Backend: MockEmbedder (Chế độ kiểm thử nhanh / baseline)")
        embedder = MockEmbedder()

    store = EmbeddingStore(collection_name="benchmark_collection", embedding_fn=embedder)
    store.add_documents(all_chunks)
    print(f"-> EmbeddingStore kích thước: {store.get_collection_size()} bản ghi.\n")

    # 4. 5 Benchmark Queries theo quy định nhóm (K4-L3A - VNU)
    queries = [
        {
            "id": 1,
            "query": "Số kí hiệu quy định học bổng ĐHQGHN?",
            "filter": {"audience": "student"},
            "gold_doc": "vnu-scholarship-regulation-2024",
            "gold_note": "4618/QĐ-ĐHQGHN",
        },
        {
            "id": 2,
            "query": "Quy định học bổng bắt đầu hiệu lực ngày nào?",
            "filter": None,
            "gold_doc": "vnu-scholarship-regulation-2024",
            "gold_note": "07/10/2024",
        },
        {
            "id": 3,
            "query": "Hạn làm bài kiểm tra tài liệu tập huấn quy chế?",
            "filter": None,
            "gold_doc": "vnu-student-training-handbook",
            "gold_note": "28/02/2023",
        },
        {
            "id": 4,
            "query": "Mã văn bản hướng dẫn khóa luận nhóm ngoài sư phạm?",
            "filter": None,
            "gold_doc": "vnu-undergraduate-guidance-directory",
            "gold_note": "3002/HD-ĐHGD",
        },
        {
            "id": 5,
            "query": "Danh mục HUS-VNU có nhóm đào tạo nào?",
            "filter": None,
            "gold_doc": "vnu-regulations-directory",
            "gold_note": "Đào tạo, gồm Đại học và Sau đại học",
        },
    ]

    print("=" * 70)
    print("CHẠY 5 BENCHMARK QUERIES (TOP-3 RETRIEVAL)")
    print("=" * 70)

    results_output = []
    results_output.append(f"BENCHMARK RESULTS - Lab 07 (K4-L3A: ĐHQGHN - VNU)")
    results_output.append(f"Strategy: FixedSizeChunker(chunk_size=250, overlap=50)")
    results_output.append(f"Total Chunks: {len(all_chunks)}")
    results_output.append(f"Embedding Backend: {embedder.__class__.__name__}")
    results_output.append("=" * 70)

    for item in queries:
        qid = item["id"]
        q = item["query"]
        flt = item["filter"]
        gold_doc = item["gold_doc"]

        print(f"\n[Query #{qid}]: {q}")
        if flt:
            print(f"  * metadata_filter = {flt}")
        print(f"  * Gold Document: {gold_doc}.md ({item['gold_note']})")

        top_results = store.search_with_filter(query=q, metadata_filter=flt, top_k=3)

        results_output.append(f"\nQuery #{qid}: {q}")
        results_output.append(f"Filter: {flt}")
        results_output.append(f"Gold Document: {gold_doc}")

        for rank, res in enumerate(top_results, 1):
            doc_id = res.get("metadata", {}).get("doc_id", "unknown")
            chunk_id = res.get("id", "unknown")
            score = res.get("score", 0.0)
            content_preview = res.get("content", "").replace("\n", " ")[:100]
            is_gold = "(GOLD MATCH)" if doc_id == gold_doc else ""

            line = f"  Top-{rank}: [{doc_id}] score={score:.4f} {is_gold} | ID={chunk_id}"
            print(line)
            print(f"         Preview: {content_preview}...")
            results_output.append(f"  Top-{rank}: [{doc_id}] score={score:.4f} {is_gold} | {content_preview}...")

    print("\n" + "=" * 70)
    print("HOÀN THÀNH BENCHMARK!")
    print("=" * 70)

    # Ghi ra ket_qua_benchmark.txt
    output_path = REPO_ROOT / "ket_qua_benchmark.txt"
    output_path.write_text("\n".join(results_output), encoding="utf-8")
    print(f"-> Đã xuất kết quả ra file: {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
