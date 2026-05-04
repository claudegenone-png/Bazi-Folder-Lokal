"""Hikmat Klasik (古書云) page V4.8.

Layout:
1. Hero (red gradient) — 古書云 hanzi + tagline
2. Verse stack — each verse as classical scroll card with citation chip
3. Synthesis card (cream) — Indo intro paragraph
4. Bullet list — explained insights
"""
import html as _html
from templates.page_shell import page_shell
from canonical_model import HikmatBundle


def _esc(s):
    return _html.escape(s or "", quote=False)


def _hero():
    return '''<div class="hk-hero">
  <div class="hk-hero-glyph hz">古 書 云</div>
  <div class="hk-hero-body">
    <div class="hk-hero-eyebrow">HIKMAT KLASIK · 古 書 云 (Gǔ Shū Yún)</div>
    <div class="hk-hero-title">Pepatah dari Kitab-Kitab Kuno</div>
    <div class="hk-hero-sub">Bait-bait klasik dari naskah <span class="hz">三命通會</span>, <span class="hz">滴天髓</span>, dan <span class="hz">子平真詮</span> — refleksi karakter Anda dalam bahasa para leluhur.</div>
  </div>
</div>'''


def _verse_card(idx, v):
    src_chip = ""
    if v.sumber:
        sumber_indo = f' <span class="hk-src-py">{_esc(v.sumber_indo)}</span>' if v.sumber_indo else ""
        src_chip = f'<div class="hk-src-chip"><span class="hz">{_esc(v.sumber)}</span>{sumber_indo}</div>'
    return f'''<div class="hk-verse">
  <div class="hk-verse-num">{idx:02d}</div>
  <div class="hk-verse-body">
    {src_chip}
    <div class="hk-verse-hanzi hz">{_esc(v.hanzi)}</div>
  </div>
</div>'''


def _synthesis_intro(text):
    return f'''<div class="hk-synth">
  <div class="hk-synth-eb">釋 義 · Penjelasan Indo</div>
  <div class="hk-synth-body">{_esc(text)}</div>
</div>'''


def _bullet_list(bullets):
    if not bullets:
        return ""
    items = "\n".join(
        f'<div class="hk-bullet"><span class="hk-bullet-mark">◆</span><span>{_esc(b)}</span></div>'
        for b in bullets
    )
    return f'<div class="hk-bullet-list">{items}</div>'


def _catatan(text):
    return f'<div class="hk-catatan"><em>{_esc(text)}</em></div>'


def render_hikmat_page(pn: int, bundle: HikmatBundle, subject_name: str = "") -> str:
    parts = ['<div class="hk-frame">', _hero()]
    if bundle.catatan:
        parts.append(_catatan(bundle.catatan))
    if bundle.verses:
        verses_html = "\n".join(_verse_card(i + 1, v) for i, v in enumerate(bundle.verses))
        parts.append(f'<div class="hk-verse-stack">{verses_html}</div>')
    if bundle.synthesis_intro:
        parts.append(_synthesis_intro(bundle.synthesis_intro))
    if bundle.synthesis_bullets:
        parts.append(_bullet_list(bundle.synthesis_bullets))
    parts.append('</div>')
    return page_shell(
        pn, "Hikmat Klasik", "古 書 云",
        "HIKMAT · 古 書 云",
        "\n".join(parts),
        subject_name,
        footer_l="Gǔ Shū Yún — Pepatah Para Leluhur",
    )


