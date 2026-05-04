"""BaZi page V4.8 — port V4.6 visual.

Single page layout:
1. Lead intro callout — explain Empat Pilar dengan ringkas
2. Pilar grid (4 cards) — Tahun · Bulan · Hari (DM) · Jam, dengan element chip + ten god
3. Wu Xing distribution chart — 5 vertical bars (color-coded by yong/xi/ji)
4. 5 Dewa Elemen cards — Yong/Xi/Ji shen (favorable/unfavorable elements)
"""
import html as _html
from templates.page_shell import page_shell
from templates.primitives import callout
from canonical_model import BaZi


def _esc(s):
    return _html.escape(s or "", quote=False)


ELEMEN_HZ = {"Kayu": "木", "Api": "火", "Tanah": "土", "Logam": "金", "Air": "水"}
ELEMEN_COLOR = {
    "Kayu":  "#4C8C47",
    "Api":   "#8B1A1A",
    "Tanah": "#A8843E",
    "Logam": "#8C8FA0",
    "Air":   "#2A4F6E",
}


def _pilar_card(p, idx):
    cls = "bz-pilar dm" if p.is_day_master else "bz-pilar"
    gan_hz = p.gan.hz if p.gan else "—"
    gan_indo = p.gan.indo if p.gan else ""
    zhi_hz = p.zhi.hz if p.zhi else "—"
    zhi_indo = p.zhi.indo if p.zhi else ""
    elem = p.elem or ""
    elem_hz = ELEMEN_HZ.get(elem, "")
    color = ELEMEN_COLOR.get(elem, "#888")
    ten_god_hz = p.ten_god.hz if p.ten_god else ""
    ten_god_indo = p.ten_god.indo if p.ten_god else ""

    dm_badge = '<div class="bz-pilar-dm">DAY MASTER · 命主</div>' if p.is_day_master else ""
    tg_block = ""
    if ten_god_hz:
        tg_block = f'''<div class="bz-pilar-tg">
  <div class="tg-lbl">十 神 · Ten God</div>
  <div class="tg-val"><span class="hz">{_esc(ten_god_hz)}</span></div>
  <div class="tg-indo">{_esc(ten_god_indo)}</div>
</div>'''

    return f'''<div class="{cls}" style="--p-color:{color}">
  <div class="bz-pilar-head">
    <div class="bz-pilar-pos">{_esc(p.posisi)}</div>
    <div class="bz-pilar-pos-hz hz">{_esc(p.posisi_hz)}</div>
  </div>
  <div class="bz-pilar-glyph">
    <span class="hz">{_esc(gan_hz)}</span>
    <span class="hz">{_esc(zhi_hz)}</span>
  </div>
  <div class="bz-pilar-decode">
    <div class="bz-pilar-line"><span class="dl">天 干</span> {_esc(gan_indo)}</div>
    <div class="bz-pilar-line"><span class="dl">地 支</span> {_esc(zhi_indo)}</div>
  </div>
  <div class="bz-pilar-elem"><span class="bz-elem-chip">{_esc(elem_hz)} · {_esc(elem)}</span></div>
  {tg_block}
  {dm_badge}
</div>'''


def _wuxing_chart(wuxing_count, yong_xi_elements, ji_elements, dm_element=None):
    """5-element vertical bar chart with color coding.
    Priority: yong_xi > ji > self (DM element) > neutral.
    """
    if not wuxing_count or all(v == 0 for v in wuxing_count.values()):
        return ""
    elem_order = ["Kayu", "Api", "Tanah", "Logam", "Air"]
    max_count = max(wuxing_count.values()) or 1
    cells = ""
    for e in elem_order:
        cnt = wuxing_count.get(e, 0)
        pct = int(round(cnt / max_count * 100)) if max_count else 0
        if e in yong_xi_elements: cls = "fav"
        elif e in ji_elements: cls = "unfav"
        elif e == dm_element: cls = "self"
        else: cls = "neutral"
        cells += f'''<div class="bz-wux-cell {cls}">
  <div class="bz-wux-track"><div class="bz-wux-fill" style="height: {pct}%"></div></div>
  <div class="bz-wux-label">
    <span class="hz">{ELEMEN_HZ.get(e,"")}</span>
    <span class="id">{e}</span>
    <span class="cnt">×{cnt}</span>
  </div>
</div>'''
    legend_extra = '<span class="leg-item"><span class="dot self"></span> Diri Sendiri (日 主)</span>' if dm_element else ""
    return f'''<div class="bz-wux-chart">
  <div class="bz-wux-bars">{cells}</div>
  <div class="bz-wux-legend">
    <span class="leg-item"><span class="dot fav"></span> Disukai (用 / 喜)</span>
    {legend_extra}
    <span class="leg-item"><span class="dot neutral"></span> Netral (閒)</span>
    <span class="leg-item"><span class="dot unfav"></span> Dihindari (忌 / 仇)</span>
  </div>
</div>'''


