"""Crop panels dari foto BaZi grid + enhance + per-row split.

Software Xing Qiao layout (fixed UI dalam window):
- Panel 先天體檢: kiri-atas, ~10% lebar × 60% tinggi (TIGHT crop)
- Panel 喜用神:   kiri-bawah, ~10% lebar × 25% tinggi
- Panel 八字 grid: tengah, ~50% lebar × 35% tinggi

Strategi:
1. Tight crop (sesuai user-verified crop yang clear) + PIL enhance (contrast + sharpness)
2. Per-row split panel 先天體檢 → 10 mini-images, agen baca per-row dengan full attention
3. Upscale 2x untuk crops kecil supaya glyph lebih besar

Usage:
  python crop_panels.py {foto_path} {out_dir}
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageEnhance


def enhance(img: Image.Image, contrast: float = 1.4, sharpness: float = 2.0) -> Image.Image:
    """Boost contrast + sharpness, bantu cyan-on-blue glyph jadi crisp."""
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)
    return img


def upscale(img: Image.Image, factor: float = 2.0) -> Image.Image:
    """Upscale dengan LANCZOS (high-quality bicubic-like)."""
    w, h = img.size
    return img.resize((int(w * factor), int(h * factor)), Image.LANCZOS)


def crop_panels(foto_path: Path, out_dir: Path) -> dict[str, Path]:
    """Crop 3 panel + per-row split. Return dict nama → path."""
    img = Image.open(foto_path)
    W, H = img.size

    # TIGHT crop area (panel content only, mimick user's manual crop)
    # Panel 先天體檢: x=4-18%, y=10-72% (10 rows). y_start lowered to 0.10 to capture 甲膽 digit fully.
    xt_box = (int(0.04 * W), int(0.10 * H), int(0.20 * W), int(0.72 * H))
    xt = img.crop(xt_box)
    xt = enhance(xt)
    xt = upscale(xt, 2.0)

    # Panel 喜用神: x=4-18%, y=68-90% (5 rows)
    xy_box = (int(0.04 * W), int(0.68 * H), int(0.20 * W), int(0.90 * H))
    xy = img.crop(xy_box)
    xy = enhance(xy)
    xy = upscale(xy, 2.0)

    # Panel 八字 grid (4 pillars + 人元): x=22-78%, y=10-58%
    bz_box = (int(0.22 * W), int(0.10 * H), int(0.78 * W), int(0.58 * H))
    bz = img.crop(bz_box)
    bz = enhance(bz)
    # bazi grid sudah cukup besar, no upscale

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = foto_path.stem.replace(" ", "_")[:40]
    paths = {}
    for name, crop in [("xiantian", xt), ("xiyong", xy), ("bazi", bz)]:
        out_path = out_dir / f"{stem}__{name}.jpg"
        crop.save(out_path, quality=95)
        paths[name] = out_path

    # Per-row split panel 先天體檢 (10 rows, each ~6% of foto height)
    # Row N (1..10): y from row_y_start[N-1] to row_y_end[N-1]
    xt_W, xt_H = xt.size  # already 2x upscaled
    row_height = xt_H / 10
    rows_dir = out_dir / f"{stem}__rows"
    rows_dir.mkdir(exist_ok=True)
    organ_names = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]
    for i, name in enumerate(organ_names):
        y0 = int(i * row_height)
        y1 = int((i + 1) * row_height) + 5  # tiny overlap
        row = xt.crop((0, max(0, y0), xt_W, min(xt_H, y1)))
        row = upscale(row, 1.5)  # extra upscale for tiny rows
        row_path = rows_dir / f"row{i+1:02d}_{name}.jpg"
        row.save(row_path, quality=95)
        paths[f"row_{name}"] = row_path

    return paths


def main():
    if len(sys.argv) != 3:
        print("usage: crop_panels.py {foto_path} {out_dir}")
        sys.exit(1)
    foto = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    paths = crop_panels(foto, out_dir)
    panel_paths = {k: v for k, v in paths.items() if not k.startswith("row_")}
    for name, p in panel_paths.items():
        print(f"  {name}: {p}")
    print(f"  + 10 row crops in {paths['row_jia'].parent}/")


if __name__ == "__main__":
    main()
