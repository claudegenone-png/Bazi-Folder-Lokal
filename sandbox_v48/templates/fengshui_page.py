"""Feng Shui Rumah page V4.8.

Layout:
1. Interpretasi top card (red gradient) — subject-specific Saran from MD
2. Trigram Rumah panel — Hanzi big + Indo + meaning
3. 8-direction compass infographic (visual)
4. Element grid — icon + aspek + arah chips per row
5. (Optional) catatan callout
"""
import html as _html
from templates.page_shell import page_shell
from templates.primitives import callout
from canonical_model import FengShuiRumah


def _esc(s):
    return _html.escape(s or "", quote=False)


def _trigram_card(hz, indo, meaning):
    if not hz: return ""
    indo_html = f'<span class="fs-tg-indo">{_esc(indo)}</span>' if indo else ""
    meaning_html = f'<div class="fs-tg-meaning">{_esc(meaning)}</div>' if meaning else ""
    return f'''<div class="fs-trigram">
  <div class="fs-tg-glyph hz">{_esc(hz)}</div>
  <div class="fs-tg-body">
    <div class="fs-tg-eyebrow">TRIGRAM RUMAH · 卦 象</div>
    <div class="fs-tg-name"><span class="hz">{_esc(hz)}</span> {indo_html}</div>
    {meaning_html}
  </div>
</div>'''


def _compass_svg():
    """Inline SVG of 8-direction compass (decorative)."""
    return '''<svg class="fs-compass" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="55" fill="none" stroke="#C9A961" stroke-width="0.4" stroke-dasharray="2 1.5" opacity="0.7"/>
  <circle cx="60" cy="60" r="44" fill="none" stroke="#E5D3A1" stroke-width="0.3" opacity="0.5"/>
  <circle cx="60" cy="60" r="3" fill="#8B1A1A"/>
  <circle cx="60" cy="60" r="1.4" fill="#C9A961"/>
  <line x1="60" y1="8" x2="60" y2="112" stroke="#C9A961" stroke-width="0.25" opacity="0.5"/>
  <line x1="8" y1="60" x2="112" y2="60" stroke="#C9A961" stroke-width="0.25" opacity="0.5"/>
  <line x1="23" y1="23" x2="97" y2="97" stroke="#C9A961" stroke-width="0.2" opacity="0.4" stroke-dasharray="1 1"/>
  <line x1="97" y1="23" x2="23" y2="97" stroke="#C9A961" stroke-width="0.2" opacity="0.4" stroke-dasharray="1 1"/>
  <text x="60" y="6" text-anchor="middle" fill="#8B1A1A" font-size="6" font-family="Inter, sans-serif" font-weight="700">U</text>
  <text x="60" y="118" text-anchor="middle" fill="#6A5240" font-size="5" font-family="Inter, sans-serif">S</text>
  <text x="3" y="62" fill="#6A5240" font-size="5" font-family="Inter, sans-serif">B</text>
  <text x="115" y="62" fill="#6A5240" font-size="5" font-family="Inter, sans-serif">T</text>
  <text x="22" y="20" text-anchor="middle" fill="#A8843E" font-size="4.2" font-family="Inter, sans-serif">BL</text>
  <text x="98" y="20" text-anchor="middle" fill="#A8843E" font-size="4.2" font-family="Inter, sans-serif">TL</text>
  <text x="22" y="105" text-anchor="middle" fill="#A8843E" font-size="4.2" font-family="Inter, sans-serif">BD</text>
  <text x="98" y="105" text-anchor="middle" fill="#A8843E" font-size="4.2" font-family="Inter, sans-serif">TG</text>
  <text x="60" y="64" text-anchor="middle" fill="#8B1A1A" font-size="11" font-family="Noto Serif TC, serif" font-weight="700">陽</text>
  <text x="60" y="76" text-anchor="middle" fill="#A8843E" font-size="6" font-family="Noto Serif TC, serif">宅</text>
</svg>'''


# Split arah string into list of direction chips
import re as _re
def _arah_chips(arah_str):
    if not arah_str: return ""
    # Split by , / atau / dan / →
    parts = _re.split(r"[,，;]|\satau\s|\sdan\s", arah_str)
    chips = []
    for p in parts:
        p = p.strip().strip(".").strip()
        if not p: continue
        chips.append(f'<span class="fs-arah-chip">{_esc(p)}</span>')
    return "".join(chips)


def _element_card(idx, el):
    chips = _arah_chips(el.arah)
    aspek_hz = f' <span class="hz">{_esc(el.aspek_hz)}</span>' if el.aspek_hz else ""
    return f'''<div class="fs-element">
  <div class="fs-el-num">{idx:02d}</div>
  <div class="fs-el-icon">{_esc(el.icon or "✦")}</div>
  <div class="fs-el-body">
    <div class="fs-el-aspek">{_esc(el.aspek)}{aspek_hz}</div>
    <div class="fs-el-arah">{chips}</div>
  </div>
</div>'''


