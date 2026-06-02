"""rename_photos_sequential.py - Rename foto subjek ke 1.jpeg, 2.jpeg, ..., N.jpeg

Run di STEP 0 daily render workflow (sebelum cache_check, crop, audit).
Tujuan: user bisa easily reference foto per nomor saat diskusi (mis. "foto #5
itu apa?"). Filename sequential = pengurutan natural by timestamp.

Behavior:
- Scan folder untuk .jpeg/.jpg/.png/.webp (case-insensitive).
- Urut by name (WhatsApp format alphabetical = timestamp ascending).
- Rename ke 1.jpeg / 2.jpeg / ... pakai 2-phase rename (avoid collision).
- IDEMPOTEN: kalau semua sudah numeric sequential (1..N), skip no-op.
- Preserve extension dari file original.
- Cache_check.py pakai SHA256 hash content, jadi rename TIDAK invalidate cache.

Usage:
    python rename_photos_sequential.py <photos_dir>
"""
import sys
import os
from pathlib import Path


PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def is_sequential_already(files):
    names = sorted([f.stem for f in files])
    try:
        nums = sorted([int(n) for n in names])
        return nums == list(range(1, len(files) + 1))
    except ValueError:
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python rename_photos_sequential.py <photos_dir>")
        sys.exit(1)

    photos_dir = Path(sys.argv[1])
    if not photos_dir.is_dir():
        print(f"[ERR] not a directory: {photos_dir}")
        sys.exit(1)

    files = sorted(
        [p for p in photos_dir.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXTS],
        key=lambda p: p.name,
    )
    if not files:
        print(f"[skip] no photos in {photos_dir}")
        return

    if is_sequential_already(files):
        print(f"[skip] already sequential 1..{len(files)} in {photos_dir.name}")
        return

    # Phase 1: rename ke .tmp_renaming_NNN
    tmp_paths = []
    for i, src in enumerate(files, start=1):
        tmp = src.with_name(f".tmp_renaming_{i:03d}{src.suffix.lower()}")
        src.rename(tmp)
        tmp_paths.append((tmp, src.suffix.lower()))

    # Phase 2: rename .tmp ke 1.ext / 2.ext / ...
    renamed = []
    for i, (tmp, orig_ext) in enumerate(tmp_paths, start=1):
        target = photos_dir / f"{i}{orig_ext}"
        tmp.rename(target)
        renamed.append(target.name)

    print(f"[OK] Renamed {len(renamed)} photos in {photos_dir.name}:")
    for name in renamed[:5]:
        print(f"     {name}")
    if len(renamed) > 5:
        print(f"     ... + {len(renamed) - 5} more")


if __name__ == "__main__":
    main()
