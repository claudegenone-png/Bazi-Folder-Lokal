# -*- coding: utf-8 -*-
"""Per-page tester for V4.6 MD-driven build.

Usage: python test_page.py <md_file> <page_name> [page_name2 ...]
  page_name: cover | toc | pengantar | s1 | s2 | ... | s20 | skor | saran | gloss | disc

Renders only the requested pages → HTML + PDF for review.
"""
import sys, os, time, shutil, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Import everything from build.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B

ROOT = Path(__file__).resolve().parent

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_page.py <md_file> <page_name> [page_name2 ...]")
        print("page_name: cover | toc | pengantar | s1..s20 | skor | saran | gloss | disc")
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    pages_req = [a for a in sys.argv[2:] if not a.startswith("--")]
    md_text = md_path.read_text(encoding='utf-8')
    parsed = B.parse_md(md_text)
    subject_name = parsed["subject"].get("Nama", "Subject")

    # Build all section pages first to allow correct page numbering
    pn_map = {}  # name → start page
    # ADAPTIVE: dispatch per BAB by TOPIC (not number)
    # Each BAB has detected topic — get_builder_for_topic returns correct builder.

    pn = 4
    section_pages = {}  # num → list of page htmls
    page_starts = {}
    for sec in parsed["sections"]:
        n = sec["num"]
        topic = sec.get("topic", "generic")
        builder = B.get_builder_for_topic(topic)
        page_starts[n] = pn
        try:
            sps, pn = builder(sec, subject_name, pn)
        except Exception as e:
            print(f"!! Error section {n} (topic={topic}): {e}")
            sps = [B.page(pn, sec["title"], "", "ERROR", f"<div class='lead'>Error rendering: {e}</div>", subject_name)]
            pn += 1
        section_pages[n] = sps

    siklus_pn = pn
    siklus_html = B.build_tabel_siklus_besar(parsed, subject_name, pn); pn += 1
    kesimpulan_pn = pn
    kesimpulan_html = B.build_kesimpulan(parsed, subject_name, pn); pn += 1
    ringkasan_pn = pn
    ringkasan_pages = B.build_profil_saran(parsed, subject_name, pn); pn += len(ringkasan_pages)
    gloss_pn = pn
    gloss_pages = B.build_glossary(md_text, subject_name, pn); pn += len(gloss_pages)
    disc_pn = pn
    disc_html = B.build_disclaimer(subject_name, pn); pn += 1

    # Build TOC extras (Section VI Lampiran — sorted by page)
    extras = [
        {"label": "Siklus Besar Hidup",       "hz": "大 運", "page": siklus_pn,     "icon": "⟳"},
        {"label": "Kesimpulan Keseluruhan",   "hz": "結 論", "page": kesimpulan_pn, "icon": "✦"},
        {"label": "Saran Praktis",            "hz": "建 議", "page": ringkasan_pn,  "icon": "💡"},
        {"label": "Glosarium Istilah",        "hz": "詞 彙", "page": gloss_pn,      "icon": "📚"},
        {"label": "Disclaimer &amp; Etika",   "hz": "告 白", "page": disc_pn,       "icon": "⚖"},
    ]

    cover_html = B.build_cover(parsed["subject"], parsed["sections"])
    toc_html = B.build_toc(parsed["toc"], subject_name, page_starts, extras=extras)
    pengantar_html = B.build_pengantar(subject_name)

    selected = []
    for name in pages_req:
        if name == "cover": selected.append(cover_html)
        elif name == "toc": selected.append(toc_html)
        elif name == "pengantar": selected.append(pengantar_html)
        elif name == "siklus": selected.append(siklus_html)
        elif name == "kesimpulan": selected.append(kesimpulan_html)
        elif name == "ringkasan": selected.extend(ringkasan_pages)
        elif name == "gloss": selected.extend(gloss_pages)
        elif name == "disc": selected.append(disc_html)
        elif name.startswith("s") and name[1:].isdigit():
            n = int(name[1:])
            if n in section_pages:
                selected.extend(section_pages[n])
        else:
            print(f"Unknown page: {name}")

    if not selected:
        print("Nothing selected.")
        sys.exit(1)

    master = B.assemble_master(selected, subject_name)
    out_html = ROOT / "_out" / f"test_{'_'.join(pages_req)}.html"
    out_pdf = ROOT / "_out" / f"test_{'_'.join(pages_req)}.pdf"
    out_html.parent.mkdir(exist_ok=True)
    out_html.write_text(master, encoding='utf-8')
    print(f"HTML: {out_html}")

    # HTML-only mode: skip PDF unless --pdf flag
    do_pdf = "--pdf" in sys.argv
    if do_pdf:
        pdf = B.run_chrome(out_html, out_pdf)
        print(f"PDF:  {pdf}")

    # Copy HTML + style to OneDrive test folder
    test_dir = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\#result\2026-05-03\_test_v46")
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        # Copy style.css alongside HTML for direct browser preview
        shutil.copy(str(ROOT / "style.css"), str(test_dir / "style.css"))
        # Rewrite HTML link to local style.css
        html_text = out_html.read_text(encoding='utf-8')
        html_text = html_text.replace(
            'href="file:///' + str((ROOT / "style.css").resolve()).replace("\\", "/") + '"',
            'href="style.css"'
        )
        dst_html = test_dir / out_html.name
        dst_html.write_text(html_text, encoding='utf-8')
        print(f"OneDrive HTML: {dst_html}")
        if do_pdf:
            shutil.copy(str(pdf), str(test_dir / out_pdf.name))
            print(f"OneDrive PDF:  {test_dir / out_pdf.name}")
    except Exception as e:
        print(f"OneDrive copy fail: {e}")

if __name__ == "__main__":
    main()