def render_fengshui_page(num: int, fs: FengShuiRumah, subject_name: str = "") -> str:
    if not fs:
        body = callout("Data Feng Shui Rumah tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, "Feng Shui Rumah", "陽 宅", "FENG SHUI · 陽宅", body, subject_name)

    parts = []

    # 1. Interpretasi top
    if fs.interpretasi:
        parts.append(f'''<div class="fs-interp">
  <div class="fs-interp-icon">💡</div>
  <div class="fs-interp-body">
    <div class="fs-interp-eyebrow">INTERPRETASI · 陽 宅 解 析</div>
    <div class="fs-interp-text">{_esc(fs.interpretasi)}</div>
  </div>
</div>''')

    # 2. Trigram + compass row (kalau trigram ada). Else: hero generic + compass.
    if fs.trigram_hz:
        trig_html = _trigram_card(fs.trigram_hz, fs.trigram_indo, fs.trigram_meaning)
        parts.append(f'''<div class="fs-hero">
  {trig_html}
  <div class="fs-compass-wrap">{_compass_svg()}</div>
</div>''')
    elif fs.elements:
        # No trigram in MD — show generic intro panel + compass
        parts.append(f'''<div class="fs-hero fs-hero-generic">
  <div class="fs-trigram fs-trigram-generic">
    <div class="fs-tg-glyph hz">陽宅</div>
    <div class="fs-tg-body">
      <div class="fs-tg-eyebrow">FENG SHUI RUMAH · 陽 宅</div>
      <div class="fs-tg-name">Tata Letak Rumah Selaras Energi Anda</div>
      <div class="fs-tg-meaning">Penataan rumah yang selaras dengan elemen kelahiran membantu mengalirkan energi positif (氣 / qi) ke setiap aspek hidup — kesehatan, rezeki, hubungan, dan ketenangan.</div>
    </div>
  </div>
  <div class="fs-compass-wrap">{_compass_svg()}</div>
</div>''')

    # 3. Element grid
    if fs.elements:
        parts.append('''<div class="fs-section-head">
  <span class="num">1</span>
  <span class="ttl">Panduan Tata Letak Rumah</span>
  <span class="hz hz-label">陽 宅 指 南</span>
</div>''')
        parts.append(callout(
            "Tata letak rumah Anda sebaiknya selaras dengan elemen kelahiran. "
            "Setiap aspek di bawah ini punya arah ideal — orientasi rumah, posisi pintu utama, dapur, "
            "kamar tidur, altar, dan toilet. Ikuti arah-arah ini untuk membawa energi positif yang lancar.",
            variant="info", icon="✦",
        ))
        cards = "".join(_element_card(i + 1, e) for i, e in enumerate(fs.elements))
        parts.append(f'<div class="fs-element-stack">{cards}</div>')

    body = "\n".join(parts)
    return page_shell(num, "Feng Shui Rumah", "陽 宅", "FENG SHUI · 陽宅", body, subject_name)


FENGSHUI_PAGE_CSS = """
/* === FENG SHUI PAGE V4.8 === */

/* Interpretasi top card (red gradient) */
.fs-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.fs-interp-icon { font-size: 22pt; line-height: 1; align-self: center; text-align: center; }
.fs-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.fs-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.fs-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Section heading */
.fs-section-head {
  display: grid; grid-template-columns: 8mm 1fr auto; gap: var(--sp-3); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1.5mm;
  margin: var(--sp-4) 0 var(--sp-2) 0;
}
.fs-section-head .num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; text-align: center;
}
.fs-section-head .ttl {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.fs-section-head .hz-label {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-muted);
  letter-spacing: 4px;
}

/* Hero: trigram + compass */
.fs-hero {
  display: grid; grid-template-columns: 1fr 50mm; gap: var(--sp-4); align-items: center;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-cream-deep) 0%, var(--color-paper) 100%);
  border: 0.3mm solid var(--color-gold); border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.fs-trigram {
  display: grid; grid-template-columns: 22mm 1fr; gap: var(--sp-3); align-items: center;
}
.fs-tg-glyph {
  font-family: var(--font-serif-tc); font-size: 36pt;
  color: var(--color-red); font-weight: 800; line-height: 1; text-align: center;
  text-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.18);
}
.fs-tg-body { display: flex; flex-direction: column; gap: 0.8mm; min-width: 0; }
.fs-tg-eyebrow {
  font-family: var(--font-display); font-size: 7pt; letter-spacing: 3px;
  color: var(--color-gold-deep); text-transform: uppercase; font-weight: 700;
}
.fs-tg-name {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.4px;
}
.fs-tg-name .hz {
  font-family: var(--font-serif-tc); margin-right: 1.5mm;
}
.fs-tg-indo { color: var(--color-ink); font-size: 11pt; }
.fs-tg-meaning {
  font-size: 8.5pt; line-height: 1.5; color: var(--color-muted); font-style: italic;
}
.fs-compass-wrap {
  display: flex; justify-content: center; align-items: center;
}
.fs-compass { width: 40mm; height: 40mm; }

/* Element stack */
.fs-element-stack { display: flex; flex-direction: column; gap: 1.5mm; margin: var(--sp-2) 0; }

.fs-element {
  display: grid; grid-template-columns: 8mm 9mm 1fr; gap: var(--sp-2); align-items: center;
  padding: var(--sp-2) var(--sp-3);
  background: var(--color-paper); border: 0.2mm solid var(--color-gold-soft);
  border-left: 0.6mm solid var(--color-gold); border-radius: var(--r-sm);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.fs-el-num {
  font-family: var(--font-display); font-size: 11pt; color: var(--color-gold-deep);
  font-weight: 700; text-align: center; letter-spacing: 0.5px;
}
.fs-el-icon { font-size: 14pt; text-align: center; line-height: 1; }
.fs-el-body { display: flex; flex-direction: column; gap: 0.8mm; min-width: 0; }
.fs-el-aspek {
  font-family: var(--font-display); font-size: 10pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.3px;
}
.fs-el-aspek .hz {
  font-family: var(--font-serif-tc); font-size: 8.5pt; color: var(--color-muted);
  font-weight: 600; margin-left: 1mm;
}
.fs-el-arah {
  display: flex; flex-wrap: wrap; gap: 1mm;
}
.fs-arah-chip {
  display: inline-block; padding: 0.5mm 2mm;
  background: var(--color-gold-tint); color: var(--color-ink);
  border: 0.15mm solid var(--color-gold-soft); border-radius: 0.6mm;
  font-size: 8.2pt; line-height: 1.4;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
"""
