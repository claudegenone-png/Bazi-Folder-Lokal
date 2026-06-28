"""Build PDF khusus Feng Shui Hunian — 8 halaman.

PAGE ORDER:
  1. page_cover_fengshui  — cover simplified (identitas + judul)
  2. page_bagua_grid      — 八卦 Ringkasan Grid (foto 1)
  3. page_bagua_rect      — 八卦 Peta Radial / Codex rectangular chart (foto 2)
  4. page_bagua_octagon   — 八卦 Analisis Lengkap Oktagon / Codex 5-ring chart (foto 4)
  5. page_hongshui_pair_1 — Pair 1: foto 3 + foto 5
  6. page_hongshui_pair_2 — Pair 2: foto 6 + foto 7
  7. page_hongshui_pair_3 — Pair 3: foto 8 + foto 9
  8. page_hongshui_pair_4 — Pair 4: foto 10 + foto 12

Usage:
  python build_fengshui_pdf.py linxiumei
"""
import sys, time, json, re, shutil, os, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engines"))
sys.dont_write_bytecode = True
try:
    import shutil as _sh
    for _r, _ds, _fs in os.walk(str(ROOT)):
        if "__pycache__" in _ds:
            _sh.rmtree(os.path.join(_r, "__pycache__"), ignore_errors=True)
except Exception:
    pass

from build_from_ocr import build_subject_from_ocr
from render import (
    _normalize_subject_for_render, build_substitutions,
    apply_blocks, inject_tafsir_blocks, build_master, run_chrome,
    TEMPLATES_DIR, ASSETS_DIR, BUILD_DIR, DATA_DIR,
    _HONGSHUI_PAIR_MAP, _HONGSHUI_PAIR_TEMPLATE,
    _apply_toc_dynamic, EM_DASH
)
from parse_md import parse_md, md_inline
from bagua_svg import (render_bagua_rect_svg, render_bagua_octagon_svg,
                       render_bagua_rect_svg_v11, render_bagua_octagon_svg_v11,
                       _inject_bagua_rect_panel, _inject_bagua_oct_panel)

# ── Fixed 8-page order ──────────────────────────────────────────
FS_PAGE_ORDER = [
    "page_cover_fengshui.html",      # hal 1 — cover
    "page_bagua_grid.html",           # hal 2 — ringkasan 8 sektor
    "page_bagua_rect.html",           # hal 3 — peta radial (Codex rectangular)
    "page_bagua_octagon.html",        # hal 4 — analisis oktagon (Codex 5-ring)
    "page_hongshui_pair_1.html",      # hal 5 — analisis 1+2 (foto 3+5)
    "page_hongshui_pair_2.html",      # hal 6 — analisis 3+4 (foto 6+7)
    "page_hongshui_pair_3.html",      # hal 7 — analisis 5+6 (foto 8+9)
    "page_hongshui_pair_4.html",      # hal 8 — cara menilai & perabot (foto 10+12)
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p): return p
    raise FileNotFoundError("Chrome/Edge not found")


