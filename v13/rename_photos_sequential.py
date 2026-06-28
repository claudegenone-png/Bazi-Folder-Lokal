"""rename_photos_sequential.py — V11 version (subfolder-aware)

Rename foto di data/ dan transelate/ subfolders secara sequential.
Urutan: data/ dulu (1..N_data), lanjut transelate/ (N_data+1..N_total).

Usage:
    python rename_photos_sequential.py <photos_dir>
    # photos_dir = folder subjek, mis. C:\...\foto\30-05-2026\1

Behavior:
- Scan data/ → rename ke 1.jpeg..N_data.jpeg
- Scan transelate/ → rename ke (N_data+1).jpeg..(N_data+N_transelate).jpeg
- IDEMPOTEN: kalau sudah sequential, skip no-op
- Cache_check.py pakai SHA256 hash, rename tidak invalidate cache
- Fallback: kalau tidak ada subfolder data/ + transelate/, rename flat (V7.1 mode)
"""
import sys
import os
from pathlib import Path

PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def collect_photos(folder: Path) -> list:
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXTS],
        key=lambda p: p.name,
    )


def is_sequential(files: list, start: int) -> bool:
    try:
        nums = sorted([int(f.stem) for f in files])
        return nums == list(range(start, start + len(files)))
    except ValueError:
        return False


def rename_batch(files: list, start_num: int, folder_label: str) -> int:
    """Rename files starting from start_num. Returns count renamed."""
    if not files:
        print(f"[skip] no photos in {folder_label}")
        return 0

    if is_sequential(files, start_num):
        print(f"[skip] already sequential {start_num}..{start_num + len(files) - 1} in {folder_label}")
        return 0

    # Phase 1: temp rename
    tmp_paths = []
    for i, src in enumerate(files, start=start_num):
        tmp = src.with_name(f".tmp_renaming_{i:03d}{src.suffix.lower()}")
        src.rename(tmp)
        tmp_paths.append((tmp, src.suffix.lower()))

    # Phase 2: final rename
    renamed = []
    for i, (tmp, ext) in enumerate(tmp_paths, start=start_num):
        target = tmp.parent / f"{i}{ext}"
        tmp.rename(target)
        renamed.append(target.name)

    print(f"[OK] Renamed {len(renamed)} photos in {folder_label} ({renamed[0]}..{renamed[-1]})")
    return len(renamed)


def main():
    if len(sys.argv) != 2:
        print("Usage: python rename_photos_sequential.py <photos_dir>")
        sys.exit(1)

    photos_dir = Path(sys.argv[1])
    if not photos_dir.is_dir():
        print(f"[ERR] not a directory: {photos_dir}")
        sys.exit(1)

    data_dir = photos_dir / "data"
    transelate_dir = photos_dir / "transelate"

    # Root folder photos = arsip (BaZi grid, 命宮, shio) — diabaikan tanpa warning
    root_photos = collect_photos(photos_dir)
    if root_photos:
        print(f"[skip] {len(root_photos)} foto di root folder (arsip) — diabaikan")

    # V11 mode: subfolder exists
    if data_dir.is_dir() and transelate_dir.is_dir():
        data_files = collect_photos(data_dir)
        trans_files = collect_photos(transelate_dir)

        rename_batch(data_files, start_num=1, folder_label="data/")
        rename_batch(trans_files, start_num=len(data_files) + 1, folder_label="transelate/")

        total = len(data_files) + len(trans_files)
        print(f"[OK] Total: {total} photos (data: {len(data_files)}, transelate: {len(trans_files)})")

    # Fallback: flat folder (V7.1 / legacy mode)
    else:
        files = collect_photos(photos_dir)
        if not files:
            print(f"[skip] no photos in {photos_dir.name}")
            return
        if is_sequential(files, 1):
            print(f"[skip] already sequential 1..{len(files)} in {photos_dir.name}")
            return
        rename_batch(files, start_num=1, folder_label=photos_dir.name)


if __name__ == "__main__":
    main()
