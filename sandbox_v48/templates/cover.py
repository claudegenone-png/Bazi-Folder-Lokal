"""Cover page V4.8 — port V4.6 visual (premium hero) ke 3-layer arch.

Visual elements:
- Outer cream-gradient page + cv-frame with double gold border + corner ornaments
- Dragon band ornament top
- Hero title 命 (huge serif TC) + Mìng italic + tagline
- Center: shio SVG inside circle with bagua trigram ring + 4-pilar mini badge
- Name row + red gradient info panel (multi-row dual-date / time / shio / etc)
- Bottom: footer line + seal stamp 命理真解
- Watermarks 福壽命 corners (subtle 4% red)
"""
import re
import math
import html as _html
from pathlib import Path
from canonical_model import Subject, BaZi


# Indo shio name → (Hanzi, asset filename, pinyin)
SHIO_MAP = {
    "Tikus":    ("鼠", "Tikus",    "Shǔ"),
    "Kerbau":   ("牛", "Kerbau",   "Niú"),
    "Macan":    ("虎", "Harimau",  "Hǔ"),    # asset path: Harimau-Merah.svg
    "Harimau":  ("虎", "Harimau",  "Hǔ"),
    "Kelinci":  ("兔", "Kelinci",  "Tù"),
    "Naga":     ("龍", "Naga",     "Lóng"),
    "Ular":     ("蛇", "Ular",     "Shé"),
    "Kuda":     ("馬", "Kuda",     "Mǎ"),
    "Kambing":  ("羊", "Kambing",  "Yáng"),
    "Monyet":   ("猴", "Monyet",   "Hóu"),
    "Ayam":     ("雞", "Ayam",     "Jī"),
    "Anjing":   ("狗", "Anjing",   "Gǒu"),
    "Babi":     ("豬", "Babi",     "Zhū"),
}


GAN_PY = {"甲":"Jia","乙":"Yi","丙":"Bing","丁":"Ding","戊":"Wu","己":"Ji","庚":"Geng","辛":"Xin","壬":"Ren","癸":"Gui"}
ZHI_PY = {"子":"Zi","丑":"Chou","寅":"Yin","卯":"Mao","辰":"Chen","巳":"Si","午":"Wu","未":"Wei","申":"Shen","酉":"You","戌":"Xu","亥":"Hai"}


