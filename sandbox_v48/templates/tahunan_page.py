"""Tahunan page — year cards (3/page, auto-paginate, mood-aware visual)."""
import html as _html
import re
from templates.page_shell import page_shell
import html as _htmllib
from templates.primitives import callout, hz_gloss, gloss_text


def _rich_callout(html_body: str, *, variant: str = "info", icon: str = "✦") -> str:
    """Variant of callout() that accepts pre-rendered HTML body (no escape).
    Use when intro text needs <strong>/<em>/<br> markup that callout() would
    otherwise html-escape into literal text."""
    return (
        f'<div class="callout v-{variant}">'
        f'<span class="co-icon">{_htmllib.escape(icon)}</span>'
        f'<div class="co-text">{html_body}</div>'
        f'</div>'
    )
from canonical_model import Tahun


def _esc(s):
    return _html.escape(s or "", quote=False)


# Tema-keyword mood inference (when stars are absent)
_MOOD_GOOD = re.compile(r"\b(baik|beruntung|prosperit|cerdas|peluang|stabil|panen|naik|hoki)\b", re.I)
_MOOD_WARN = re.compile(r"\b(tantangan|hati|waspada|perhatian|transisi|berat|ekstra|krisis|hindari)\b", re.I)


def _resolve_mood(t: Tahun):
    if t.mood: return t.mood
    if t.stars_rating is not None:
        if t.stars_rating >= 4: return "good"
        if t.stars_rating == 3: return "neutral"
        if t.stars_rating == 2: return "warn"
        return "bad"
    if t.tema:
        if _MOOD_WARN.search(t.tema): return "warn"
        if _MOOD_GOOD.search(t.tema): return "good"
    return "neutral"


def _stars_visual(stars):
    """Bigger gold/dim stars with label."""
    if stars is None: return ""
    s = "".join(f'<span class="yc-star {"on" if i < stars else "off"}">★</span>' for i in range(5))
    return f'<div class="yc-stars">{s}</div>'


def _pos_warn_block(label, items, mood):
    if not items: return ""
    lis = "".join(
        f'<li><strong>{_esc(b.label)}</strong> — {gloss_text(b.text)}</li>' if b.label
        else f'<li>{gloss_text(b.text)}</li>'
        for b in items[:3]
    )
    icon = "✓" if mood == "good" else "!"
    return f'<div class="yc-block yc-{mood}"><div class="yc-block-lbl"><span class="yc-block-icon">{icon}</span>{_esc(label)}</div><ul>{lis}</ul></div>'


def _bintang_chips(items):
    if not items: return ""
    chips = "".join(
        f'<span class="yc-bintang-chip">{hz_gloss(b.label or "", b.text or "", inline=True)}</span>' if b.label
        else f'<span class="yc-bintang-chip">{gloss_text(b.text or "")}</span>'
        for b in items[:4]
    )
    return f'<div class="yc-bintang-row"><span class="yc-bintang-lbl">✦ Bintang Aktif</span>{chips}</div>'


