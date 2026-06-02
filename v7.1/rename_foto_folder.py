"""Rename foto folder dari numeric (1-10) ke nama subjek (Indonesian) setelah PDF.

Usage:
    python v45/rename_foto_folder.py "<foto_folder_path>" <subject_id>

Examples:
    python v45/rename_foto_folder.py "C:/.../foto/database/07-05-2026/1" lijialing
    → renames folder "1" menjadi "Li Jia Ling" (dari MD nama field)

    python v45/rename_foto_folder.py "C:/.../06-05-2026/1" wu_huan_yang
    → renames folder "1" menjadi "Wu Huan Yang"

Behavior:
- Read MD `data/subjects/{subject_id}.md` field `nama:` (Indonesian latin name)
- Sanitize name (remove special chars, OK spaces)
- Rename folder
- Skip kalau folder sudah bukan numeric (1-10)
- Skip kalau target name folder already exists
"""
import sys, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


REPO = Path(__file__).parent  # v45/
DATA_DIR = REPO / "data" / "subjects"


def get_subject_name(subject_id: str) -> str | None:
    """Read MD `nama:` field. Returns Indonesian latin name or None if missing."""
    md_path = DATA_DIR / f"{subject_id}.md"
    if not md_path.exists():
        return None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- nama:\s*(.+?)\s*$", line)
        if m:
            name = m.group(1).strip()
            if name and name.lower() not in ("null", "none", ""):
                return name
    return None


def sanitize_folder_name(name: str) -> str:
    """Remove special chars unsafe for Windows folder names."""
    # Windows reserved: < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Strip trailing dots/spaces (Windows quirk)
    name = name.strip().rstrip('.')
    return name


def rename_foto_folder(foto_path: Path, subject_id: str) -> tuple[bool, str]:
    """Rename foto folder dari numeric ke nama subjek. Return (success, message)."""
    if not foto_path.exists() or not foto_path.is_dir():
        return False, f"Path tidak ada / bukan folder: {foto_path}"

    current_name = foto_path.name
    # Only rename if current name is numeric 1-10 (or single digit)
    if not re.match(r"^([1-9]|10)$", current_name):
        return False, f"Folder name '{current_name}' bukan numeric (1-10), skip rename"

    subject_name = get_subject_name(subject_id)
    if not subject_name:
        return False, f"MD `nama:` field kosong untuk subject_id={subject_id}"

    new_name = sanitize_folder_name(subject_name)
    if not new_name:
        return False, f"Sanitized name kosong dari '{subject_name}'"

    new_path = foto_path.parent / new_name
    if new_path.exists():
        return False, f"Target folder sudah ada: {new_path} (skip rename, no overwrite)"

    foto_path.rename(new_path)
    return True, f"Renamed: '{current_name}' → '{new_name}' di {foto_path.parent}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python rename_foto_folder.py <foto_folder_path> <subject_id>")
        sys.exit(1)

    foto_path = Path(sys.argv[1])
    subject_id = sys.argv[2]

    success, msg = rename_foto_folder(foto_path, subject_id)
    if success:
        print(f"[OK] {msg}")
    else:
        print(f"[SKIP] {msg}")
        sys.exit(1)
