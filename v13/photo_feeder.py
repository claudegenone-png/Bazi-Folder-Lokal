"""
photo_feeder.py — Structural gate untuk V13 Step 1
Memastikan agent baca 1 foto -> Edit MD -> baru dapat foto berikutnya.

Usage:
    python photo_feeder.py init <subject_id> <photos_dir>
    python photo_feeder.py next <subject_id>
    python photo_feeder.py status <subject_id>
    python photo_feeder.py cleanup <subject_id>   # restore queue ke data/ (setelah selesai)

Folder structure:
    {photos_dir}/          <- original (tidak diubah saat init)
    {photos_dir}/queue/    <- semua foto menunggu
    {photos_dir}/current/  <- hanya 1 foto aktif (yang agent baca)

State file: {photos_dir}/.feeder_state.json
    {
        "subject_id": "said",
        "photos_dir": "...",
        "total": 19,
        "current_index": 1,        # foto ke berapa yang sedang di current/
        "current_file": "1.jpeg",
        "md_mtime_before": 1234567890.0,
        "done": false
    }
"""

import sys
import os
import json
import shutil
import glob
from pathlib import Path


STATE_FILE = ".feeder_state.json"
MD_BASE = r"C:\Users\sukam\OneDrive\Documents\Ramalan\v13\data\subjects"


def get_state_path(photos_dir: str) -> Path:
    return Path(photos_dir) / STATE_FILE


def load_state(photos_dir: str) -> dict:
    p = get_state_path(photos_dir)
    if not p.exists():
        print(f"ERROR: State file tidak ditemukan di {photos_dir}")
        print("       Jalankan: python photo_feeder.py init <id> <photos_dir>")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_state(photos_dir: str, state: dict):
    p = get_state_path(photos_dir)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_md_path(subject_id: str) -> Path:
    return Path(MD_BASE) / f"{subject_id}.md"


def get_md_mtime(subject_id: str) -> float:
    md = get_md_path(subject_id)
    if not md.exists():
        return 0.0
    return md.stat().st_mtime


def cmd_init(subject_id: str, photos_dir: str):
    photos_dir = str(Path(photos_dir).resolve())
    queue_dir = Path(photos_dir) / "queue"
    current_dir = Path(photos_dir) / "current"

    # Idempoten: kalau state sudah ada, tanya konfirmasi
    state_path = get_state_path(photos_dir)
    if state_path.exists():
        old = load_state(photos_dir)
        if not old.get("done", False):
            print(f"WARNING: Feeder sudah aktif (foto {old['current_index']}/{old['total']})")
            print("         Jalankan 'cleanup' dulu kalau mau reset.")
            sys.exit(1)

    # Buat queue/ dan current/
    queue_dir.mkdir(exist_ok=True)
    current_dir.mkdir(exist_ok=True)

    # Kumpulkan semua jpeg di photos_dir (langsung, bukan subfolder)
    jpegs = sorted(
        [f for f in Path(photos_dir).iterdir()
         if f.is_file() and f.suffix.lower() in (".jpeg", ".jpg")],
        key=lambda f: int(f.stem) if f.stem.isdigit() else 9999
    )

    if not jpegs:
        print(f"INFO: Tidak ada foto jpeg di {photos_dir} — feeder skip (0 foto).")
        # Tulis state done=true supaya next/status tahu
        save_state(photos_dir, {
            "subject_id": subject_id,
            "photos_dir": photos_dir,
            "total": 0,
            "current_index": 0,
            "current_file": None,
            "md_mtime_before": get_md_mtime(subject_id),
            "done": True
        })
        return

    # Pindah semua foto ke queue/
    for f in jpegs:
        shutil.move(str(f), str(queue_dir / f.name))

    # Bersihkan current/ kalau ada sisa — kembalikan ke photos_dir, JANGAN delete
    for f in current_dir.iterdir():
        if f.is_file():
            dest = Path(photos_dir) / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
            else:
                f.unlink()  # duplikat nama saja

    # Pindah foto pertama ke current/ (hapus dari queue)
    first = jpegs[0]
    shutil.move(str(queue_dir / first.name), str(current_dir / first.name))

    state = {
        "subject_id": subject_id,
        "photos_dir": photos_dir,
        "total": len(jpegs),
        "current_index": 1,
        "current_file": first.name,
        "md_mtime_before": get_md_mtime(subject_id),
        "done": False
    }
    save_state(photos_dir, state)

    print(f"Feeder init: {len(jpegs)} foto -> queue/")
    print(f"current/: {first.name} (foto 1/{len(jpegs)})")
    print(f"Baca data/current/{first.name}, Edit MD, lalu: python photo_feeder.py next {subject_id}")