def _year_card_html(t: Tahun) -> str:
    mood = _resolve_mood(t)

    age_html = f'<div class="yc-age">Usia <strong>{t.age}</strong> th</div>' if t.age else ""

    gz_html = ""
    if t.ganzhi:
        gz_html = f'<div class="yc-gz">{hz_gloss(t.ganzhi, t.ganzhi_indo or "", inline=True)}</div>'

    star_html = _stars_visual(t.stars_rating)

    tema_html = ""
    if t.tema:
        tema_html = (
            f'<div class="yc-tema">'
            f'<span class="yc-tema-lbl">TEMA</span>'
            f'<span class="yc-tema-text">{_esc(t.tema)}</span>'
            f'</div>'
        )

    narasi_html = ""
    if t.narasi:
        narasi_html = f'<div class="yc-narasi">{gloss_text(t.narasi)}</div>'

    saran_html = ""
    if t.saran:
        saran_html = (
            f'<div class="yc-saran"><span class="yc-saran-icon">💡</span>'
            f'<span class="yc-saran-text">{gloss_text(t.saran)}</span></div>'
        )

    bintang_html = _bintang_chips(t.bintang_aktif)

    pos_block = _pos_warn_block("Hal Positif", t.hal_positif, "good")
    warn_block = _pos_warn_block("Perlu Diwaspadai", t.hal_diwaspadai, "warn")

    if pos_block and warn_block:
        pw_html = f'<div class="yc-pos-warn cols-2">{pos_block}{warn_block}</div>'
    elif pos_block or warn_block:
        pw_html = f'<div class="yc-pos-warn cols-1">{pos_block or warn_block}</div>'
    else:
        pw_html = ""

    return f'''<div class="yc-card mood-{mood}">
  <div class="yc-head">
    <div class="yc-year-glyph">📅</div>
    <div class="yc-year">{t.year}</div>
    {age_html}
    {star_html}
    {gz_html}
  </div>
  <div class="yc-body">
    {tema_html}
    {narasi_html}
    {bintang_html}
    {saran_html}
    {pw_html}
  </div>
</div>'''


def _card_char_estimate(t: Tahun) -> int:
    """Estimate rendered char-weight of a year card. Used for page packing."""
    base = 220                                     # header + meta + ganzhi + stars
    if t.tema: base += min(len(t.tema), 80)
    if t.narasi: base += min(len(t.narasi), 320)
    if t.saran: base += min(len(t.saran), 220)
    for items in (t.hal_positif[:3], t.hal_diwaspadai[:3], t.bintang_aktif[:4]):
        for b in items:
            base += min(len((b.label or "") + (b.text or "")), 140) + 25
    return base


def _chunk_by_budget(years):
    """Pack years per page using char-budget. If all fit single page → 1 chunk.
    Avoids creating sparse pages when content is light."""
    if not years: return []
    total = sum(_card_char_estimate(t) for t in years)
    INTRO_CHARS = 950      # rich Liu Nian explainer callout (apa/cara baca/bintang)
    PAGE_BUDGET = 4800     # safe fit per A4 (header/footer reserved)
    # If total + intro fits in single page → don't split
    if total + INTRO_CHARS <= PAGE_BUDGET:
        return [list(years)]
    # Otherwise: greedy pack
    chunks, cur, cur_w = [], [], INTRO_CHARS
    for t in years:
        w = _card_char_estimate(t)
        if cur and cur_w + w > PAGE_BUDGET:
            chunks.append(cur); cur = []; cur_w = 0
        cur.append(t); cur_w += w
    if cur: chunks.append(cur)
    return chunks


def _density_class_for_chunk(chunk):
    """When packing a lot in one page, return CSS density modifier to scale down."""
    total = sum(_card_char_estimate(t) for t in chunk)
    if total > 3800: return "yc-density-tight"
    if total > 2800: return "yc-density-mid"
    return ""


SECTION_LABEL = "RAMALAN TAHUNAN · 流年"


