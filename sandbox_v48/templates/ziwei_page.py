"""ZiWei page V4.8 — Peta Bintang Zi Wei (紫微斗數).

Layout:
1. Interpretasi card (red gradient) di top — subject-specific from MD
2. Data Inti panel — 命主/身主/命宮/身宮/五行/etc
3. Empat Transformasi (4 cards) — 化祿/化權/化科/化忌
4. 12 Istana Grid — palace summary cards (kalau MD ada tabel; else section bawah saja)
"""
import html as _html
import re
from templates.page_shell import page_shell
from templates.primitives import callout
from canonical_model import ZiWei


def _esc(s):
    return _html.escape(s or "", quote=False)


# Role color mapping for 4 transformations
ROLE_INFO = {
    "化祿": {"color": "#4C8C47", "icon": "💰", "label_id": "Rezeki", "pinyin": "Huà Lù"},
    "化權": {"color": "#8B1A1A", "icon": "⚡", "label_id": "Kekuasaan", "pinyin": "Huà Quán"},
    "化科": {"color": "#A8843E", "icon": "🎓", "label_id": "Reputasi", "pinyin": "Huà Kē"},
    "化忌": {"color": "#A65917", "icon": "⚠", "label_id": "Hambatan", "pinyin": "Huà Jì"},
}


# Palace canonical order (for grid layout)
PALACE_ORDER = [
    ("命宮",   "Istana Nasib",        "Karakter & arah hidup",       "✦"),
    ("兄弟宮", "Istana Saudara",      "Hubungan saudara & teman",    "👥"),
    ("夫妻宮", "Istana Pasangan",     "Asmara & pernikahan",          "💕"),
    ("子女宮", "Istana Anak",         "Anak-anak & keturunan",        "👶"),
    ("財帛宮", "Istana Keuangan",     "Rezeki & kekayaan",            "💰"),
    ("疾厄宮", "Istana Kesehatan",    "Tubuh & penyakit",             "🏥"),
    ("遷移宮", "Istana Perpindahan",  "Perjalanan & mobilitas",       "✈"),
    ("僕役宮", "Istana Bawahan",      "Rekan kerja & bawahan",        "🤝"),
    ("官祿宮", "Istana Karier",       "Profesi & jabatan",            "💼"),
    ("田宅宮", "Istana Properti",     "Tanah & rumah",                "🏠"),
    ("福德宮", "Istana Kebahagiaan",  "Batin & spiritualitas",        "🌸"),
    ("父母宮", "Istana Orang Tua",    "Hubungan ayah & ibu",          "👨‍👩"),
]


def _palace_lookup(palaces):
    """Build dict: nama_hz → Palace, with flexible matching."""
    d = {}
    for p in palaces:
        # Try matching with both 宮 suffix variants
        d[p.nama_hz] = p
        if not p.nama_hz.endswith("宮"):
            d[p.nama_hz + "宮"] = p
        elif p.nama_hz.endswith("宮"):
            d[p.nama_hz[:-1]] = p
    return d


def _palace_card(canon_hz, canon_id, desc, icon, palace=None):
    """Render one palace card. palace=None → empty placeholder card.
    Strip 'Istana ' prefix — page title sudah cukup ('Dua Belas Istana Hidup').
    """
    short_id = re.sub(r"^Istana\s+", "", canon_id or "")
    bintang_html = ""
    age_html = ""
    ganzhi_html = ""
    if palace:
        if palace.bintang_utama:
            stars = " · ".join(b.hz for b in palace.bintang_utama[:2])
            bintang_html = f'<div class="zw-pal-stars"><span class="hz">{_esc(stars)}</span></div>'
        if palace.age_range:
            age_html = f'<div class="zw-pal-age">Usia {_esc(palace.age_range)}</div>'
        if palace.ganzhi:
            ganzhi_html = f'<div class="zw-pal-gz hz">{_esc(palace.ganzhi)}</div>'
        klass = "zw-palace filled"
    else:
        klass = "zw-palace empty"

    return f'''<div class="{klass}">
  <div class="zw-pal-icon">{icon}</div>
  <div class="zw-pal-hz hz">{_esc(canon_hz)}</div>
  <div class="zw-pal-id">{_esc(short_id)}</div>
  <div class="zw-pal-desc">{_esc(desc)}</div>
  {bintang_html}
  {ganzhi_html}
  {age_html}
</div>'''


def _transformasi_card(t):
    info = ROLE_INFO.get(t.role_hz, {"color": "#888", "icon": "✦", "label_id": "", "pinyin": ""})
    role_indo = t.role_indo or info["label_id"]
    star_indo = t.star_indo or ""
    makna = t.makna or ""
    return f'''<div class="zw-trans-card" style="--t-color:{info['color']}">
  <div class="zw-trans-icon">{info['icon']}</div>
  <div class="zw-trans-role-hz hz">{_esc(t.role_hz)}</div>
  <div class="zw-trans-role-id">{_esc(role_indo)}</div>
  <div class="zw-trans-star">
    <span class="hz">{_esc(t.star_hz)}</span>
    <span class="indo">{_esc(star_indo)}</span>
  </div>
  <div class="zw-trans-makna">{_esc(makna)}</div>
</div>'''


