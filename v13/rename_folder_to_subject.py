"""Rename numbered photo folder → subject display name after daily render.

Usage:
    python v13/rename_folder_to_subject.py "{photos_dir}" {subject_id}

Example:
    python v13/rename_folder_to_subject.py "C:\\...\\foto\\2026-06-21\\1" ah
    → renames folder  1  →  AH

Idempoten: kalau target sudah ada dengan nama yang sama → skip.
"""
import sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "subjects"


def rename_folder_to_subject(photos_dir: str, subject_id: str) -> None:
    photos_path = Path(photos_dir)

    if not photos_path.exists():
        print(f"[rename] Folder tidak ada: {photos_path}")
        return

    md_path = DATA_DIR / f"{subject_id}.md"
    if not md_path.exists():
        print(f"[rename] MD tidak ada: {md_path}")
        return

    md_text = md_path.read_text(encoding="utf-8")
    m = re.search(r"^\s*-\s*nama\s*:\s*(.+)$", md_text, re.M)
    if not m:
        print(f"[rename] Field 'nama' tidak ditemukan di MD — skip")
        return

    nama = m.group(1).strip()
    if not nama or nama.lower() in ("null", "none", "fill", "—", "-"):
        print(f"[rename] Nama tidak valid: {nama!r} — skip")
        return

    new_path = photos_path.parent / nama

    if photos_path.resolve() == new_path.resolve():
        print(f"[rename] Folder sudah bernama '{nama}' — skip")
        return

    if new_path.exists():
        print(f"[rename] Target '{nama}' sudah ada di {new_path.parent} — skip (manual rename jika perlu)")
        return

    photos_path.rename(new_path)
    print(f"[rename] OK: {photos_path.name}  ->  {nama}")
    print(f"         {new_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: rename_folder_to_subject.py <photos_dir> <subject_id>")
        sys.exit(1)
    rename_folder_to_subject(sys.argv[1], sys.argv[2])
