"""V4.5 cache write helper — Claude pakai untuk simpan OCR hasil per foto.

Usage (dari Claude window setelah parse hasil Read tool):
    python cache_save.py <photo_path> '<json_string>'

Atau pipe:
    echo '{...}' | python cache_save.py <photo_path>
"""
import sys, json, hashlib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "data" / "ocr_cache_v45"


def photo_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def main():
    if len(sys.argv) < 2:
        print("Usage: python cache_save.py <photo_path> [<json_string>]", file=sys.stderr)
        sys.exit(1)

    photo = Path(sys.argv[1])
    if not photo.exists():
        print(f"Photo not found: {photo}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        raw = sys.argv[2]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = photo_hash(photo)
    cf = CACHE_DIR / f"{h}.json"
    data["_photo"] = photo.name
    data["_hash"] = h
    cf.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {cf}")


if __name__ == "__main__":
    main()
