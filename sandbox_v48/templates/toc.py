"""TOC V6 — detailed 1-column drop-down with auto-pagination.

Pattern:
- toc-lead: hero band (大 hz glyph + intro)
- toc-list: vertical list of entries
  - Group header rows (Roman numeral + category title + range) between group members
  - Detail rows: number + Hanzi cartouche + title-id + Hanzi sub + dotted leader + page
- Auto-paginate: if total visual rows > threshold → split to 2 pages

All info preserved, no truncation, small font OK.
"""
import html as _html
from templates.page_shell import page_shell


def _esc(s):
    return _html.escape(s or "", quote=False)


# Categories (no roman — assigned by appearance order in render).
# Each: (id, hz, py, [topics])
CATEGORIES = [
    ("Pembuka",            "前 篇",  "Qián Piān",   ["pengantar"]),
    ("Inti Bagan",         "本 命",  "Běn Mìng",    ["bazi", "ziwei", "ziwei_palace_collection", "karakter"]),
    ("Aspek Kehidupan",    "生 活",  "Shēng Huó",   ["karir", "keuangan", "properti", "fengshui", "pernikahan",
                                                       "kecocokan_shio", "anak", "kesehatan", "orangtua",
                                                       "saudara", "bawahan", "perpindahan", "peruntungan"]),
    ("Peruntungan Waktu",  "氣 運",  "Qì Yùn",      ["shensha", "takdir", "da_yun", "tahunan", "tabel_tahunan"]),
    ("Hikmat Klasik",      "古 書",  "Gǔ Shū",      ["hikmat_klasik"]),
    ("Kesimpulan",         "結 語",  "Jié Yǔ",      ["ringkasan", "kesimpulan", "glosarium", "glossary", "disclaimer"]),
]

ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

TOPIC_ICONS = {
    "pengantar": "前", "bazi": "命", "ziwei": "紫", "ziwei_palace_collection": "宮",
    "karakter": "性", "karir": "官", "keuangan": "財", "properti": "宅",
    "fengshui": "風", "pernikahan": "婚", "kecocokan_shio": "合", "anak": "子",
    "kesehatan": "疾", "orangtua": "父", "saudara": "兄", "bawahan": "僕",
    "perpindahan": "遷", "peruntungan": "福", "shensha": "煞", "takdir": "宿",
    "da_yun": "運", "tahunan": "流", "tabel_tahunan": "鑑", "hikmat_klasik": "古",
    "ringkasan": "結", "kesimpulan": "結", "glosarium": "詞",
    "glossary": "辭", "disclaimer": "告", "UNKNOWN": "·",
}


def _group_entries(entries):
    """Group entries by category, sort groups by min page (ascending),
    then assign Roman numerals I, II, III... in that order."""
    grouped_raw = []
    placed = set()
    for cat_id, cat_hz, cat_py, topics in CATEGORIES:
        members = [e for e in entries if e.get("topic") in topics]
        if members:
            members.sort(key=lambda e: e["page"])
            pages = [e["page"] for e in members]
            grouped_raw.append({
                "id": cat_id, "hz": cat_hz, "py": cat_py,
                "members": members,
                "pg_start": min(pages), "pg_end": max(pages),
                "n_bab": len(members),
            })
        placed.update(topics)
    others = [e for e in entries if e.get("topic") not in placed]
    if others:
        others.sort(key=lambda e: e["page"])
        pages = [e["page"] for e in others]
        grouped_raw.append({
            "id": "Bagian Tambahan", "hz": "附 篇", "py": "Fù Piān",
            "members": others,
            "pg_start": min(pages), "pg_end": max(pages),
            "n_bab": len(others),
        })
    # Sort by page-start ascending → Roman numerals follow page order
    grouped_raw.sort(key=lambda g: g["pg_start"])
    for i, g in enumerate(grouped_raw):
        g["roman"] = ROMAN_NUMERALS[i] if i < len(ROMAN_NUMERALS) else str(i + 1)
    return grouped_raw


def _group_header_html(g):
    pg = f"{g['pg_start']} – {g['pg_end']}" if g['pg_start'] != g['pg_end'] else str(g['pg_start'])
    return f'''<div class="toc-grp-head">
  <div class="toc-grp-roman">{_esc(g["roman"])}</div>
  <div class="toc-grp-titles">
    <span class="toc-grp-id">{_esc(g["id"])}</span>
    <span class="toc-grp-hz hz">{_esc(g["hz"])}</span>
    <span class="toc-grp-py">{_esc(g["py"])}</span>
  </div>
  <div class="toc-grp-rule"></div>
  <div class="toc-grp-meta">
    <span class="grp-bab">{g["n_bab"]} BAB</span>
    <span class="grp-pg">hal. {pg}</span>
  </div>
</div>'''


