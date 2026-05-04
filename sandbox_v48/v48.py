"""V4.8 Entry Point — MD → HTML/PDF.

Phase 2: cover + TOC + pengantar + bazi + karakter + tahunan + ringkasan
         + generic section catchall for any other topic + UNKNOWN sections.

Usage:
    python v48.py <md_file>
"""
import sys
import time
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from canonical_model import (
    Canonical, UnknownSection, validate
)
from extractors.md_utils import split_sections, split_sections_deep
from extractors.subject import extract_subject
from extractors.bazi import extract_bazi, derive_penguasa_hari, derive_elemen_utama
from extractors.karakter import extract_karakter
from extractors.tahunan import extract_tahunan
from extractors.ringkasan import extract_ringkasan
from extractors.ziwei import extract_ziwei
from extractors.istana_detail import extract_istana_details, get_consumed_h2_titles
from extractors.fengshui import extract_fengshui
from lookups.topic_taxonomy import detect_topic

from templates.cover import render_cover, COVER_CSS
from templates.page_shell import page_shell, PAGE_SHELL_CSS
from templates.toc import render_toc, TOC_CSS
from templates.pengantar import render_pengantar, PENGANTAR_CSS
from templates.bazi_page import render_bazi_page, BAZI_PAGE_CSS
from templates.karakter_page import render_karakter_page, KARAKTER_PAGE_CSS
from templates.tahunan_page import render_tahunan_pages, TAHUNAN_PAGE_CSS
from templates.ringkasan_page import render_ringkasan_pages, RINGKASAN_PAGE_CSS
from templates.ziwei_page import render_ziwei_page, ZIWEI_PAGE_CSS
from templates.istana_detail_page import render_istana_detail_pages, ISTANA_DETAIL_CSS
from templates.fengshui_page import render_fengshui_page, FENGSHUI_PAGE_CSS
from templates.takdir_page import render_takdir_page, TAKDIR_PAGE_CSS
from templates.hikmat_page import render_hikmat_page, HIKMAT_PAGE_CSS
from templates.glossary_page import render_glossary_pages, GLOSSARY_PAGE_CSS
from templates.disclaimer_page import render_disclaimer_page, DISCLAIMER_PAGE_CSS
from extractors.takdir import extract_takdir
from extractors.hikmat import extract_hikmat
from templates.generic_section import render_generic_page, GENERIC_PAGE_CSS
from templates.primitives import PRIMITIVES_CSS


TODAY = time.strftime("%Y-%m-%d")
RESULT_DIR = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\#result") / TODAY / "_test_v48"


# Map topic → (section_label, default_title_id, default_title_hz, page-builder)
LIFE_AREA_LABELS = {
    "karir":         ("Karir & Profesi",        "事 業 官 祿", "KARIR · 事業"),
    "keuangan":      ("Keuangan & Kekayaan",    "財 帛 財 富", "KEUANGAN · 財富"),
    "properti":      ("Properti & Rumah",       "田 宅",       "PROPERTI · 田宅"),
    "fengshui":      ("Feng Shui Rumah",        "陽 宅",       "FENG SHUI · 陽宅"),
    "pernikahan":    ("Cinta & Pernikahan",     "夫 妻 婚 配", "PERNIKAHAN · 夫妻"),
    "kecocokan_shio":("Kecocokan Shio Pasangan","婚 配",       "KECOCOKAN · 婚配"),
    "anak":          ("Anak & Keturunan",       "子 女",       "ANAK · 子女"),
    "kesehatan":     ("Kesehatan & Tubuh",      "疾 厄",       "KESEHATAN · 疾厄"),
    "orangtua":      ("Orang Tua",              "父 母",       "ORANG TUA · 父母"),
    "saudara":       ("Saudara & Persahabatan", "兄 弟",       "SAUDARA · 兄弟"),
    "bawahan":       ("Bawahan & Rekan Kerja",  "僕 役",       "BAWAHAN · 僕役"),
    "perpindahan":   ("Perpindahan & Mobilitas","遷 移",       "PERPINDAHAN · 遷移"),
    "peruntungan":   ("Peruntungan & Kebajikan","福 德",       "PERUNTUNGAN · 福德"),
    "shensha":       ("Bintang Khusus",         "神 煞",       "SHEN SHA · 神煞"),
    "takdir":        ("Takdir & Misi Hidup",    "宿 命",       "TAKDIR · 宿命"),
    "hikmat_klasik": ("Hikmat Klasik",          "古 書 云",    "HIKMAT · 古書云"),
    "ziwei":         ("Peta Bintang Zi Wei",    "紫 微 命 盤", "ZI WEI · 紫微"),
    "ziwei_palace_collection": ("Detail 12 Istana", "十 二 宮", "ZI WEI · 12 宮"),
    "da_yun":        ("Siklus Besar",           "大 運",       "DA YUN · 大運"),
    "tabel_tahunan": ("Tabel Nasib Tahunan",    "流 年 易 鑒", "TABEL TAHUNAN · 流年"),
    "glosarium":     ("Glosarium Istilah",      "詞 彙 表",   "GLOSARIUM · 詞彙"),
}

