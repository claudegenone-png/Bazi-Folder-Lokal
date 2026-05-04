"""Kecocokan Shio Pasangan page V4.8.

Layout:
1. Interpretasi top card (red gradient) — subject-specific Saran from MD
2. Hero: 12-shio compatibility ring/grid showing rating per shio
3. Breakdown groups:
   - 🟢 Sangat Cocok (rating 5)
   - 🟡 Cukup Cocok (rating 3-4)
   - 🔴 Pantangan (rating 1-2)
4. Pantangan summary callout (warn) — kalau ada
"""
import html as _html
from templates.page_shell import page_shell
from templates.primitives import callout
from canonical_model import KecocokanShio


def _esc(s):
    return _html.escape(s or "", quote=False)


# Canonical 12 shio order (Tikus first per Tionghoa convention)
SHIO_ORDER = [
    ("Tikus",   "鼠", "🐀"), ("Kerbau",  "牛", "🐂"),
    ("Macan",   "虎", "🐯"), ("Kelinci", "兔", "🐰"),
    ("Naga",    "龍", "🐲"), ("Ular",    "蛇", "🐍"),
    ("Kuda",    "馬", "🐴"), ("Kambing", "羊", "🐑"),
    ("Monyet",  "猴", "🐒"), ("Ayam",    "雞", "🐓"),
    ("Anjing",  "狗", "🐕"), ("Babi",    "豬", "🐷"),
]


def _shio_lookup(matches):
    """shio_id → ShioMatch dict. Plus 'others' entry kalau ada."""
    d = {}
    others = None
    for m in matches:
        if m.is_other:
            others = m
        else:
            d[m.shio_id] = m
    return d, others


def _stars_html(n):
    on = "★" * n
    off = "☆" * (5 - n)
    return f'<span class="ks-stars on">{on}</span><span class="ks-stars off">{off}</span>'


def _shio_card(indo, hz, emoji, match=None, default_match=None):
    """Render one shio card in the 12-grid."""
    if match:
        rating = match.rating
        mood = match.mood
        note = match.note or ""
    elif default_match:
        rating = default_match.rating
        mood = default_match.mood
        note = "(Shio lainnya)"
    else:
        rating = 3
        mood = "neutral"
        note = "—"

    return f'''<div class="ks-cell mood-{mood}">
  <div class="ks-emoji">{emoji}</div>
  <div class="ks-hz hz">{_esc(hz)}</div>
  <div class="ks-id">{_esc(indo)}</div>
  <div class="ks-rating">{_stars_html(rating)}</div>
</div>'''


def _breakdown_group(title, mood, label_short, matches_in_group):
    if not matches_in_group: return ""
    items = "".join(
        f'<li><strong>{_esc(m.shio_id)}</strong> <span class="hz">{_esc(m.shio_hz)}</span>' +
        (f' — <span class="ks-note-text">{_esc(m.note)}</span>' if m.note else "") +
        '</li>'
        for m in matches_in_group
    )
    return f'''<div class="ks-bd ks-bd-{mood}">
  <div class="ks-bd-head">
    <span class="ks-bd-icon">{label_short}</span>
    <span class="ks-bd-title">{_esc(title)}</span>
    <span class="ks-bd-count">{len(matches_in_group)}</span>
  </div>
  <ul class="ks-bd-list">{items}</ul>
</div>'''