def _row_html(idx, e):
    icon = TOPIC_ICONS.get(e.get("topic"), "·")
    return f'''<div class="toc-detail-row">
  <span class="td-cart hz">{_esc(icon)}</span>
  <span class="td-id">{_esc(e.get("title", ""))}</span>
  <span class="td-hz hz">{_esc(e.get("hz", ""))}</span>
  <span class="td-leader"></span>
  <span class="td-pg">{e.get("page", "")}</span>
</div>'''


def _build_entries_html(grouped, start_idx=1):
    """Returns ordered list of HTML strings (group headers + detail rows)."""
    out = []
    idx = start_idx
    for g in grouped:
        out.append(("group_head", _group_header_html(g), 0))
        for e in g["members"]:
            out.append(("row", _row_html(idx, e), 1))
            idx += 1
    return out


def render_toc(num: int, entries: list, subject_name: str = ""):
    """Returns (list[html_pages], next_pn)."""
    grouped = _group_entries(entries)
    total_chapters = len(entries)
    total_groups = len(grouped)

    # Estimate visual units. Threshold high — only split when truly overflowing.
    # Dense mode font fits ~50 units per A4. Below that = 1 page.
    visual_units = total_chapters * 1 + total_groups * 1.8
    needs_split = visual_units > 50

    lead = f'''<div class="toc-lead">
  <div class="toc-lead-hz">目 錄</div>
  <div class="toc-lead-text">
    <strong>Daftar Isi</strong> — {total_chapters} bab dalam {total_groups} bagian besar.
    Setiap bab dapat dibaca berdiri sendiri.
  </div>
</div>'''

    if not needs_split:
        # Single page TOC
        items = _build_entries_html(grouped, start_idx=1)
        body_inner = "".join(html for kind, html, lvl in items)
        body = f'{lead}<div class="toc-list">{body_inner}</div>'
        return [page_shell(num, "Daftar Isi", "目 錄", "DAFTAR ISI · 目錄", body, subject_name)], num + 1

    # Split into 2 pages — SEQUENTIAL distribution (preserves Roman numeral order)
    # Once a group doesn't fit on page A, all subsequent go to page B
    page_a, page_b = [], []
    weight_a = 0
    target = visual_units / 2
    on_page_b = False
    for g in grouped:
        gw = 1.8 + len(g["members"])
        if not on_page_b and (weight_a + gw) <= (target + 4):
            page_a.append(g); weight_a += gw
        else:
            on_page_b = True
            page_b.append(g)

    # Page A
    items_a = _build_entries_html(page_a, start_idx=1)
    body_a = f'{lead}<div class="toc-list dense"><div class="toc-page-tag">— Bagian 1 / 2 —</div>{"".join(h for k,h,l in items_a)}</div>'
    a = page_shell(num, "Daftar Isi (1/2)", "目 錄", "DAFTAR ISI · 目錄", body_a, subject_name)

    # Page B
    start_b = sum(len(g["members"]) for g in page_a) + 1
    items_b = _build_entries_html(page_b, start_idx=start_b)
    body_b = f'<div class="toc-list dense"><div class="toc-page-tag">— Bagian 2 / 2 —</div>{"".join(h for k,h,l in items_b)}</div>'
    b = page_shell(num + 1, "Daftar Isi (2/2)", "目 錄", "DAFTAR ISI · 目錄", body_b, subject_name)

    return [a, b], num + 2


