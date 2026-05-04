"""Karakter page V4.8 — adaptive untuk multi-pola MD.

Layout:
1. Interpretasi card (red gradient) di paling top — pakai karakter.intro dari MD
2. Section heading "Lapisan-Lapisan Kepribadian"
3. Stacked Lapisan cards (kekuatan list) — each card:
   - Numbered icon + label header
   - Body text (paragraph + sub-bullets if any)
4. (Optional) Kelemahan section kalau ada

Adaptive ke 3 pola karakter MD:
- Pola A (Li Yuanxiang): 3 Lapisan terstruktur
- Pola B (Lin Ruyi): 1-2 paragraf interpretasi
- Pola C (Lin Wen Han): 5 Pola numbered patterns
"""
import html as _html
import re
from templates.page_shell import page_shell
from templates.primitives import callout
from canonical_model import Karakter


def _esc(s):
    return _html.escape(s or "", quote=False)


def _render_lapisan_text(text):
    """Render lapisan body text — handle line breaks + sub-bullets."""
    if not text: return ""
    # Split on sub-bullet markers (• at line start)
    parts = re.split(r"\n", text)
    paragraphs = []
    bullets = []
    for p in parts:
        p = p.strip()
        if not p: continue
        if p.startswith("•"):
            bullets.append(re.sub(r"^•\s*", "", p))
        else:
            if bullets:
                # flush bullets first
                paragraphs.append(("bullets", bullets))
                bullets = []
            paragraphs.append(("para", p))
    if bullets:
        paragraphs.append(("bullets", bullets))

    out = []
    for kind, content in paragraphs:
        if kind == "para":
            out.append(f'<p class="kr-text">{_esc(content)}</p>')
        else:
            items = "".join(f"<li>{_esc(b)}</li>" for b in content)
            out.append(f'<ul class="kr-bullets">{items}</ul>')
    return "".join(out)


def _lapisan_card(idx, bullet):
    label = (bullet.label or f"Aspek {idx}").strip()
    label = re.sub(r":\s*$", "", label)  # strip trailing colon
    text = bullet.text or ""
    return f'''<div class="kr-lapisan">
  <div class="kr-lapisan-num">{idx:02d}</div>
  <div class="kr-lapisan-body">
    <div class="kr-lapisan-label">{_esc(label)}</div>
    <div class="kr-lapisan-text">{_render_lapisan_text(text)}</div>
  </div>
</div>'''


def _kelemahan_card(idx, bullet):
    label = (bullet.label or "Tantangan").strip()
    label = re.sub(r":\s*$", "", label)
    text = bullet.text or ""
    return f'''<div class="kr-lapisan kr-warn">
  <div class="kr-lapisan-num">{idx:02d}</div>
  <div class="kr-lapisan-body">
    <div class="kr-lapisan-label">{_esc(label)}</div>
    <div class="kr-lapisan-text">{_render_lapisan_text(text)}</div>
  </div>
</div>'''


