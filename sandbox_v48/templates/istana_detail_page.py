"""Istana Detail page V4.8 — render 12 istana details as vertical card stack.

Each card per Palace:
- Header: Hanzi + Indo name + bintang utama chip
- Body: Interpretasi narrative
- Footer: Saran callout (if exists)

Auto-paginate: typically 2 pages for 12 istana.
"""
import re
import html as _html
from templates.page_shell import page_shell
from templates.primitives import callout, gloss_text


def _esc(s):
    return _html.escape(s or "", quote=False)


# Per-istana icon (semantic)
ISTANA_ICON = {
    "命宮": "✦",  "兄弟宮": "👥", "夫妻宮": "💕", "子女宮": "👶",
    "財帛宮": "💰", "疾厄宮": "🏥", "遷移宮": "✈",  "僕役宮": "🤝",
    "官祿宮": "💼", "田宅宮": "🏠", "福德宮": "🌸", "父母宮": "👨‍👩",
    "命":   "✦",  "兄弟": "👥", "夫妻": "💕", "子女": "👶",
    "財帛": "💰", "疾厄": "🏥", "遷移": "✈",  "僕役": "🤝",
    "官祿": "💼", "田宅": "🏠", "福德": "🌸", "父母": "👨‍👩",
}


def _palace_card(idx, palace):
    icon = ISTANA_ICON.get(palace.nama_hz, "✦")
    # Strip "Istana " prefix from card title (per user request — "Istana" only on page title)
    card_title = re.sub(r"^Istana\s+", "", palace.nama_id or "")
    bintang_chip = ""
    if palace.bintang_utama:
        b = palace.bintang_utama[0]
        bintang_indo = f' <span class="indo">{_esc(b.indo)}</span>' if b.indo else ""
        bintang_chip = (
            f'<div class="id-bintang">'
            f'<span class="bint-lbl">Bintang Utama</span>'
            f'<span class="hz">{_esc(b.hz)}</span>{bintang_indo}'
            f'</div>'
        )
    ganzhi_chip = ""
    if palace.ganzhi:
        ganzhi_chip = f'<div class="id-ganzhi"><span class="hz">{_esc(palace.ganzhi)}</span></div>'

    interp_html = ""
    if palace.interpretasi:
        # Split into paragraphs vs bullets (lines starting with •)
        parts = []
        for line in palace.interpretasi.split("\n"):
            line = line.strip()
            if not line: continue
            if line.startswith("•"):
                content = line[1:].strip()
                parts.append(("bullet", content))
            else:
                parts.append(("para", line))
        # Group consecutive bullets into one ul
        rendered = []
        cur_bullets = []
        for kind, txt in parts:
            if kind == "bullet":
                cur_bullets.append(txt)
            else:
                if cur_bullets:
                    items = "".join(f'<li>{gloss_text(b)}</li>' for b in cur_bullets)
                    rendered.append(f'<ul class="id-bullets">{items}</ul>')
                    cur_bullets = []
                rendered.append(f'<p class="id-para">{gloss_text(txt)}</p>')
        if cur_bullets:
            items = "".join(f'<li>{gloss_text(b)}</li>' for b in cur_bullets)
            rendered.append(f'<ul class="id-bullets">{items}</ul>')
        interp_html = f'<div class="id-interp">{"".join(rendered)}</div>'

    saran_html = ""
    if palace.saran:
        si = palace.saran_icon or "💡"
        # Split saran into title-line + bullets if multi-line
        saran_parts = palace.saran.split("\n")
        saran_main = saran_parts[0].strip() if saran_parts else ""
        saran_bullets = [p[1:].strip() for p in saran_parts[1:] if p.strip().startswith("•")]
        bullet_html = ""
        if saran_bullets:
            items = "".join(f'<li>{gloss_text(b)}</li>' for b in saran_bullets)
            bullet_html = f'<ul class="id-saran-bullets">{items}</ul>'
        # Dynamic label: "Saran" / "Catatan" / "Tips" / "Note" — fallback to "Saran"
        sl = (palace.saran_label or "Saran").upper()
        # Variant color: catatan → gold (info), saran → red (action), tips → green
        variant = "info"
        if sl in ("CATATAN", "NOTE", "INFO"): variant = "info"
        elif sl in ("TIPS", "REKOMENDASI"): variant = "tips"
        else: variant = "saran"
        saran_html = f'''<div class="id-saran v-{variant}">
  <span class="id-saran-icon">{_esc(si)}</span>
  <div class="id-saran-body">
    <span class="id-saran-lbl">{_esc(sl)}</span>
    <span class="id-saran-text">{gloss_text(saran_main)}</span>
    {bullet_html}
  </div>
</div>'''

    if not (interp_html or saran_html):
        return ""  # skip empty palace

    return f'''<div class="id-card">
  <div class="id-head">
    <div class="id-num">{idx:02d}</div>
    <div class="id-icon">{_esc(icon)}</div>
    <div class="id-titles">
      <div class="id-name-id">{_esc(card_title)}</div>
      <div class="id-name-hz hz">{_esc(palace.nama_hz)}</div>
    </div>
    <div class="id-meta">
      {bintang_chip}
      {ganzhi_chip}
    </div>
  </div>
  {interp_html}
  {saran_html}
</div>'''