def render_fengshui(subject: dict, tafsir_blocks: dict, out_dir: Path) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Detect skippable pages
    skip = set()
    raw_yz  = subject.get("yang_zhai") or {}
    raw_bg  = subject.get("bagua_sectors") or {}
    raw_hs  = subject.get("hongshui_pages") or {}

    if not raw_yz or not raw_yz.get("gua_hz"):
        skip.add("page_yangzhai.html")
    if not raw_bg:
        skip.add("page_bagua_grid.html")
        skip.add("page_bagua_rect.html")
        skip.add("page_bagua_octagon.html")

    def _hs_has(idx):
        return bool((raw_hs.get(idx) or {}).get("content_id", "").strip())

    for pfname, (li, ri) in _HONGSHUI_PAIR_MAP.items():
        if not _hs_has(li) and not _hs_has(ri):
            skip.add(pfname)

    subject = _normalize_subject_for_render(subject)
    pairs   = build_substitutions(subject)

    # Extra cover substitutions
    iden = subject.get("identity") or {}
    bagua = subject.get("bagua_sectors") or {}
    life_type_hz = subject.get("bagua_life_type_hz") or "—"
    life_type_id = subject.get("bagua_life_type_id") or ""

    # Build birth date in Indonesian
    try:
        bd = iden.get("birth_date", "1900-01-01")
        y, m, d = bd.split("-")
        months = ["","Januari","Februari","Maret","April","Mei","Juni",
                  "Juli","Agustus","September","Oktober","November","Desember"]
        birth_date_id = f"{int(d)} {months[int(m)]} {int(y)}"
    except Exception:
        birth_date_id = iden.get("birth_date", "—")

    shio = subject.get("shio") or {}

    cover_subs = {
        "{{SUBJECT_NAME_HZ}}":       iden.get("name_hanzi") or "—",
        "{{SUBJECT_NAME_FULL}}":     iden.get("name_id")    or "—",
        "{{SUBJECT_BIRTH_DATE_ID}}": birth_date_id,
        "{{SUBJECT_BIRTH_TIME}}":    iden.get("birth_time") or "—",
        "{{SUBJECT_SHIO_BRANCH_HZ}}":shio.get("branch_hz") or "—",
        "{{SUBJECT_SHIO_ID_TITLE}}": shio.get("id")         or "—",
        "{{BAGUA_LIFE_TYPE_HZ}}":    life_type_hz,
        "{{BAGUA_LIFE_TYPE_ID}}":    life_type_id,
    }

    active = [f for f in FS_PAGE_ORDER if f not in skip]
    page_num_map = {f: i + 1 for i, f in enumerate(active)}
    total = len(active)

    rendered = []
    for fname in FS_PAGE_ORDER:
        if fname in skip:
            print(f"  [SKIP] {fname}")
            continue

        # Choose source template
        if fname == "page_cover_fengshui.html":
            src = TEMPLATES_DIR / "page_cover_fengshui.html"
        elif fname in _HONGSHUI_PAIR_MAP:
            src = TEMPLATES_DIR / _HONGSHUI_PAIR_TEMPLATE
        else:
            src = TEMPLATES_DIR / fname

        if not src.exists():
            print(f"  [WARN] missing template: {fname}")
            continue

        content = src.read_text(encoding="utf-8")

        # Apply standard substitutions (except cover which uses custom subs)
        if fname != "page_cover_fengshui.html":
            for search, replace in pairs:
                if search and search != replace:
                    content = content.replace(search, replace)
            content = apply_blocks(content, subject, fname)
            content = inject_tafsir_blocks(content, tafsir_blocks)
            # Bagua SVG + data injection
            if fname == "page_bagua_rect.html":
                sectors = subject.get("bagua_sectors") or {}
                content = content.replace("{{BAGUA_RECT_SVG}}", render_bagua_rect_svg_v11(sectors))
                content = _inject_bagua_rect_panel(content, subject)
            elif fname == "page_bagua_octagon.html":
                sectors = subject.get("bagua_sectors") or {}
                content = content.replace("{{BAGUA_OCTAGON_SVG}}", render_bagua_octagon_svg_v11(sectors))
                content = _inject_bagua_oct_panel(content, subject)
        else:
            # Cover: apply custom subs only
            for k, v in cover_subs.items():
                content = content.replace(k, str(v))

        # Page numbering
        my_num = page_num_map.get(fname, 0)
        content = content.replace("{{PAGE_NUM}}", str(my_num))
        content = content.replace("{{TOTAL_PAGES}}", str(total))
        content = content.replace("{{PAGE_NUM_PADDED}}", f"{my_num:02d}")
        # Clear unused TOC range placeholders
        for ph in ["{{SECTION_PENDAHULUAN_RANGE}}","{{SECTION_BAZI_RANGE}}",
                   "{{SECTION_ZIWEI_RANGE}}","{{SECTION_PENUTUP_RANGE}}",
                   "{{PAGE_GLOSSARY_NUM}}","{{PAGE_DISCLAIMER_NUM}}"]:
            content = content.replace(ph, "—")

        # Remove page number footer (fengshui build — page nums not needed)
        content = re.sub(r'<div class="pg-num">.*?</div>', '', content)

        dst = out_dir / fname
        dst.write_text(content, encoding="utf-8")
        rendered.append(dst)
        print(f"  [OK] {fname} (hal {my_num}/{total})")

    return rendered