def _data_inti_panel(items):
    rows = ""
    for kv in items:
        # Strip leading **bold** + parens already cleaned
        key = re.sub(r"\*\*", "", kv.key).strip()
        val = re.sub(r"\*\*", "", kv.value).strip()
        rows += f'''<div class="zw-di-row">
  <div class="zw-di-key">{_esc(key)}</div>
  <div class="zw-di-val">{_esc(val)}</div>
</div>'''
    return f'''<div class="zw-data-inti">
  <div class="zw-di-head"><span class="zw-di-icon">⊙</span><span class="zw-di-title">Data Inti Peta</span><span class="zw-di-hz hz">命 主 · 身 主</span></div>
  <div class="zw-di-rows">{rows}</div>
</div>'''


def render_ziwei_page(num: int, ziwei: ZiWei, subject_name: str = "") -> str:
    if not ziwei:
        body = callout("Data Zi Wei tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, "Peta Bintang Zi Wei", "紫 微 命 盤",
                          "ZI WEI · 紫微", body, subject_name)

    parts = []

    # 1. Interpretasi top card
    if ziwei.interpretasi:
        parts.append(f'''<div class="zw-interp">
  <div class="zw-interp-icon">💡</div>
  <div class="zw-interp-body">
    <div class="zw-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div>
    <div class="zw-interp-text">{_esc(ziwei.interpretasi)}</div>
  </div>
</div>''')

    # 2. Data Inti panel
    if ziwei.data_inti:
        parts.append(_data_inti_panel(ziwei.data_inti))

    # 3. Empat Transformasi cards
    if ziwei.transformasi:
        parts.append('''<div class="zw-section-head">
  <span class="num">1</span>
  <span class="ttl">Empat Transformasi Bintang</span>
  <span class="hz hz-label">四 化 · Sì Huà</span>
</div>''')
        parts.append(callout(
            "<strong>四化 (Si Hua)</strong> = empat transformasi yang membentuk dinamika hidup. "
            "Setiap orang punya 4 bintang ter-transformasi: <strong>祿 Rezeki</strong>, "
            "<strong>權 Kekuasaan</strong>, <strong>科 Reputasi</strong>, dan <strong>忌 Hambatan</strong>. "
            "Tahu bintang mana yang ter-transformasi = tahu di area mana hidup Anda paling dinamis.",
            variant="info", icon="✦"
        ))
        cards = "".join(_transformasi_card(t) for t in ziwei.transformasi)
        parts.append(f'<div class="zw-trans-grid">{cards}</div>')

    # 4. 12 Palace grid
    if ziwei.palaces or len(ziwei.palaces or []) == 0:
        # Always render full grid (12 slots), filled or empty
        palace_dict = _palace_lookup(ziwei.palaces or [])
        parts.append('''<div class="zw-section-head">
  <span class="num">2</span>
  <span class="ttl">Dua Belas Istana Hidup</span>
  <span class="hz hz-label">十 二 宮 · Shí Èr Gōng</span>
</div>''')
        parts.append(callout(
            "Setiap dimensi hidup dipetakan ke <strong>satu istana</strong>. "
            "Bintang yang menempati istana memberi tema dominan untuk area tersebut. "
            "Detail per-istana dijelaskan di bab-bab berikutnya.",
            variant="info", icon="✦"
        ))
        cards = "".join(
            _palace_card(canon_hz, canon_id, desc, icon, palace_dict.get(canon_hz))
            for (canon_hz, canon_id, desc, icon) in PALACE_ORDER
        )
        parts.append(f'<div class="zw-palace-grid">{cards}</div>')

    body = "\n".join(parts)
    return page_shell(num, "Peta Bintang Zi Wei", "紫 微 命 盤",
                      "ZI WEI · 紫微", body, subject_name)


