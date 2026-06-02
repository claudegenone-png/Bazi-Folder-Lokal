"""Daily folder setup — bikin folder hari ini + 10 sub-folder kosong (1-10).

Usage:
    python v7.1/daily_folder_setup.py

Output:
    foto/{DD-MM-YYYY}/
        ├── 1/
        ├── 2/
        ...
        └── 10/

Idempoten: kalau folder sudah ada, skip (tidak overwrite). Aman re-run.

Auto-run setiap hari via Windows Task Scheduler (set up 2026-05-09).
Atau run manual via: python v7.1/daily_folder_setup.py
"""
from pathlib import Path
from datetime import date


FOTO_BASE = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\foto")


def setup_daily_folder(target_date: date | None = None) -> Path:
    """Create today's folder + 10 subfolders. Idempoten."""
    target_date = target_date or date.today()
    folder_name = target_date.strftime("%d-%m-%Y")  # 08-05-2026
    daily_dir = FOTO_BASE / folder_name
    daily_dir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for i in range(1, 11):
        sub = daily_dir / str(i)
        if sub.exists():
            skipped.append(str(i))
        else:
            sub.mkdir()
            created.append(str(i))

    print(f"[OK] Daily folder: {daily_dir}")
    if created:
        print(f"     Created subfolders: {', '.join(created)}")
    if skipped:
        print(f"     Already exist (skipped): {', '.join(skipped)}")
    print()
    print(f"     Workflow: drop foto subjek ke salah satu folder 1-10,")
    print(f"     trigger di window baru: '{daily_dir}\\{{N}} pakai V7.1'")
    return daily_dir


if __name__ == "__main__":
    setup_daily_folder()