def render_tahunan_pages(start_num: int, tahun_list, subject_name: str = ""):
    if not tahun_list:
        body = callout("Data ramalan tahunan tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        html = page_shell(start_num, "Ramalan Tahunan", "流 年 判 斷",
                          SECTION_LABEL, body, subject_name)
        return [html], start_num + 1

    chunks = _chunk_by_budget(tahun_list)
    pages_out = []
    for idx, chunk in enumerate(chunks):
        page_num = start_num + idx
        years_range = f"{chunk[0].year}–{chunk[-1].year}" if len(chunk) > 1 else str(chunk[0].year)
        title_id = f"Ramalan Tahunan {years_range}"
        body_parts = []
        if idx == 0:
            body_parts.append(_rich_callout(
                '<p class="yc-intro-p"><strong>Apa itu Ramalan Tahunan (流年 — Liu Nian)?</strong> '
                'Bagan kelahiran Anda (BaZi/Zi Wei) bersifat <em>tetap</em>, namun setiap tahun ia '
                'bertemu dengan energi <strong>Penguasa Tahun (太歲 — Tai Sui)</strong> yang berbeda. '
                'Pertemuan inilah yang menghasilkan corak peruntungan khas tiap tahun.</p>'
                '<p class="yc-intro-p"><strong>Cara membaca kartu di bawah:</strong></p>'
                '<ul class="yc-intro-list">'
                '<li><strong>★ Bintang</strong> — tingkat keberuntungan tahun (5★ = puncak, 1★ = paling menantang).</li>'
                '<li><strong>Tema</strong> — judul singkat corak tahunan yang dominan.</li>'
                '<li><strong>Bintang Aktif</strong> — energi/dewa yang sedang menyorot tahun itu (mis. 龍德 = pelindung; 天掃 = pembersih).</li>'
                '<li><strong>Hal Positif / Perlu Diwaspadai</strong> — peluang yang bisa dimanfaatkan dan risiko yang patut dijaga.</li>'
                '</ul>',
                variant="info", icon="✦",
            ))
        density = _density_class_for_chunk(chunk)
        stack_class = f"yc-stack {density}".strip()
        body_parts.append(f'<div class="{stack_class}">{"".join(_year_card_html(t) for t in chunk)}</div>')
        body = "\n".join(body_parts)
        pages_out.append(page_shell(page_num, title_id, "流 年 判 斷",
                                    SECTION_LABEL, body, subject_name))
    return pages_out, start_num + len(chunks)