def _shen_card(label_id, label_hz, hz, indo, kind):
    """kind: yong (used) / xi (loved) / ji (avoided)."""
    color = {"yong": "#C9A961", "xi": "#4C8C47", "ji": "#A65917"}.get(kind, "#888")
    desc = {
        "yong": "Elemen yang paling Anda butuhkan — perkuat lewat warna, arah, profesi.",
        "xi":   "Elemen pendukung yang menyenangkan — bantu kelancaran hidup.",
        "ji":   "Elemen yang harus dihindari atau diseimbangkan — bisa membawa beban.",
    }.get(kind, "")
    return f'''<div class="bz-shen-card kind-{kind}" style="--s-color:{color}">
  <div class="bz-shen-head">
    <span class="bz-shen-id">{_esc(label_id)}</span>
    <span class="bz-shen-hz hz">{_esc(label_hz)}</span>
  </div>
  <div class="bz-shen-elem">
    <span class="hz">{_esc(hz)}</span>
    <span class="indo">{_esc(indo)}</span>
  </div>
  <div class="bz-shen-desc">{desc}</div>
</div>'''


def render_bazi_page(num: int, bazi: BaZi, subject_name: str = "") -> str:
    if not bazi or not bazi.pilar:
        body = callout("Data Empat Pilar tidak tersedia di sumber MD ini.", variant="warn", icon="⚠")
        return page_shell(num, "Empat Pilar Kelahiran", "四 柱 八 字", "BA ZI · 四柱八字", body, subject_name)

    # 1a. Interpretasi Indonesia (subject-specific) from MD — di paling top
    interp_html = ""
    if bazi.interpretasi:
        interp_html = f'''<div class="bz-interp">
  <div class="bz-interp-icon">💡</div>
  <div class="bz-interp-body">
    <div class="bz-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div>
    <div class="bz-interp-text">{_esc(bazi.interpretasi)}</div>
  </div>
</div>'''

    # 1b. Lead intro callout (universal explanation)
    intro = callout(
        "Empat pasang aksara di bawah adalah \"DNA Kosmis\" Anda — dihitung dari Tahun · Bulan · Hari · Jam kelahiran. "
        "Pilar Hari (日) adalah Anda sendiri (Day Master); tiga pilar lain adalah lingkungan yang membentuk Anda. "
        "Setiap pilar membawa satu Batang Langit (天干) di atas + satu Cabang Bumi (地支) di bawah, masing-masing dengan elemen tersendiri.",
        variant="info", icon="✦",
    )
    intro = interp_html + intro

    # 2. Pilar grid
    pilar_html = "".join(_pilar_card(p, i) for i, p in enumerate(bazi.pilar))
    pilar_section = f'''<div class="bz-section-head">
  <span class="num">1</span>
  <span class="ttl">Empat Pilar Kelahiran</span>
  <span class="hz hz-label">四 柱 八 字</span>
</div>
<div class="bz-pilar-grid">{pilar_html}</div>'''

    # 3. Wu Xing distribution
    yong_xi_elements = set()
    if bazi.yong_shen and bazi.yong_shen.indo: yong_xi_elements.add(bazi.yong_shen.indo)
    if bazi.xi_shen and bazi.xi_shen.indo: yong_xi_elements.add(bazi.xi_shen.indo)
    ji_elements = set()
    if bazi.ji_shen and bazi.ji_shen.indo: ji_elements.add(bazi.ji_shen.indo)
    # Day Master element for "self" color (fallback when yong/xi/ji not in MD)
    dm_element = None
    if len(bazi.pilar) >= 3 and bazi.pilar[2].elem:
        dm_element = bazi.pilar[2].elem
    wuxing_section = ""
    if bazi.wuxing_count:
        wuxing_section = f'''<div class="bz-section-head">
  <span class="num">2</span>
  <span class="ttl">Distribusi 5 Unsur</span>
  <span class="hz hz-label">五 行 分 布</span>
</div>
<div class="bz-section-intro">
  <strong>Wu Xing (五行)</strong> = lima unsur dasar (Kayu · Api · Tanah · Logam · Air). Tiap pilar membawa unsur tertentu —
  distribusi ini menunjukkan unsur mana yang <strong>terlalu banyak</strong> atau <strong>kurang</strong> di bagan Anda.
  <span class="bz-fav-tag">Hijau</span> = unsur yang membantu;
  <span class="bz-self-tag">Emas</span> = elemen Diri (Day Master);
  <span class="bz-unfav-tag">Merah</span> = unsur yang harus diwaspadai.
</div>
{_wuxing_chart(bazi.wuxing_count, yong_xi_elements, ji_elements, dm_element)}'''

    # 4. 5 Dewa Elemen (Yong/Xi/Ji)
    shen_cards = []
    if bazi.yong_shen and bazi.yong_shen.hz:
        shen_cards.append(_shen_card("Dewa Penolong", "用 神 · Yòng Shén",
                                     bazi.yong_shen.hz, bazi.yong_shen.indo or "", "yong"))
    if bazi.xi_shen and bazi.xi_shen.hz:
        shen_cards.append(_shen_card("Dewa Disukai", "喜 神 · Xǐ Shén",
                                     bazi.xi_shen.hz, bazi.xi_shen.indo or "", "xi"))
    if bazi.ji_shen and bazi.ji_shen.hz:
        shen_cards.append(_shen_card("Dewa Dihindari", "忌 神 · Jì Shén",
                                     bazi.ji_shen.hz, bazi.ji_shen.indo or "", "ji"))
    shen_section = ""
    if shen_cards:
        shen_section = f'''<div class="bz-section-head">
  <span class="num">3</span>
  <span class="ttl">Elemen Pelindung & Musuh</span>
  <span class="hz hz-label">喜 用 神</span>
</div>
<div class="bz-section-intro">
  <strong>5 Dewa Elemen</strong> mengkategorikan unsur menjadi: <strong>用 神</strong> paling dibutuhkan,
  <strong>喜 神</strong> pendukung, <strong>忌 神</strong> yang harus dihindari. Pakai warna, arah, dan profesi
  yang sesuai dewa <strong>用</strong> &amp; <strong>喜</strong> untuk hidup lebih lancar.
</div>
<div class="bz-shen-grid">{"".join(shen_cards)}</div>'''

    body = intro + pilar_section + wuxing_section + shen_section
    return page_shell(num, "Empat Pilar Kelahiran", "四 柱 八 字", "BA ZI · 四柱八字", body, subject_name)