def _chunk_palaces(palaces, per_page=6):
    """Split palaces into chunks. Default 6 per page (12 istana → 2 pages).
    Cards auto-fit via min-height + break-inside:avoid; overflow gracefully."""
    return [palaces[i:i+per_page] for i in range(0, len(palaces), per_page)]


def render_istana_detail_pages(start_num: int, palaces, subject_name: str = ""):
    """Returns (list_of_html_pages, next_pn)."""
    if not palaces:
        return [], start_num

    PER_PAGE = 6
    chunks = _chunk_palaces(palaces, per_page=PER_PAGE)
    pages = []

    for i, chunk in enumerate(chunks):
        cards = "".join(_palace_card(idx + 1 + i*PER_PAGE, p) for idx, p in enumerate(chunk))
        if i == 0:
            intro = callout(
                "Setiap dimensi hidup dipetakan ke <strong>satu istana</strong>. "
                "Bintang yang menempati istana memberi tema dominan untuk area tersebut. "
                "Berikut interpretasi rinci per istana.",
                variant="info", icon="✦",
            )
            body = intro + f'<div class="id-stack">{cards}</div>'
        else:
            body = f'<div class="id-stack">{cards}</div>'

        title_id = "Detail Istana — Bagian " + str(i + 1)
        if len(chunks) == 1: title_id = "Detail 12 Istana Hidup"
        pages.append(page_shell(start_num + i, title_id, "十 二 宮 詳 解",
                                "ISTANA DETAIL · 十二宮", body, subject_name))

    return pages, start_num + len(pages)