ZIWEI_PAGE_CSS = """
/* === ZIWEI PAGE V4.8 === */

/* Interpretasi top card (red gradient) */
.zw-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.zw-interp-icon { font-size: 22pt; line-height: 1; align-self: center; text-align: center; }
.zw-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.zw-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.zw-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Section heading */
.zw-section-head {
  display: grid; grid-template-columns: 8mm 1fr auto; gap: var(--sp-3); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1.5mm;
  margin: var(--sp-4) 0 var(--sp-2) 0;
}
.zw-section-head .num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; text-align: center;
}
.zw-section-head .ttl {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.zw-section-head .hz-label {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-muted);
  letter-spacing: 4px;
}

/* Data Inti panel */
.zw-data-inti {
  background: linear-gradient(135deg, var(--color-cream-deep) 0%, var(--color-paper) 100%);
  border: 0.3mm solid var(--color-gold); border-radius: var(--r-md);
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.zw-di-head {
  display: flex; align-items: baseline; gap: var(--sp-2);
  padding-bottom: 1.5mm; margin-bottom: 2mm;
  border-bottom: 0.2mm solid var(--color-gold-soft);
}
.zw-di-icon { font-size: 14pt; color: var(--color-red); }
.zw-di-title {
  font-family: var(--font-display); font-size: 11pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.4px;
}
.zw-di-hz {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted);
  letter-spacing: 3px; margin-left: auto;
}
.zw-di-rows {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.2mm var(--sp-4);
}
.zw-di-row {
  display: grid; grid-template-columns: 38mm 1fr; gap: var(--sp-2);
  align-items: baseline; padding: 0.6mm 0;
  border-bottom: 0.1mm dashed var(--color-gold-soft); font-size: 8.5pt;
}
.zw-di-key {
  font-family: var(--font-serif-tc); color: var(--color-red); font-weight: 600;
  font-size: 9pt; letter-spacing: 0.5px;
}
.zw-di-val { color: var(--color-ink); font-weight: 500; }

/* Transformasi grid (4 cards) */
.zw-trans-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-3);
  margin: var(--sp-2) 0 var(--sp-3) 0;
}
.zw-trans-card {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-top: 1.2mm solid var(--t-color);
  border-radius: var(--r-md); padding: var(--sp-2) var(--sp-3);
  display: flex; flex-direction: column; align-items: center; gap: 1mm;
  text-align: center;
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.05);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.zw-trans-icon { font-size: 16pt; line-height: 1; }
.zw-trans-role-hz {
  font-family: var(--font-serif-tc); font-size: 18pt; color: var(--t-color);
  font-weight: 700; line-height: 1; letter-spacing: 1px;
}
.zw-trans-role-id {
  font-family: var(--font-display); font-size: 9pt; color: var(--color-ink);
  font-weight: 700; letter-spacing: 0.4px;
  padding: 0.6mm 2mm; background: var(--color-gold-tint); border-radius: 0.6mm;
}
.zw-trans-star {
  display: flex; flex-direction: column; align-items: center; gap: 0.2mm;
  margin-top: 1mm; padding-top: 1mm;
  border-top: 0.15mm dashed var(--color-gold-soft); width: 100%;
}
.zw-trans-star .hz {
  font-family: var(--font-serif-tc); font-size: 12pt; color: var(--color-red);
  font-weight: 700; line-height: 1;
}
.zw-trans-star .indo {
  font-size: 7.5pt; color: var(--color-muted); font-style: italic;
}
.zw-trans-makna {
  font-size: 7.5pt; line-height: 1.4; color: var(--color-ink-soft);
  margin-top: 0.5mm; min-height: 9mm;
}

/* 12 Palace Grid (4 columns × 3 rows) */
.zw-palace-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm;
  margin: var(--sp-2) 0 var(--sp-3) 0;
}
.zw-palace {
  background: var(--color-paper); border: 0.25mm solid var(--color-gold-soft);
  border-radius: var(--r-sm); padding: 1.5mm 2mm;
  display: flex; flex-direction: column; align-items: center; gap: 0.5mm;
  text-align: center; min-height: 26mm;
  box-shadow: 0 0.3mm 1mm rgba(0, 0, 0, 0.04);
  break-inside: avoid; position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.zw-palace.filled {
  background: linear-gradient(180deg, var(--color-paper) 0%, var(--color-cream-deep) 100%);
  border-left: 0.4mm solid var(--color-gold);
}
.zw-palace.empty {
  background: rgba(251, 247, 240, 0.5);
  opacity: 0.65;
}
.zw-pal-icon { font-size: 11pt; line-height: 1; margin-top: 0.3mm; }
.zw-pal-hz {
  font-family: var(--font-serif-tc); font-size: 13pt; color: var(--color-red);
  font-weight: 700; line-height: 1; letter-spacing: 1px;
}
.zw-pal-id {
  font-family: var(--font-display); font-size: 8.5pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.2px;
}
.zw-pal-desc {
  font-size: 6.5pt; line-height: 1.25; color: var(--color-muted);
  font-style: italic; padding: 0 1mm;
}
.zw-pal-stars {
  margin-top: auto; padding-top: 0.8mm;
  border-top: 0.15mm dashed var(--color-gold-soft); width: 100%;
}
.zw-pal-stars .hz {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-gold-deep);
  font-weight: 600;
}
.zw-pal-age {
  font-size: 6.5pt; color: var(--color-muted); font-style: italic;
}
.zw-pal-gz {
  font-family: var(--font-serif-tc); font-size: 8pt; color: var(--color-gold-deep);
  font-weight: 700; padding: 0.3mm 1.5mm;
  background: var(--color-gold-tint); border-radius: 0.5mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
"""