def render_karakter_page(num: int, karakter: Karakter, subject_name: str = "") -> str:
    if not karakter:
        body = callout("Data karakter tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, "Karakter & Kepribadian", "性 情",
                          "KARAKTER · 性情", body, subject_name)

    sections_html = []

    # 1. Interpretasi (red gradient card di top — wajib semua bab)
    if karakter.intro:
        intro_text = karakter.intro
        # Filter out meta-line "Transkripsi dari Software:" if it leaks in
        if not re.match(r"^transkripsi\b", intro_text, re.IGNORECASE):
            sections_html.append(f'''<div class="kr-interp">
  <div class="kr-interp-icon">💡</div>
  <div class="kr-interp-body">
    <div class="kr-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div>
    <div class="kr-interp-text">{_esc(intro_text)}</div>
  </div>
</div>''')

    # 2. Lapisan/Aspek/Pola cards (kekuatan)
    if karakter.kekuatan:
        sections_html.append('''<div class="kr-section-head">
  <span class="num">1</span>
  <span class="ttl">Lapisan-Lapisan Kepribadian</span>
  <span class="hz hz-label">性 情 層 次</span>
</div>''')
        sections_html.append(callout(
            "Karakter setiap orang terdiri dari beberapa lapisan yang saling melengkapi. "
            "Lapisan-lapisan di bawah ini menggambarkan dimensi-dimensi paling menonjol dari pribadi Anda.",
            variant="info", icon="✦",
        ))
        cards = "".join(_lapisan_card(i + 1, b) for i, b in enumerate(karakter.kekuatan))
        sections_html.append(f'<div class="kr-lapisan-stack">{cards}</div>')

    # 3. Kelemahan / tantangan (if extractor populates)
    if karakter.kelemahan:
        sections_html.append('''<div class="kr-section-head">
  <span class="num">2</span>
  <span class="ttl">Tantangan & Hal yang Perlu Diperhatikan</span>
  <span class="hz hz-label">需 注 意</span>
</div>''')
        cards = "".join(_kelemahan_card(i + 1, b) for i, b in enumerate(karakter.kelemahan))
        sections_html.append(f'<div class="kr-lapisan-stack">{cards}</div>')

    body = "\n".join(sections_html)
    return page_shell(num, "Karakter & Kepribadian", "性 情",
                      "KARAKTER · 性情", body, subject_name)


KARAKTER_PAGE_CSS = """
/* === KARAKTER PAGE V4.8 === */

/* Interpretasi top card (red gradient) */
.kr-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-interp-icon {
  font-size: 22pt; line-height: 1; text-align: center; align-self: center;
}
.kr-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.kr-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.kr-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Section heading */
.kr-section-head {
  display: grid; grid-template-columns: 8mm 1fr auto; gap: var(--sp-3); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1.5mm;
  margin: var(--sp-4) 0 var(--sp-2) 0;
}
.kr-section-head .num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; text-align: center;
}
.kr-section-head .ttl {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.kr-section-head .hz-label {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-muted);
  letter-spacing: 4px;
}

/* Lapisan stack */
.kr-lapisan-stack { display: flex; flex-direction: column; gap: var(--sp-3); margin: var(--sp-2) 0 var(--sp-3) 0; }

.kr-lapisan {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3);
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-left: 1.2mm solid var(--color-gold);
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4);
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.05);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-lapisan.kr-warn {
  border-left-color: var(--color-warn);
  background: linear-gradient(135deg, #FCF4E8 0%, var(--color-paper) 100%);
}

.kr-lapisan-num {
  font-family: var(--font-display); font-size: 28pt; color: var(--color-red);
  font-weight: 800; line-height: 1; text-align: center;
  border-right: 0.2mm dashed var(--color-gold-soft); padding-right: var(--sp-2);
  align-self: center;
}
.kr-lapisan.kr-warn .kr-lapisan-num { color: var(--color-warn); }

.kr-lapisan-body { display: flex; flex-direction: column; gap: 1.5mm; min-width: 0; }

.kr-lapisan-label {
  font-family: var(--font-display); font-size: 12pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.4px; line-height: 1.2;
  padding-bottom: 1.2mm; border-bottom: 0.2mm solid var(--color-gold-soft);
}
.kr-lapisan.kr-warn .kr-lapisan-label { color: var(--color-warn); }

.kr-lapisan-text {
  font-size: 9pt; line-height: 1.55; color: var(--color-ink-soft);
}
.kr-lapisan-text .kr-text {
  margin: 0 0 1.5mm 0; text-align: justify; word-wrap: break-word;
}
.kr-lapisan-text .kr-text:last-child { margin-bottom: 0; }
.kr-lapisan-text .kr-bullets {
  margin: 1mm 0 1.5mm 4mm; padding: 0; list-style: none;
}
.kr-lapisan-text .kr-bullets li {
  position: relative; padding: 0.4mm 0 0.4mm 4mm;
  font-size: 8.8pt; line-height: 1.5;
}
.kr-lapisan-text .kr-bullets li::before {
  content: "◆"; color: var(--color-gold); position: absolute; left: 0; top: 0.5mm; font-size: 6pt;
}
"""