ISTANA_DETAIL_CSS = """
/* === ISTANA DETAIL PAGE V4.8 === */
.id-stack { display: flex; flex-direction: column; gap: var(--sp-3); margin: var(--sp-2) 0; }

.id-card {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-left: 1.2mm solid var(--color-red);
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4);
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.05);
  break-inside: avoid; page-break-inside: avoid;
  display: flex; flex-direction: column; gap: var(--sp-2);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}

.id-head {
  display: grid; grid-template-columns: 10mm 8mm 1fr auto;
  gap: var(--sp-2); align-items: center;
  padding-bottom: 1.5mm; border-bottom: 0.2mm solid var(--color-gold-soft);
}
.id-num {
  font-family: var(--font-display); font-size: 22pt; color: var(--color-red);
  font-weight: 800; line-height: 1; text-align: center;
}
.id-icon { font-size: 16pt; line-height: 1; text-align: center; }
.id-titles { display: flex; flex-direction: column; gap: 0.4mm; min-width: 0; }
.id-name-id {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.4px; line-height: 1.1;
}
.id-name-hz {
  font-family: var(--font-serif-tc); font-size: 11pt; color: var(--color-muted);
  letter-spacing: 4px; line-height: 1;
}

.id-meta { display: flex; flex-direction: column; gap: 1mm; align-items: flex-end; white-space: nowrap; }
.id-bintang {
  display: flex; align-items: baseline; gap: 1.5mm;
  padding: 0.6mm 2mm; background: var(--color-gold-tint);
  border: 0.15mm solid var(--color-gold-soft); border-radius: 0.8mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.id-bintang .bint-lbl {
  font-family: var(--font-display); font-size: 6.5pt; color: var(--color-gold-deep);
  letter-spacing: 1px; text-transform: uppercase; font-weight: 700;
}
.id-bintang .hz {
  font-family: var(--font-serif-tc); font-size: 11pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.id-bintang .indo {
  font-size: 7.5pt; color: var(--color-ink-soft); font-style: italic;
}

.id-ganzhi {
  padding: 0.4mm 2mm; background: var(--color-red);
  color: #FBF7F0; border-radius: 0.6mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.id-ganzhi .hz {
  font-family: var(--font-serif-tc); font-size: 9pt; font-weight: 700;
}

.id-interp {
  font-size: 9pt; line-height: 1.55; color: var(--color-ink-soft);
}
.id-interp .id-para {
  margin: 0 0 1.5mm 0; text-align: justify;
}
.id-interp .id-para:last-child { margin-bottom: 0; }
.id-interp .id-bullets {
  margin: 0 0 1.5mm 0; padding: 0 0 0 5mm; list-style: none;
}
.id-interp .id-bullets li {
  position: relative; padding: 0.4mm 0 0.4mm 4mm;
  font-size: 8.5pt; line-height: 1.45;
}
.id-interp .id-bullets li::before {
  content: "◆"; color: var(--color-gold); position: absolute; left: 0;
  font-size: 7pt; top: 1mm;
}
.id-interp strong { color: var(--color-red); font-weight: 600; }
.id-interp em { color: var(--color-gold-deep); font-style: italic; }

.id-saran {
  display: grid; grid-template-columns: 10mm 1fr; gap: var(--sp-2); align-items: start;
  padding: 1.5mm var(--sp-3); border-radius: var(--r-sm);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.id-saran.v-saran {
  background: linear-gradient(135deg, rgba(139,26,26,0.08) 0%, var(--color-paper) 100%);
  border-left: 0.5mm solid var(--color-red);
}
.id-saran.v-info {
  background: linear-gradient(135deg, var(--color-cream-deep) 0%, var(--color-paper) 100%);
  border-left: 0.5mm solid var(--color-gold);
}
.id-saran.v-tips {
  background: linear-gradient(135deg, rgba(76,140,73,0.10) 0%, var(--color-paper) 100%);
  border-left: 0.5mm solid var(--color-success);
}
.id-saran.v-saran .id-saran-lbl { color: var(--color-red); }
.id-saran.v-info .id-saran-lbl { color: var(--color-gold-deep); }
.id-saran.v-tips .id-saran-lbl { color: var(--color-success); }
.id-saran-icon { font-size: 14pt; text-align: center; }
.id-saran-body { display: flex; flex-direction: column; gap: 0.3mm; }
.id-saran-lbl {
  font-family: var(--font-display); font-size: 7pt; color: var(--color-gold-deep);
  letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700;
}
.id-saran-text {
  font-size: 8.5pt; line-height: 1.5; color: var(--color-ink-soft);
}
.id-saran-text strong { color: var(--color-red); }
.id-saran-bullets {
  margin: 1mm 0 0 0; padding: 0 0 0 4mm; list-style: none;
}
.id-saran-bullets li {
  position: relative; padding: 0.3mm 0 0.3mm 3mm;
  font-size: 8pt; line-height: 1.45; color: var(--color-ink-soft);
}
.id-saran-bullets li::before {
  content: "◆"; color: var(--color-gold-deep); position: absolute; left: 0; font-size: 6pt; top: 0.8mm;
}
"""