# Skip these topics — handled by dedicated extractors/templates
SKIP_AS_GENERIC = {"subject", "header_meta", "epilogue_meta",
                   "bazi", "karakter", "tahunan", "ringkasan", "ziwei",
                   "ziwei_palace_collection", "fengshui", "takdir", "hikmat_klasik"}


def extract_all(md_path: Path) -> Canonical:
    md_text = md_path.read_text(encoding='utf-8')
    canonical = Canonical()
    canonical.md_source = str(md_path)
    h2_sections = split_sections_deep(md_text)  # H2 keeps all H3 children inside .lines
    all_lines = md_text.split("\n")

    canonical.subject = extract_subject(md_text)
    canonical.bazi = extract_bazi(h2_sections, all_lines)
    canonical.karakter = extract_karakter(h2_sections)
    canonical.tahunan = extract_tahunan(h2_sections)
    canonical.ringkasan = extract_ringkasan(h2_sections)
    canonical.ziwei = extract_ziwei(h2_sections)
    canonical.feng_shui = extract_fengshui(h2_sections)
    canonical.takdir = extract_takdir(h2_sections)
    canonical.hikmat_bundle = extract_hikmat(h2_sections)

    return canonical, h2_sections


def print_validation_report(canonical: Canonical, h2_sections):
    """Validation report with extra unknown topic detection."""
    # Detect topics for all H2
    topics_found = []
    unknown_titles = []
    for s in h2_sections:
        topic = detect_topic(s["title"])
        if topic == "UNKNOWN":
            unknown_titles.append(s["title"])
        topics_found.append((topic, s["title"]))

    print()
    print("┌─ V4.8 Extraction Report " + "─" * 60)
    print(f"│  Source: {canonical.md_source}")
    print("│")

    report = validate(canonical)
    if report["recognized"]:
        print(f"│  ✓ Extracted ({len(report['recognized'])}):")
        for r in report["recognized"]:
            print(f"│      • {r}")
        print("│")
    if report["missing_critical"]:
        print(f"│  ✗ MISSING CRITICAL:")
        for m in report["missing_critical"]:
            print(f"│      ! {m}")
        print("│")
    if unknown_titles:
        print(f"│  ? UNKNOWN topics ({len(unknown_titles)}) — akan render via generic template:")
        for t in unknown_titles:
            print(f"│      ? {t}")
        print("│")
    print(f"│  → Section count: {len(h2_sections)}, recognized topics: {len([t for t,_ in topics_found if t != 'UNKNOWN'])}")
    print("└" + "─" * 85)


