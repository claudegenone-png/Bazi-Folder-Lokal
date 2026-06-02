"""Daily folder setup — V11 version

Bikin folder hari ini + 10 sub-folder + subfolders data/ & transelate/ per subjek.

Usage:
    python v11/daily_folder_setup.py

Output:
    foto/{DD-MM-YYYY}/
        ├── 1/
        │   ├── data/       ← foto BaZi grid, ZiWei, da yun table
        │   └── transelate/ ← foto palace narasi, 性情, 流年, dll
        ├── 2/
        │   ├── data/
        │   └── transelate/
        ...
        └── 10/

Idempoten: kalau folder sudah ada, skip. Aman re-run.
Auto-run setiap hari via Windows Task Scheduler (06:00 AM).
"""
from pathlib import Path
from datetime import date

FOTO_BASE = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\foto")


def setup_daily_folder(target_date=None):
    target_date = target_date or date.today()
    folder_name = target_date.strftime("%d-%m-%Y")
    daily_dir = FOTO_BASE / folder_name
    daily_dir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for i in range(1, 11):
        sub = daily_dir / str(i)
        sub.mkdir(exist_ok=True)
        # Create data/ and transelate/ subfolders
        data_dir = sub / "data"
        trans_dir = sub / "transelate"
        is_new = not data_dir.exists()
        data_dir.mkdir(exist_ok=True)
        trans_dir.mkdir(exist_ok=True)
        if is_new:
            created.append(str(i))
        else:
            skipped.append(str(i))

    print(f"[OK] Daily folder: {daily_dir}")
    if created:
        print(f"     Created: {', '.join(created)} (each with data/ + transelate/)")
    if skipped:
        print(f"     Already exist (skipped): {', '.join(skipped)}")
    print()
    print(f"     Drop foto ke:")
    print(f"       data/       - BaZi grid, ZiWei, da yun table, marriage, yang zhai, shen sha, liu nian prose, gushu")
    print(f"       transelate/ - 12 palace narasi, xing qing, quan ju, shiye, caifu")
    print(f"     Trigger: '{daily_dir}\\{{N}} pakai V11'")
    return daily_dir


if __name__ == "__main__":
    setup_daily_folder()
