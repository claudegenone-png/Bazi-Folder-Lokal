"""Takdir & Misi Hidup (宿命) page V4.8.

Layout:
1. Hero banner — 宿命 big Hanzi + tagline
2. Transkripsi Asli card (cream gradient + Hanzi block)
3. Interpretasi card (red gradient, prominent)
4. Body paragraphs (clean cards)
5. Kunci Takdir highlight pull-quote (gold gradient)
"""
import html as _html
from templates.page_shell import page_shell
from canonical_model import LifeArea


def _esc(s):
    return _html.escape(s or "", quote=False)


def _hero():
    return '''<div class="tk-hero">
  <div class="tk-hero-glyph hz">宿 命</div>
  <div class="tk-hero-body">
    <div class="tk-hero-eyebrow">TAKDIR &amp; MISI HIDUP · 宿 命 (Sù Mìng)</div>
    <div class="tk-hero-title">Pesan Inti dari Peta Nasib Anda</div>
    <div class="tk-hero-sub">Bagian ini meringkas <strong>arah utama hidup</strong> — bukan vonis, melainkan kompas batin: arah ke mana energi Anda paling alami mengalir.</div>
  </div>
</div>'''


def _transkripsi_card(hz_text):
    return f'''<div class="tk-trans">
  <div class="tk-trans-eb">古 籍 原 文 · Transkripsi Asli</div>
  <div class="tk-trans-body hz">{_esc(hz_text)}</div>
</div>'''


def _interp_card(intro):
    return f'''<div class="tk-interp">
  <div class="tk-interp-eb">釋 義 · Interpretasi Inti</div>
  <div class="tk-interp-body">{_esc(intro)}</div>
</div>'''


def _para_cards(paragraphs):
    if not paragraphs:
        return ""
    items = "\n".join(f'<div class="tk-para">{_esc(p)}</div>' for p in paragraphs)
    return f'<div class="tk-para-stack">{items}</div>'


def _kunci_pull(bullets):
    if not bullets:
        return ""
    items = "\n".join(
        f'''<div class="tk-kunci-item">
  <div class="tk-kunci-label">{_esc(b.label)}</div>
  <div class="tk-kunci-body">{_esc(b.text)}</div>
</div>''' for b in bullets
    )
    return f'''<div class="tk-kunci-wrap">
  <div class="tk-kunci-eb">鎖 鑰 · Kunci Takdir</div>
  {items}
</div>'''


def render_takdir_page(pn: int, takdir: LifeArea, subject_name: str = "") -> str:
    parts = ['<div class="tk-frame">', _hero()]
    if takdir.raw_quotes:
        parts.append(_transkripsi_card(takdir.raw_quotes[0]))
    if takdir.intro:
        parts.append(_interp_card(takdir.intro))
    if takdir.raw_paragraphs:
        parts.append(_para_cards(takdir.raw_paragraphs))
    if takdir.rekomendasi:
        parts.append(_kunci_pull(takdir.rekomendasi))
    parts.append('</div>')
    body = "\n".join(parts)
    return page_shell(
        pn, "Takdir & Misi Hidup", "宿 命",
        "TAKDIR · 宿 命",
        body,
        subject_name,
        footer_l="Sù Mìng — Pesan Inti Peta Nasib",
    )