def render_kecocokan_shio_page(num: int, ks: KecocokanShio, subject_name: str = "") -> str:
    if not ks:
        body = callout("Data kecocokan shio tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, "Kecocokan Shio Pasangan", "婚 配",
                          "KECOCOKAN · 婚配", body, subject_name)

    parts = []

    # 1. Interpretasi top
    if ks.interpretasi:
        parts.append(f'''<div class="ks-interp">
  <div class="ks-interp-icon">💡</div>
  <div class="ks-interp-body">
    <div class="ks-interp-eyebrow">INTERPRETASI · 婚 配 解 析</div>
    <div class="ks-interp-text">{_esc(ks.interpretasi)}</div>
  </div>
</div>''')

    # 2. 12-shio grid
    lookup, others = _shio_lookup(ks.matches)
    grid_cells = "".join(
        _shio_card(indo, hz, emoji, lookup.get(indo), others)
        for indo, hz, emoji in SHIO_ORDER
    )

    parts.append('''<div class="ks-section-head">
  <span class="num">1</span>
  <span class="ttl">Peta Kecocokan 12 Shio</span>
  <span class="hz hz-label">十 二 生 肖</span>
</div>''')
    parts.append(callout(
        "Setiap shio punya kompatibilitas alami dengan shio Anda. Bintang ⭐ menunjukkan tingkat kecocokan: "
        "<strong>5★ sangat cocok</strong>, <strong>3★ sedang</strong>, <strong>1-2★ pantangan</strong>. "
        "Warna hijau = harmonis, kuning = perlu effort, merah = sebaiknya hindari.",
        variant="info", icon="✦"
    ))
    parts.append(f'<div class="ks-grid">{grid_cells}</div>')

    # 3. Breakdown groups
    sangat_cocok = [m for m in ks.matches if not m.is_other and m.rating >= 4]
    sedang = [m for m in ks.matches if not m.is_other and m.rating == 3]
    pantang = [m for m in ks.matches if not m.is_other and m.rating <= 2]

    parts.append('''<div class="ks-section-head">
  <span class="num">2</span>
  <span class="ttl">Detail Per Kelompok</span>
  <span class="hz hz-label">分 類</span>
</div>''')

    bd_html = ""
    bd_html += _breakdown_group("Sangat Cocok", "good", "✓", sangat_cocok)
    bd_html += _breakdown_group("Cukup Cocok / Sedang", "neutral", "~", sedang)
    bd_html += _breakdown_group("Pantangan — Sebaiknya Hindari", "bad", "✗", pantang)
    parts.append(f'<div class="ks-bd-stack">{bd_html}</div>')

    body = "\n".join(parts)
    return page_shell(num, "Kecocokan Shio Pasangan", "婚 配",
                      "KECOCOKAN · 婚配", body, subject_name)