BAZI_PAGE_CSS = """
/* === BAZI PAGE V4.8 === */

/* Interpretasi card (Indonesian intro from MD — at top of every section page) */
.bz-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-interp-icon {
  font-size: 22pt; line-height: 1; text-align: center; align-self: center;
}
.bz-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.bz-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.bz-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Section heading inside body */
.bz-section-head {
  display: grid; grid-template-columns: 7mm 1fr auto; gap: var(--sp-3); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1mm;
  margin: var(--sp-2) 0 var(--sp-1) 0;
}
.bz-section-head .num {
  font-family: var(--font-display); font-size: 14pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; text-align: center;
}
.bz-section-head .ttl {
  font-family: var(--font-display); font-size: 11pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.bz-section-head .hz-label {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted);
  letter-spacing: 3px;
}
.bz-section-intro {
  font-size: 7.8pt; line-height: 1.45; color: var(--color-ink);
  background: var(--color-gold-tint); border-left: 0.5mm solid var(--color-gold);
  border-radius: 0 var(--r-sm) var(--r-sm) 0; padding: 1.2mm 2.5mm;
  margin: 0.5mm 0 1.2mm 0;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-section-intro strong { color: var(--color-red); }
.bz-fav-tag { background: rgba(76,140,73,0.18); color: var(--color-success); padding: 0.3mm 1.5mm; border-radius: 0.6mm; font-weight: 600; font-size: 7.5pt; }
.bz-self-tag { background: var(--color-gold-tint); color: var(--color-gold-deep); padding: 0.3mm 1.5mm; border-radius: 0.6mm; font-weight: 600; font-size: 7.5pt; }
.bz-unfav-tag { background: rgba(166,89,23,0.18); color: var(--color-warn); padding: 0.3mm 1.5mm; border-radius: 0.6mm; font-weight: 600; font-size: 7.5pt; }

/* === Pilar Grid (4 cards) === */
.bz-pilar-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-3);
  margin: var(--sp-2) 0 var(--sp-3) 0;
  align-items: stretch;
}
.bz-pilar {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-top: 1.2mm solid var(--p-color, var(--color-gold));
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-2) var(--sp-2);
  position: relative; display: flex; flex-direction: column; gap: 1.5mm;
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.06);
  min-width: 0; min-height: 0; height: auto;
  word-wrap: break-word; overflow-wrap: break-word;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-pilar.dm {
  border: 0.5mm solid var(--color-red);
  border-top: 1.5mm solid var(--p-color, var(--color-red));
  background: linear-gradient(180deg, #FFF7E5 0%, var(--color-paper) 100%);
  box-shadow: 0 1.5mm 4mm rgba(201, 169, 97, 0.25);
}
.bz-pilar-head {
  display: flex; align-items: baseline; justify-content: space-between;
  border-bottom: 0.15mm solid var(--color-gold-soft); padding-bottom: 0.8mm;
}
.bz-pilar-pos {
  font-family: var(--font-display); font-size: 9.5pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px;
}
.bz-pilar-pos-hz {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted);
  letter-spacing: 1.5px;
}
.bz-pilar-glyph {
  display: flex; flex-direction: column; align-items: center; gap: 0.5mm;
  padding: 1mm 0; line-height: 1;
}
.bz-pilar-glyph .hz {
  font-family: var(--font-serif-tc); font-size: 24pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 1.5px;
  text-shadow: 0 1mm 2mm rgba(139, 26, 26, 0.15);
}
.bz-pilar.dm .bz-pilar-glyph .hz { font-size: 26pt; }
.bz-pilar-decode {
  font-size: 7.2pt; color: var(--color-ink-soft); line-height: 1.45;
  text-align: center;
  word-wrap: break-word; overflow-wrap: break-word; hyphens: auto;
}
.bz-pilar-line { padding: 0.2mm 0; word-break: break-word; }
.bz-pilar-line .dl {
  font-family: var(--font-serif-tc); color: var(--color-gold-deep);
  font-size: 6.8pt; margin-right: 1mm; letter-spacing: 0.5px;
}
.bz-pilar-elem { text-align: center; padding-top: 0.5mm; }
.bz-elem-chip {
  display: inline-block; padding: 0.6mm 2mm; border-radius: var(--r-sm);
  background: var(--p-color); color: white;
  font-size: 7.5pt; font-weight: 600; letter-spacing: 0.5px;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-pilar-tg {
  margin-top: 0.5mm; padding-top: 1.2mm;
  border-top: 0.15mm dashed var(--color-gold-soft);
  text-align: center;
  word-wrap: break-word;
}
.bz-pilar-tg .tg-lbl {
  font-family: var(--font-serif-tc); font-size: 6.2pt; color: var(--color-gold-deep);
  letter-spacing: 0.8px;
}
.bz-pilar-tg .tg-val {
  font-family: var(--font-serif-tc); font-size: 10pt; color: var(--color-red);
  font-weight: 700; line-height: 1.1; padding: 0.3mm 0;
}
.bz-pilar-tg .tg-indo {
  font-size: 6.5pt; color: var(--color-ink-soft); line-height: 1.25;
  word-break: break-word;
}
.bz-pilar-dm {
  position: absolute; top: -2.2mm; left: 50%; transform: translateX(-50%);
  background: var(--color-red); color: #F5EBD0;
  font-family: var(--font-display); font-size: 6.5pt; font-weight: 700;
  letter-spacing: 1.2px; padding: 0.4mm 2.5mm; border-radius: 1.5mm;
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.15); white-space: nowrap;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}

/* === Wu Xing Chart === */
.bz-wux-chart {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4) var(--sp-2);
  margin: var(--sp-2) 0 var(--sp-3) 0;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-wux-bars {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--sp-3);
  align-items: end; min-height: 22mm;
}
.bz-wux-cell {
  display: grid; grid-template-rows: 1fr auto; gap: 1mm; align-items: end;
  min-height: 0; min-width: 0; word-wrap: break-word;
}
.bz-wux-track {
  background: rgba(201, 169, 97, 0.12); border-radius: 0.8mm 0.8mm 0 0;
  display: flex; align-items: flex-end; height: 100%; min-height: 15mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-wux-fill {
  width: 100%; background: var(--color-gold-soft);
  border-radius: 0.6mm 0.6mm 0 0; min-height: 3mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-wux-cell.fav .bz-wux-fill {
  background: linear-gradient(180deg, #6DAA68 0%, #4C8C47 100%);
}
.bz-wux-cell.self .bz-wux-fill {
  background: linear-gradient(180deg, #E5D3A1 0%, #C9A961 100%);
}
.bz-wux-cell.unfav .bz-wux-fill {
  background: linear-gradient(180deg, #C58383 0%, #A65917 100%);
}
.bz-wux-cell.neutral .bz-wux-fill {
  background: linear-gradient(180deg, #DCDCD8 0%, #B8B8B0 100%);
  opacity: 0.7;
}
.bz-wux-label {
  text-align: center; font-size: 7.5pt; line-height: 1.2;
  display: flex; flex-direction: column; gap: 0.3mm;
  padding-top: 1mm;
}
.bz-wux-label .hz {
  font-family: var(--font-serif-tc); color: var(--color-red);
  font-size: 10pt; font-weight: 700; line-height: 1;
}
.bz-wux-label .id {
  font-family: var(--font-display); font-size: 7pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.3px;
}
.bz-wux-label .cnt {
  font-family: var(--font-display); font-size: 6.8pt; color: var(--color-gold-deep);
  font-weight: 700; letter-spacing: 0.5px;
}
.bz-wux-cell.fav .bz-wux-label .hz { color: var(--color-success); }
.bz-wux-cell.self .bz-wux-label .hz { color: var(--color-gold-deep); }
.bz-wux-cell.unfav .bz-wux-label .hz { color: var(--color-warn); }
.bz-wux-cell.neutral .bz-wux-label .hz { color: var(--color-faint); }
.bz-wux-legend {
  display: flex; gap: var(--sp-5); justify-content: center; padding-top: var(--sp-2);
  font-size: 7.5pt; color: var(--color-muted); letter-spacing: 0.3px;
}
.bz-wux-legend .leg-item { display: flex; align-items: center; gap: 1.5mm; }
.bz-wux-legend .dot { width: 2.5mm; height: 2.5mm; border-radius: 50%; display: inline-block;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-wux-legend .dot.fav { background: var(--color-success); }
.bz-wux-legend .dot.self { background: var(--color-gold); }
.bz-wux-legend .dot.unfav { background: var(--color-warn); }
.bz-wux-legend .dot.neutral { background: #B8B8B0; }

/* === 5 Dewa Elemen Cards === */
.bz-shen-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sp-3);
  margin: var(--sp-2) 0;
}
.bz-shen-card {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-top: 1mm solid var(--s-color);
  border-radius: var(--r-md); padding: 1.5mm 2.5mm;
  display: flex; flex-direction: column; gap: 1mm;
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.05);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-shen-head {
  display: flex; flex-direction: column; gap: 0.2mm;
  border-bottom: 0.15mm solid var(--color-gold-soft); padding-bottom: 0.6mm;
}
.bz-shen-id {
  font-family: var(--font-display); font-size: 8.5pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.3px;
}
.bz-shen-hz {
  font-family: var(--font-serif-tc); font-size: 7.5pt; color: var(--color-muted);
  letter-spacing: 1.5px;
}
.bz-shen-elem {
  display: flex; align-items: baseline; gap: var(--sp-2);
  padding: 0.8mm 1.5mm; border-radius: var(--r-sm);
  background: var(--color-gold-tint);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bz-shen-elem .hz {
  font-family: var(--font-serif-tc); font-size: 16pt; color: var(--s-color);
  font-weight: 800; line-height: 1;
}
.bz-shen-elem .indo {
  font-family: var(--font-display); font-size: 9.5pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.3px;
}
.bz-shen-desc {
  font-size: 6.8pt; line-height: 1.35; color: var(--color-muted);
  font-style: italic;
}
"""