HIKMAT_PAGE_CSS = """
/* === HIKMAT KLASIK PAGE V4.8 === */
.hk-frame {
  display: flex; flex-direction: column;
  gap: 3.5mm; height: 100%; overflow: hidden;
}

/* Hero */
.hk-hero {
  background: linear-gradient(135deg, #8B1A1A 0%, #6E1414 100%);
  color: #F5EBD0;
  border-radius: var(--r-md);
  padding: 4.5mm 6mm;
  display: grid; grid-template-columns: auto 1fr;
  gap: 5mm; align-items: center;
  overflow: hidden; position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.hk-hero::before {
  content: '書'; position: absolute;
  bottom: -14mm; right: -3mm;
  font-family: var(--font-serif-tc);
  font-size: 100pt; color: rgba(245,235,208,0.06);
  font-weight: 700; line-height: 1; pointer-events: none;
}
.hk-hero-glyph {
  font-family: var(--font-serif-tc); font-size: 22pt;
  color: #F5EBD0; font-weight: 700; line-height: 1.05;
  letter-spacing: 4px; text-align: center;
  text-shadow: 0 1mm 4mm rgba(0,0,0,0.25);
  white-space: nowrap;
}
.hk-hero-body { min-width: 0; }
.hk-hero-eyebrow {
  font-size: 7pt; color: rgba(245,235,208,0.78);
  letter-spacing: 3px; text-transform: uppercase; font-weight: 700;
}
.hk-hero-title {
  font-family: var(--font-display); font-size: 13pt;
  color: #fff; font-weight: 700; line-height: 1.2;
  margin-top: 1.5mm;
}
.hk-hero-sub {
  font-size: 8pt; line-height: 1.45; color: rgba(245,235,208,0.92);
  margin-top: 1.5mm; font-style: italic;
}
.hk-hero-sub .hz {
  font-family: var(--font-serif-tc); color: #fff;
  font-style: normal; font-weight: 700;
}

/* Catatan */
.hk-catatan {
  font-size: 7.5pt; color: var(--color-muted);
  text-align: center; padding: 1mm 4mm;
  border-top: 0.15mm dotted var(--color-gold-soft);
  border-bottom: 0.15mm dotted var(--color-gold-soft);
}

/* Verse stack */
.hk-verse-stack {
  display: flex; flex-direction: column; gap: 2mm;
  overflow: hidden;
}
.hk-verse {
  display: grid; grid-template-columns: 9mm 1fr;
  gap: 3mm; align-items: start;
  background: linear-gradient(135deg, #FFF8E1 0%, #F5EBD0 100%);
  border: 0.3mm solid var(--color-gold-soft);
  border-left: 0.8mm solid var(--color-gold);
  border-radius: var(--r-sm);
  padding: 2.5mm 4mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  break-inside: avoid;
}
.hk-verse-num {
  font-family: var(--font-display); font-size: 13pt;
  color: var(--color-gold-deep); font-weight: 700;
  line-height: 1; text-align: center;
  border-right: 0.2mm solid var(--color-gold-soft);
  padding-right: 2mm; padding-top: 0.8mm;
}
.hk-verse-body { min-width: 0; }
.hk-src-chip {
  display: inline-flex; align-items: baseline; gap: 2mm;
  background: var(--color-red); color: #fff;
  padding: 0.6mm 2.5mm; border-radius: 0.8mm;
  font-size: 7.5pt; font-weight: 700;
  margin-bottom: 1.2mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.hk-src-chip .hz {
  font-family: var(--font-serif-tc); letter-spacing: 1px;
}
.hk-src-py {
  font-family: var(--font-display); font-size: 6.5pt;
  font-style: italic; color: rgba(245,235,208,0.85);
  font-weight: 500;
}
.hk-verse-hanzi {
  font-family: var(--font-serif-tc); font-size: 9pt;
  color: var(--color-ink); line-height: 1.7; letter-spacing: 0.4px;
  text-align: justify;
}

/* Synthesis */
.hk-synth {
  background: linear-gradient(135deg, #FFF1F0 0%, #FFFAF8 100%);
  border-left: 0.8mm solid var(--color-red);
  border-radius: var(--r-sm);
  padding: 3mm 4.5mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.hk-synth-eb {
  font-family: var(--font-display); font-size: 7pt;
  color: var(--color-red); letter-spacing: 3px;
  text-transform: uppercase; font-weight: 700;
  margin-bottom: 1.5mm;
}
.hk-synth-body {
  font-size: 9pt; line-height: 1.5; color: var(--color-ink);
  font-weight: 500;
}

/* Bullets */
.hk-bullet-list {
  display: flex; flex-direction: column; gap: 1.5mm;
  background: var(--color-paper);
  border: 0.2mm solid var(--color-gold-soft);
  border-radius: var(--r-sm);
  padding: 3mm 4mm;
}
.hk-bullet {
  display: grid; grid-template-columns: 4mm 1fr;
  gap: 2mm; align-items: baseline;
  font-size: 8pt; line-height: 1.45; color: var(--color-ink);
}
.hk-bullet-mark {
  color: var(--color-gold-deep); font-weight: 700;
}
"""