def find_photos_dir(subject_id: str) -> str:
    """Cari photos_dir dari state file di semua drive/folder umum."""
    import glob as glob_mod
    search_roots = [
        r"C:\Users\sukam\OneDrive\Documents\Ramalan\foto",
        r"C:\temp",
        r"C:\Users\sukam\Desktop",
    ]
    for root in search_roots:
        pattern = os.path.join(root, "**", ".feeder_state.json")
        for m in glob_mod.glob(pattern, recursive=True):
            try:
                with open(m, encoding="utf-8") as f:
                    s = json.load(f)
                if s.get("subject_id") == subject_id:
                    return s["photos_dir"]
            except Exception:
                continue
    return None


def cmd_next(subject_id: str):
    photos_dir = find_photos_dir(subject_id)
    if not photos_dir:
        print(f"ERROR: Tidak ada feeder aktif untuk subject '{subject_id}'. Jalankan init dulu.")
        sys.exit(1)
    _do_next(subject_id, photos_dir)


def _do_next(subject_id: str, photos_dir: str):
    state = load_state(photos_dir)

    if state.get("done"):
        print("INFO: Semua foto sudah selesai diproses.")
        return

    # Cek apakah MD sudah diupdate sejak foto terakhir ditaruh
    current_mtime = get_md_mtime(subject_id)
    required_mtime = state["md_mtime_before"]

    if current_mtime <= required_mtime:
        print(f"ERROR: MD belum diupdate sejak foto {state['current_index']}/{state['total']} ({state['current_file']}) ditaruh.")
        print(f"       Edit MD dulu untuk foto {state['current_file']}, baru jalankan next lagi.")
        sys.exit(1)

    queue_dir = Path(photos_dir) / "queue"
    current_dir = Path(photos_dir) / "current"

    # Kembalikan foto lama dari current/ ke photos_dir (JANGAN delete)
    for f in current_dir.iterdir():
        if f.is_file():
            dest = Path(photos_dir) / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
            else:
                f.unlink()  # duplikat nama — hapus copy di current saja

    # Kembalikan foto yang baru diproses dari queue ke photos_dir (JANGAN delete)
    processed = queue_dir / state["current_file"]
    if processed.exists():
        dest = Path(photos_dir) / processed.name
        if not dest.exists():
            shutil.move(str(processed), str(dest))
        else:
            processed.unlink()  # duplikat nama — hapus copy di queue saja

    # Ambil sisa foto di queue, sorted
    queued = sorted(
        [f for f in queue_dir.iterdir() if f.suffix.lower() in (".jpeg", ".jpg")],
        key=lambda f: int(f.stem) if f.stem.isdigit() else 9999
    )

    next_index = state["current_index"] + 1

    if not queued:
        # Semua sudah diproses
        state["done"] = True
        state["current_file"] = None
        save_state(photos_dir, state)
        print(f"Semua {state['total']} foto selesai diproses.")
        print("Lanjut ke Step 2: python build_pdf.py " + subject_id)
        return

    # Taruh foto berikutnya di current/ (move dari queue)
    next_foto = queued[0]
    shutil.move(str(next_foto), str(current_dir / next_foto.name))

    state["current_index"] = next_index
    state["current_file"] = next_foto.name
    state["md_mtime_before"] = get_md_mtime(subject_id)
    save_state(photos_dir, state)

    remaining = len(queued) - 1
    print(f"OK: foto {next_index}/{state['total']} aktif: current/{next_foto.name}")
    if remaining > 0:
        print(f"    {remaining} foto lagi di queue.")
        print(f"    Baca current/{next_foto.name}, Edit MD, lalu: python photo_feeder.py next {subject_id}")
    else:
        print(f"    Ini foto terakhir.")
        print(f"    Baca current/{next_foto.name}, Edit MD, lalu: python photo_feeder.py next {subject_id}")