def render_all_pages(canonical: Canonical, h2_sections):
    """Render full document. Returns (list[html_pages], pn)."""
    subject_name = canonical.subject.nama or "Subject"
    pages = []
    pn = 1

    # Cover (page 1)
    penguasa_hari = derive_penguasa_hari(canonical.bazi)
    elemen_utama = derive_elemen_utama(canonical.bazi)
    pages.append(render_cover(canonical.subject,
                              bazi=canonical.bazi,
                              penguasa_hari=penguasa_hari,
                              elemen_utama=elemen_utama))
    pn += 1

    # Pre-compute TOC page count: 3 fixed (pengantar/bazi/karakter)
    # + N generic sections (skip handled-by-extractor topics + tahunan)
    # + 1 (tahunan group) + 1 (kesimpulan) = total entries
    n_sections = sum(1 for s in h2_sections
                     if detect_topic(s["title"]) not in SKIP_AS_GENERIC | {"tahunan"})
    estimated_entries = 3 + n_sections + 2 + 1  # +1 for ziwei page if present
    toc_pages_needed = 2 if (estimated_entries + 11) > 50 else 1  # 6 groups * 1.8 ≈ 11
    toc_pn = pn; pn += toc_pages_needed

    # Pengantar
    pengantar_pn = pn
    pages.append(render_pengantar(pn, subject_name))
    pn += 1

    # BaZi page
    bazi_pn = pn
    pages.append(render_bazi_page(pn, canonical.bazi, subject_name))
    pn += 1

    # Karakter page
    karakter_pn = pn
    pages.append(render_karakter_page(pn, canonical.karakter, subject_name))
    pn += 1

    # ZiWei page (kalau extractor punya data)
    ziwei_pn = None
    if canonical.ziwei:
        ziwei_pn = pn
        pages.append(render_ziwei_page(pn, canonical.ziwei, subject_name))
        pn += 1

    # Istana Detail pages (kalau MD punya BAGIAN INTERPRETASI DETAIL SETIAP ISTANA)
    istana_detail_palaces, istana_detail_section_title = extract_istana_details(h2_sections)
    istana_detail_pn = None
    if istana_detail_palaces:
        istana_detail_pn = pn
        idp, pn = render_istana_detail_pages(pn, istana_detail_palaces, subject_name)
        pages.extend(idp)

    # FengShui Rumah page (kalau MD punya feng shui section)
    fengshui_pn = None
    if canonical.feng_shui:
        fengshui_pn = pn
        pages.append(render_fengshui_page(pn, canonical.feng_shui, subject_name))
        pn += 1

    takdir_pn = None
    hikmat_pn = None

    # H2 titles consumed by istana_detail (to skip from generic)
    consumed_istana_titles = get_consumed_h2_titles(h2_sections)

    # Generic life-area + UNKNOWN sections (in MD order)
    section_pages = []  # [(topic, title_id, page_num)] for TOC
    for s in h2_sections:
        topic = detect_topic(s["title"])
        if topic in SKIP_AS_GENERIC:
            continue
        if topic == "tahunan":
            continue  # rendered separately below
        if s.get("raw_title", "") in consumed_istana_titles:
            continue  # already rendered in istana_detail collection
        # Resolve labels
        if topic in LIFE_AREA_LABELS:
            title_id, title_hz, sec_label = LIFE_AREA_LABELS[topic]
        else:
            # Unknown topic — keep raw title (cleaned)
            raw = s["title"]
            # Try to split (Hanzi) if any
            m = re.search(r"([一-鿿\s]+)", raw)
            title_hz = (m.group(0).strip() if m else "").strip()
            title_id = re.sub(r"[一-鿿]+", "", raw).strip(" /()-—–")
            if not title_id:
                title_id = raw
            sec_label = "BAGIAN TAMBAHAN · " + (title_hz or "")
        page_html = render_generic_page(pn, title_id, title_hz, sec_label, s["lines"], subject_name, all_sections=h2_sections, section=s)
        pages.append(page_html)
        section_pages.append((topic, title_id, title_hz, pn))
        pn += 1

    # Takdir & Misi Hidup (after generic Aspek Kehidupan, before Tahunan)
    if canonical.takdir:
        takdir_pn = pn
        pages.append(render_takdir_page(pn, canonical.takdir, subject_name))
        pn += 1

    # Tahunan pages
    tahunan_pn = pn
    tahunan_pages, pn = render_tahunan_pages(pn, canonical.tahunan, subject_name)
    pages.extend(tahunan_pages)

    # Hikmat Klasik (after Tahunan, before Kesimpulan)
    if canonical.hikmat_bundle:
        hikmat_pn = pn
        pages.append(render_hikmat_page(pn, canonical.hikmat_bundle, subject_name))
        pn += 1

    # Ringkasan pages
    ringkasan_pn = pn
    ringkasan_pages, pn = render_ringkasan_pages(pn, canonical.ringkasan, subject_name)
    pages.extend(ringkasan_pages)

    # Glossary (2 halaman) — penultimate
    glossary_pn = pn
    glossary_pages, pn = render_glossary_pages(pn, subject_name)
    pages.extend(glossary_pages)

    # Disclaimer — last page
    disclaimer_pn = pn
    pages.append(render_disclaimer_page(pn, subject_name))
    pn += 1

    # Build TOC entries (each tagged with topic for category grouping)
    toc_entries = [
        {"topic": "pengantar", "title": "Pengantar & Cara Membaca", "hz": "前 言",       "page": pengantar_pn},
        {"topic": "bazi",      "title": "Empat Pilar Kelahiran",     "hz": "四 柱 八 字", "page": bazi_pn},
        {"topic": "karakter",  "title": "Karakter & Kepribadian",    "hz": "性 情",       "page": karakter_pn},
    ]
    if ziwei_pn:
        toc_entries.append({"topic": "ziwei", "title": "Peta Bintang Zi Wei", "hz": "紫 微 命 盤", "page": ziwei_pn})
    if istana_detail_pn:
        toc_entries.append({"topic": "ziwei_palace_collection", "title": "Detail 12 Istana Hidup", "hz": "十 二 宮 詳 解", "page": istana_detail_pn})
    if fengshui_pn:
        toc_entries.append({"topic": "fengshui", "title": "Feng Shui Rumah", "hz": "陽 宅", "page": fengshui_pn})
    if takdir_pn:
        toc_entries.append({"topic": "takdir", "title": "Takdir & Misi Hidup", "hz": "宿 命", "page": takdir_pn})
    if hikmat_pn:
        toc_entries.append({"topic": "hikmat_klasik", "title": "Hikmat Klasik", "hz": "古 書 云", "page": hikmat_pn})
    for topic, title_id, title_hz, p in section_pages:
        toc_entries.append({"topic": topic, "title": title_id, "hz": title_hz, "page": p})
    toc_entries.append({"topic": "tahunan",  "title": "Ramalan Tahunan",         "hz": "流 年 判 斷", "page": tahunan_pn})
    toc_entries.append({"topic": "kesimpulan","title": "Kesimpulan & Saran Praktis","hz": "結 語 · 建 議", "page": ringkasan_pn})
    toc_entries.append({"topic": "glossary",  "title": "Daftar Istilah",            "hz": "辭 典",       "page": glossary_pn})
    toc_entries.append({"topic": "disclaimer","title": "Disclaimer & Etika",        "hz": "告 白",       "page": disclaimer_pn})

    # Insert TOC page(s) at index 1 (may be 1 or 2 pages depending on density)
    toc_pages, _ = render_toc(toc_pn, toc_entries, subject_name)
    for i, p in enumerate(toc_pages):
        pages.insert(1 + i, p)

    return pages