TOC_CSS = """
/* === TOC V6 — detailed 1-column drop-down + auto-paginate === */
.page:has(.toc-lead) { padding: 12mm 16mm 10mm 16mm; }

.toc-lead {
  display: grid; grid-template-columns: 28mm 1fr; gap: var(--sp-3); align-items: center;
  padding: var(--sp-2) var(--sp-4); margin-bottom: var(--sp-3);
  background: linear-gradient(135deg, var(--color-gold-tint) 0%, var(--color-paper) 100%);
  border: 0.3mm solid var(--color-gold); border-radius: var(--r-md);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.toc-lead-hz {
  font-family: var(--font-serif-tc); font-size: 26pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 5px; line-height: 1; text-align: center;
  text-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.15);
}
.toc-lead-text {
  font-size: 9.5pt; line-height: 1.5; color: var(--color-ink);
  border-left: 0.5mm solid var(--color-gold); padding-left: var(--sp-3);
}
.toc-lead-text strong { color: var(--color-red); font-weight: 700; }

.toc-list { display: flex; flex-direction: column; gap: 0; }
.toc-page-tag {
  text-align: center; font-family: var(--font-display);
  font-size: 7.5pt; letter-spacing: 4px; color: var(--color-gold-deep);
  margin-bottom: var(--sp-2); text-transform: uppercase; font-weight: 600;
}

/* Group header row */
.toc-grp-head {
  display: grid; grid-template-columns: 14mm 1fr auto;
  gap: var(--sp-2); align-items: baseline;
  margin: var(--sp-3) 0 1mm 0; padding: 1mm 0 1.5mm 0;
  border-bottom: 0.4mm double var(--color-gold);
}
.toc-grp-head:first-child { margin-top: 0; }
.toc-grp-roman {
  font-family: var(--font-display); font-size: 24pt; color: var(--color-red);
  font-weight: 800; line-height: 1; text-align: center; letter-spacing: 0.5px;
}
.toc-grp-titles { display: flex; align-items: baseline; gap: var(--sp-2); flex-wrap: wrap; min-width: 0; }
.toc-grp-id {
  font-family: var(--font-display); font-size: 14pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.4px;
}
.toc-grp-hz {
  font-family: var(--font-serif-tc); font-size: 11pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 4px;
}
.toc-grp-py {
  font-family: var(--font-display); font-size: 8pt; font-style: italic;
  color: var(--color-gold-deep); letter-spacing: 0.5px;
}
.toc-grp-rule { display: none; }
.toc-grp-meta {
  display: flex; flex-direction: column; align-items: flex-end; gap: 0.5mm; white-space: nowrap;
}
.toc-grp-meta .grp-bab {
  font-family: var(--font-display); font-size: 6.5pt; color: var(--color-gold-deep);
  letter-spacing: 1.2px; font-weight: 700; text-transform: uppercase;
  padding: 0.3mm 1.5mm; border: 0.15mm solid var(--color-gold-soft); border-radius: 0.6mm;
  background: var(--color-gold-tint);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.toc-grp-meta .grp-pg {
  font-family: var(--font-display); font-size: 9pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.3px;
}

/* Detail row */
.toc-detail-row {
  display: grid; grid-template-columns: 5mm minmax(0, 1fr) auto auto auto;
  align-items: baseline; gap: var(--sp-1);
  padding: 0.8mm var(--sp-2); padding-left: 16mm;
  font-size: 9pt;
}
.toc-detail-row .td-cart {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-red);
  font-weight: 700; text-align: center; line-height: 1;
  border: 0.15mm solid var(--color-gold); border-radius: 0.6mm;
  width: 4.5mm; height: 4.5mm;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--color-gold-tint);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.toc-detail-row .td-id {
  font-family: var(--font-display); font-size: 9.5pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.1px; line-height: 1.15;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  padding-left: var(--sp-1);
}
.toc-detail-row .td-hz {
  font-family: var(--font-serif-tc); font-size: 7.5pt; color: var(--color-muted);
  letter-spacing: 1.5px; line-height: 1; white-space: nowrap;
  padding: 0 var(--sp-1);
}
.toc-detail-row .td-leader {
  align-self: end; margin-bottom: 1mm; min-width: 6mm;
  height: 0.3mm;
  background-image: radial-gradient(circle, var(--color-gold-soft) 0.16mm, transparent 0.16mm);
  background-size: 1.5mm 0.4mm; background-position: 0 100%; background-repeat: repeat-x;
}
.toc-detail-row .td-pg {
  font-family: var(--font-display); font-size: 10pt; color: var(--color-red);
  font-weight: 700; text-align: right; line-height: 1; letter-spacing: 0.3px;
  min-width: 8mm;
}

/* Dense mode (split-page or auto-shrunk) */
.toc-list.dense .toc-grp-head { margin: var(--sp-2) 0 0.6mm 0; padding: 0.6mm 0 1mm 0; }
.toc-list.dense .toc-grp-roman { font-size: 18pt; }
.toc-list.dense .toc-grp-id { font-size: 11pt; }
.toc-list.dense .toc-grp-hz { font-size: 9pt; letter-spacing: 2px; }
.toc-list.dense .toc-grp-py { font-size: 6.5pt; }
.toc-list.dense .toc-grp-meta .grp-pg { font-size: 8pt; }
.toc-list.dense .toc-detail-row { padding: 0.4mm var(--sp-2); padding-left: 12mm; gap: 1mm; grid-template-columns: 4mm minmax(0,1fr) auto auto auto; }
.toc-list.dense .toc-detail-row .td-cart { width: 3.8mm; height: 3.8mm; font-size: 7.5pt; }
.toc-list.dense .toc-detail-row .td-id { font-size: 8.2pt; }
.toc-list.dense .toc-detail-row .td-hz { font-size: 6.5pt; letter-spacing: 1px; }
.toc-list.dense .toc-detail-row .td-pg { font-size: 8.5pt; }
"""
