"""BaZi PDF Generator (sandbox_v46) — JSON-driven, ZERO FABRICATION.

Usage:
    python bazi_pdf.py <input.json> [output.pdf]

Aturan:
- Setiap teks di PDF harus bisa dilacak ke key JSON.
- Section hanya muncul jika datanya ada di JSON.
- Validasi 7 field kritis sebelum render. Gagal -> exit error.
- Master style FIXED (lihat PROMPT_CLAUDE_CODE_BAZI.md).
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Master style (FIXED — sama lintas klien)
# ---------------------------------------------------------------------------
MASTER_CSS = """
@page { size: A4; margin: 36px 40px; }
* { box-sizing: border-box; }
body {
  font-family: 'Georgia', 'Noto Serif', 'Times New Roman', serif;
  background: #FDFAF5;
  color: #2C2C2C;
  margin: 0;
  padding: 0;
  line-height: 1.55;
  font-size: 11pt;
}
.han { font-family: 'Noto Serif CJK SC', 'Microsoft YaHei', 'SimSun', serif; }
.page {
  padding: 36px 40px;
  page-break-after: always;
  background: #FDFAF5;
  min-height: calc(100vh - 0px);
}
.page:last-child { page-break-after: auto; }
h1 { color: #8B1A1A; font-size: 26pt; margin: 0 0 8px 0; letter-spacing: 1px; }
h2 { color: #8B1A1A; font-size: 16pt; margin: 0 0 14px 0; border-bottom: 1px solid #E8DCC8; padding-bottom: 6px; }
h3 { color: #8B1A1A; font-size: 12pt; margin: 14px 0 6px 0; }
p  { margin: 0 0 8px 0; text-align: justify; }
.cover {
  text-align: center;
  padding: 120px 40px 40px 40px;
}
.cover .accent { color: #C8A84B; letter-spacing: 4px; font-size: 11pt; text-transform: uppercase; }
.cover h1 { font-size: 34pt; margin: 18px 0 10px 0; }
.cover .meta { color: #2C2C2C; font-size: 12pt; margin-top: 30px; line-height: 2; }
.cover .meta b { color: #8B1A1A; }
.section {
  border: 1px solid #E8DCC8;
  border-radius: 4px;
  padding: 14px 18px;
  margin: 0 0 12px 0;
  background: #FFFEFB;
}
.kv { display: flex; flex-wrap: wrap; gap: 6px 28px; margin: 4px 0 10px 0; }
.kv > div { min-width: 220px; }
.kv b { color: #8B1A1A; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px 0; font-size: 10.5pt; }
th, td { border: 1px solid #E8DCC8; padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: #F4ECD8; color: #8B1A1A; font-weight: bold; }
ul { margin: 4px 0 8px 18px; padding: 0; }
li { margin-bottom: 4px; }
.pos { color: #2D6A4F; }
.muted { color: #7A6A52; font-size: 9.5pt; }
.pillar-row { display: flex; gap: 10px; margin: 8px 0; }
.pillar { flex: 1; border: 1px solid #E8DCC8; border-radius: 4px; padding: 10px; background: #FFFEFB; text-align: center; }
.pillar .label { font-size: 9pt; color: #C8A84B; letter-spacing: 2px; text-transform: uppercase; }
.pillar .ganzhi { color: #8B1A1A; font-weight: bold; font-size: 14pt; margin: 4px 0; }
.pillar .rel { font-size: 9.5pt; color: #2C2C2C; }
.footer-note { color: #7A6A52; font-size: 9pt; margin-top: 18px; font-style: italic; }
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
MISSING = object()


def safe_get(data, *keys, default=MISSING):
    cur = data
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def has(value):
    return value is not MISSING and value not in (None, "", [], {})


def esc(text):
    if text is None:
        return ""
    return html.escape(str(text))


# ---------------------------------------------------------------------------
# Validation: 7 critical fields
# ---------------------------------------------------------------------------
def validate(data):
    checks = [
        ("identitas.shio",                ("identitas", "shio")),
        ("identitas.empat_pilar.tahun",   ("identitas", "empat_pilar", "tahun")),
        ("identitas.empat_pilar.bulan",   ("identitas", "empat_pilar", "bulan")),
        ("identitas.empat_pilar.hari",    ("identitas", "empat_pilar", "hari")),
        ("identitas.empat_pilar.jam",     ("identitas", "empat_pilar", "jam")),
        ("foto_31_si_zhu_ming_pan.da_yun", ("foto_31_si_zhu_ming_pan", "da_yun")),
    ]
    cai_fu_present = has(safe_get(data, "foto_26_cai_fu")) or has(safe_get(data, "foto_18_cai_bo"))

    errors = []
    for name, path in checks:
        val = safe_get(data, *path)
        if not has(val):
            errors.append(f"  - {name}  -> tidak ada di JSON")
    if not cai_fu_present:
        errors.append("  - cai_fu / cai_bo (rezeki)  -> tidak ada di JSON")
    return errors


# ---------------------------------------------------------------------------
# Section renderers — semua mengembalikan string HTML atau "" jika data kosong
# ---------------------------------------------------------------------------
def render_cover(data):
    ident = safe_get(data, "identitas", default={}) or {}
    nama = safe_get(data, "identitas", "nama")
    if not has(nama):
        return ""
    rows = []
    if has(ident.get("jenis_kelamin")):
        rows.append(f"Jenis Kelamin: <b>{esc(ident['jenis_kelamin'])}</b>")
    if has(ident.get("tahun_masehi")):
        rows.append(f"Tahun Lahir (Masehi): <b>{esc(ident['tahun_masehi'])}</b>")
    if has(ident.get("hari")):
        rows.append(f"Hari Lahir: <b>{esc(ident['hari'])}</b>")
    kn = ident.get("kalender_nasional")
    if isinstance(kn, dict):
        parts = []
        if kn.get("tahun"): parts.append(str(kn["tahun"]))
        if kn.get("bulan") and kn.get("tanggal"):
            parts.append(f"{kn['tanggal']}/{kn['bulan']}")
        if kn.get("jam") is not None: parts.append(f"jam {kn['jam']}")
        if parts:
            rows.append(f"Kalender Nasional: <b>{esc(' · '.join(parts))}</b>")
    kl = ident.get("kalender_lunar")
    if isinstance(kl, dict):
        parts = []
        if kl.get("tahun"): parts.append(str(kl["tahun"]))
        if kl.get("bulan") and kl.get("tanggal"):
            parts.append(f"bulan {kl['bulan']}, tanggal {kl['tanggal']}")
        if kl.get("jam") is not None: parts.append(f"jam {kl['jam']}")
        if parts:
            rows.append(f"Kalender Lunar: <b>{esc(' · '.join(parts))}</b>")
    if has(ident.get("shio")):
        rows.append(f"Shio: <b>{esc(ident['shio'])}</b>")

    meta = "<br/>".join(rows) if rows else ""
    return f"""
<section class="page cover">
  <div class="accent">Laporan Astrologi BaZi</div>
  <h1>{esc(nama)}</h1>
  <div class="muted">Analisis Empat Pilar &middot; Zi Wei Dou Shu</div>
  <div class="meta">{meta}</div>
</section>
"""


def render_profil(data):
    ident = safe_get(data, "identitas", default={}) or {}
    pilar = ident.get("empat_pilar") if isinstance(ident, dict) else None
    if not isinstance(pilar, dict):
        return ""
    pilar_html = []
    for label, key in (("Tahun", "tahun"), ("Bulan", "bulan"),
                       ("Hari (Day Master)", "hari"), ("Jam", "jam")):
        v = pilar.get(key)
        if has(v):
            pilar_html.append(
                f'<div class="pillar"><div class="label">{esc(label)}</div>'
                f'<div class="ganzhi">{esc(v)}</div></div>'
            )
    pilar_block = f'<div class="pillar-row">{"".join(pilar_html)}</div>' if pilar_html else ""

    extras = []
    si = safe_get(data, "foto_31_si_zhu_ming_pan", default={}) or {}
    if has(si.get("format_istana")):
        extras.append(f"<div><b>Format Istana:</b> {esc(si['format_istana'])}</div>")
    dewa = si.get("dewa_penggunaan") if isinstance(si, dict) else None
    if isinstance(dewa, dict):
        for lbl, k in (("Yong Shen", "yong_shen"), ("Xi Shen", "xi_shen"),
                       ("Jian Shen", "jian_shen"), ("Chou Shen", "chou_shen"),
                       ("Ji Shen", "ji_shen")):
            if has(dewa.get(k)):
                extras.append(f"<div><b>{lbl}:</b> {esc(dewa[k])}</div>")
    if has(ident.get("lima_unsur")):
        extras.append(f"<div><b>Lima Unsur:</b> {esc(ident['lima_unsur'])}</div>")
    if has(si.get("hari_utama_kuat")):
        extras.append(f"<div><b>Hari Utama Kuat:</b> {esc(si['hari_utama_kuat'])}</div>")
    nk = si.get("nilai_keseimbangan") if isinstance(si, dict) else None
    if isinstance(nk, dict):
        if has(nk.get("positif")):
            extras.append(f"<div><b>Nilai Positif:</b> {esc(nk['positif'])}</div>")
        if has(nk.get("negatif")):
            extras.append(f"<div><b>Nilai Negatif:</b> {esc(nk['negatif'])}</div>")

    # Ziwei main stars (only if present)
    bu = ident.get("bintang_utama") if isinstance(ident, dict) else None
    if isinstance(bu, dict):
        for lbl, k in (("Bintang Minguo", "bintang_minguo"), ("Istana Minguo", "istana_minguo"),
                       ("Bintang Shen", "bintang_shen"), ("Istana Shen", "istana_shen")):
            if has(bu.get(k)):
                extras.append(f"<div><b>{lbl}:</b> {esc(bu[k])}</div>")

    extras_html = f'<div class="kv">{"".join(extras)}</div>' if extras else ""

    if not pilar_block and not extras_html:
        return ""
    return f"""
<section class="page">
  <h2>Profil Empat Pilar</h2>
  <div class="section">
    {pilar_block}
    {extras_html}
  </div>
</section>
"""


def render_transformasi(data):
    t = safe_get(data, "identitas", "transformasi")
    if not isinstance(t, dict) or not t:
        return ""
    rows = "".join(
        f"<tr><td><b>{esc(k.replace('_', ' ').title())}</b></td><td>{esc(v)}</td></tr>"
        for k, v in t.items() if has(v)
    )
    if not rows:
        return ""
    return f"""
<section class="page">
  <h2>Transformasi (Hua)</h2>
  <table><thead><tr><th style="width:35%">Jenis</th><th>Keterangan</th></tr></thead>
  <tbody>{rows}</tbody></table>
</section>
"""


def render_kepribadian(data):
    x = safe_get(data, "foto_28_xing_qing")
    if not isinstance(x, dict):
        return ""
    isi = x.get("isi")
    if not isi:
        return ""
    if isinstance(isi, list):
        body = "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in isi if has(p)) + "</ul>"
    else:
        body = f"<p>{esc(isi)}</p>"
    judul = x.get("judul") or "Sifat dan Watak (Xing Qing)"
    return f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>'


def render_da_yun(data):
    dy = safe_get(data, "foto_31_si_zhu_ming_pan", "da_yun")
    if not isinstance(dy, list) or not dy:
        return ""
    rows = []
    for fase in dy:
        if not isinstance(fase, dict):
            continue
        usia = fase.get("usia", "")
        gz = fase.get("ganzhi", "")
        rows.append(f"<tr><td>{esc(usia)}</td><td>{esc(gz)}</td></tr>")
    if not rows:
        return ""
    return f"""
<section class="page">
  <h2>Da Yun — Fase 10 Tahunan</h2>
  <table><thead><tr><th style="width:25%">Usia</th><th>Ganzhi</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
"""


def render_rezeki(data):
    parts = []
    cf = safe_get(data, "foto_26_cai_fu")
    if isinstance(cf, dict):
        judul = cf.get("judul") or "Kekayaan Harta (Cai Fu)"
        block = f"<h2>{esc(judul)}</h2>"
        for label, key in (("Harta Sampingan", "harta_sampingan"), ("Harta Tetap", "harta_tetap")):
            sub = cf.get(key)
            if isinstance(sub, dict):
                kvs = []
                if has(sub.get("sumber")):
                    kvs.append(f"<p><b>Sumber:</b> {esc(sub['sumber'])}</p>")
                if has(sub.get("hubungan")):
                    kvs.append(f"<p><b>Hubungan:</b> {esc(sub['hubungan'])}</p>")
                if kvs:
                    block += f'<div class="section"><h3>{label}</h3>{"".join(kvs)}</div>'
        if has(cf.get("catatan")):
            block += f'<p class="footer-note">{esc(cf["catatan"])}</p>'
        parts.append(f'<section class="page">{block}</section>')

    cb = safe_get(data, "foto_18_cai_bo")
    if isinstance(cb, dict) and has(cb.get("isi")):
        parts.append(
            f'<section class="page"><h2>{esc(cb.get("judul") or "Keuangan (Cai Bo)")}</h2>'
            f'<div class="section"><p>{esc(cb["isi"])}</p></div></section>'
        )
    return "".join(parts)


def render_kesehatan(data):
    organ = safe_get(data, "foto_31_si_zhu_ming_pan", "kesehatan_organ")
    if not isinstance(organ, list) or not organ:
        # fallback: ji_e
        je = safe_get(data, "foto_20_ji_e")
        if isinstance(je, dict) and has(je.get("isi")):
            return (f'<section class="page"><h2>{esc(je.get("judul") or "Kesehatan")}</h2>'
                    f'<div class="section"><p>{esc(je["isi"])}</p></div></section>')
        return ""
    rows = []
    for o in organ:
        if not isinstance(o, dict):
            continue
        rows.append(f"<tr><td>{esc(o.get('organ',''))}</td><td>{esc(o.get('kode',''))}</td></tr>")
    je = safe_get(data, "foto_20_ji_e")
    extra = ""
    if isinstance(je, dict) and has(je.get("isi")):
        extra = f'<div class="section"><h3>{esc(je.get("judul") or "Catatan Kesehatan")}</h3><p>{esc(je["isi"])}</p></div>'
    return f"""
<section class="page">
  <h2>Kesehatan Organ</h2>
  <table><thead><tr><th>Organ</th><th style="width:25%">Kode</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
  {extra}
</section>
"""


def render_karir(data):
    parts = []
    sy = safe_get(data, "foto_25_shi_ye")
    if isinstance(sy, dict):
        judul = sy.get("judul") or "Pekerjaan dan Usaha (Shi Ye)"
        body = ""
        for k, v in sy.items():
            if k in ("judul", "bagian"):
                continue
            if has(v):
                body += f"<p><b>{esc(k.replace('_',' ').title())}:</b> {esc(v)}</p>"
        if body:
            parts.append(f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>')
    gl = safe_get(data, "foto_17_guan_lu")
    if isinstance(gl, dict) and has(gl.get("isi")):
        parts.append(f'<section class="page"><h2>{esc(gl.get("judul") or "Jabatan dan Karir")}</h2>'
                     f'<div class="section"><p>{esc(gl["isi"])}</p></div></section>')
    return "".join(parts)


def render_feng_shui(data):
    yz = safe_get(data, "foto_27_yang_zhai")
    if not isinstance(yz, dict):
        return ""
    fs = yz.get("feng_shui")
    if not isinstance(fs, dict) or not fs:
        return ""
    rows = "".join(
        f"<tr><td><b>{esc(k.replace('_',' ').title())}</b></td><td>{esc(v)}</td></tr>"
        for k, v in fs.items() if has(v)
    )
    if not rows:
        return ""
    judul = yz.get("judul") or "Feng Shui Rumah (Yang Zhai)"
    return f'<section class="page"><h2>{esc(judul)}</h2><table>{rows}</table></section>'


def render_shen_sha(data):
    ss = safe_get(data, "foto_29_shen_sha")
    if not isinstance(ss, dict):
        return ""
    bintang = ss.get("bintang")
    if not isinstance(bintang, list) or not bintang:
        return ""
    items = []
    for b in bintang:
        if not isinstance(b, dict):
            continue
        n = b.get("nama"); e = b.get("efek")
        if has(n) or has(e):
            items.append(f"<li><b>{esc(n)}</b>{(' — ' + esc(e)) if has(e) else ''}</li>")
    if not items:
        return ""
    judul = ss.get("judul") or "Bintang Nasib (Shen Sha)"
    return f'<section class="page"><h2>{esc(judul)}</h2><div class="section"><ul>{"".join(items)}</ul></div></section>'


def render_liu_nian(data):
    sections = []
    for key, val in data.items():
        if "liu_nian" in key and isinstance(val, dict) and has(val.get("isi")):
            sections.append(val)
    sections.sort(key=lambda x: x.get("tahun_masehi", 0))
    if not sections:
        return ""
    parts = []
    for s in sections:
        meta = []
        if has(s.get("tahun_masehi")): meta.append(f"Tahun {s['tahun_masehi']}")
        if has(s.get("usia")): meta.append(f"Usia {s['usia']}")
        if has(s.get("ganzhi")): meta.append(f"Ganzhi {s['ganzhi']}")
        meta_html = f'<div class="muted">{esc(" · ".join(meta))}</div>' if meta else ""
        judul = s.get("judul") or "Liu Nian"
        parts.append(f'<section class="page"><h2>{esc(judul)}</h2>'
                     f'{meta_html}<div class="section"><p>{esc(s["isi"])}</p></div></section>')
    return "".join(parts)


def render_tabel_liu_nian(data):
    parts = []
    for key, val in data.items():
        if not (isinstance(val, dict) and "tabel_tahunan" in val):
            continue
        tabel = val["tabel_tahunan"]
        if not isinstance(tabel, list) or not tabel:
            continue
        rows = []
        for r in tabel:
            if not isinstance(r, dict):
                continue
            rows.append(
                "<tr>"
                f"<td>{esc(r.get('usia',''))}</td>"
                f"<td>{esc(r.get('ganzhi',''))}</td>"
                f"<td>{esc(r.get('hubungan',''))}</td>"
                f"<td>{esc(r.get('fase',''))}</td>"
                "</tr>"
            )
        if not rows:
            continue
        judul = val.get("judul") or "Tabel Liu Nian"
        meta = []
        if has(val.get("rentang_usia")): meta.append(f"Rentang Usia {val['rentang_usia']}")
        if has(val.get("da_yun")): meta.append(f"Da Yun: {val['da_yun']}")
        if has(val.get("rentang_da_yun")): meta.append(f"Rentang Da Yun: {val['rentang_da_yun']}")
        meta_html = f'<div class="muted">{esc(" · ".join(meta))}</div>' if meta else ""
        parts.append(f"""
<section class="page">
  <h2>{esc(judul)}</h2>
  {meta_html}
  <table><thead><tr><th>Usia</th><th>Ganzhi</th><th>Hubungan</th><th>Fase</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
""")
    return "".join(parts)


def render_palace_pages(data):
    """Render istana / pelengkap detail (foto_11..foto_24 narratives)."""
    mapping = [
        ("foto_11_su_ming",   "Nasib Takdir (Su Ming)"),
        ("foto_12_fu_de",     "Keberuntungan dan Kebajikan (Fu De)"),
        ("foto_14_tian_zhai", "Tanah dan Rumah (Tian Zhai)"),
        ("foto_15_pu_yi",     "Pelayan/Bawahan (Pu Yi)"),
        ("foto_16_fu_mu",     "Orang Tua (Fu Mu)"),
        ("foto_19_qian_yi",   "Perpindahan (Qian Yi)"),
        ("foto_21_fu_qi",     "Suami Istri (Fu Qi)"),
        ("foto_22_zi_nu",     "Anak (Zi Nu)"),
        ("foto_24_ming_gong", "Istana Nasib (Ming Gong)"),
    ]
    parts = []
    for key, default_title in mapping:
        v = safe_get(data, key)
        if not isinstance(v, dict):
            continue
        body = ""
        if has(v.get("isi")):
            isi = v["isi"]
            if isinstance(isi, list):
                body = "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in isi if has(p)) + "</ul>"
            else:
                body = f"<p>{esc(isi)}</p>"
        # extra structured fields (mis. foto_23 punya pantangan/yang_cocok dll)
        for k, val in v.items():
            if k in ("judul", "bagian", "isi"):
                continue
            if has(val) and isinstance(val, str):
                body += f"<p><b>{esc(k.replace('_',' ').title())}:</b> {esc(val)}</p>"
        if not body:
            continue
        judul = v.get("judul") or default_title
        parts.append(f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>')
    # foto_23 (pasangan) ditangani lewat loop di atas? key tidak di mapping; tambah eksplisit
    fp = safe_get(data, "foto_23_hun_pei")
    if isinstance(fp, dict):
        body = ""
        for k, val in fp.items():
            if k in ("judul", "bagian"):
                continue
            if has(val) and isinstance(val, str):
                body += f"<p><b>{esc(k.replace('_',' ').title())}:</b> {esc(val)}</p>"
        if body:
            judul = fp.get("judul") or "Pasangan (Hun Pei)"
            parts.append(f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>')
    return "".join(parts)


def render_gu_shu_yun(data):
    g = safe_get(data, "foto_09_gu_shu_yun")
    if not isinstance(g, dict):
        return ""
    isi = g.get("isi")
    if not isi:
        return ""
    if isinstance(isi, list):
        body = "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in isi if has(p)) + "</ul>"
    else:
        body = f"<p>{esc(isi)}</p>"
    judul = g.get("judul") or "Kutipan Kitab Klasik"
    return f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>'


def render_kesimpulan(data):
    q = safe_get(data, "foto_30_quan_ju_zong_lun")
    if not isinstance(q, dict):
        return ""
    isi = q.get("isi")
    if not isi:
        return ""
    if isinstance(isi, list):
        body = "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in isi if has(p)) + "</ul>"
    else:
        body = f"<p>{esc(isi)}</p>"
    judul = q.get("judul") or "Kesimpulan Keseluruhan"
    return f'<section class="page"><h2>{esc(judul)}</h2><div class="section">{body}</div></section>'


# ---------------------------------------------------------------------------
# Master assembly
# ---------------------------------------------------------------------------
def build_html(data):
    sections = [
        render_cover(data),
        render_profil(data),
        render_transformasi(data),
        render_kepribadian(data),
        render_da_yun(data),
        render_rezeki(data),
        render_kesehatan(data),
        render_karir(data),
        render_feng_shui(data),
        render_shen_sha(data),
        render_palace_pages(data),
        render_liu_nian(data),
        render_tabel_liu_nian(data),
        render_gu_shu_yun(data),
        render_kesimpulan(data),
    ]
    body = "\n".join(s for s in sections if s)
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/>
<title>Laporan BaZi</title>
<style>{MASTER_CSS}</style>
</head><body>
{body}
</body></html>"""


# ---------------------------------------------------------------------------
# PDF conversion (Chrome headless)
# ---------------------------------------------------------------------------
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    raise RuntimeError("Chrome/Edge tidak ditemukan untuk render PDF.")


def html_to_pdf(html_path: Path, pdf_path: Path):
    chrome = find_chrome()
    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, timeout=180)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python bazi_pdf.py <input.json> [output.pdf]")
        sys.exit(1)

    in_path = Path(sys.argv[1]).resolve()
    if not in_path.exists():
        print(f"ERROR: file tidak ditemukan: {in_path}")
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[1/4] Loaded JSON: {in_path.name}")

    errors = validate(data)
    if errors:
        print("VALIDASI GAGAL — field kritis tidak ada di JSON:")
        for e in errors:
            print(e)
        sys.exit(2)
    print("[2/4] Validasi 7 field kritis: OK")

    html_str = build_html(data)
    out_pdf = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else in_path.with_suffix(".pdf")
    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(html_str, encoding="utf-8")
    print(f"[3/4] HTML ditulis: {html_path}")

    html_to_pdf(html_path, out_pdf)
    print(f"[4/4] PDF: {out_pdf}")


if __name__ == "__main__":
    main()