TAHUNAN_PAGE_CSS = """
/* === Intro callout (Liu Nian explainer) === */
.yc-intro-p { margin: 0 0 1.2mm 0; font-size: 8.5pt; line-height: 1.55; color: var(--color-ink-soft); }
.yc-intro-p:last-of-type { margin-bottom: 0.5mm; }
.yc-intro-p strong { color: var(--color-red); font-weight: 700; }
.yc-intro-p em { color: var(--color-gold-deep); font-style: italic; }
.yc-intro-list { margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 0.4mm 3mm; }
.yc-intro-list li {
  position: relative; padding: 0.3mm 0 0.3mm 4mm;
  font-size: 8pt; line-height: 1.45; color: var(--color-ink-soft);
}
.yc-intro-list li::before {
  content: "◆"; color: var(--color-gold); position: absolute; left: 0.5mm; top: 1mm;
  font-size: 6pt;
}
.yc-intro-list li strong { color: var(--color-red); font-weight: 700; }

/* === TAHUNAN YEAR CARDS === */
.yc-stack { display: flex; flex-direction: column; gap: 2.5mm; }

.yc-card {
  display: grid; grid-template-columns: 36mm 1fr; gap: var(--sp-3);
  padding: var(--sp-3); border-radius: var(--r-md);
  border: var(--bw-thin) solid var(--color-gold-soft);
  background: var(--color-paper);
  box-shadow: var(--sh-card);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.yc-card.mood-good {
  border-left: 1mm solid var(--color-success);
  background: linear-gradient(90deg, #F0F8EC 0%, var(--color-paper) 28%);
}
.yc-card.mood-warn {
  border-left: 1mm solid var(--color-warn);
  background: linear-gradient(90deg, #FCF4E8 0%, var(--color-paper) 28%);
}
.yc-card.mood-bad {
  border-left: 1mm solid var(--color-danger);
  background: linear-gradient(90deg, #FBE9E9 0%, var(--color-paper) 28%);
}
.yc-card.mood-neutral {
  border-left: 1mm solid var(--color-gold);
  background: linear-gradient(90deg, #FCF8EC 0%, var(--color-paper) 28%);
}

/* Left column: year hero */
.yc-head {
  display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
  gap: 1.2mm; padding: 1.5mm 0;
  border-right: 0.2mm dashed var(--color-gold-soft);
  text-align: center;
}
.yc-year-glyph {
  font-size: 9pt; line-height: 1; opacity: 0.7;
}
.yc-year {
  font-family: var(--font-display); font-size: 26pt; color: var(--color-red);
  font-weight: 700; line-height: 1; letter-spacing: 0.5px;
}
.yc-card.mood-good .yc-year { color: var(--color-success); }
.yc-card.mood-warn .yc-year { color: var(--color-warn); }
.yc-card.mood-bad  .yc-year { color: var(--color-danger); }

.yc-age {
  font-family: var(--font-body); font-size: 8pt; color: var(--color-muted);
  letter-spacing: 0.3px;
}
.yc-age strong { color: var(--color-ink); font-weight: 600; }

.yc-stars {
  display: flex; gap: 0.3mm; margin-top: 0.5mm;
  font-size: 9.5pt; line-height: 1;
}
.yc-star.on  { color: var(--color-gold-deep); }
.yc-star.off { color: rgba(201,169,97,0.25); }

.yc-gz {
  margin-top: 0.5mm; font-size: 8.5pt; color: var(--color-ink-soft);
  padding: 0.8mm 2mm; border-radius: var(--r-sm);
  background: var(--color-gold-tint);
}
.yc-gz .hz { color: var(--color-red); font-weight: 600; }

/* Right column: body */
.yc-body { display: flex; flex-direction: column; gap: 1.4mm; min-width: 0; }

.yc-tema {
  display: flex; align-items: baseline; gap: 1.5mm;
  padding: 1.2mm 2mm; border-radius: var(--r-sm);
  background: linear-gradient(90deg, rgba(201,169,97,0.18) 0%, rgba(201,169,97,0.05) 100%);
  border-left: 0.4mm solid var(--color-gold);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.yc-tema-lbl {
  font-family: var(--font-display); font-size: 7pt; font-weight: 700;
  color: var(--color-gold-deep); letter-spacing: 1.5px;
  flex-shrink: 0;
}
.yc-tema-text {
  font-family: var(--font-display); font-size: 10pt; font-weight: 600;
  color: var(--color-red); line-height: 1.35; letter-spacing: 0.2px;
}

.yc-narasi {
  font-size: 8.4pt; line-height: 1.55; color: var(--color-ink-soft);
  font-style: italic; padding: 0 1mm;
  text-align: justify;
}

.yc-bintang-row {
  display: flex; flex-wrap: wrap; align-items: center; gap: 1.2mm;
  font-size: 7.8pt;
}
.yc-bintang-lbl {
  font-family: var(--font-display); font-size: 7pt; font-weight: 700;
  color: var(--color-gold-deep); letter-spacing: 1px;
  text-transform: uppercase;
}
.yc-bintang-chip {
  padding: 0.4mm 1.5mm; border-radius: 1mm;
  background: var(--color-gold-tint); color: var(--color-ink-soft);
  border: 0.1mm solid var(--color-gold-soft);
  print-color-adjust: exact;
}

.yc-saran {
  display: flex; gap: 1.5mm; align-items: flex-start;
  font-size: 8.4pt; line-height: 1.5; color: var(--color-ink);
  padding: 1.2mm 2mm; border-radius: 0 var(--r-sm) var(--r-sm) 0;
  background: var(--color-red-soft); border-left: 0.4mm solid var(--color-red);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.yc-saran-icon { flex-shrink: 0; font-size: 9pt; line-height: 1.4; }
.yc-saran-text strong { color: var(--color-red); font-weight: 600; }

.yc-pos-warn {
  display: grid; gap: 1.5mm; margin-top: 0.5mm;
}
.yc-pos-warn.cols-2 { grid-template-columns: 1fr 1fr; }
.yc-pos-warn.cols-1 { grid-template-columns: 1fr; }

.yc-block {
  padding: 1.5mm 2mm; border-radius: var(--r-sm);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  break-inside: avoid;
}
.yc-block.yc-good {
  background: var(--color-success-bg);
  border: 0.15mm solid rgba(76,140,73,0.25);
  border-left: 0.4mm solid var(--color-success);
}
.yc-block.yc-warn {
  background: var(--color-warn-bg);
  border: 0.15mm solid rgba(166,89,23,0.25);
  border-left: 0.4mm solid var(--color-warn);
}
.yc-block-lbl {
  display: flex; align-items: center; gap: 1mm;
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 0.5px; text-transform: uppercase;
  margin-bottom: 0.7mm;
}
.yc-block-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 3.5mm; height: 3.5mm; border-radius: 50%;
  font-weight: 700; color: white; font-size: 7pt;
}
.yc-block.yc-good .yc-block-lbl { color: var(--color-success); }
.yc-block.yc-good .yc-block-icon { background: var(--color-success); }
.yc-block.yc-warn .yc-block-lbl { color: var(--color-warn); }
.yc-block.yc-warn .yc-block-icon { background: var(--color-warn); }

.yc-block ul { margin: 0; padding: 0; list-style: none; }
.yc-block li {
  font-size: 7.7pt; line-height: 1.45; color: var(--color-ink-soft);
  padding: 0.3mm 0 0.3mm 4mm; position: relative;
}
.yc-block li::before {
  position: absolute; left: 0.8mm; top: 1.1mm;
  font-size: 6pt; font-weight: 700;
}
.yc-block.yc-good li::before { content: "+"; color: var(--color-success); }
.yc-block.yc-warn li::before { content: "!"; color: var(--color-warn); }
.yc-block li strong { color: var(--color-red); font-weight: 600; }

/* === Density modifiers — tighten layout when many cards per page === */
.yc-stack.yc-density-mid { gap: 1.8mm; }
.yc-density-mid .yc-card { padding: 2mm; grid-template-columns: 32mm 1fr; gap: 2mm; }
.yc-density-mid .yc-year { font-size: 22pt; }
.yc-density-mid .yc-tema-text { font-size: 9.5pt; }
.yc-density-mid .yc-narasi { font-size: 8.1pt; line-height: 1.45; }
.yc-density-mid .yc-block li { font-size: 7.4pt; line-height: 1.35; padding: 0.2mm 0 0.2mm 4mm; }
.yc-density-mid .yc-saran { font-size: 8.1pt; line-height: 1.4; padding: 1mm 1.8mm; }

.yc-stack.yc-density-tight { gap: 1.3mm; }
.yc-density-tight .yc-card { padding: 1.6mm; grid-template-columns: 28mm 1fr; gap: 1.5mm; }
.yc-density-tight .yc-year { font-size: 18pt; }
.yc-density-tight .yc-stars { font-size: 8.5pt; }
.yc-density-tight .yc-age { font-size: 7.2pt; }
.yc-density-tight .yc-gz { font-size: 7.5pt; padding: 0.6mm 1.5mm; }
.yc-density-tight .yc-tema { padding: 0.8mm 1.5mm; }
.yc-density-tight .yc-tema-lbl { font-size: 6.5pt; }
.yc-density-tight .yc-tema-text { font-size: 8.8pt; line-height: 1.25; }
.yc-density-tight .yc-narasi { font-size: 7.6pt; line-height: 1.4; }
.yc-density-tight .yc-bintang-row { font-size: 7pt; }
.yc-density-tight .yc-bintang-chip { padding: 0.2mm 1.2mm; }
.yc-density-tight .yc-saran { font-size: 7.7pt; line-height: 1.35; padding: 0.8mm 1.5mm; }
.yc-density-tight .yc-block { padding: 1mm 1.4mm; }
.yc-density-tight .yc-block-lbl { font-size: 6.8pt; margin-bottom: 0.4mm; }
.yc-density-tight .yc-block li { font-size: 7pt; line-height: 1.3; padding: 0.15mm 0 0.15mm 3.5mm; }
.yc-density-tight .yc-pos-warn { gap: 1mm; margin-top: 0.3mm; }
"""
