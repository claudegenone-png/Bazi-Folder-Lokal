"""Mass replace Michele identity -> Hu Li Li identity across 23 pages.
Michele:  22 Juli 1995 14:48 / 乙亥 癸未 甲寅 辛未 / DM 甲木 / Babi
Hu Li Li: 5 Mei 1964 00:05 / 甲辰 戊辰 甲寅 甲子 / DM 甲木 / Naga
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DIR = Path(__file__).parent

REPLACEMENTS = [
    # ===== COVER CSS — widen panel + smaller font + nowrap rows =====
    ('padding: 5mm 8mm;\n    margin: 4mm auto 0;\n    max-width: 130mm;',
     'padding: 5mm 9mm;\n    margin: 4mm auto 0;\n    max-width: 158mm;'),
    ('font-size: 10pt;\n    line-height: 1.7;',
     'font-size: 9pt;\n    line-height: 1.65;'),
    ('grid-template-columns: 36mm 4mm 1fr;\n    gap: 0;\n    align-items: baseline;\n  }',
     'grid-template-columns: 50mm 3mm 1fr;\n    gap: 0;\n    align-items: baseline;\n    white-space: nowrap;\n  }'),
    ('letter-spacing: 0.5px;\n    font-size: 9.5pt;\n  }\n  .cv-info-panel .colon',
     'letter-spacing: 0.3px;\n    font-size: 8.5pt;\n  }\n  .cv-info-panel .colon'),
    ('color: white;\n    font-weight: 500;\n  }\n  .cv-info-panel .val .hz',
     'color: white;\n    font-weight: 500;\n    overflow: hidden;\n    text-overflow: ellipsis;\n  }\n  .cv-info-panel .val .hz'),
    ('color: #E5D3A1; font-style: italic;\n    font-weight: 400; font-size: 9pt;',
     'color: #E5D3A1; font-style: italic;\n    font-weight: 400; font-size: 8pt;'),

    # ===== TITLE =====
    ('<title>Michele', '<title>Hu Li Li'),

    # ===== SHIO (Naga / Dragon) =====
    ('src="Babi-Merah.svg"', 'src="Naga-Merah.svg"'),
    ('src="Babi-Hitam.svg"', 'src="Naga-Hitam.svg"'),
    ('alt="Babi"', 'alt="Naga"'),

    # ===== SUBJECT-BAR =====
    ('Michele · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">亥 Babi</span>',
     'Hu Li Li · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">辰 Naga</span>'),

    # ===== SUBJECT-DETAIL =====
    ('22 Juli 1995 · 14:48 · Wanita · 民國 84 年 6 月 25 日',
     '5 Mei 1964 · 00:05 · Wanita · 民國 53 年 3 月 24 日'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 tahun',
     '5 Mei 1964 · 00:05 · Wanita · Umur 61 tahun'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 · 大運 sekarang: <strong style="color:var(--red)">己丑 (土)</strong>',
     '5 Mei 1964 · 00:05 · Wanita · Umur 61 · 大運 sekarang: <strong style="color:var(--red)">壬戌 (水)</strong>'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30',
     '5 Mei 1964 · 00:05 · Wanita · Umur 61'),

    # ===== FOOTER =====
    ('<span>Michele · Ramalan 命</span>', '<span>Hu Li Li · Ramalan 命</span>'),

    # ===== COVER name =====
    ('<div class="cv-name">Michele</div>', '<div class="cv-name">Hu Li Li</div>'),
    ('<div class="cv-name-cn">米雪</div>', '<div class="cv-name-cn">胡莉莉</div>'),

    # ===== COVER info-panel rows (Michele 3-baris lama → 3-baris baru) =====
    ('<div class="row"><span class="lbl">Tanggal Lahir</span><span class="colon">:</span><span class="val">22 Juli 1995 <em>(Sabtu)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 14:48 <em>(siang)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Kalender Lunar</span><span class="colon">:</span><span class="val">25 / bulan 6 / tahun Yi Hai <span class="hz">乙亥</span></span></div>',
     '<div class="row"><span class="lbl">Tanggal Lahir (Indonesia)</span><span class="colon">:</span><span class="val">5 Mei 1964 <em>(Selasa)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Tanggal Lahir (Tionghoa)</span><span class="colon">:</span><span class="val">tanggal 24 bulan 3 tahun <span class="hz">甲辰</span> <em>(Jia Chen · 1964)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 00:05 <em>(dini hari · 子時)</em></span></div>'),
    ('<span class="hz">亥</span> Babi', '<span class="hz">辰</span> Naga'),
    ('Kayu &amp; Air <span class="hz">木 水</span>', 'Api &amp; Tanah <span class="hz">火 土</span>'),

    # ===== COVER metadata =====
    ('<span class="val">乙亥年 癸未月<span class="id">22 Juli 1995 · 14:48</span></span>',
     '<span class="val">甲辰年 戊辰月<span class="id">5 Mei 1964 · 00:05</span></span>'),
    ('<span class="val">甲木 · 傷官格<span class="id">Kayu Pohon Besar · Shang Guan Ge</span></span>',
     '<span class="val">甲木 · 偏財格<span class="id">Kayu Pohon Besar · Pian Cai Ge</span></span>'),

    # ===== CSS ::after content (cover badge) =====
    ("content: '亥 · BABI'", "content: '辰 · NAGA'"),

    # ===== Misc identity references =====
    ('Michele · Profil', 'Hu Li Li · Profil'),
    ('— Michele', '— Hu Li Li'),
    ('subjek: Michele', 'subjek: Hu Li Li'),
    ('Subjek: Michele', 'Subjek: Hu Li Li'),

    # ===== Format global swap (Michele=傷官格 → Hu Li Li=偏財格) =====
    ('傷官格', '偏財格'),
    ('Shang Guan Ge', 'Pian Cai Ge'),
    ('Pemikir Kreatif', 'Penjala Wealth'),
    ('Pencipta Kreatif', 'Penjala Wealth'),
]

count = 0
for page in sorted(DIR.glob("page_*.html")):
    html = page.read_text(encoding="utf-8")
    original = html
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    if html != original:
        page.write_text(html, encoding="utf-8")
        count += 1
        print(f"  updated: {page.name}")

idx = DIR / "index.html"
if idx.exists():
    h = idx.read_text(encoding="utf-8")
    o = h
    for old, new in REPLACEMENTS:
        h = h.replace(old, new)
    if h != o:
        idx.write_text(h, encoding="utf-8")
        count += 1
        print(f"  updated: index.html")

print(f"\nUpdated identity in {count} files")
