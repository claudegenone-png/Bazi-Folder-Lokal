"""V7.1 narrative_crop.py - Auto-enhance narrative photos before vision Read.

Ported from v9 (2026-05-24). Purpose: tajam-kan foto narasi (palace/liu_nian/dll)
sebelum dibaca main agent vision, mencegah halusinasi karena foto buram.

Default params (proven di V9 test):
- Contrast 1.5 (range V7.1 AUTORUN 1.4-1.6)
- Sharpness 2.2 (range V7.1 AUTORUN 2.0-2.5)
- Upscale 2x LANCZOS (range V7.1 AUTORUN 2-3x)
- JPEG quality 92

Usage:
    python narrative_crop.py <photos_dir> <output_dir>
    python narrative_crop.py <single_photo> <single_output>

Output: <stem>_enh.jpg in output_dir (or output as single file if single input).
"""
import sys
from pathlib import Path
from PIL import Image, ImageEnhance

DEFAULT_CONTRAST = 1.5
DEFAULT_SHARPNESS = 2.2
DEFAULT_UPSCALE = 2
JPEG_QUALITY = 92
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def enhance_photo(src_path, out_path, contrast=DEFAULT_CONTRAST,
                  sharpness=DEFAULT_SHARPNESS, upscale=DEFAULT_UPSCALE):
    """Enhance single photo + save to out_path. Returns dict with metadata."""
    src_path = Path(src_path)
    out_path = Path(out_path)
    img = Image.open(src_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    orig_size = img.size
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)
    new_size = (orig_size[0] * upscale, orig_size[1] * upscale)
    img = img.resize(new_size, Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=JPEG_QUALITY)
    return {
        "src": str(src_path),
        "out": str(out_path),
        "orig_size": orig_size,
        "enh_size": new_size,
        "out_kb": out_path.stat().st_size // 1024,
    }


def enhance_folder(photos_dir, output_dir):
    """Enhance all supported photos in folder. Returns list of result dicts."""
    photos_dir = Path(photos_dir)
    output_dir = Path(output_dir)
    photos = sorted([
        p for p in photos_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ])
    results = []
    for p in photos:
        out_path = output_dir / (p.stem + "_enh.jpg")
        try:
            res = enhance_photo(p, out_path)
            results.append(res)
        except Exception as e:
            results.append({"src": str(p), "error": str(e)})
    return results


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python narrative_crop.py <photos_dir|photo> <output_dir|output>\n")
        sys.exit(2)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    if not src.exists():
        sys.stderr.write("Source not found: " + str(src) + "\n")
        sys.exit(2)
    if src.is_file():
        if src.suffix.lower() not in SUPPORTED_EXTS:
            sys.stderr.write("Unsupported extension: " + src.suffix + "\n")
            sys.exit(2)
        res = enhance_photo(src, dst)
        print("[narrative_crop] enhanced 1 photo")
        print("  " + Path(res["src"]).name + ":",
              res["orig_size"], "->", res["enh_size"],
              "(" + str(res["out_kb"]) + " KB)")
    else:
        print("[narrative_crop] enhance from", src, "->", dst)
        results = enhance_folder(src, dst)
        ok = [r for r in results if "error" not in r]
        errs = [r for r in results if "error" in r]
        print("[narrative_crop] DONE -", len(ok), "ok,", len(errs), "errors")
        for r in ok[:3]:
            print("  " + Path(r["src"]).name + ":",
                  r["orig_size"], "->", r["enh_size"],
                  "(" + str(r["out_kb"]) + " KB)")
        if len(ok) > 3:
            print("  ... and", len(ok) - 3, "more")
        for r in errs:
            print("  [ERR]", Path(r["src"]).name + ":", r["error"])
        if errs:
            sys.exit(1)


if __name__ == "__main__":
    main()