KECOCOKAN_SHIO_PAGE_CSS = """
/* === KECOCOKAN SHIO PAGE V4.8 === */

/* Interpretasi top card (red gradient) */
.ks-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-interp-icon { font-size: 22pt; line-height: 1; align-self: center; text-align: center; }
.ks-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.ks-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.ks-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Section heading */
.ks-section-head {
  display: grid; grid-template-columns: 8mm 1fr auto; gap: var(--sp-3); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1.5mm;
  margin: var(--sp-4) 0 var(--sp-2) 0;
}
.ks-section-head .num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; text-align: center;
}
.ks-section-head .ttl {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.ks-section-head .hz-label {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-muted);
  letter-spacing: 4px;
}

/* 12-shio grid (4×3 cards) */
.ks-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm;
  margin: var(--sp-2) 0 var(--sp-3) 0;
}
.ks-cell {
  background: var(--color-paper); border: 0.25mm solid var(--color-gold-soft);
  border-radius: var(--r-sm); padding: 1.5mm 2mm;
  display: flex; flex-direction: column; align-items: center; gap: 0.5mm;
  text-align: center; min-height: 30mm;
  box-shadow: 0 0.3mm 1mm rgba(0, 0, 0, 0.04);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-cell.mood-good {
  background: linear-gradient(180deg, #F0F8EC 0%, var(--color-paper) 100%);
  border-left: 0.6mm solid var(--color-success);
}
.ks-cell.mood-neutral {
  background: linear-gradient(180deg, #FCF8EC 0%, var(--color-paper) 100%);
  border-left: 0.6mm solid var(--color-gold);
}
.ks-cell.mood-warn {
  background: linear-gradient(180deg, #FCF4E8 0%, var(--color-paper) 100%);
  border-left: 0.6mm solid var(--color-warn);
}
.ks-cell.mood-bad {
  background: linear-gradient(180deg, #FBE9E9 0%, var(--color-paper) 100%);
  border-left: 0.6mm solid var(--color-danger);
  opacity: 0.95;
}
.ks-emoji { font-size: 18pt; line-height: 1; }
.ks-hz {
  font-family: var(--font-serif-tc); font-size: 14pt; color: var(--color-red);
  font-weight: 700; line-height: 1;
}
.ks-cell.mood-good .ks-hz { color: var(--color-success); }
.ks-cell.mood-bad .ks-hz { color: var(--color-danger); }
.ks-id {
  font-family: var(--font-display); font-size: 9pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.2px;
}
.ks-rating { font-size: 9pt; line-height: 1; margin-top: auto; padding-top: 1mm; }
.ks-stars.on { color: var(--color-gold-deep); letter-spacing: 0.3px; }
.ks-stars.off { color: rgba(201, 169, 97, 0.25); letter-spacing: 0.3px; }

/* Breakdown groups */
.ks-bd-stack { display: flex; flex-direction: column; gap: var(--sp-2); margin: var(--sp-2) 0 var(--sp-3) 0; }
.ks-bd {
  border: 0.25mm solid var(--color-gold-soft); border-radius: var(--r-md);
  padding: var(--sp-2) var(--sp-3);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-bd.ks-bd-good {
  background: linear-gradient(135deg, #F0F8EC 0%, var(--color-paper) 100%);
  border-left: 0.8mm solid var(--color-success);
}
.ks-bd.ks-bd-neutral {
  background: linear-gradient(135deg, var(--color-cream-deep) 0%, var(--color-paper) 100%);
  border-left: 0.8mm solid var(--color-gold);
}
.ks-bd.ks-bd-bad {
  background: linear-gradient(135deg, #FBE9E9 0%, var(--color-paper) 100%);
  border-left: 0.8mm solid var(--color-danger);
}
.ks-bd-head {
  display: flex; align-items: center; gap: var(--sp-2);
  padding-bottom: 1mm; margin-bottom: 1.5mm;
  border-bottom: 0.15mm solid var(--color-gold-soft);
}
.ks-bd-icon {
  font-family: var(--font-display); font-size: 13pt; font-weight: 800;
  width: 7mm; height: 7mm; border-radius: 50%; display: inline-flex;
  align-items: center; justify-content: center;
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
}
.ks-bd-good .ks-bd-icon { color: var(--color-success); border-color: var(--color-success); }
.ks-bd-neutral .ks-bd-icon { color: var(--color-gold-deep); border-color: var(--color-gold); }
.ks-bd-bad .ks-bd-icon { color: var(--color-danger); border-color: var(--color-danger); }
.ks-bd-title {
  font-family: var(--font-display); font-size: 11pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.3px;
}
.ks-bd-count {
  margin-left: auto; font-family: var(--font-display); font-size: 8pt;
  color: var(--color-gold-deep); font-weight: 700; letter-spacing: 0.5px;
  padding: 0.4mm 1.5mm; background: var(--color-gold-tint); border-radius: 0.6mm;
  print-color-adjust: exact;
}
.ks-bd-list {
  margin: 0; padding: 0; list-style: none;
  display: flex; flex-direction: column; gap: 0.6mm;
}
.ks-bd-list li {
  font-size: 9pt; line-height: 1.5; color: var(--color-ink);
  padding: 0.4mm 0;
}
.ks-bd-list li strong { color: var(--color-red); font-weight: 600; }
.ks-bd-list li .hz { font-family: var(--font-serif-tc); color: var(--color-red); }
.ks-bd-list li .ks-note-text { color: var(--color-ink-soft); font-style: italic; }
"""