def cmd_status(subject_id: str):
    photos_dir = find_photos_dir(subject_id)
    if not photos_dir:
        print(f"Tidak ada feeder aktif untuk '{subject_id}'")
        return
    import glob as glob_mod
    pattern = os.path.join(photos_dir, ".feeder_state.json")
    matches = [pattern] if os.path.exists(pattern) else []

    for m in matches:
        with open(m, encoding="utf-8") as f:
            s = json.load(f)
        if s.get("subject_id") == subject_id:
            if s.get("done"):
                print(f"Status {subject_id}: SELESAI ({s['total']}/{s['total']} foto)")
            else:
                print(f"Status {subject_id}: foto {s['current_index']}/{s['total']} aktif ({s['current_file']})")
                md_mtime = get_md_mtime(subject_id)
                if md_mtime > s["md_mtime_before"]:
                    print(f"  MD: sudah diupdate (siap next)")
                else:
                    print(f"  MD: BELUM diupdate (Edit MD dulu)")
            return

    print(f"Tidak ada feeder aktif untuk '{subject_id}'")


def cmd_cleanup(subject_id: str):
    """Restore semua foto dari queue/ dan current/ kembali ke photos_dir."""
    photos_dir = find_photos_dir(subject_id)
    if not photos_dir:
        print(f"Tidak ada feeder untuk '{subject_id}'")
        return

    queue_dir = Path(photos_dir) / "queue"
    current_dir = Path(photos_dir) / "current"

    moved = 0
    for src in list(queue_dir.iterdir()) + list(current_dir.iterdir()):
        if src.is_file() and src.suffix.lower() in (".jpeg", ".jpg"):
            dest = Path(photos_dir) / src.name
            if not dest.exists():
                shutil.move(str(src), str(dest))
                moved += 1

    # Hapus state file
    state_path = Path(photos_dir) / STATE_FILE
    if state_path.exists():
        state_path.unlink()
    print(f"Cleanup: {moved} foto dikembalikan ke {photos_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python photo_feeder.py init <subject_id> <photos_dir>")
        print("  python photo_feeder.py next <subject_id>")
        print("  python photo_feeder.py status <subject_id>")
        print("  python photo_feeder.py cleanup <subject_id>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "init":
        if len(sys.argv) < 4:
            print("Usage: python photo_feeder.py init <subject_id> <photos_dir>")
            sys.exit(1)
        cmd_init(sys.argv[2], sys.argv[3])

    elif cmd == "next":
        if len(sys.argv) < 3:
            print("Usage: python photo_feeder.py next <subject_id>")
            sys.exit(1)
        cmd_next(sys.argv[2])

    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: python photo_feeder.py status <subject_id>")
            sys.exit(1)
        cmd_status(sys.argv[2])

    elif cmd == "cleanup":
        if len(sys.argv) < 3:
            print("Usage: python photo_feeder.py cleanup <subject_id>")
            sys.exit(1)
        cmd_cleanup(sys.argv[2])

    else:
        print(f"ERROR: Command tidak dikenal: {cmd}")
        print("       Gunakan: init / next / status / cleanup")
        sys.exit(1)