def assemble_html(pages, subject_name="Subject") -> str:
    tokens_css = (ROOT / "design_system" / "tokens.css").read_text(encoding='utf-8')
    # Google Fonts @import — blocking, ensures Chrome loads + embeds fonts in PDF.
    # @import (vs <link>) blocks rendering until fonts ready → embedded fonts in PDF
    # work portably across desktop, mobile, all PDF readers.
    fonts_import = (
        "@import url('https://fonts.googleapis.com/css2?"
        "family=Inter:wght@400;500;600&"
        "family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&"
        "family=Noto+Serif+SC:wght@400;500;600;700&"
        "family=Noto+Serif+TC:wght@400;500;600;700&"
        "display=swap');"
    )
    full_css = "\n".join([
        fonts_import,
        tokens_css,
        PRIMITIVES_CSS,
        PAGE_SHELL_CSS,
        COVER_CSS,
        TOC_CSS,
        PENGANTAR_CSS,
        BAZI_PAGE_CSS,
        KARAKTER_PAGE_CSS,
        ZIWEI_PAGE_CSS,
        ISTANA_DETAIL_CSS,
        FENGSHUI_PAGE_CSS,
        TAKDIR_PAGE_CSS,
        HIKMAT_PAGE_CSS,
        TAHUNAN_PAGE_CSS,
        RINGKASAN_PAGE_CSS,
        GLOSSARY_PAGE_CSS,
        DISCLAIMER_PAGE_CSS,
        GENERIC_PAGE_CSS,
    ])
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{subject_name} — Laporan Ramalan (V4.8)</title>
<style>
{full_css}
</style>
</head>
<body>
{"".join(pages)}
</body>
</html>"""


def safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name).strip("_") or "subject"


def main():
    if len(sys.argv) < 2:
        print("Usage: python v48.py <md_file>")
        sys.exit(1)
    md_path = Path(sys.argv[1]).resolve()
    if not md_path.exists():
        print(f"Error: {md_path} not found"); sys.exit(1)

    print(f"\n[V4.8] Extracting from: {md_path.name}")
    canonical, h2_sections = extract_all(md_path)
    print_validation_report(canonical, h2_sections)

    pages = render_all_pages(canonical, h2_sections)
    html = assemble_html(pages, canonical.subject.nama or md_path.stem)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    name = safe_filename(canonical.subject.nama or md_path.stem)
    out_html = RESULT_DIR / f"full_{name}.html"
    out_html.write_text(html, encoding='utf-8-sig')  # BOM required for Chrome PDF + @font-face
    print(f"\n  → HTML: {out_html} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
