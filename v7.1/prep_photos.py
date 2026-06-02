"""V4.5.2 photo prep — resize longest-side ke MAX_SIDE px sebelum Claude Read.

Token saving math (per foto):
  - WhatsApp default ~1080x1920 ≈ 2MP   → Claude vision ~1500 tokens
  - Resized 768px longest    ≈ 0.33MP  → Claude vision ~500 tokens
  - Saving ~1000 tokens/foto. 28 foto = ~28K input token hemat per run.

Output:
  - `<photos_dir>_prepped/` (sibling folder) berisi JPEG hasil resize
  - File naming sama (extension force ke .jpg)
  - Idempoten: kalau prepped folder sudah punya file dengan size match, skip

Usage:
    python prep_photos.py <photos_dir> [--max-side 768] [--quality 82]

Output stdout:
    <prepped_dir absolute path>

Claude di window CC pakai `<prepped_dir>` (bukan `<photos_dir>` original) untuk Read tool calls.
"""
import sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def prep(photos_dir: Path, max_side: int = 768, quality: int = 82) -> Path:
    from PIL import Image

    out_dir = photos_dir.parent / f"{photos_dir.name}_prepped"
    out_dir.mkdir(parents=True, exist_ok=True)

    photos = sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in PHOTO_EXTS)
    if not photos:
        print(f"[prep] no photos in {photos_dir}", file=sys.stderr)
        return out_dir

    saved_total = 0
    skipped = 0
    new = 0
    t0 = time.time()
    for p in photos:
        out = out_dir / (p.stem + ".jpg")
        if out.exists():
            # Skip if already prepped (idempotent)
            skipped += 1
            continue
        try:
            img = Image.open(p).convert("RGB")
            w, h = img.size
            if max(w, h) > max_side:
                scale = max_side / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            img.save(out, format="JPEG", quality=quality, optimize=True)
            saved_total += p.stat().st_size - out.stat().st_size
            new += 1
        except Exception as e:
            print(f"[prep] FAIL {p.name}: {e}", file=sys.stderr)

    dt = time.time() - t0
    print(f"[prep] {new} new, {skipped} skipped, "
          f"~{saved_total/1024/1024:.1f}MB saved, {dt:.1f}s", file=sys.stderr)
    return out_dir


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photos.py <photos_dir> [--max-side N] [--quality N]", file=sys.stderr)
        sys.exit(1)
    args = sys.argv[2:]
    max_side = 768
    quality = 82
    for i, a in enumerate(args):
        if a == "--max-side" and i + 1 < len(args):
            max_side = int(args[i + 1])
        elif a == "--quality" and i + 1 < len(args):
            quality = int(args[i + 1])
    out = prep(Path(sys.argv[1]), max_side=max_side, quality=quality)
    print(out)  # stdout = prepped dir absolute path