def build_fs_master(out_dir: Path, subject: dict) -> Path:
    name = subject["identity"]["name_id"]
    asset_url = "file:///" + str(ASSETS_DIR).replace("\\", "/") + "/"
    css_url   = "file:///" + str(out_dir / "style.css").replace("\\", "/")
    shutil.copy(TEMPLATES_DIR / "style.css", out_dir / "style.css")

    styles, bodies = "", ""
    for fname in FS_PAGE_ORDER:
        path = out_dir / fname
        if not path.exists(): continue
        content = path.read_text(encoding="utf-8")
        m_style = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
        if m_style:
            styles += f"\n/* === {fname} === */\n" + m_style.group(1) + "\n"
        m_body = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
        if m_body:
            body = m_body.group(1)
            body = re.sub(r'src="([^/"][^":]*\.(svg|png|jpg|jpeg))"',
                          lambda m: f'src="{asset_url}{m.group(1)}"', body)
            bodies += body + "\n"

    master = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{name} · Feng Shui Hunian</title>
<link rel="stylesheet" href="{css_url}">
<style>
{styles}
@page {{ size: A4 portrait; margin: 0; }}
html, body {{ background: white !important; margin: 0 !important; padding: 0 !important; }}
.page {{
  page-break-after: always !important;
  page-break-inside: avoid !important;
  margin: 0 !important; box-shadow: none !important;
}}
.page:last-child {{ page-break-after: auto !important; }}
</style>
</head>
<body>
{bodies}
</body>
</html>"""

    mp = out_dir / "_master_fengshui.html"
    mp.write_text(master, encoding="utf-8")
    return mp


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_fengshui_pdf.py <subject_id>")
        sys.exit(1)

    subject_id = sys.argv[1]
    t0 = time.time()

    # Parse MD
    md_path = DATA_DIR / f"{subject_id}.md"
    if not md_path.exists():
        print(f"MD not found: {md_path}"); sys.exit(1)

    print(f"=== Feng Shui PDF · {subject_id} ===")
    print(f"[1] Parsing MD...")
    ocr_data, tafsir_blocks, warns = parse_md(md_path)
    if warns:
        for w in warns: print(f"  ⚠ {w}")
    ocr_path = DATA_DIR / f"{subject_id}.ocr.json"
    ocr_path.write_text(json.dumps(ocr_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[2] Building subject...")
    subject = build_subject_from_ocr(subject_id)

    print(f"[3] Rendering {len(FS_PAGE_ORDER)} pages...")
    out_dir = BUILD_DIR / f"{subject_id}_fengshui"
    if out_dir.exists(): shutil.rmtree(out_dir)
    render_fengshui(subject, tafsir_blocks, out_dir)

    print(f"[4] Building master HTML...")
    master = build_fs_master(out_dir, subject)
    print(f"    {master.stat().st_size // 1024} KB")

    # Output PDF
    iden = subject["identity"]
    hanzi = (iden.get("name_hanzi") or "").strip()
    if hanzi in ("_", "-", "null", ""): hanzi = ""
    name  = iden.get("name_id", subject_id)
    birth = iden.get("birth_date", "")
    today = time.strftime("%Y-%m-%d")
    pdf_name = f"{name}-{hanzi}-FengShui-{birth}.pdf" if hanzi else f"{name}-FengShui-{birth}.pdf"
    out_pdf = ROOT.parent / "#result" / today / pdf_name

    print(f"[5] Chrome → PDF...")
    final = run_chrome(master, out_pdf)
    print(f"\n✓ DONE in {time.time()-t0:.1f}s")
    print(f"  PDF: {final}")
    print(f"  Size: {final.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