def _format_lunar(lunar_raw, fallback_year=None):
    """Parse '農曆乙亥 84年 5月 2日' or '民國 82年 癸酉年 3月 26日 (...)'
    Return: 'tanggal D bulan M tahun <span class="hz">XX</span> <em>(Pinyin · YYYY)</em>'
    """
    if not lunar_raw:
        return ""
    s = lunar_raw

    # Find pillar (2 Hanzi gan-zhi pair)
    pillar = ""
    pm = re.search(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*年?", s)
    if pm: pillar = pm.group(1)

    # Find minguo year
    minguo_m = re.search(r"民國\s*(\d{1,3})\s*年|農曆[^\d]*(\d{1,3})\s*年|^(\d{1,3})\s*年", s)
    minguo = None
    if minguo_m:
        minguo = int(next(g for g in minguo_m.groups() if g))
    year = minguo + 1911 if minguo else fallback_year

    # Find month + day (Hanzi pattern)
    md_m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", s)
    if not md_m:
        return _html.escape(lunar_raw, quote=False)
    month, day = int(md_m.group(1)), int(md_m.group(2))

    pinyin = ""
    if pillar and len(pillar) == 2:
        pinyin = f"{GAN_PY.get(pillar[0], '')} {ZHI_PY.get(pillar[1], '')}".strip()

    pillar_part = ""
    if pillar:
        pillar_part = f' tahun <span class="hz">{pillar}</span>'
    extras = []
    if pinyin: extras.append(pinyin)
    if year: extras.append(str(year))
    extras_str = f' <em>({" · ".join(extras)})</em>' if extras else ""
    return f"tanggal {day} bulan {month}{pillar_part}{extras_str}"


SHIO_HZ_TO_INDO = {
    "鼠": "Tikus", "牛": "Kerbau", "虎": "Macan", "兔": "Kelinci",
    "龍": "Naga",  "蛇": "Ular",   "馬": "Kuda",  "羊": "Kambing",
    "猴": "Monyet","雞": "Ayam",   "狗": "Anjing","豬": "Babi",
}


SHIO_ASSET_DIRS = [
    Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\v45\assets"),
    Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\assets"),
]


def _esc(s):
    return _html.escape(s or "", quote=False)


def _resolve_shio(subj: Subject):
    """Return (hanzi, indo_label, asset_filename, pinyin)."""
    indo = subj.shio or ""
    hz = subj.shio_hz or ""
    # Strip 屬 prefix
    hz = re.sub(r"^屬\s*", "", hz)
    # Resolve from indo first
    indo_clean = indo.strip()
    for key, (hanzi, asset, py) in SHIO_MAP.items():
        if key.lower() == indo_clean.lower():
            return hanzi, key, asset, py
    # Fallback resolve from Hanzi
    if hz in SHIO_HZ_TO_INDO:
        indo_resolved = SHIO_HZ_TO_INDO[hz]
        _, asset, py = SHIO_MAP[indo_resolved]
        return hz, indo_resolved, asset, py
    # Last resort
    return hz or "?", indo or "—", "Kelinci", ""


def _load_shio_svg(asset_name: str) -> str:
    """Load Shio SVG file content. Returns inline SVG markup or empty placeholder."""
    for d in SHIO_ASSET_DIRS:
        p = d / f"{asset_name}-Merah.svg"
        if p.exists():
            try:
                content = p.read_text(encoding='utf-8')
                # Strip XML declaration if present
                content = re.sub(r"^<\?xml.*?\?>\s*", "", content, flags=re.DOTALL)
                # Ensure viewBox set + width/height responsive
                content = re.sub(r'<svg([^>]*)\swidth="[^"]+"', r'<svg\1', content)
                content = re.sub(r'<svg([^>]*)\sheight="[^"]+"', r'<svg\1', content)
                return content
            except Exception:
                continue
    # Fallback: emoji glyph
    return ""


def _bagua_ring_svg() -> str:
    """8 trigrams arranged on a circle (Pre-Heaven order)."""
    bagua = ["☰", "☱", "☲", "☳", "☷", "☶", "☵", "☴"]
    R = 56; cx = cy = 60
    items = ""
    for i, sym in enumerate(bagua):
        ang = math.radians(-90 + i * 45)
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        items += (
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="#C9A961" font-size="11" '
            f'font-family="Noto Serif TC, serif" opacity="0.85">{sym}</text>'
        )
    return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" class="cv-bagua-svg" preserveAspectRatio="xMidYMid meet">
  <circle cx="60" cy="60" r="58" fill="none" stroke="#C9A961" stroke-width="0.5" stroke-dasharray="2 1.5" opacity="0.6"/>
  <circle cx="60" cy="60" r="51" fill="none" stroke="#E5D3A1" stroke-width="0.3" opacity="0.4"/>
  {items}
</svg>"""


DRAGON_BAND_SVG = """<svg viewBox="0 0 200 14" xmlns="http://www.w3.org/2000/svg" class="cv-dragon-band" preserveAspectRatio="none">
  <defs>
    <linearGradient id="goldFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#C9A961" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#C9A961" stop-opacity="1"/>
      <stop offset="1" stop-color="#C9A961" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="7" x2="200" y2="7" stroke="url(#goldFade)" stroke-width="0.4"/>
  <circle cx="100" cy="7" r="2.5" fill="#8B1A1A"/>
  <circle cx="100" cy="7" r="1.2" fill="#C9A961"/>
  <path d="M 75 7 Q 87 3 100 7 Q 113 11 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
  <path d="M 75 7 Q 87 11 100 7 Q 113 3 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
</svg>"""


SEAL_SVG = """<svg class="cv-seal" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="36" height="36" fill="#8B1A1A" rx="1"/>
  <rect x="3" y="3" width="34" height="34" fill="none" stroke="#F5EBD0" stroke-width="0.4"/>
  <text x="11" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">命</text>
  <text x="22" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">理</text>
  <text x="11" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">真</text>
  <text x="22" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">解</text>
</svg>"""


def render_cover(subj: Subject, bazi: BaZi = None,
                 penguasa_hari=None, elemen_utama=None) -> str:
    """Render cover.
    penguasa_hari: tuple (indo, hanzi) e.g. ("Tanah Gunung", "戊土")
    elemen_utama: list of (indo, hanzi) e.g. [("Logam","金"),("Air","水")]
    """
    nama_id = subj.nama or "—"
    nama_hz = subj.nama_hanzi if (subj.nama_hanzi and subj.nama_hanzi != subj.nama) else ""

    shio_hz, shio_indo, shio_asset, shio_py = _resolve_shio(subj)
    shio_svg = _load_shio_svg(shio_asset)
    if shio_svg:
        shio_inner = shio_svg
    else:
        # Emoji fallback (rare)
        shio_inner = '<div class="cv-shio-fallback">' + (shio_hz or "?") + '</div>'

    # 4-pilar mini badge (BaZi might be None)
    pilar_hz = ["—", "—", "—", "—"]
    if bazi and bazi.pilar:
        for i, p in enumerate(bazi.pilar[:4]):
            gan_hz = (p.gan.hz if p.gan else "")
            zhi_hz = (p.zhi.hz if p.zhi else "")
            if gan_hz or zhi_hz:
                pilar_hz[i] = (gan_hz + zhi_hz) or "—"

    # Info panel rows
    rows = []

    # Tanggal Indonesia (extract clean if verbose)
    if subj.lahir_tanggal:
        # Try to find "(DD Bulan YYYY)" Indonesian inside
        m = re.search(r"\(?(\d{1,2}\s+\w+\s+\d{4})\)?", subj.lahir_tanggal)
        nasional_clean = m.group(1) if m else subj.lahir_tanggal
        dow = ""
        if subj.hari_lahir:
            hm = re.search(r"\b(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)\b", subj.hari_lahir)
            if hm: dow = hm.group(1)
        dow_html = f' <em>({dow})</em>' if dow else ""
        rows.append(("Tanggal Lahir (Indonesia)", _esc(nasional_clean) + dow_html))

    # Tanggal Tionghoa — formatted with pillar + pinyin + Gregorian year
    if subj.lahir_lunar:
        try:
            fb_year = int(subj.tahun_masehi) if subj.tahun_masehi else None
        except Exception:
            fb_year = None
        rows.append(("Tanggal Lahir (Tionghoa)", _format_lunar(subj.lahir_lunar, fb_year)))

    # Waktu Lahir
    if subj.lahir_jam:
        # Decode "HH時MM分" → "HH:MM"
        jm = re.match(r"(\d{1,2})\s*時\s*(\d{1,2})\s*分", subj.lahir_jam)
        if jm:
            jam_str = f"pukul {jm.group(1)}:{jm.group(2).zfill(2)}"
        else:
            jam_str = _esc(subj.lahir_jam)
        rows.append(("Waktu Lahir", jam_str))

    # Shio
    rows.append(("Shio", f'<span class="hz">{_esc(shio_hz)}</span> {_esc(shio_indo)}' + (f' <em>({shio_py})</em>' if shio_py else '')))

    # Jenis Kelamin
    if subj.gender:
        gender_yy = ""
        if subj.yin_yang:
            gender_yy = f" · {subj.yin_yang}"
        rows.append(("Jenis Kelamin", _esc(subj.gender) + gender_yy))

    # Penguasa Hari (Day Master) — from BaZi
    if penguasa_hari:
        ph_indo, ph_hz = penguasa_hari
        rows.append(("Penguasa Hari", f'{_esc(ph_indo)} <span class="hz">{_esc(ph_hz)}</span>'))

    # Elemen Utama (Yong/Xi Shen)
    if elemen_utama:
        indo_part = " &amp; ".join(_esc(i) for i, _ in elemen_utama)
        hz_part = " ".join(_esc(h) for _, h in elemen_utama if h)
        rows.append(("Elemen Utama", f'{indo_part} <span class="hz">{hz_part}</span>'))

    info_rows_html = ""
    for label, val in rows:
        info_rows_html += (
            f'<div class="row">'
            f'<span class="lbl">{label}</span>'
            f'<span class="colon">:</span>'
            f'<span class="val">{val}</span>'
            f'</div>'
        )

    # Pilar mini badge
    pillars_mini = f"""<div class="cv-pillars-mini">
  <div class="pm-item"><div class="pm-lbl">TAHUN · 年</div><div class="pm-hz">{_esc(pilar_hz[0])}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">BULAN · 月</div><div class="pm-hz">{_esc(pilar_hz[1])}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item active"><div class="pm-lbl">HARI · 日</div><div class="pm-hz">{_esc(pilar_hz[2])}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">JAM · 時</div><div class="pm-hz">{_esc(pilar_hz[3])}</div></div>
</div>""" if any(p != "—" for p in pilar_hz) else ""

    name_row = f"""<div class="cv-name-row">
  <div class="cv-name">{_esc(nama_id)}</div>
  {f'<div class="cv-name-cn">{_esc(nama_hz)}</div>' if nama_hz else ''}
</div>"""

    bagua_svg = _bagua_ring_svg()

    return f"""<section class="page cover">
  <div class="cv-frame">
    <span class="cv-watermark tl">福</span>
    <span class="cv-watermark br">壽</span>
    <span class="cv-watermark side">命</span>

    <div class="cv-top-band">{DRAGON_BAND_SVG}</div>

    <div class="cv-eyebrow">命 · Laporan Ramalan Tionghoa Klasik · 命</div>

    <div class="cv-title-block">
      <div class="cv-title-cn">命</div>
      <div class="cv-title-id">Mìng — Takdir &amp; Bagan Hidup</div>
      <div class="cv-title-sub">四柱論命 · 紫微斗數 · 風水陽宅</div>
    </div>

    <div class="cv-mid">
      <div class="cv-shio-wrap">
        {bagua_svg}
        <div class="cv-shio-frame" data-shio="{_esc(shio_hz)} · {_esc(shio_indo).upper()}">{shio_inner}</div>
      </div>

      {name_row}

      {pillars_mini}

      <div class="cv-info-panel">
        {info_rows_html}
      </div>
    </div>

    <div class="cv-bottom">
      <div class="cv-footer-l">
        <div class="cv-footer-line">八字 · 紫微斗數 · 風水陽宅</div>
        <div class="cv-footer-date">Disusun dengan hormat terhadap hikmat klasik Tionghoa</div>
      </div>
      {SEAL_SVG}
    </div>
  </div>
</section>"""


COVER_CSS = """
/* === COVER PAGE V4.8 (port V4.6 visual) === */
.page.cover {
  padding: 0; display: flex; align-items: stretch;
  width: 210mm; height: 297mm;
  background-color: #FBF7F0;
  background: #FBF7F0 radial-gradient(ellipse at center top, #FFF8E1 0%, #FBF7F0 60%, #F4E8CC 100%);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}
.cv-frame {
  flex: 1; margin: 12mm; padding: 8mm 14mm;
  border: 0.6mm double var(--color-gold);
  border-radius: var(--r-md);
  display: grid; grid-template-rows: auto auto auto 1fr auto; gap: 3mm;
  position: relative; overflow: hidden; text-align: center;
}
.cv-frame::before, .cv-frame::after {
  content: ''; position: absolute; width: 22mm; height: 22mm;
  border: 0.4mm solid var(--color-gold); pointer-events: none;
}
.cv-frame::before { top: 4mm; left: 4mm; border-right: none; border-bottom: none; }
.cv-frame::after  { bottom: 4mm; right: 4mm; border-left: none; border-top: none; }

.cv-watermark {
  position: absolute; font-family: var(--font-serif-tc);
  color: rgba(139, 26, 26, 0.04); font-weight: 700;
  pointer-events: none; user-select: none;
}
.cv-watermark.tl   { top: 6mm; left: 12mm; font-size: 80pt; line-height: 1; transform: rotate(-8deg); }
.cv-watermark.br   { bottom: 6mm; right: 12mm; font-size: 60pt; line-height: 1; transform: rotate(6deg); }
.cv-watermark.side { top: 50%; right: 6mm; font-size: 140pt; transform: rotate(90deg) translateY(50%); transform-origin: right center; }

.cv-top-band { width: 100%; padding: 0 8mm; }
.cv-dragon-band { width: 100%; height: 8mm; opacity: 0.6; }

.cv-eyebrow {
  font-family: var(--font-body); font-size: 8.5pt; letter-spacing: 5px;
  color: var(--color-gold-deep); text-transform: uppercase; font-weight: 600;
  border-bottom: 0.3mm solid var(--color-gold-soft);
  padding: 2mm 0 4mm 0; white-space: nowrap;
}

.cv-title-block { display: flex; flex-direction: column; align-items: center; gap: 1mm; margin-top: 2mm; }
.cv-title-cn {
  font-family: var(--font-serif-tc); font-size: 86pt; font-weight: 700;
  color: var(--color-red); line-height: 1; letter-spacing: 16px;
  text-shadow: 0 2mm 6mm rgba(139, 26, 26, 0.18);
}
.cv-title-id {
  font-family: var(--font-display); font-size: 16pt; font-style: italic;
  color: var(--color-ink); letter-spacing: 4px; margin-top: 2mm;
}
.cv-title-sub {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-gold-deep);
  letter-spacing: 8px; margin-top: 1mm; opacity: 0.9;
}

.cv-mid { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; gap: 3mm; }
.cv-shio-wrap { width: 76mm; height: 76mm; position: relative; margin: 1mm auto; }
.cv-bagua-svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.cv-shio-frame {
  width: 56mm; height: 56mm; margin: 10mm auto 0;
  border-radius: 50%; padding: 4mm;
  background: linear-gradient(135deg, #FFFEF8 0%, #F5EBD0 100%);
  border: 0.8mm solid var(--color-gold);
  box-shadow: 0 4mm 12mm rgba(201, 169, 97, 0.3);
  display: flex; align-items: center; justify-content: center;
  position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.cv-shio-frame > svg { width: 100%; height: 100%; object-fit: contain; }
.cv-shio-frame > .cv-shio-fallback { font-family: var(--font-serif-tc); font-size: 50pt; color: var(--color-red); font-weight: 800; }
.cv-shio-frame::after {
  content: attr(data-shio);
  position: absolute; bottom: -3mm; left: 50%; transform: translateX(-50%);
  background: var(--color-red); color: #F5EBD0;
  font-family: var(--font-serif-tc); font-size: 8pt;
  padding: 1.5mm 5mm; border-radius: 4mm; letter-spacing: 3px;
  font-weight: 600; white-space: nowrap;
  box-shadow: 0 1mm 3mm rgba(0, 0, 0, 0.2);
}

.cv-name-row { display: flex; align-items: baseline; justify-content: center; gap: 6mm; margin-top: 4mm; }
.cv-name {
  font-family: var(--font-display); font-size: 30pt; color: var(--color-ink);
  font-weight: 600; line-height: 1;
}
.cv-name-cn {
  font-family: var(--font-serif-tc); font-size: 24pt; color: var(--color-red);
  font-weight: 700; line-height: 1; letter-spacing: 4px;
}

.cv-pillars-mini {
  display: flex; align-items: center; justify-content: center; gap: 3mm;
  margin: 1mm auto 0; padding: 1.5mm 4mm;
  background: rgba(255, 252, 245, 0.6);
  border: 0.2mm solid var(--color-gold-soft); border-radius: var(--r-sm);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.cv-pillars-mini .pm-item { display: flex; flex-direction: column; align-items: center; gap: 0.3mm; padding: 0 1mm; }
.cv-pillars-mini .pm-lbl { font-family: var(--font-body); font-size: 6.5pt; color: var(--color-gold-deep); letter-spacing: 2px; font-weight: 700; }
.cv-pillars-mini .pm-hz { font-family: var(--font-serif-tc); font-size: 13pt; color: var(--color-red); font-weight: 700; line-height: 1; letter-spacing: 1px; }
.cv-pillars-mini .pm-item.active { transform: scale(1.1); position: relative; }
.cv-pillars-mini .pm-item.active .pm-hz { text-shadow: 0 0 8px rgba(201,169,97,0.5); }
.cv-pillars-mini .pm-sep { color: var(--color-gold); font-size: 11pt; opacity: 0.5; }

.cv-info-panel {
  background: linear-gradient(135deg, #8B1A1A 0%, #6E1414 100%);
  color: white; border-radius: var(--r-md); padding: 4.5mm 8mm;
  margin: 3mm auto 0; max-width: 158mm;
  box-shadow: 0 2mm 6mm rgba(139, 26, 26, 0.25);
  text-align: left; font-size: 9pt; line-height: 1.7;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.cv-info-panel .row {
  display: grid; grid-template-columns: 50mm 3mm 1fr;
  align-items: baseline; white-space: nowrap;
}
.cv-info-panel .lbl { color: #F5EBD0; font-weight: 500; letter-spacing: 0.3px; font-size: 8.5pt; }
.cv-info-panel .colon { color: var(--color-gold); font-weight: 600; }
.cv-info-panel .val { color: white; font-weight: 500; }
.cv-info-panel .val .hz { font-family: var(--font-serif-tc); color: #F5EBD0; font-weight: 700; margin: 0 1mm; }
.cv-info-panel .val em { color: #E5D3A1; font-style: italic; font-weight: 400; font-size: 8pt; }

.cv-bottom {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-top: 4mm; padding: 0 2mm;
}
.cv-footer-l { text-align: left; }
.cv-footer-line { font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-red); letter-spacing: 2px; }
.cv-footer-date { font-family: var(--font-body); font-size: 7pt; color: var(--color-muted); letter-spacing: 1.5px; text-transform: uppercase; margin-top: 1mm; }
.cv-seal { width: 18mm; height: 18mm; transform: rotate(-4deg); filter: drop-shadow(0 1mm 2mm rgba(139,26,26,0.3)); print-color-adjust: exact; -webkit-print-color-adjust: exact; }
"""
