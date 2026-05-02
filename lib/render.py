"""
render.py — Orchestrator HTML untuk skill xingqiao-fortune-id.

Input  : dict dengan {subject, chart, transcripts, dayun_now_age?}
Output : self-contained report.html (CSS inline, SVG inline)

Pakai bazi_calc + shio_compat sebagai source of truth.
Tidak butuh dependency external (no Jinja, no chart libs) — semua SVG
chart digenerate manual supaya PDF self-contained dan deterministik.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from html import escape
from pathlib import Path

# Allow running as script atau import sebagai module
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bazi_calc  # noqa: E402
import shio_compat  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = ROOT / "SVG Shio" / "V2"
TEMPLATE_DIR = ROOT / "template"

ELEMENT_LABEL = {
    "金": ("Logam", "jin"),
    "木": ("Kayu", "mu"),
    "水": ("Air", "shui"),
    "火": ("Api", "huo"),
    "土": ("Tanah", "tu"),
}

# Indonesian labels for the 14 standard Zi Wei palaces
PALACE_ID = {
    "命宮": "Palace Diri",
    "兄弟": "Saudara",
    "夫妻": "Pasangan",
    "子女": "Anak",
    "財帛": "Rezeki Harian",
    "疾厄": "Kesehatan",
    "遷移": "Perpindahan",
    "僕役": "Bawahan & Teman",
    "官祿": "Karir Formal",
    "田宅": "Properti & Rumah",
    "福德": "Berkah & Karma",
    "父母": "Orangtua",
}

CATEGORY_ID = {
    "性情": "Kepribadian",
    "全局總論": "Ringkasan Menyeluruh",
    "神煞": "Bintang Nasib (Shensha)",
    "財富": "Kekayaan",
    "婚配": "Kompatibilitas Pernikahan",
    "事業": "Karir & Profesi",
    "陽宅": "Feng Shui Hunian",
    "古書云": "Catatan dari Kitab Klasik",
    "宿命": "Takdir & Pesan Hidup",
}


# ===== File loaders ==============================================

def load_svg(svg_basename: str, color: str = "Hitam") -> str:
    """Read an SVG file inline. svg_basename is the value from
    shio_compat.SHIO_INFO[branch]["svg"] (e.g. 'Harimau' for 寅)."""
    path = SVG_DIR / f"{svg_basename}-{color}.svg"
    if not path.exists():
        return f"<!-- missing SVG: {path.name} -->"
    txt = path.read_text(encoding="utf-8")
    # strip xml prolog so we can inline directly
    if txt.startswith("<?xml"):
        txt = txt.split("?>", 1)[1].lstrip()
    # Inject only a class on root <svg> — let CSS in style.css control sizing
    # per context. (Shio files have only viewBox; sizing is applied via .shio-svg.)
    txt = txt.replace(
        "<svg ",
        '<svg class="shio-svg" preserveAspectRatio="xMidYMid meet" ',
        1,
    )
    return txt


def load_css() -> str:
    return (TEMPLATE_DIR / "style.css").read_text(encoding="utf-8")


def load_partial(name: str) -> str:
    p = TEMPLATE_DIR / "partials" / f"{name}.html"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def load_tafsir(name: str) -> str:
    """Optional fallback narrative when photo transcript missing."""
    p = TEMPLATE_DIR / "tafsir" / f"{name}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ===== SVG chart generators ======================================

def wu_xing_radar(counts: dict, size: int = 220) -> str:
    """Pentagon radar: 木 火 土 金 水 clockwise from top."""
    elements = [("木", "Kayu"), ("火", "Api"), ("土", "Tanah"),
                ("金", "Logam"), ("水", "Air")]
    cx = cy = size / 2
    radius = size * 0.35
    max_v = max(counts.values()) or 1.0

    grid_layers = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = []
        for i, (ch, _) in enumerate(elements):
            ang = -math.pi / 2 + i * 2 * math.pi / 5
            x = cx + radius * frac * math.cos(ang)
            y = cy + radius * frac * math.sin(ang)
            pts.append(f"{x:.1f},{y:.1f}")
        grid_layers.append(
            f'<polygon points="{" ".join(pts)}" fill="none" '
            f'stroke="#c9a04c" stroke-width="{0.4 if frac < 1 else 0.9}" '
            f'opacity="{0.5 if frac < 1 else 1}"/>'
        )

    spokes = []
    labels = []
    data_pts = []
    for i, (ch, name) in enumerate(elements):
        ang = -math.pi / 2 + i * 2 * math.pi / 5
        ex = cx + radius * math.cos(ang)
        ey = cy + radius * math.sin(ang)
        spokes.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="#e8c87a" stroke-width="0.4"/>'
        )
        # data
        v = counts[ch] / max_v
        dx = cx + radius * v * math.cos(ang)
        dy = cy + radius * v * math.sin(ang)
        data_pts.append(f"{dx:.1f},{dy:.1f}")
        # label
        lx = cx + (radius + 14) * math.cos(ang)
        ly = cy + (radius + 14) * math.sin(ang)
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="Noto Serif TC" '
            f'font-size="11" fill="#7a0d0d" font-weight="700">{ch}</text>'
            f'<text x="{lx:.1f}" y="{ly + 11:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="Noto Serif" '
            f'font-size="8" fill="#5c4a36">{name} {counts[ch]:.1f}</text>'
        )

    polygon = (
        f'<polygon points="{" ".join(data_pts)}" '
        f'fill="rgba(185,28,28,0.25)" stroke="#b91c1c" stroke-width="1.5"/>'
    )

    return (
        f'<svg viewBox="0 0 {size} {size}" preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;max-width:120mm;height:auto;display:block;margin:0 auto;">'
        + "".join(grid_layers) + "".join(spokes) + polygon + "".join(labels)
        + '</svg>'
    )


def compat_wheel(self_branch: str, size: int = 240) -> str:
    """Circular wheel of 12 shio centered around self_branch."""
    branches = ["子", "丑", "寅", "卯", "辰", "巳",
                "午", "未", "申", "酉", "戌", "亥"]
    cx = cy = size / 2
    r_outer = size * 0.42
    r_inner = size * 0.20

    # Two rings: outer ring with 12 shio segments, inner circle with self
    segs = []
    for i, b in enumerate(branches):
        rel = shio_compat.relation(self_branch, b)
        ang_start = -math.pi / 2 + (i - 0.5) * (math.pi / 6)
        ang_end = ang_start + math.pi / 6
        ang_mid = (ang_start + ang_end) / 2
        # color per tier
        fill = {
            "self": "#7a0d0d",
            "very_good": "#b91c1c",
            "good": "#c9a04c",
            "neutral": "#ede0bf",
            "warning": "#a16207",
            "avoid": "#3a1010",
        }[rel["tier"]]
        text_color = "#f7f0e0" if rel["tier"] in ("self", "very_good", "avoid") else "#2a1a0a"
        # arc path
        x1 = cx + r_outer * math.cos(ang_start)
        y1 = cy + r_outer * math.sin(ang_start)
        x2 = cx + r_outer * math.cos(ang_end)
        y2 = cy + r_outer * math.sin(ang_end)
        x3 = cx + r_inner * math.cos(ang_end)
        y3 = cy + r_inner * math.sin(ang_end)
        x4 = cx + r_inner * math.cos(ang_start)
        y4 = cy + r_inner * math.sin(ang_start)
        d = (f"M {x1:.1f} {y1:.1f} A {r_outer} {r_outer} 0 0 1 {x2:.1f} {y2:.1f} "
             f"L {x3:.1f} {y3:.1f} A {r_inner} {r_inner} 0 0 0 {x4:.1f} {y4:.1f} Z")
        segs.append(
            f'<path d="{d}" fill="{fill}" stroke="#f7f0e0" stroke-width="1"/>'
        )
        # branch label
        r_lbl = (r_outer + r_inner) / 2
        lx = cx + r_lbl * math.cos(ang_mid)
        ly = cy + r_lbl * math.sin(ang_mid)
        segs.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="Ma Shan Zheng" '
            f'font-size="14" fill="{text_color}">{b}</text>'
        )
        # outer relation label
        r_out_lbl = r_outer + 10
        ox = cx + r_out_lbl * math.cos(ang_mid)
        oy = cy + r_out_lbl * math.sin(ang_mid)
        if b != self_branch:
            segs.append(
                f'<text x="{ox:.1f}" y="{oy:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="Noto Serif TC" '
                f'font-size="8" fill="#5c4a36">{rel["label_cn"]}</text>'
            )

    # Center self circle
    info = shio_compat.SHIO_INFO[self_branch]
    center = (
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner - 1}" fill="#f7f0e0" '
        f'stroke="#b91c1c" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="Ma Shan Zheng" '
        f'font-size="20" fill="#b91c1c">{self_branch}</text>'
        f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="Noto Serif" '
        f'font-size="8" fill="#5c4a36">{info["id"]}</text>'
    )

    return (
        f'<svg viewBox="0 0 {size} {size}" preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;max-width:130mm;height:auto;display:block;margin:0 auto;">'
        + "".join(segs) + center + '</svg>'
    )


def dayun_bar_chart(da_yun: list, size_w: int = 320, size_h: int = 110,
                    current_age: int | None = None) -> str:
    """Horizontal bar timeline of 大運 cycles, color by element."""
    n = len(da_yun)
    pad_l, pad_r, pad_t, pad_b = 8, 8, 24, 28
    seg_w = (size_w - pad_l - pad_r) / n
    color = {
        "金": "#94a3b8", "木": "#16a34a", "水": "#0284c7",
        "火": "#dc2626", "土": "#a16207",
    }
    parts = [
        f'<rect x="{pad_l}" y="{pad_t}" '
        f'width="{size_w - pad_l - pad_r}" height="{size_h - pad_t - pad_b}" '
        f'fill="rgba(201,160,76,0.06)" stroke="#e8c87a" stroke-width="0.5"/>'
    ]
    for i, c in enumerate(da_yun):
        x = pad_l + i * seg_w
        col = color.get(c["element"], "#5c4a36")
        is_now = (current_age is not None
                  and c["age_start"] <= current_age <= c["age_end"])
        parts.append(
            f'<rect x="{x:.1f}" y="{pad_t}" width="{seg_w - 1:.1f}" '
            f'height="{size_h - pad_t - pad_b}" fill="{col}" '
            f'opacity="{0.95 if is_now else 0.55}"/>'
        )
        if is_now:
            parts.append(
                f'<rect x="{x:.1f}" y="{pad_t}" width="{seg_w - 1:.1f}" '
                f'height="{size_h - pad_t - pad_b}" fill="none" '
                f'stroke="#7a0d0d" stroke-width="1.5"/>'
            )
        # gz label inside
        parts.append(
            f'<text x="{x + seg_w/2:.1f}" y="{(pad_t + size_h - pad_b)/2 + pad_t/2:.1f}" '
            f'text-anchor="middle" font-family="Ma Shan Zheng" font-size="11" '
            f'fill="#f7f0e0">{c["gz"]}</text>'
        )
        # age below
        parts.append(
            f'<text x="{x + seg_w/2:.1f}" y="{size_h - pad_b + 10:.1f}" '
            f'text-anchor="middle" font-family="Noto Serif" font-size="7" '
            f'fill="#5c4a36">{c["age_start"]}-{c["age_end"]}</text>'
        )
        # shi shen above
        parts.append(
            f'<text x="{x + seg_w/2:.1f}" y="{pad_t - 4:.1f}" '
            f'text-anchor="middle" font-family="Noto Serif TC" font-size="7.5" '
            f'fill="#7a0d0d">{c["shi_shen"]}</text>'
        )
    return (
        f'<svg viewBox="0 0 {size_w} {size_h}" preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;max-width:160mm;height:auto;display:block;margin:0 auto;">'
        + "".join(parts) + '</svg>'
    )


# ===== HTML helpers ==============================================

def _e(s: str) -> str:
    """Escape string for HTML, allowing already-html None."""
    return escape(s) if s else ""


def _wuxing_bars_html(counts: dict) -> str:
    rows = []
    max_v = max(counts.values()) or 1.0
    for ch, (id_name, cls) in ELEMENT_LABEL.items():
        v = counts[ch]
        pct = v / max_v * 100
        rows.append(f'''
        <div class="bar-row">
          <div class="bar-label"><span class="ch">{ch}</span>
            <span>{id_name}<br><small>{v:.1f}</small></span>
          </div>
          <div class="bar-track">
            <div class="bar-fill {cls}" style="width:{pct:.1f}%;">{v:.1f}</div>
          </div>
          <div class="bar-tag"></div>
        </div>''')
    return "".join(rows)


def _pillar_chart_html(pilar: dict, day_master: dict) -> str:
    cells = []
    labels = [("year", "年柱 · Pilar Tahun"),
              ("month", "月柱 · Pilar Bulan"),
              ("day", "日柱 · Pilar Hari (Diri)"),
              ("hour", "時柱 · Pilar Jam")]
    for key, label in labels:
        p = pilar[key]
        is_dm = (key == "day")
        stem_el = bazi_calc.STEM_ELEMENT[p["stem"]]
        branch_el = bazi_calc.BRANCH_ELEMENT[p["branch"]]
        shio_id = bazi_calc.SHIO_ID[p["branch"]]
        cls = "pillar-cell dm" if is_dm else "pillar-cell"
        badge = '<div class="dm-badge">日主 Day Master</div>' if is_dm else ""
        cells.append(f'''
        <div class="{cls}">
          <div class="pillar-label">{label}</div>
          <div class="pillar-stem">{p["stem"]}</div>
          <div class="pillar-branch">{p["branch"]}</div>
          <div class="pillar-element">{stem_el[0]} {stem_el[1]} · {branch_el}<br>{shio_id}</div>
          {badge}
        </div>''')
    return f'<div class="pillar-grid">{"".join(cells)}</div>'


def _transcript_block(category: str, transcripts: dict) -> str:
    """Render bilingual transcript card if transcript present, else fallback."""
    t = transcripts.get(category, {})
    hanzi = t.get("hanzi", "").strip()
    indo = t.get("indonesia", "").strip()
    label_id = CATEGORY_ID.get(category, category)

    if not hanzi and not indo:
        return (f'<div class="card">'
                f'<div class="card-title">{category} · {label_id}</div>'
                f'<p><em>Foto kategori ini tidak tersedia di folder. '
                f'Bagian ini di-skip secara sengaja.</em></p></div>')

    parts = []
    if hanzi:
        parts.append(
            f'<div class="transcript">'
            f'<span class="lbl">Transkrip Asli ({category})</span>'
            f'<div class="cn">{escape(hanzi)}</div></div>'
        )
    if indo:
        parts.append(
            f'<div class="card emas"><div class="card-title">Terjemahan Indonesia</div>'
            f'<p>{escape(indo).replace(chr(10), "<br>")}</p></div>'
        )
    tafsir = t.get("tafsir") or []
    if isinstance(tafsir, str):
        # accept string with newline-separated bullets
        tafsir = [b.strip(" -•·\t") for b in tafsir.splitlines() if b.strip()]
    if tafsir:
        bullets = "".join(
            f'<li>{escape(str(b))}</li>' for b in tafsir
        )
        parts.append(
            f'<div class="card merah">'
            f'<div class="card-title">Tafsir &amp; Saran Praktis</div>'
            f'<ul style="margin:0 0 0 5mm;font-size:9.5pt;line-height:1.55;">'
            f'{bullets}</ul></div>'
        )
    return "".join(parts)


# ===== Page builders =============================================

def page_cover(subject: dict, shio_info: dict) -> str:
    svg = load_svg(shio_info["svg"], "Merah")
    # Format birth date
    birth = subject.get("birth_solar", "")
    name = _e(subject.get("name", "—"))
    return f'''
<section class="page cover">
  <div class="shio-wrap">{svg}</div>
  <div class="title-cn">命理分析</div>
  <div class="subtitle">RAMALAN NASIB &middot; LAPORAN LENGKAP</div>
  <div class="name">{name}</div>
  <div class="meta">{_e(birth)}<br>屬 {shio_info["id"]} · {subject.get("shio_branch","")}</div>
  <div class="seal">命</div>
</section>'''


def page_toc() -> str:
    items = [
        ("01", "Pengantar & Disclaimer Etika", ""),
        ("02", "Profil Subjek & Chart 4 Pilar", ""),
        ("", "BAGIAN I — 八字四柱 BAZI", "section"),
        ("03", "Day Master & Wu Xing Balance", ""),
        ("04", "性情 Kepribadian", ""),
        ("05", "全局總論 Ringkasan Menyeluruh", ""),
        ("06", "神煞 Bintang Nasib", ""),
        ("07", "財富 Kekayaan", ""),
        ("08", "婚配 Kompatibilitas Pernikahan", ""),
        ("09", "事業 Karir & Profesi", ""),
        ("10", "陽宅 Feng Shui Hunian", ""),
        ("11", "大運 Timeline Hidup", ""),
        ("", "BAGIAN II — 紫微斗數 ZI WEI", "section"),
        ("12", "12 Palace Overview", ""),
        ("13", "命宮 · 兄弟 · 夫妻 · 子女", ""),
        ("14", "財帛 · 疾厄 · 遷移 · 僕役", ""),
        ("15", "官祿 · 田宅 · 福德 · 父母", ""),
        ("", "BAGIAN III — PENUTUP", "section"),
        ("16", "Sintesis & Saran Action", ""),
        ("17", "Glossary Istilah Tionghoa", ""),
        ("18", "Disclaimer & Catatan Etika", ""),
    ]
    rows = []
    for num, label, kind in items:
        if kind == "section":
            rows.append(f'<tr><td colspan="2" style="background:rgba(185,28,28,0.08);'
                        f'color:var(--merah-deep);font-weight:700;'
                        f'font-family:\'Noto Serif TC\',serif;text-align:center;'
                        f'letter-spacing:3px;padding:3mm;">{label}</td></tr>')
        else:
            rows.append(f'<tr><td style="width:18mm;text-align:center;'
                        f'font-family:\'Cormorant Garamond\',serif;color:var(--emas-rich);'
                        f'font-weight:600;">{num}</td><td>{label}</td></tr>')
    return f'''
<section class="page">
  <h2 style="text-align:center;">Daftar Isi · 目錄</h2>
  <div class="divider">❖ ❖ ❖</div>
  <table style="margin-top:6mm;">
    {"".join(rows)}
  </table>
  <div class="page-num">II</div>
</section>'''


def page_intro() -> str:
    return f'''
<section class="page">
  <h2>Pengantar</h2>
  <div class="divider">❖ ❖ ❖</div>
  <p>Laporan ini adalah konversi setia dari output software ramalan Taiwan
  <span class="cn">星僑五術 — 四柱論命附加紫微斗數 V2.6</span>
  ke dalam Bahasa Indonesia, dengan ditambah visualisasi yang dihasilkan
  dari perhitungan deterministik (BaZi calculator + tabel kompatibilitas shio).</p>

  <p>Sistem yang digunakan menggabungkan tiga ranah klasik:</p>
  <div class="info-grid">
    <div class="info-card">
      <div class="info-card-title">八字四柱 — BaZi</div>
      <p>Empat Pilar (Tahun, Bulan, Hari, Jam) sebagai cetakan watak dan trend
      hidup. Day Master adalah inti diri Anda.</p>
    </div>
    <div class="info-card">
      <div class="info-card-title">紫微斗數 — Zi Wei</div>
      <p>Astrologi 12 Palace dengan 14 bintang utama yang memetakan area
      kehidupan: keluarga, karir, rezeki, kesehatan, dll.</p>
    </div>
    <div class="info-card">
      <div class="info-card-title">陽宅 — Yang Zhai</div>
      <p>Feng shui hunian berbasis BaZi pribadi: arah hadap, tata ruang,
      titik beruntung untuk pintu, ranjang, dan altar.</p>
    </div>
    <div class="info-card">
      <div class="info-card-title">⚖ Etika</div>
      <p>Laporan ini bersifat <em>referensi tradisi</em>. Tidak menggantikan
      keputusan medis, hukum, atau finansial profesional. Tidak ada prediksi
      kematian. Bahasa diorientasikan ke pemberdayaan.</p>
    </div>
  </div>
  <blockquote>
    Ramalan Tionghoa membaca <em>kecenderungan</em> dan <em>trend</em>, bukan
    nasib mati. Kemampuan untuk memilih dan bertindak tetap ada di tangan Anda.
  </blockquote>
  <div class="page-num">III</div>
</section>'''


def page_profile(subject: dict, chart: dict, shio_info: dict) -> str:
    svg = load_svg(shio_info["svg"], "Merah")
    dm = chart["day_master"]
    fmt = chart["format"]
    fav = " · ".join(f'{x} {ELEMENT_LABEL[x][0]}' for x in chart["favorable"])
    unfav = " · ".join(f'{x} {ELEMENT_LABEL[x][0]}' for x in chart["unfavorable"])

    return f'''
<section class="page">
  <h2>Profil Subjek</h2>
  <div class="divider">❖ ❖ ❖</div>
  <div style="display:grid;grid-template-columns:55mm 1fr;gap:6mm;align-items:center;margin-top:4mm;">
    <div style="text-align:center;">
      <div class="shio-portrait">{svg}</div>
      <div style="margin-top:2mm;font-family:'Ma Shan Zheng',cursive;
                  color:var(--merah-imperial);font-size:22pt;">屬{shio_info["id"]}</div>
    </div>
    <div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:24pt;
                  color:var(--ink-black);font-weight:700;letter-spacing:2px;">
        {_e(subject.get("name", "—"))}
      </div>
      <p style="font-size:10pt;color:var(--ink-soft);margin-top:1mm;">
        {_e(subject.get("birth_solar", ""))}
        {("· " + _e(subject.get("birth_lunar", ""))) if subject.get("birth_lunar") else ""}<br>
        Gender: <strong>{"Laki-laki (男)" if subject.get("gender") == "M" else "Perempuan (女)"}</strong>
      </p>
      <div class="card merah" style="margin-top:3mm;">
        <div class="card-title">Day Master · 日主</div>
        <p style="font-size:13pt;font-family:'Noto Serif TC',serif;color:var(--merah-deep);">
          {dm["stem"]}{dm["element"]} — <strong>{dm["element_id"]} {dm["yin_yang"]}</strong>
        </p>
        <p style="font-size:9pt;color:var(--ink-soft);">
          Format (格局): <strong>{fmt["name_cn"]}</strong> ({fmt["name_pinyin"]})
        </p>
      </div>
    </div>
  </div>

  <h3 style="margin-top:6mm;">Empat Pilar (四柱)</h3>
  {_pillar_chart_html(chart["pilar"], dm)}

  <div class="info-grid" style="margin-top:5mm;">
    <div class="info-card" style="border-color:#16a34a;">
      <div class="info-card-title" style="color:#16a34a;">✓ 喜用神 — Elemen Beruntung</div>
      <p>{fav}</p>
    </div>
    <div class="info-card" style="border-color:#a16207;">
      <div class="info-card-title" style="color:#a16207;">⚠ 忌神 — Elemen Hindari</div>
      <p>{unfav}</p>
    </div>
  </div>
  <div class="page-num">IV</div>
</section>'''


def page_section_opener(roman: str, hanzi: str, label_id: str, desc: str) -> str:
    return f'''
<section class="page section-opener">
  <div class="roman">{roman}</div>
  <div class="title-cn">{hanzi}</div>
  <div class="label-id">{label_id}</div>
  <p class="desc">{desc}</p>
</section>'''


def page_day_master_wuxing(chart: dict, page_num: str) -> str:
    radar = wu_xing_radar(chart["wu_xing"])
    bars = _wuxing_bars_html(chart["wu_xing"])
    dm = chart["day_master"]
    return f'''
<section class="page">
  <h2>Day Master & Wu Xing Balance</h2>
  <div class="divider">❖ ❖ ❖</div>
  <div class="card merah">
    <div class="card-title">Inti Diri Anda</div>
    <p>Day Master Anda adalah <strong class="cn">{dm["stem"]}{dm["element"]}</strong>
    ({dm["element_id"]} {dm["yin_yang"]}). Inilah cetakan watak inti Anda — bagaimana
    Anda memandang dunia dan apa yang membuat Anda merasa hidup.</p>
  </div>

  <h3>Distribusi 5 Elemen di Bagan</h3>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:4mm;align-items:center;">
    <div>{radar}</div>
    <div>{bars}</div>
  </div>

  <div class="card emas">
    <div class="card-title">Bacaan Praktis</div>
    <p>Elemen yang <em>kurang</em> bisa Anda perkuat lewat warna, arah, profesi, dan
    relasi. Elemen yang <em>berlebih</em> perlu disalurkan agar tidak macet.</p>
  </div>
  <div class="page-num">{page_num}</div>
</section>'''


def page_dayun_timeline(chart: dict, page_num: str,
                        current_age: int | None = None) -> str:
    bar = dayun_bar_chart(chart["da_yun"], current_age=current_age)
    rows = []
    for c in chart["da_yun"]:
        is_now = (current_age is not None
                  and c["age_start"] <= current_age <= c["age_end"])
        cls = "card merah" if is_now else "card"
        rows.append(f'''
        <div class="{cls}" style="padding:2mm 3mm;">
          <strong class="cn">{c["gz"]}</strong>
          <span style="font-size:9pt;color:var(--ink-soft);">
            ({c["age_start"]}–{c["age_end"]} thn) — 十神: {c["shi_shen"]} —
            Elemen: {ELEMENT_LABEL[c["element"]][0]}
          </span>
        </div>''')
    return f'''
<section class="page">
  <h2>大運 — Timeline Hidup 10-Tahunan</h2>
  <div class="divider">❖ ❖ ❖</div>
  <p>Setiap fase 10 tahun membawa kombinasi 干支 (stem-branch) dan 十神 (Ten Gods)
  yang berbeda. Fase saat ini ditandai dengan border merah tebal.</p>
  {bar}
  <h3 style="margin-top:5mm;">Detail Setiap Fase</h3>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:2mm;">
    {"".join(rows)}
  </div>
  <div class="page-num">{page_num}</div>
</section>'''


def page_category_text(category: str, transcripts: dict, page_num: str) -> str:
    label_id = CATEGORY_ID.get(category, category)
    block = _transcript_block(category, transcripts)
    return f'''
<section class="page">
  <h2>{category} — {label_id}</h2>
  <div class="divider">❖ ❖ ❖</div>
  {block}
  <div class="page-num">{page_num}</div>
</section>'''


def page_marriage(chart: dict, transcripts: dict, page_num: str) -> str:
    self_branch = chart["subject"]["shio_branch"]
    wheel = compat_wheel(self_branch)
    compat = shio_compat.full_compatibility(self_branch)

    # Build 3 cells of compatible shio (very_good first, then good)
    very_good = compat["grouped"]["very_good"]
    good = compat["grouped"]["good"]
    avoid = compat["grouped"]["avoid"]

    def _shio_grid(items: list, color: str) -> str:
        if not items:
            return '<p style="font-size:9pt;color:var(--ink-soft);font-style:italic;">— tidak ada —</p>'
        cells = []
        for it in items:
            svg = load_svg(it["svg"], color)
            cells.append(f'''
            <div class="compat-cell {"lucky" if color == "Merah" else "warning"}"
                 style="width:30mm;flex:0 0 auto;">
              {svg}
              <div class="ch">{it["branch"]}</div>
              <div class="label">{it["id"]}</div>
              <div class="relation" style="font-size:6.5pt;">{it["label_cn"]} {it["label_id"]}</div>
            </div>''')
        return ('<div style="display:flex;flex-wrap:wrap;gap:2mm;'
                'justify-content:center;margin:1.5mm 0;">'
                + "".join(cells) + '</div>')

    block = _transcript_block("婚配", transcripts)

    return f'''
<section class="page">
  <h2>婚配 — Kompatibilitas Pernikahan</h2>
  <div class="divider">❖ ❖ ❖</div>
  <div style="width:100%;max-width:90mm;margin:0 auto;">{wheel}</div>

  <h3 style="margin-top:3mm;">三合 Trinitas Harmoni — Sangat Cocok</h3>
  {_shio_grid(very_good, "Merah")}

  <h3>六合 Pasangan Harmonis — Cocok</h3>
  {_shio_grid(good, "Merah")}

  <h3>Hindari (沖 / 害 / 刑)</h3>
  {_shio_grid(avoid, "Hitam")}

  {block}
  <div class="page-num">{page_num}</div>
</section>'''


def page_career_industries(chart: dict, transcripts: dict, page_num: str) -> str:
    """Career page with Wu Xing → industry mapping."""
    fav = chart["favorable"]
    industri = {
        "金": ["Logam, mesin, otomotif", "Keuangan, asuransi", "Hukum, militer", "IT hardware"],
        "木": ["Pendidikan, riset", "Tekstil, furniture", "Pertanian, kehutanan", "Penerbitan"],
        "水": ["Logistik, shipping", "F&B beverage", "Pariwisata, perhotelan", "Komunikasi"],
        "火": ["Energi, listrik", "Hiburan, fashion", "Pemasaran, branding", "Kuliner panas"],
        "土": ["Properti, konstruksi", "Pertambangan", "Konsultasi, manajemen", "Layanan publik"],
    }
    cards = []
    for el in chart["wu_xing"]:
        is_fav = el in fav
        cards.append(f'''
        <div class="info-card" style="{"border-color:var(--merah-imperial);" if is_fav else ""}">
          <div class="info-card-title">{el} {ELEMENT_LABEL[el][0]}{" ★" if is_fav else ""}</div>
          <ul style="font-size:9pt;">{"".join(f"<li>{x}</li>" for x in industri[el])}</ul>
        </div>''')

    block = _transcript_block("事業", transcripts)
    return f'''
<section class="page">
  <h2>事業 — Karir & Profesi</h2>
  <div class="divider">❖ ❖ ❖</div>
  {block}
  <h3>Industri per Elemen (★ = sesuai 喜用神 Anda)</h3>
  <div class="info-grid info-grid-3" style="grid-template-columns:repeat(3,1fr);">
    {"".join(cards)}
  </div>
  <div class="page-num">{page_num}</div>
</section>'''


def page_ziwei_overview(transcripts: dict, page_num: str,
                        ziwei_meta: dict | None = None) -> str:
    """List all 12 palaces with snippet from transcripts.
    Optionally show Zi Wei meta info (Life Lord, Body Lord, etc.)."""
    palaces = list(PALACE_ID.keys())
    cells = []
    for p in palaces:
        t = transcripts.get(p, {})
        snippet = (t.get("indonesia") or t.get("hanzi") or "—")[:110]
        if t.get("indonesia") or t.get("hanzi"):
            snippet = snippet + ("…" if len(snippet) >= 110 else "")
        cells.append(f'''
        <div class="info-card">
          <div class="info-card-title">{p} · {PALACE_ID[p]}</div>
          <p style="font-size:8pt;">{escape(snippet)}</p>
        </div>''')

    meta_block = ""
    if ziwei_meta:
        meta_items = [
            ("命主", "Life Lord", ziwei_meta.get("life_lord", "—")),
            ("身主", "Body Lord", ziwei_meta.get("body_lord", "—")),
            ("命宮", "Life Palace", ziwei_meta.get("life_palace", "—")),
            ("身宮", "Body Palace", ziwei_meta.get("body_palace", "—")),
            ("五行局", "Five-Element School", ziwei_meta.get("five_element_school", "—")),
            ("子年斗君", "Time Lord", ziwei_meta.get("time_lord", "—")),
        ]
        cells_meta = "".join(
            f'<div class="info-card" style="text-align:center;">'
            f'<div class="info-card-title">{ch}<br><small style="font-weight:400;color:var(--ink-soft);">{en}</small></div>'
            f'<p style="font-size:14pt;font-family:\'Ma Shan Zheng\',cursive;color:var(--merah-deep);">{val}</p>'
            f'</div>'
            for ch, en, val in meta_items
        )
        meta_block = f'''
  <h3 style="margin-top:1mm;">Konfigurasi Bagan</h3>
  <div class="info-grid info-grid-3" style="grid-template-columns:repeat(3,1fr);gap:2mm;">
    {cells_meta}
  </div>'''

    return f'''
<section class="page">
  <h2>紫微斗數 — 12 Palace</h2>
  <div class="divider">❖ ❖ ❖</div>
  <p>Zi Wei membagi hidup ke dalam 12 area (palace). Tiap palace dihuni
  bintang-bintang yang menentukan watak area tersebut.</p>
  {meta_block}
  <h3 style="margin-top:3mm;">Ringkasan 12 Palace</h3>
  <div class="info-grid info-grid-3" style="grid-template-columns:repeat(3,1fr);gap:2mm;">
    {"".join(cells)}
  </div>
  <div class="page-num">{page_num}</div>
</section>'''


def page_ziwei_group(group: list, transcripts: dict, page_num: str) -> str:
    blocks = []
    for p in group:
        block = _transcript_block(p, transcripts)
        blocks.append(f'<h3>{p} · {PALACE_ID[p]}</h3>{block}')
    return f'''
<section class="page">
  <h2>紫微 Detail — {" · ".join(group)}</h2>
  <div class="divider">❖ ❖ ❖</div>
  {"".join(blocks)}
  <div class="page-num">{page_num}</div>
</section>'''


def page_synthesis(chart: dict, page_num: str) -> str:
    dm = chart["day_master"]
    fmt = chart["format"]
    return f'''
<section class="page">
  <h2>Sintesis & Saran Action</h2>
  <div class="divider">❖ ❖ ❖</div>
  <p>Benang merah bagan Anda:</p>
  <div class="card merah">
    <div class="card-title">Inti</div>
    <p>Day Master <span class="cn">{dm["stem"]}{dm["element"]}</span>
    ({dm["element_id"]} {dm["yin_yang"]}) — Format <strong>{fmt["name_cn"]}</strong>.
    Fokus hidup Anda berputar di sekitar tema yang dibawa oleh format ini.</p>
  </div>

  <h3>Saran Praktis</h3>
  <div class="timeline">
    <div class="timeline-item"><strong>Bulanan</strong>
      <p>Cek elemen 喜用神 Anda — tambah aktivitas, warna, atau lingkungan
      yang menguatkan elemen tersebut.</p></div>
    <div class="timeline-item"><strong>Tahunan</strong>
      <p>Lihat di fase 大運 mana Anda berada (lihat halaman timeline).
      Sesuaikan keputusan besar dengan tema fase tersebut.</p></div>
    <div class="timeline-item"><strong>Pernikahan & Kerjasama</strong>
      <p>Perhatikan tabel 三合/六合 sebagai panduan partner ideal,
      bukan aturan kaku. Karakter pribadi tetap nomor satu.</p></div>
    <div class="timeline-item"><strong>Karir</strong>
      <p>Pilih industri yang elemennya cocok dengan 喜用神 (★) untuk
      flow yang lebih lancar.</p></div>
  </div>
  <div class="page-num">{page_num}</div>
</section>'''


def page_glossary(page_num: str) -> str:
    items = [
        ("八字", "Bā Zì", "Empat Pilar berdasarkan tahun, bulan, hari, jam lahir"),
        ("日主", "Rì Zhǔ", "Day Master — stem hari lahir, inti diri"),
        ("天干", "Tiān Gān", "10 Heavenly Stems"),
        ("地支", "Dì Zhī", "12 Earthly Branches"),
        ("十神", "Shí Shén", "Ten Gods — relasi 10 stem dengan day master"),
        ("五行", "Wǔ Xíng", "5 Elemen: 金木水火土"),
        ("喜用神", "Xǐ Yòng Shén", "Elemen beruntung yang mendukung diri"),
        ("忌神", "Jì Shén", "Elemen yang perlu dihindari"),
        ("大運", "Dà Yùn", "Major cycles 10-tahunan"),
        ("流年", "Liú Nián", "Annual luck flow"),
        ("格局", "Gé Jú", "Format bagan / pola dasar"),
        ("紫微斗數", "Zǐ Wēi Dòu Shù", "Astrologi bintang ungu"),
        ("命宮", "Mìng Gōng", "Palace Diri / Hidup"),
        ("三合", "Sān Hé", "Trinitas Harmoni shio"),
        ("六合", "Liù Hé", "Pasangan Harmonis"),
        ("六沖", "Liù Chōng", "Konflik langsung"),
        ("六害", "Liù Hài", "Saling melukai"),
        ("陽宅", "Yáng Zhái", "Feng shui rumah hunian"),
    ]
    rows = "".join(
        f'<tr><td class="cn" style="width:25mm;text-align:center;">{ch}</td>'
        f'<td style="width:30mm;font-style:italic;color:var(--ink-soft);">{py}</td>'
        f'<td>{desc}</td></tr>' for ch, py, desc in items
    )
    return f'''
<section class="page">
  <h2>Glossary Istilah Tionghoa</h2>
  <div class="divider">❖ ❖ ❖</div>
  <table>{rows}</table>
  <div class="page-num">{page_num}</div>
</section>'''


def page_disclaimer(page_num: str) -> str:
    return f'''
<section class="page">
  <h2>Disclaimer & Etika</h2>
  <div class="divider">❖ ❖ ❖</div>
  <blockquote>
    Laporan ini adalah <strong>referensi tradisi & eksplorasi diri</strong>,
    bukan ilmu pasti. Tidak menggantikan keputusan medis, hukum, atau
    finansial profesional.
  </blockquote>
  <h3>Apa yang dilakukan laporan ini</h3>
  <ul>
    <li>Mengkonversi hasil software 星僑 V2.6 ke Bahasa Indonesia secara setia.</li>
    <li>Menambah visualisasi yang dihitung deterministik dari data lahir.</li>
    <li>Memberikan glossary dan struktur baca yang mudah.</li>
  </ul>
  <h3>Apa yang TIDAK dilakukan</h3>
  <ul>
    <li>Tidak memberi prediksi kematian, dalam bentuk apapun.</li>
    <li>Tidak menjamin akurasi terjemahan untuk istilah klasik —
        glossary diberikan sebagai pegangan.</li>
    <li>Tidak menambah ramalan baru yang tidak ada di foto sumber.</li>
  </ul>
  <p style="margin-top:5mm;font-size:9pt;color:var(--ink-soft);text-align:center;">
    Generated {datetime.now().strftime("%Y-%m-%d")} · xingqiao-fortune-id v1.0
  </p>
  <div class="page-num">{page_num}</div>
</section>'''


# ===== Main entry ================================================

def render_html(data: dict) -> str:
    """Build full self-contained HTML.

    data structure:
    {
      "subject": {
        "name": "Leana",
        "gender": "F",
        "birth_solar": "1985-08-15 14:30",
        "birth_lunar": "...",   # optional
      },
      "chart": <output of bazi_calc.full_chart>,
      "transcripts": {
        "性情": {"hanzi": "...", "indonesia": "..."},
        "全局總論": {...},
        # any of: 性情 全局總論 神煞 財富 婚配 事業 陽宅
        # plus 12 palace names: 命宮 兄弟 夫妻 子女 財帛 疾厄 遷移 僕役 官祿 田宅 福德 父母
      },
      "current_age": 62  # optional, untuk highlight da_yun aktif
    }
    """
    chart = data["chart"]
    subject = {**data["subject"], **chart["subject"]}
    transcripts = data.get("transcripts", {})
    current_age = data.get("current_age")
    ziwei_meta = data.get("ziwei_meta")
    shio_info = shio_compat.SHIO_INFO[chart["subject"]["shio_branch"]]

    bazi_pages = [
        page_section_opener(
            "BAGIAN I", "八字四柱",
            "BaZi · Empat Pilar Nasib",
            "Bacaan dari empat pilar lahir. Day Master sebagai inti, "
            "didukung 5 elemen dan 10 dewa, untuk membaca watak dan trend hidup."
        ),
        page_day_master_wuxing(chart, "1"),
    ]
    n = 2
    if "古書云" in transcripts:
        bazi_pages.append(page_category_text("古書云", transcripts, str(n))); n += 1
    for cat in ("性情", "全局總論", "神煞", "財富"):
        bazi_pages.append(page_category_text(cat, transcripts, str(n))); n += 1
    bazi_pages.append(page_marriage(chart, transcripts, str(n))); n += 1
    bazi_pages.append(page_career_industries(chart, transcripts, str(n))); n += 1
    bazi_pages.append(page_category_text("陽宅", transcripts, str(n))); n += 1
    bazi_pages.append(page_dayun_timeline(chart, str(n), current_age))

    pages = [
        page_cover(subject, shio_info),
        page_toc(),
        page_intro(),
        page_profile(subject, chart, shio_info),
        *bazi_pages,

        page_section_opener(
            "BAGIAN II", "紫微斗數",
            "Zi Wei Dou Shu · 12 Palace",
            "Astrologi bintang ungu yang membagi hidup ke dalam dua belas area: "
            "diri, keluarga, rezeki, kesehatan, dan seterusnya."
        ),
        page_ziwei_overview(transcripts, "1", ziwei_meta),
        page_ziwei_group(["命宮", "兄弟", "夫妻", "子女"], transcripts, "2"),
        page_ziwei_group(["財帛", "疾厄", "遷移", "僕役"], transcripts, "3"),
        page_ziwei_group(["官祿", "田宅", "福德", "父母"], transcripts, "4"),

        page_section_opener(
            "BAGIAN III", "綜合 · 結語",
            "Sintesis & Penutup",
            "Benang merah, saran praktis, glossary, dan catatan etika."
        ),
        page_synthesis(chart, "1"),
        page_glossary("2"),
        page_disclaimer("3"),
    ]

    css = load_css()
    name = _e(subject.get("name", "Subjek"))
    return f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Ramalan {name} — 命理分析</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&family=Noto+Serif:ital,wght@0,400;0,700;1,400&family=Ma+Shan+Zheng&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{"".join(pages)}
</body>
</html>'''


def render_to_file(data: dict, output_html: str | Path) -> Path:
    out = Path(output_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(data), encoding="utf-8")
    return out


# ===== CLI for testing ===========================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Render HTML laporan ramalan dari JSON input.")
    parser.add_argument("input_json", nargs="?",
                        help="Path ke JSON input (lihat docstring render_html). "
                             "Default: cache/_test_henry.json (data test).")
    parser.add_argument("-o", "--output",
                        default=str(ROOT / "cache" / "report.html"),
                        help="Output HTML path.")
    args = parser.parse_args()

    if args.input_json:
        data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        # accept either {chart: {...}} wrapper or raw chart
        if "chart" not in data:
            data = {
                "subject": {"name": "Test", **data["subject"]},
                "chart": data,
                "transcripts": {},
            }
    else:
        # Demo: load Henry chart from cache, no transcripts
        chart = json.loads((ROOT / "cache" / "_test_henry.json").read_text(encoding="utf-8"))
        data = {
            "subject": {
                "name": "Henry (Demo)",
                "gender": chart["subject"]["gender"],
                "birth_solar": chart["subject"]["birth_solar"],
            },
            "chart": chart,
            "transcripts": {},
            "current_age": datetime.now().year - 1962,
        }

    out = render_to_file(data, args.output)
    print(f"OK -> {out}")
    print(f"   {out.stat().st_size // 1024} KB")