TAKDIR_PAGE_CSS = """
/* === TAKDIR PAGE V4.8 === */
.tk-frame {
  display: flex; flex-direction: column;
  gap: 4mm; height: 100%; overflow: hidden;
}

/* Hero */
.tk-hero {
  background: linear-gradient(135deg, #8B1A1A 0%, #6E1414 100%);
  color: #F5EBD0;
  border-radius: var(--r-md);
  padding: 5mm 7mm;
  display: grid; grid-template-columns: auto 1fr;
  gap: 6mm; align-items: center;
  overflow: hidden; position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.tk-hero::before {
  content: '宿'; position: absolute;
  bottom: -14mm; right: -3mm;
  font-family: var(--font-serif-tc);
  font-size: 100pt; color: rgba(245,235,208,0.06);
  font-weight: 700; line-height: 1; pointer-events: none;
}
.tk-hero-glyph {
  font-family: var(--font-serif-tc); font-size: 30pt;
  color: #F5EBD0; font-weight: 700; line-height: 1;
  letter-spacing: 4px; text-align: center;
  text-shadow: 0 1mm 4mm rgba(0,0,0,0.25);
  white-space: nowrap;
}
.tk-hero-body { min-width: 0; }
.tk-hero-eyebrow {
  font-size: 7pt; color: rgba(245,235,208,0.75);
  letter-spacing: 3px; text-transform: uppercase; font-weight: 700;
}
.tk-hero-title {
  font-family: var(--font-display); font-size: 14pt;
  color: #fff; font-weight: 700; line-height: 1.2;
  margin-top: 1.5mm; letter-spacing: 0.3px;
}
.tk-hero-sub {
  font-size: 8.5pt; line-height: 1.45; color: rgba(245,235,208,0.92);
  margin-top: 1.8mm; font-style: italic;
}
.tk-hero-sub strong { color: #fff; font-weight: 700; font-style: normal; }

/* Transkripsi */
.tk-trans {
  background: linear-gradient(135deg, #FFF8E1 0%, #F5EBD0 100%);
  border: 0.4mm solid var(--color-gold);
  border-radius: var(--r-md);
  padding: 3.5mm 5mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.tk-trans-eb {
  font-family: var(--font-display); font-size: 7pt;
  color: var(--color-gold-deep); letter-spacing: 3px;
  text-transform: uppercase; font-weight: 700;
  margin-bottom: 1.5mm;
}
.tk-trans-body {
  font-family: var(--font-serif-tc); font-size: 9.5pt;
  color: var(--color-ink); line-height: 1.7; letter-spacing: 0.5px;
  text-align: justify;
}

/* Interpretasi */
.tk-interp {
  background: linear-gradient(135deg, #FFF1F0 0%, #FFFAF8 100%);
  border-left: 0.8mm solid var(--color-red);
  border-radius: var(--r-sm);
  padding: 3.5mm 5mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.tk-interp-eb {
  font-family: var(--font-display); font-size: 7pt;
  color: var(--color-red); letter-spacing: 3px;
  text-transform: uppercase; font-weight: 700;
  margin-bottom: 1.8mm;
}
.tk-interp-body {
  font-size: 10pt; line-height: 1.55; color: var(--color-ink);
  font-weight: 500;
}

/* Paragraph stack */
.tk-para-stack {
  display: flex; flex-direction: column; gap: 2.5mm;
  overflow: hidden;
}
.tk-para {
  background: var(--color-paper);
  border: 0.2mm solid var(--color-gold-soft);
  border-radius: var(--r-sm);
  padding: 2.5mm 4mm;
  font-size: 8.5pt; line-height: 1.5; color: var(--color-ink);
  text-align: justify;
}

/* Kunci pull-quote */
.tk-kunci-wrap {
  background: linear-gradient(135deg, var(--color-gold-tint) 0%, #FFF8E1 100%);
  border: 0.4mm solid var(--color-gold);
  border-radius: var(--r-md);
  padding: 3.5mm 5mm;
  display: flex; flex-direction: column; gap: 2mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  flex-shrink: 0;
}
.tk-kunci-eb {
  font-family: var(--font-display); font-size: 7pt;
  color: var(--color-gold-deep); letter-spacing: 3px;
  text-transform: uppercase; font-weight: 700;
}
.tk-kunci-item {
  display: grid; grid-template-columns: auto 1fr;
  gap: 4mm; align-items: baseline;
  padding: 1.5mm 0;
  border-top: 0.15mm dotted var(--color-gold-soft);
}
.tk-kunci-item:first-of-type { border-top: none; }
.tk-kunci-label {
  font-family: var(--font-display); font-size: 9.5pt;
  color: var(--color-red); font-weight: 700;
  white-space: nowrap;
}
.tk-kunci-body {
  font-size: 8.5pt; line-height: 1.45; color: var(--color-ink);
}
"""
