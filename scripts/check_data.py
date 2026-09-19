#!/usr/bin/env python3
"""Script kiem tra tinh hop le cua tap du lieu truoc khi benchmark (Lab 7 - K4-L3A).

Cac tieu chi kiem tra:
1. So luong tai lieu tu 5 den 10 file .md.
2. Moi file co day du cac truong metadata bat buoc:
   doc_id, title, source_url, retrieved_at, document_version, audience.
3. doc_id phai khop voi ten file (<doc_id>.md).
4. File sources.csv ton tai va khop 1-1 voi danh sach file .md.
5. Truong 'audience' phai co it nhat 2 gia tri khac nhau (vi du: student, all).
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# Dam bao in tieng Viet tren Windows console khong bi loi UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REQUIRED_FIELDS = [
    "doc_id",
    "title",
    "source_url",
    "retrieved_at",
    "document_version",
    "audience",
]


def check_dataset(data_dir: Path) -> bool:
    if not data_dir.exists() or not data_dir.is_dir():
        print(f"Loi: Thu muc khong ton tai: {data_dir}", file=sys.stderr)
        return False

    md_files = sorted(data_dir.glob("*.md"))
    sources_csv = data_dir / "sources.csv"

    print("=" * 65)
    print(f"KIEM TRA DU LIEU: {data_dir.resolve()}")
    print("=" * 65)

    all_passed = True
    ids: list[str] = []
    audiences: dict[str, int] = {}

    print(f"{'Tên file':<45} {'Trạng thái':<15}")
    print("-" * 65)

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8")
        parts = content.split("---")

        if len(parts) < 3:
            print(f"{file_path.name:<45} [THIẾU FRONTMATTER]")
            all_passed = False
            continue

        front_matter_raw = parts[1]
        fm = dict(re.findall(r"^(\w+):\s*(.+)$", front_matter_raw, re.MULTILINE))

        # Lam sach gia tri doc_id va audience
        doc_id = fm.get("doc_id", "").strip("\"' ")
        ids.append(doc_id)

        aud = fm.get("audience", "").split("#")[0].strip("\"' ")
        if aud:
            audiences[aud] = audiences.get(aud, 0) + 1

        missing_fields = [f for f in REQUIRED_FIELDS if f not in fm]

        if missing_fields:
            print(f"{file_path.name:<45} [THIẾU: {', '.join(missing_fields)}]")
            all_passed = False
        elif doc_id != file_path.stem:
            print(f"{file_path.name:<45} [ID LECH: {doc_id} != {file_path.stem}]")
            all_passed = False
        else:
            print(f"{file_path.name:<45} OK")

    print("-" * 65)

    # 1. Kiem tra so luong file
    num_files = len(md_files)
    file_count_ok = 5 <= num_files <= 10
    if not file_count_ok:
        all_passed = False
    print(f"Số lượng file : {num_files} (Yêu cầu: 5-10) -> {'OK' if file_count_ok else 'KHÔNG ĐẠT'}")

    # 2. Kiem tra sources.csv
    if not sources_csv.exists():
        print("sources.csv   : KHÔNG TÌM THẤY FILE sources.csv -> THẤT BẠI")
        all_passed = False
    else:
        with sources_csv.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        csv_ids = [r.get("doc_id", "").strip() for r in rows if r.get("doc_id")]
        csv_ok = sorted(csv_ids) == sorted(ids)
        if not csv_ok:
            all_passed = False
        print(f"sources.csv   : {'Khớp 1-1 với file .md' if csv_ok else 'LỆCH VỚI DANH SÁCH FILE'}")

    # 3. Kiem tra phan bo audience
    aud_diverse = len(audiences) >= 2
    if not aud_diverse:
        all_passed = False
    print(f"Phân loại audience: {dict(audiences)} -> {'ĐA DẠNG (OK)' if aud_diverse else 'CẦN ÍT NHẤT 2 GIÁ TRỊ'}")

    print("=" * 65)
    if all_passed:
        print("KẾT QUẢ TỔNG THỂ: TẤT CẢ TIÊU CHÍ ĐỀU ĐẠT CHUẨN (PASSED)!")
    else:
        print("KẾT QUẢ TỔNG THỂ: CÓ TIÊU CHÍ CHƯA ĐẠT (FAILED).")
    print("=" * 65)

    return all_passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Kiểm tra dữ liệu data/ cho Lab 7")
    default_dir = Path("data/vnu") if Path("data/vnu").exists() else Path("data/vinuni")
    parser.add_argument(
        "--dir",
        type=Path,
        default=default_dir,
        help="Đường dẫn thư mục chứa dữ liệu (mặc định: data/vnu hoặc data/vinuni)",
    )
    args = parser.parse_args()
    success = check_dataset(args.dir)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
