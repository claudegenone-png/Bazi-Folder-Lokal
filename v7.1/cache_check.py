"""V4.5 cache hash helper — checks which photos are already OCR'd.

Usage:
    python cache_check.py <photos_dir>

Output (stdout, JSON):
    {
      "total": 28,
      "cached": [{"photo": "...", "hash": "abc123", "screen_type": "..."}, ...],
      "needs_ocr": [{"photo": "...", "hash": "def456", "path": "C:\\..."}, ...]
    }

Claude di window CC pakai output ini untuk skip Read foto yang sudah ada di cache.
Cache file: sandbox2/data/ocr_cache_v45/{first16chars_sha256}.json
"""
import sys, json, hashlib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "data" / "ocr_cache_v45"
PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def photo_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def main():
    if len(sys.argv) < 2:
        print("Usage: python cache_check.py <photos_dir>", file=sys.stderr)
        sys.exit(1)

    photos_dir = Path(sys.argv[1])
    if not photos_dir.exists():
        print(f"Folder not found: {photos_dir}", file=sys.stderr)
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    photos = sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in PHOTO_EXTS)
    cached, needs = [], []

    for p in photos:
        h = photo_hash(p)
        cache_file = CACHE_DIR / f"{h}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                cached.append({
                    "photo": p.name,
                    "hash": h,
                    "screen_type": data.get("screen_type", "?"),
                    "cache_file": str(cache_file),
                })
            except Exception:
                needs.append({"photo": p.name, "hash": h, "path": str(p)})
        else:
            needs.append({"photo": p.name, "hash": h, "path": str(p)})

    result = {
        "total": len(photos),
        "cached_count": len(cached),
        "needs_ocr_count": len(needs),
        "cached": cached,
        "needs_ocr": needs,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def save_to_cache(photo_path: Path, ocr_data: dict):
    """Helper: dipanggil dari Claude (manual) atau script lain untuk simpan hasil OCR ke cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = photo_hash(photo_path)
    cf = CACHE_DIR / f"{h}.json"
    cf.write_text(json.dumps(ocr_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(cf)


if __name__ == "__main__":
    main()
